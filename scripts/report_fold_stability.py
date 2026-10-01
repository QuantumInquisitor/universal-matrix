"""Rebased powered continuation and a finite velocity perturbation; no new dynamics."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.integrate import RK45

try:
    from .report_fold_supply import (
        BASE_SIZES,
        EDGES,
        TREE,
        compile_hierarchy,
        measure,
        power_setting,
        rhs,
        scalar,
        vector,
    )
except ImportError:
    from report_fold_supply import (
        BASE_SIZES,
        EDGES,
        TREE,
        compile_hierarchy,
        measure,
        power_setting,
        rhs,
        scalar,
        vector,
    )

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "docs/experiments/fold-supply-summary.json"


def text_hash(path):
    return hashlib.sha256(path.read_text(encoding="utf-8").encode()).hexdigest()


SEED_SHA256 = "db0b76cccb2e7c98f92ef0b467e740347a06c7e7baa1af52886465148f60a27a"


COMPATIBILITY = ROOT / "docs/experiments/fold-seed-compatibility.json"
COMPATIBILITY_SHA256 = "3a5c5cd522ab13bb2ebd7988a5a95f931ed485f5c68a8287527c231fdbfe6c0a"


def compatible_sources(historical):
    """Accept only reviewed source pairs; never relabel historical provenance."""
    current = {name: text_hash(ROOT / "scripts" / name) for name in historical}
    if current == historical:
        return current, None
    if text_hash(COMPATIBILITY) != COMPATIBILITY_SHA256:
        raise ValueError("checkpoint compatibility manifest hash mismatch")
    manifest = json.loads(COMPATIBILITY.read_text(encoding="utf-8"))
    if manifest["seed_sha256"] != SEED_SHA256:
        raise ValueError("checkpoint compatibility seed mismatch")
    transitions = manifest["source_transitions"]
    for name, expected in historical.items():
        if current[name] == expected:
            continue
        accepted = transitions.get(name)
        if accepted is None or (expected, current[name]) != (
            accepted["historical_sha256"],
            accepted["current_sha256"],
        ):
            raise ValueError("checkpoint source hash mismatch: " + name)
        snapshot = ROOT / accepted["historical_snapshot"]
        if text_hash(snapshot) != expected:
            raise ValueError("checkpoint historical source snapshot mismatch: " + name)
    return current, dict(
        path=COMPATIBILITY.relative_to(ROOT).as_posix(),
        normalized_utf8_sha256=COMPATIBILITY_SHA256,
        scope=manifest["scope"],
    )


def load_seed(path=SEED):
    if text_hash(path) != SEED_SHA256:
        raise ValueError("checkpoint content hash mismatch")
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {
        f"report_fold_{n}.py"
        for n in (
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
    }
    if set(data["sources"]) != required:
        raise ValueError("checkpoint source inventory mismatch")
    current_sources, compatibility = compatible_sources(data["sources"])
    case = data["cases"]["powered"]
    if (
        case["termination"]["status"] != "completed"
        or case["termination"]["last_accepted_time_s"] != 20
        or data["refinement"]["matched_final_time_s"] != 20
    ):
        raise ValueError("checkpoint must complete matched 20 seconds")
    if case["settings"]["power_density_w"] != 6e-6 or tuple(case["settings"]["sizes"]) != tuple(
        BASE_SIZES
    ):
        raise ValueError("checkpoint model settings mismatch")
    state = vector(case["final_state"], 48, "checkpoint state").copy()
    rhs(state)
    return (
        state,
        dict(
            path="docs/experiments/fold-supply-summary.json",
            normalized_utf8_sha256=text_hash(path),
            physical_time_s=20.0,
            historical_sources=data["sources"],
            current_sources=current_sources,
            compatibility=compatibility,
        ),
        current_sources,
    )


def prepare(state, velocity_factor=1.0):
    factor = scalar(velocity_factor, "velocity_factor")
    if not 0.99 <= factor <= 1.01:
        raise ValueError("invalid velocity factor")
    y = vector(state, 48, "checkpoint state").copy()
    layout = compile_hierarchy(4, EDGES, TREE)
    before = measure(y[:44], BASE_SIZES, EDGES, layout)[0].sum()
    y[:36].reshape(4, 9)[:, 2:4] *= factor
    after = measure(y[:44], BASE_SIZES, EDGES, layout)[0].sum()
    y[:36].reshape(4, 9)[:, 5:] = 0
    y[36:] = 0
    return y, float(after - before)


def window(samples):
    rows = [s for s in samples if 50 <= s["physical_time_s"] <= 60]
    return dict(
        requested_physical_interval_s=[50, 60],
        covered_physical_interval_s=None
        if not rows
        else [rows[0]["physical_time_s"], rows[-1]["physical_time_s"]],
        complete=bool(
            rows and rows[0]["physical_time_s"] == 50 and rows[-1]["physical_time_s"] == 60
        ),
        sample_count=len(rows),
        mechanical_range_j=None
        if not rows
        else [
            min(s["total_mechanical_j"] for s in rows),
            max(s["total_mechanical_j"] for s in rows),
        ],
        q_ranges=None
        if not rows
        else np.stack(
            [np.min([s["q"] for s in rows], axis=0), np.max([s["q"] for s in rows], axis=0)],
            axis=-1,
        ).tolist(),
        rate_ranges=None
        if not rows
        else np.stack(
            [
                np.min([s["rates"] for s in rows], axis=0),
                np.max([s["rates"] for s in rows], axis=0),
            ],
            axis=-1,
        ).tolist(),
        endpoint_energy_slope_w=None
        if len(rows) < 2
        else (rows[-1]["total_mechanical_j"] - rows[0]["total_mechanical_j"])
        / (rows[-1]["time_s"] - rows[0]["time_s"]),
    )


def simulate(initial, duration=40.0, *, power_density=6e-6, max_step=0.05, rtol=1e-8):
    duration, max_step, rtol = (
        scalar(v, n) for v, n in ((duration, "duration"), (max_step, "max_step"), (rtol, "rtol"))
    )
    power_density = power_setting(power_density)
    if not 0 < duration <= 40 or not 0 < max_step <= 0.1 or not 1e-12 <= rtol <= 1e-6:
        raise ValueError("invalid duration, max_step or rtol")
    sizes = np.array(BASE_SIZES)
    layout = compile_hierarchy(4, EDGES, TREE)
    y = vector(initial, 48, "initial").copy()
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
    samples = []

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
        if save:
            samples.append(
                dict(
                    time_s=float(t),
                    physical_time_s=float(t + 20),
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
        dense = solver.dense_output()
        next_t = (int(round(samples[-1]["time_s"] / 0.25)) + 1) * 0.25
        while next_t <= last_t + 1e-12:
            if next_t > last_t:
                break
            record(next_t, dense(next_t), True)
            next_t += 0.25
        record(last_t, y, False)
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
            physical_start_s=20.0,
            sample_interval_s=0.25,
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
        late_window=window(samples),
        **{"max_" + key: value.tolist() for key, value in maxima.items()},
    )


def compare(a, b):
    aa = {s["time_s"]: s for s in a["samples"]}
    bb = {s["time_s"]: s for s in b["samples"]}
    times = sorted(set(aa) & set(bb))
    return dict(
        common_times_s=times,
        common_physical_times_s=[20 + t for t in times],
        maximum_coordinate_difference=np.max(
            [abs(np.array(aa[t]["q"]) - bb[t]["q"]) for t in times], axis=0
        ).tolist(),
        maximum_rate_difference=np.max(
            [abs(np.array(aa[t]["rates"]) - bb[t]["rates"]) for t in times], axis=0
        ).tolist(),
        maximum_mechanical_difference_j=max(
            abs(aa[t]["total_mechanical_j"] - bb[t]["total_mechanical_j"]) for t in times
        ),
    )


def report():
    seed, provenance, sources = load_seed()
    sources = dict(sources, **{Path(__file__).name: text_hash(Path(__file__))})
    cases = {}
    for name, factor, options in (
        ("baseline", 1.0, {}),
        ("kicked", 1.01, {}),
        ("fine_baseline", 1.0, {"max_step": 0.025, "rtol": 1e-9}),
    ):
        duration = (
            cases["baseline"]["termination"]["last_accepted_time_s"]
            if name == "fine_baseline"
            else 40.0
        )
        initial, kick = prepare(seed, factor)
        settings = dict(duration=duration, **options)
        print(f"Running {name}: {duration} continuation seconds", flush=True)
        result = simulate(initial, **settings)
        result["preparation_energy_j"] = kick
        result["velocity_factor"] = factor
        cases[name] = result
        key = hashlib.sha256(
            json.dumps(
                dict(
                    sources=sources,
                    seed=provenance,
                    name=name,
                    settings=settings,
                    velocity_factor=factor,
                ),
                sort_keys=True,
            ).encode()
        ).hexdigest()[:20]
        path = ROOT / "artifacts/fold-stability" / f"{name}-{key}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                dict(sources=sources, seed=provenance, result=result), indent=2, allow_nan=False
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"Completed {name}: {result['termination']}", flush=True)
    return dict(
        schema=1,
        scope="powered continuation from physical 20 seconds with accounted velocity preparation",
        sources=sources,
        seed=provenance,
        cases=cases,
        perturbation=compare(cases["baseline"], cases["kicked"]),
        refinement=compare(cases["baseline"], cases["fine_baseline"]),
        stable_breathing=False,
        calibrated_material=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
