"""Bounded duration and depletion audit of the existing finite-source graph."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.integrate import RK45

try:
    from .report_fold_active_multiscale import BASE_SIZES, EDGES, TREE, initial_state, measure, rhs
    from .report_fold_dynamics import Q0
    from .report_fold_hierarchy import compile_hierarchy
    from .report_fold_kinematics import scalar
except ImportError:
    from report_fold_active_multiscale import BASE_SIZES, EDGES, TREE, initial_state, measure, rhs
    from report_fold_dynamics import Q0
    from report_fold_hierarchy import compile_hierarchy
    from report_fold_kinematics import scalar


def bounds(time_s, gain=4.0, reserve0=None):
    """Analytical upper reserve fraction and latest loss-dominated time for gain 4."""
    sizes = np.array(BASE_SIZES)
    reserve0 = 2e-5 * sizes**3 if reserve0 is None else np.asarray(reserve0)
    crossover = (
        np.zeros(4)
        if gain <= 1
        else sizes / 0.15 * np.maximum(0, np.log(reserve0 * (gain - 1) / (1e-5 * sizes**3)))
    )
    return dict(
        reserve_fraction_upper=np.exp(-0.15 * time_s / np.array(BASE_SIZES)).tolist(),
        damping_dominates_by_s=crossover.tolist(),
    )


def simulate(
    duration=60.0, *, gain=4.0, rest=False, max_step=0.05, rtol=1e-8, atol_factor=1.0, initial=None
):
    duration, max_step, rtol, atol_factor = (
        scalar(v, n)
        for v, n in (
            (duration, "duration"),
            (max_step, "max_step"),
            (rtol, "rtol"),
            (atol_factor, "atol_factor"),
        )
    )
    if not 0 < duration <= 60 or not 0 < max_step <= 0.1 or not 1e-12 <= rtol <= 1e-6:
        raise ValueError("duration in (0,60], max_step in (0,.1], rtol in [1e-12,1e-6] required")
    if not 1e-4 <= atol_factor <= 1 or type(rest) is not bool:
        raise ValueError("invalid tolerance factor or rest flag")
    sizes, edges = BASE_SIZES, EDGES
    layout = compile_hierarchy(4, edges, TREE)
    y = initial_state(sizes, edges) if initial is None else np.array(initial, dtype=float).copy()
    if rest:
        y[:36].reshape(4, 9)[:, :4] = np.tile(np.r_[Q0, 0, 0], (4, 1))
    # Validate initial data before solver construction; only later stage failures are terminations.
    rhs(y, sizes, edges, gain=gain)
    e0, u0, _, groups0 = measure(y, sizes, edges, layout)
    r0 = y[:36].reshape(4, 9)[:, 4].copy()
    if np.any(r0 <= 0) or np.any(y[:36].reshape(4, 9)[:, 5:] != 0) or np.any(y[36:] != 0):
        raise ValueError("positive initial reserves and zero initial ledgers required")
    start_state = y.copy()
    crossover_time = max(bounds(0, gain, r0)["damping_dominates_by_s"])
    max_late_increase, late_intervals = 0.0, 0
    maxima = {
        k: np.zeros(4)
        for k in ("node_mechanical_residual_j", "node_reservoir_residual_j", "edge_residual_j")
    }
    groupmax = dict.fromkeys(groups0, 0.0)
    samples, brackets = [], [None] * 4
    previous_t, previous_r = 0.0, r0.copy()
    max_reserve_increase, max_mechanical_increase = 0.0, 0.0
    previous_mechanical = float(e0.sum() + u0.sum())
    accepted_steps = 0

    def record(t, state, save):
        nonlocal previous_t, previous_r, previous_mechanical, max_late_increase, late_intervals
        nonlocal max_reserve_increase, max_mechanical_increase
        energy, potential, incident, groups = measure(state, sizes, edges, layout)
        b, work = state[:36].reshape(4, 9), state[36:].reshape(4, 2)
        residuals = dict(
            node_mechanical_residual_j=energy - e0 - b[:, 5] + b[:, 6] - incident,
            node_reservoir_residual_j=b[:, 4] - r0 + b[:, 5] + b[:, 7] + b[:, 8],
            edge_residual_j=potential - u0 + work.sum(axis=1),
        )
        for key, value in residuals.items():
            maxima[key] = np.maximum(maxima[key], abs(value))
        for path, account in groups.items():
            account["residual_j"] = (
                account["accounted_energy_j"]
                - groups0[path]["accounted_energy_j"]
                - account["boundary_work_j"]
            )
            groupmax[path] = max(groupmax[path], abs(account["residual_j"]))
        for i in range(4):
            if brackets[i] is None and previous_r[i] > 0.01 * r0[i] >= b[i, 4]:
                brackets[i] = [previous_t, float(t)]
        total_mechanical = float(energy.sum() + potential.sum())
        if previous_t >= crossover_time and t > previous_t:
            max_late_increase = max(max_late_increase, total_mechanical - previous_mechanical)
            late_intervals += 1
        max_mechanical_increase = max(
            max_mechanical_increase, total_mechanical - previous_mechanical
        )
        max_reserve_increase = max(max_reserve_increase, float(np.max(b[:, 4] - previous_r)))
        previous_t, previous_r, previous_mechanical = float(t), b[:, 4].copy(), total_mechanical
        if save:
            samples.append(
                dict(
                    time_s=float(t),
                    q=b[:, :2].tolist(),
                    rates=b[:, 2:4].tolist(),
                    mechanical_j=energy.tolist(),
                    reserve_j=b[:, 4].tolist(),
                    work_j=b[:, 5].tolist(),
                    damping_loss_j=b[:, 6].tolist(),
                    conversion_loss_j=b[:, 7].tolist(),
                    leakage_loss_j=b[:, 8].tolist(),
                    edge_potential_j=potential.tolist(),
                    total_mechanical_j=total_mechanical,
                    groups=groups,
                )
            )

    record(0, y, True)
    atol = np.r_[np.tile([1e-11] * 4 + [1e-16] * 5, 4), np.full(8, 1e-16)] * atol_factor
    solver = RK45(
        lambda t, state: rhs(state, sizes, edges, gain=gain),
        0,
        y,
        duration,
        max_step=max_step,
        rtol=rtol,
        atol=atol,
        first_step=min(max_step, duration),
    )
    status, reason, last_t = "completed", None, 0.0
    while solver.status == "running":
        try:
            message = solver.step()
        except ValueError as error:
            if not str(error).startswith(
                ("outside declared scope", "negative reservoir", "velocity outside numerical scope")
            ):
                raise
            status, reason = "scope_termination", str(error)
            break
        if solver.status == "failed":
            status, reason = "solver_failure", message
            break
        y, last_t = solver.y.copy(), float(solver.t)
        accepted_steps += 1
        record(last_t, y, last_t >= samples[-1]["time_s"] + 1 or solver.status == "finished")
    if samples[-1]["time_s"] != last_t:
        record(last_t, y, True)
    b = y[:36].reshape(4, 9)
    return dict(
        settings=dict(
            duration_s=duration,
            gain=gain,
            rest=rest,
            max_step_s=max_step,
            rtol=rtol,
            atol=atol.tolist(),
            sizes=sizes,
        ),
        termination=dict(status=status, reason=reason, last_accepted_time_s=last_t),
        initial_state=start_state.tolist(),
        max_post_crossover_mechanical_step_increase_j=max_late_increase,
        post_crossover_intervals=late_intervals,
        accepted_steps=accepted_steps,
        function_evaluations=solver.nfev,
        final_state=y.tolist(),
        final_reserve_fraction=(b[:, 4] / r0).tolist(),
        final_total_mechanical_j=previous_mechanical,
        max_reserve_step_increase_j=max_reserve_increase,
        max_mechanical_step_increase_j=max_mechanical_increase,
        finite_supply_margin_j=(0.8 * r0 - b[:, 5]).tolist(),
        depletion_1_percent_brackets_s=brackets,
        max_group_residual_j=groupmax,
        samples=samples,
        analytical_bounds=bounds(last_t, gain, r0),
        **{"max_" + k: v.tolist() for k, v in maxima.items()},
    )


def report():
    cases = {
        name: simulate(gain=gain, rest=rest)
        for name, gain, rest in (("active", 4, False), ("passive", 0, False), ("rest", 4, True))
    }
    end = cases["active"]["termination"]["last_accepted_time_s"]
    fine = simulate(duration=end, max_step=0.025, rtol=1e-9, atol_factor=0.1) if end else None
    matched = fine is not None and fine["termination"]["status"] == "completed"
    difference = (
        abs(
            np.array(cases["active"]["final_state"][:36]).reshape(4, 9)
            - np.array(fine["final_state"][:36]).reshape(4, 9)
        ).tolist()
        if matched
        else None
    )
    names = (
        "duration",
        "active_multiscale",
        "multiscale",
        "scaled_pair",
        "scaling",
        "mapped",
        "hierarchy",
        "network",
        "coupling",
        "reservoir",
        "dynamics",
        "kinematics",
    )
    return dict(
        schema=1,
        scope="60-second finite-source duration audit; no refill or sustained-breathing claim",
        sources={
            f"report_fold_{n}.py": hashlib.sha256(
                Path(__file__).with_name(f"report_fold_{n}.py").read_text(encoding="utf-8").encode()
            ).hexdigest()
            for n in names
        },
        cases=cases,
        refinement=dict(
            fine_settings=None if fine is None else fine["settings"],
            matched_final_time_s=end if matched else None,
            state_component_differences_by_module=difference,
            termination=None if fine is None else fine["termination"],
            max_group_residual_j=None if fine is None else fine["max_group_residual_j"],
        ),
        calibrated_material=False,
        sustained_breathing=False,
        depletion_brackets="first crossing bracket between accepted numerical endpoints; no event interpolation",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                k: {
                    "termination": v["termination"],
                    "reserve": v["final_reserve_fraction"],
                    "root_error": v["max_group_residual_j"]["root"],
                }
                for k, v in result["cases"].items()
            }
        )
    )
