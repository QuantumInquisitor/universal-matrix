"""Powered unequal-size material graph with explicit reserve and input ledgers."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.integrate import RK45

try:
    from .fold_material_multiscale import mechanical as material_mechanical
    from .fold_material_multiscale import scaled_material
    from .report_fold_dynamics import DAMPING, Q0, vector
    from .report_fold_hierarchy import compile_hierarchy
    from .report_fold_kinematics import scalar
    from .report_fold_multiscale import BASE_SIZES, EDGES, TREE, configuration, connector
    from .report_fold_reservoir import parameters
    from .report_fold_scaling import scaled_mechanical
    from .report_fold_supply import power_setting
except ImportError:
    from fold_material_multiscale import mechanical as material_mechanical
    from fold_material_multiscale import scaled_material
    from report_fold_dynamics import DAMPING, Q0, vector
    from report_fold_hierarchy import compile_hierarchy
    from report_fold_kinematics import scalar
    from report_fold_multiscale import BASE_SIZES, EDGES, TREE, configuration, connector
    from report_fold_reservoir import parameters
    from report_fold_scaling import scaled_mechanical
    from report_fold_supply import power_setting


EFFICIENCY = 0.8
LEAKAGE = 0.15
GAIN = 4.0
CAPACITY_DENSITY_J = 2e-5
ACTIVATION_DENSITY_J = 1e-5


def initial_state(sizes=BASE_SIZES, edges=EDGES):
    """Return material graph state plus one external-input ledger per module."""
    sizes, edges = configuration(sizes, edges)
    blocks = np.zeros((len(sizes), 9))
    blocks[:, :2] = Q0
    blocks[0, :4] = np.r_[Q0 + (0.005, -0.008), (0.002, 0.004)]
    blocks[:, 4] = CAPACITY_DENSITY_J * np.asarray(sizes) ** 3
    return np.r_[blocks.ravel(), np.zeros(2 * len(edges) + len(sizes))]


def active_rhs(y, sizes=BASE_SIZES, edges=EDGES, *, gain=GAIN, omitted_debit=None):
    """Material-law finite-reserve dynamics before any external replenishment."""
    sizes, edges = configuration(sizes, edges)
    gain = parameters(gain, EFFICIENCY, LEAKAGE, 1)[0]
    n = len(sizes)
    if omitted_debit is not None and (type(omitted_debit) is not int or not 0 <= omitted_debit < n):
        raise ValueError("omitted debit must identify a node")
    y = vector(y, 9 * n + 2 * len(edges), "active material graph state")
    blocks = y[: 9 * n].reshape(n, 9)
    result = np.zeros_like(y)
    out = result[: 9 * n].reshape(n, 9)
    masses = []

    for i, (block, size) in enumerate(zip(blocks, sizes, strict=True)):
        if block[4] < 0:
            raise ValueError("negative reservoir: reduce timestep; no clipping")
        state, bias, _ = scaled_mechanical(block[:2], block[2:4], size)
        masses.append(state["mass_matrix"])
        resistance = size**4 * DAMPING @ block[2:4]
        applied = gain * block[4] / (block[4] + ACTIVATION_DENSITY_J * size**3) * resistance
        delivered_power = float(applied @ block[2:4])
        leak = LEAKAGE / size * block[4]
        restoring = np.asarray(scaled_material(block[:2], size)["gradient"])
        out[i] = np.r_[
            block[2:4],
            np.linalg.solve(masses[i], applied - resistance - restoring - bias),
            -leak if omitted_debit == i else -delivered_power / EFFICIENCY - leak,
            delivered_power,
            resistance @ block[2:4],
            (1 / EFFICIENCY - 1) * delivered_power,
            leak,
        ]

    for edge_index, (a, b, weight) in enumerate(edges):
        _, force_a, force_b = connector(blocks[a, :2], blocks[b, :2], sizes[a], sizes[b], weight)
        out[a, 2:4] += np.linalg.solve(masses[a], force_a)
        out[b, 2:4] += np.linalg.solve(masses[b], force_b)
        result[9 * n + 2 * edge_index : 9 * n + 2 * edge_index + 2] = [
            force_a @ blocks[a, 2:4],
            force_b @ blocks[b, 2:4],
        ]

    if not np.all(np.isfinite(result)):
        raise ValueError("nonfinite active material derivative")
    return result


def rhs(
    y,
    sizes=BASE_SIZES,
    edges=EDGES,
    *,
    power_density=6e-6,
    gain=GAIN,
    omitted_debit=None,
):
    """Add bounded replenishing power and a separately integrated input ledger."""
    sizes, edges = configuration(sizes, edges)
    power_density = power_setting(power_density)
    n = len(sizes)
    y = vector(y, 9 * n + 2 * len(edges) + n, "powered material graph state")
    result = np.r_[
        active_rhs(
            y[: 9 * n + 2 * len(edges)],
            sizes,
            edges,
            gain=gain,
            omitted_debit=omitted_debit,
        ),
        np.zeros(n),
    ]
    blocks = y[: 9 * n].reshape(n, 9)
    size = np.asarray(sizes)
    capacity = CAPACITY_DENSITY_J * size**3
    supplied_power = power_density * size**2 * np.maximum(0.0, 1.0 - blocks[:, 4] / capacity)
    result[: 9 * n].reshape(n, 9)[:, 4] += supplied_power
    result[-n:] = supplied_power
    return result


def measure(y, sizes, edges, layout):
    """Measure owned material/mechanical, connector and group energy accounts."""
    sizes, edges = configuration(sizes, edges)
    n = len(sizes)
    y = vector(y, 9 * n + 2 * len(edges) + n, "powered material graph state")
    blocks = y[: 9 * n].reshape(n, 9)
    energies = np.asarray(
        [material_mechanical(block[:2], block[2:4], sizes[i])[2] for i, block in enumerate(blocks)]
    )
    potentials = np.asarray(
        [
            connector(blocks[a, :2], blocks[b, :2], sizes[a], sizes[b], weight)[0]
            for a, b, weight in edges
        ]
    )
    works = y[9 * n : 9 * n + 2 * len(edges)].reshape(len(edges), 2)
    supplied = y[-n:]
    incident = np.zeros(n)
    for edge_index, (a, b, _) in enumerate(edges):
        incident[a] += works[edge_index, 0]
        incident[b] += works[edge_index, 1]

    groups = {}
    for path, members in layout["groups"].items():
        internal = []
        boundary = 0.0
        for edge_index, (a, b, _) in enumerate(edges):
            if a in members and b in members:
                internal.append(edge_index)
            elif a in members:
                boundary += works[edge_index, 0]
            elif b in members:
                boundary += works[edge_index, 1]
        groups[path] = dict(
            accounted_energy_j=float(
                energies[members].sum()
                + blocks[members, 4].sum()
                + blocks[members, 6:9].sum()
                + potentials[internal].sum()
            ),
            boundary_work_j=float(boundary),
            input_j=float(supplied[members].sum()),
            internal_edges=internal,
        )
    return energies, potentials, incident, supplied, groups


def simulate(
    duration=0.4,
    *,
    power_density=6e-6,
    max_step=0.002,
    rtol=1e-9,
    omitted_debit=None,
):
    """Run a short bounded audit of powered geometry-derived material motion."""
    duration = scalar(duration, "duration")
    max_step = scalar(max_step, "max_step")
    rtol = scalar(rtol, "rtol")
    power_density = power_setting(power_density)
    if not 0 < duration <= 1 or not 0 < max_step <= 0.01 or not 1e-12 <= rtol <= 1e-6:
        raise ValueError("invalid duration, max_step or rtol")

    sizes, edges = configuration(BASE_SIZES, EDGES)
    n = len(sizes)
    layout = compile_hierarchy(n, edges, TREE)
    y = initial_state(sizes, edges)
    rhs(
        y,
        sizes,
        edges,
        power_density=power_density,
        omitted_debit=omitted_debit,
    )
    start = y.copy()
    e0, u0, _, input0, groups0 = measure(y, sizes, edges, layout)
    reserve0 = y[: 9 * n].reshape(n, 9)[:, 4].copy()
    capacity = CAPACITY_DENSITY_J * np.asarray(sizes) ** 3
    maxima = {
        key: np.zeros(n)
        for key in (
            "node_mechanical_residual_j",
            "node_reservoir_residual_j",
            "edge_residual_j",
        )
    }
    group_max = dict.fromkeys(groups0, 0.0)
    missing_input_max = dict.fromkeys(groups0, 0.0)
    minimum_reserve = reserve0.copy()
    maximum_reserve_upper_violation = np.zeros(n)
    maximum_power_budget_violation = np.zeros(n)
    samples = []

    def record(time, state, save):
        nonlocal minimum_reserve, maximum_reserve_upper_violation
        energies, potential, incident, supplied, groups = measure(state, sizes, edges, layout)
        blocks = state[: 9 * n].reshape(n, 9)
        edge_work = state[9 * n : 9 * n + 2 * len(edges)].reshape(len(edges), 2)
        residuals = dict(
            node_mechanical_residual_j=(energies - e0 - blocks[:, 5] + blocks[:, 6] - incident),
            node_reservoir_residual_j=(
                blocks[:, 4]
                - reserve0
                + blocks[:, 5]
                + blocks[:, 7]
                + blocks[:, 8]
                - (supplied - input0)
            ),
            edge_residual_j=potential - u0 + edge_work.sum(axis=1),
        )
        for key, value in residuals.items():
            maxima[key] = np.maximum(maxima[key], np.abs(value))
        for path, account in groups.items():
            missing = (
                account["accounted_energy_j"]
                - groups0[path]["accounted_energy_j"]
                - account["boundary_work_j"]
            )
            residual = missing - (account["input_j"] - groups0[path]["input_j"])
            account["residual_j"] = residual
            account["missing_input_control_residual_j"] = missing
            group_max[path] = max(group_max[path], abs(residual))
            missing_input_max[path] = max(missing_input_max[path], abs(missing))

        minimum_reserve = np.minimum(minimum_reserve, blocks[:, 4])
        maximum_reserve_upper_violation = np.maximum(
            maximum_reserve_upper_violation, blocks[:, 4] - capacity
        )
        supplied_power = (
            power_density * np.asarray(sizes) ** 2 * np.maximum(0.0, 1.0 - blocks[:, 4] / capacity)
        )
        maximum_power_budget_violation[:] = np.maximum(
            maximum_power_budget_violation,
            np.maximum(
                -supplied_power,
                supplied_power - power_density * np.asarray(sizes) ** 2,
            ),
        )
        if save:
            samples.append(
                dict(
                    time_s=float(time),
                    q=blocks[:, :2].tolist(),
                    rates=blocks[:, 2:4].tolist(),
                    mechanical_j=energies.tolist(),
                    reserve_j=blocks[:, 4].tolist(),
                    delivered_work_j=blocks[:, 5].tolist(),
                    damping_loss_j=blocks[:, 6].tolist(),
                    conversion_loss_j=blocks[:, 7].tolist(),
                    leakage_loss_j=blocks[:, 8].tolist(),
                    input_j=supplied.tolist(),
                    input_power_w=supplied_power.tolist(),
                    edge_potential_j=potential.tolist(),
                    edge_work_j=edge_work.tolist(),
                    groups=groups,
                )
            )

    record(0.0, y, True)
    atol = np.r_[
        np.tile([1e-11] * 4 + [1e-16] * 5, n),
        np.full(2 * len(edges) + n, 1e-16),
    ]
    solver = RK45(
        lambda t, state: rhs(
            state,
            sizes,
            edges,
            power_density=power_density,
            omitted_debit=omitted_debit,
        ),
        0.0,
        y,
        duration,
        max_step=max_step,
        rtol=rtol,
        atol=atol,
        first_step=min(max_step, duration),
    )
    last_saved = 0.0
    while solver.status == "running":
        message = solver.step()
        if solver.status == "failed":
            raise RuntimeError(f"powered material integration failed: {message}")
        y = solver.y.copy()
        save = solver.status == "finished" or solver.t - last_saved >= 0.05
        record(float(solver.t), y, save)
        if save:
            last_saved = float(solver.t)

    if samples[-1]["time_s"] != duration:
        record(duration, y, True)
    blocks = y[: 9 * n].reshape(n, 9)
    supplied = y[-n:]
    return dict(
        settings=dict(
            duration_s=duration,
            power_density_w=power_density,
            max_step_s=max_step,
            rtol=rtol,
            sizes=sizes,
            edges=edges,
            omitted_debit=omitted_debit,
        ),
        initial_state=start.tolist(),
        final_state=y.tolist(),
        samples=samples,
        max_group_residual_j=group_max,
        missing_input_control_max_group_residual_j=missing_input_max,
        minimum_reserve_j=minimum_reserve.tolist(),
        maximum_reserve_upper_violation_j=maximum_reserve_upper_violation.tolist(),
        maximum_power_budget_violation_w=maximum_power_budget_violation.tolist(),
        finite_supply_margin_j=(EFFICIENCY * (reserve0 + supplied) - blocks[:, 5]).tolist(),
        total_received_j=float(supplied.sum()),
        final_total_mechanical_j=float(
            np.sum(samples[-1]["mechanical_j"]) + np.sum(samples[-1]["edge_potential_j"])
        ),
        **{"max_" + key: value.tolist() for key, value in maxima.items()},
    )


def report():
    names = (
        "material_supply",
        "material_multiscale",
        "active_multiscale",
        "supply",
        "constitutive",
        "scaling",
        "mapped",
        "hierarchy",
        "multiscale",
    )
    sources = {}
    for name in names:
        candidates = [
            Path(__file__).with_name(f"report_fold_{name}.py"),
            Path(__file__).with_name(f"fold_{name}.py"),
        ]
        path = next((candidate for candidate in candidates if candidate.exists()), None)
        if path is not None:
            sources[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()

    powered = simulate()
    source_off = simulate(power_density=0)
    broken = simulate(omitted_debit=0)
    fine = simulate(max_step=0.001, rtol=1e-10)
    return dict(
        schema=1,
        scope=(
            "short powered unequal-size geometry-derived material graph; "
            "synthetic reserves and ideal replenishment"
        ),
        sources=sources,
        ledgers=[
            "stored reserve energy",
            "delivered mechanical work",
            "damping/conversion/leakage losses",
            "external input energy",
        ],
        cases=dict(
            powered=powered,
            source_off=source_off,
            omitted_reserve_debit=broken,
            fine_powered=fine,
        ),
        refinement=dict(
            absolute_state_differences=abs(
                np.asarray(powered["final_state"]) - np.asarray(fine["final_state"])
            ).tolist()
        ),
        calibrated_material=False,
        physical_supply_hardware=False,
        sustained_breathing=False,
        autonomous_energy_source=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
