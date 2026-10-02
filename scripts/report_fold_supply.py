"""Explicit ideal replenishment with separate external-input energy ledgers."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.integrate import RK45

try:
    from .report_fold_active_multiscale import BASE_SIZES, EDGES, TREE, initial_state, measure
    from .report_fold_active_multiscale import rhs as active_rhs
    from .report_fold_dynamics import Q0, vector
    from .report_fold_hierarchy import compile_hierarchy
    from .report_fold_kinematics import scalar
    from .report_fold_multiscale import configuration
except ImportError:
    from report_fold_active_multiscale import BASE_SIZES, EDGES, TREE, initial_state, measure
    from report_fold_active_multiscale import rhs as active_rhs
    from report_fold_dynamics import Q0, vector
    from report_fold_hierarchy import compile_hierarchy
    from report_fold_kinematics import scalar
    from report_fold_multiscale import configuration


def power_setting(value):
    value = scalar(value, "power_density")
    if not 0 <= value <= 1e-4:
        raise ValueError("power_density must be in [0,1e-4] W at unit size")
    return value


def rhs(y, sizes=BASE_SIZES, *, power_density=6e-6):
    sizes, _ = configuration(sizes, EDGES)
    if len(sizes) != 4:
        raise ValueError("four nodes required")
    power_density = power_setting(power_density)
    y = vector(y, 48, "supplied network state")
    result = np.r_[active_rhs(y[:44], sizes, EDGES), np.zeros(4)]
    s = np.array(sizes)
    reserve = y[:36].reshape(4, 9)[:, 4]
    supplied = power_density * s**2 * np.maximum(0, 1 - reserve / (2e-5 * s**3))
    result[:36].reshape(4, 9)[:, 4] += supplied
    result[44:] = supplied
    return result


def simulate(
    duration=20.0, *, power_density=6e-6, max_step=0.05, rtol=1e-8, rest=False, initial=None
):
    duration, max_step, rtol = (
        scalar(v, n) for v, n in ((duration, "duration"), (max_step, "max_step"), (rtol, "rtol"))
    )
    power_density = power_setting(power_density)
    if not 0 < duration <= 20 or not 0 < max_step <= 0.1 or not 1e-12 <= rtol <= 1e-6:
        raise ValueError("invalid duration, max_step or rtol")
    if type(rest) is not bool:
        raise ValueError("rest must be boolean")
    sizes = np.array(BASE_SIZES)
    layout = compile_hierarchy(4, EDGES, TREE)
    y = (
        np.r_[initial_state(BASE_SIZES, EDGES), np.zeros(4)]
        if initial is None
        else vector(initial, 48, "initial").copy()
    )
    if rest:
        y[:36].reshape(4, 9)[:, :4] = np.tile(np.r_[Q0, 0, 0], (4, 1))
    rhs(y, power_density=power_density)
    capacity = 2e-5 * sizes**3
    r0 = y[:36].reshape(4, 9)[:, 4].copy()
    if np.any(r0 > capacity) or np.any(y[:36].reshape(4, 9)[:, 5:] != 0) or np.any(y[36:] != 0):
        raise ValueError("initial reserves must not exceed capacity; initial ledgers must be zero")
    start = y.copy()
    e0, u0, _, groups0 = measure(y[:44], BASE_SIZES, EDGES, layout)
    maxima = {
        k: np.zeros(4)
        for k in ("node_mechanical_residual_j", "node_reservoir_residual_j", "edge_residual_j")
    }
    groupmax = dict.fromkeys(groups0, 0.0)
    diagnostic = dict.fromkeys(groups0, 0.0)
    min_reserve, upper_violation = r0.copy(), np.zeros(4)
    min_input_step, input_violation, power_violation = np.zeros(4), np.zeros(4), np.zeros(4)
    previous_input = np.zeros(4)
    samples, late_energy, late_rates = [], [], []

    def record(t, state, save):
        nonlocal \
            min_reserve, \
            upper_violation, \
            min_input_step, \
            input_violation, \
            power_violation, \
            previous_input
        energy, potential, incident, groups = measure(state[:44], BASE_SIZES, EDGES, layout)
        b, supplied = state[:36].reshape(4, 9), state[44:]
        residuals = dict(
            node_mechanical_residual_j=energy - e0 - b[:, 5] + b[:, 6] - incident,
            node_reservoir_residual_j=b[:, 4] - r0 + b[:, 5] + b[:, 7] + b[:, 8] - supplied,
            edge_residual_j=potential - u0 + state[36:44].reshape(4, 2).sum(axis=1),
        )
        for key, value in residuals.items():
            maxima[key] = np.maximum(maxima[key], abs(value))
        for path, account in groups.items():
            received = float(supplied[layout["groups"][path]].sum())
            missing = (
                account["accounted_energy_j"]
                - groups0[path]["accounted_energy_j"]
                - account["boundary_work_j"]
            )
            account.update(input_j=received, residual_j=missing - received)
            groupmax[path] = max(groupmax[path], abs(missing - received))
            diagnostic[path] = max(diagnostic[path], abs(missing))
        min_reserve = np.minimum(min_reserve, b[:, 4])
        upper_violation = np.maximum(upper_violation, b[:, 4] - capacity)
        min_input_step = np.minimum(min_input_step, supplied - previous_input)
        previous_input = supplied.copy()
        input_violation = np.maximum(input_violation, supplied - power_density * sizes**2 * t)
        power = power_density * sizes**2 * np.maximum(0, 1 - b[:, 4] / capacity)
        power_violation = np.maximum(
            power_violation, np.maximum(-power, power - power_density * sizes**2)
        )
        mechanical = float(energy.sum() + potential.sum())
        if t >= 0.75 * duration:
            late_energy.append(mechanical)
            late_rates.append(float(np.linalg.norm(b[:, 2:4])))
        if save:
            samples.append(
                dict(
                    time_s=float(t),
                    q=b[:, :2].tolist(),
                    rates=b[:, 2:4].tolist(),
                    mechanical_j=energy.tolist(),
                    total_mechanical_j=mechanical,
                    reserve_j=b[:, 4].tolist(),
                    work_j=b[:, 5].tolist(),
                    damping_loss_j=b[:, 6].tolist(),
                    conversion_loss_j=b[:, 7].tolist(),
                    leakage_loss_j=b[:, 8].tolist(),
                    input_j=supplied.tolist(),
                    input_power_w=power.tolist(),
                    edge_potential_j=potential.tolist(),
                    groups=groups,
                )
            )

    record(0, y, True)
    atol = np.r_[np.tile([1e-11] * 4 + [1e-16] * 5, 4), np.full(12, 1e-16)]
    solver = RK45(
        lambda t, state: rhs(state, power_density=power_density),
        0,
        y,
        duration,
        max_step=max_step,
        rtol=rtol,
        atol=atol,
        first_step=min(max_step, duration),
    )
    status, reason, last_t, steps = "completed", None, 0.0, 0
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
        steps += 1
        record(last_t, y, last_t >= samples[-1]["time_s"] + 1 or solver.status == "finished")
    if samples[-1]["time_s"] != last_t:
        record(last_t, y, True)
    blocks = y[:36].reshape(4, 9)
    return dict(
        settings=dict(
            duration_s=duration,
            power_density_w=power_density,
            max_step_s=max_step,
            rtol=rtol,
            atol=atol.tolist(),
            sizes=BASE_SIZES,
            rest=rest,
        ),
        termination=dict(status=status, reason=reason, last_accepted_time_s=last_t),
        initial_state=start.tolist(),
        final_state=y.tolist(),
        accepted_steps=steps,
        function_evaluations=solver.nfev,
        samples=samples,
        max_group_residual_j=groupmax,
        missing_input_diagnostic=dict(
            kind="postprocessing omission; same powered trajectory", max_group_residual_j=diagnostic
        ),
        minimum_reserve_j=min_reserve.tolist(),
        maximum_reserve_upper_violation_j=upper_violation.tolist(),
        minimum_input_step_j=min_input_step.tolist(),
        maximum_input_budget_violation_j=input_violation.tolist(),
        maximum_power_budget_violation_w=power_violation.tolist(),
        finite_supply_margin_j=(0.8 * (r0 + y[44:]) - blocks[:, 5]).tolist(),
        total_received_j=float(y[44:].sum()),
        final_total_mechanical_j=samples[-1]["total_mechanical_j"],
        late_window=dict(
            start_s=0.75 * duration,
            endpoint_count=len(late_energy),
            mechanical_range_j=None if not late_energy else [min(late_energy), max(late_energy)],
            rate_norm_range=None if not late_rates else [min(late_rates), max(late_rates)],
        ),
        **{"max_" + key: value.tolist() for key, value in maxima.items()},
    )


def report():
    names = (
        "supply",
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
    sources = {
        f"report_fold_{n}.py": hashlib.sha256(
            Path(__file__).with_name(f"report_fold_{n}.py").read_text(encoding="utf-8").encode()
        ).hexdigest()
        for n in names
    }
    cases = {}
    for name, options in (
        ("powered", {}),
        ("source_off", {"power_density": 0}),
        ("fine_powered", {"max_step": 0.025, "rtol": 1e-9}),
    ):
        duration = (
            cases["powered"]["termination"]["last_accepted_time_s"]
            if name == "fine_powered"
            else 20.0
        )
        print(f"Running {name}: {duration} seconds", flush=True)
        cases[name] = simulate(duration, **options)
        checkpoint_key = hashlib.sha256(
            json.dumps(
                dict(sources=sources, name=name, duration=duration, options=options), sort_keys=True
            ).encode()
        ).hexdigest()[:20]
        checkpoint = (
            Path(__file__).resolve().parents[1]
            / "artifacts"
            / "fold-supply"
            / f"{name}-{checkpoint_key}.json"
        )
        checkpoint.parent.mkdir(parents=True, exist_ok=True)
        checkpoint.write_text(
            json.dumps(dict(sources=sources, result=cases[name]), indent=2) + "\n", encoding="utf-8"
        )
        print(f"Completed {name}: {cases[name]['termination']}", flush=True)
    a, b = cases["powered"], cases["fine_powered"]
    matched = (
        b["termination"]["status"] == "completed"
        and a["termination"]["last_accepted_time_s"] == b["termination"]["last_accepted_time_s"]
    )
    return dict(
        schema=1,
        scope="ideal external source, 20-second supplied graph audit",
        sources=sources,
        cases=cases,
        refinement=dict(
            fine_settings=b["settings"],
            fine_termination=b["termination"],
            matched_final_time_s=a["termination"]["last_accepted_time_s"] if matched else None,
            absolute_state_differences=None
            if not matched
            else abs(np.array(a["final_state"]) - b["final_state"]).tolist(),
        ),
        calibrated_material=False,
        sustained_breathing=False,
        ideal_external_source=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
