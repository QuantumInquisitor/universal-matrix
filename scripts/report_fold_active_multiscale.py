"""Finite reservoirs on a synthetic mixed-size graph; no replenishment."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .report_fold_dynamics import DAMPING, Q0, STIFFNESS, vector
    from .report_fold_hierarchy import compile_hierarchy
    from .report_fold_multiscale import BASE_SIZES, EDGES, TREE, configuration, connector
    from .report_fold_reservoir import parameters
    from .report_fold_scaling import scale_value, scaled_mechanical
except ImportError:
    from report_fold_dynamics import DAMPING, Q0, STIFFNESS, vector
    from report_fold_hierarchy import compile_hierarchy
    from report_fold_multiscale import BASE_SIZES, EDGES, TREE, configuration, connector
    from report_fold_reservoir import parameters
    from report_fold_scaling import scale_value, scaled_mechanical


def initial_state(sizes, edges, global_scale=1.0):
    sizes, edges = configuration(sizes, edges)
    g = scale_value(global_scale)
    blocks = np.zeros((len(sizes), 9))
    blocks[:, :2] = Q0
    blocks[0, :4] = np.r_[Q0 + (0.005, -0.008), np.array((0.002, 0.004)) / g]
    blocks[:, 4] = 2e-5 * np.array(sizes) ** 3
    return np.r_[blocks.ravel(), np.zeros(2 * len(edges))]


def rhs(y, sizes, edges, *, gain=4.0, omitted_debit=None, fixed_leakage=False):
    sizes, edges = configuration(sizes, edges)
    gain = parameters(gain, 0.8, 0.15, 1)[0]
    n = len(sizes)
    if omitted_debit is not None and (type(omitted_debit) is not int or not 0 <= omitted_debit < n):
        raise ValueError("omitted debit must identify a node")
    if type(fixed_leakage) is not bool:
        raise ValueError("fixed_leakage must be boolean")
    y = vector(y, 9 * n + 2 * len(edges), "active mixed-size state")
    blocks = y[: 9 * n].reshape(n, 9)
    result = np.zeros_like(y)
    out = result[: 9 * n].reshape(n, 9)
    masses = []
    for i, (b, s) in enumerate(zip(blocks, sizes, strict=True)):
        if b[4] < 0:
            raise ValueError("negative reservoir: reduce timestep; no clipping")
        state, bias, _ = scaled_mechanical(b[:2], b[2:4], s)
        masses.append(state["mass_matrix"])
        resistance = s**4 * DAMPING @ b[2:4]
        applied = gain * b[4] / (b[4] + 1e-5 * s**3) * resistance
        power = float(applied @ b[2:4])
        leak = 0.15 / (1 if fixed_leakage else s) * b[4]
        out[i] = np.r_[
            b[2:4],
            np.linalg.solve(
                masses[i], applied - resistance - s**3 * STIFFNESS @ (b[:2] - Q0) - bias
            ),
            -leak if omitted_debit == i else -power / 0.8 - leak,
            power,
            resistance @ b[2:4],
            0.25 * power,
            leak,
        ]
    for e, (a, b, w) in enumerate(edges):
        _, fa, fb = connector(blocks[a, :2], blocks[b, :2], sizes[a], sizes[b], w)
        out[a, 2:4] += np.linalg.solve(masses[a], fa)
        out[b, 2:4] += np.linalg.solve(masses[b], fb)
        result[9 * n + 2 * e : 9 * n + 2 * e + 2] = [fa @ blocks[a, 2:4], fb @ blocks[b, 2:4]]
    if not np.all(np.isfinite(result)):
        raise ValueError("nonfinite active derivative")
    return result


def measure(y, sizes, edges, layout):
    n = len(sizes)
    blocks = np.asarray(y[: 9 * n]).reshape(n, 9)
    energies = np.array(
        [scaled_mechanical(b[:2], b[2:4], sizes[i])[2] for i, b in enumerate(blocks)]
    )
    potentials = np.array(
        [connector(blocks[a, :2], blocks[b, :2], sizes[a], sizes[b], w)[0] for a, b, w in edges]
    )
    works = np.asarray(y[9 * n :]).reshape(len(edges), 2)
    incident = np.zeros(n)
    for e, (a, b, _) in enumerate(edges):
        incident[a] += works[e, 0]
        incident[b] += works[e, 1]
    groups = {}
    for path, members in layout["groups"].items():
        internal, boundary = [], 0.0
        for e, (a, b, _) in enumerate(edges):
            if a in members and b in members:
                internal.append(e)
            elif a in members:
                boundary += works[e, 0]
            elif b in members:
                boundary += works[e, 1]
        groups[path] = dict(
            accounted_energy_j=float(
                sum(energies[members])
                + sum(blocks[members, 4])
                + blocks[members, 6:9].sum()
                + sum(potentials[internal])
            ),
            boundary_work_j=float(boundary),
            internal_edges=internal,
        )
    return energies, potentials, incident, groups


def simulate(global_scale=1.0, *, refinement=1, omitted_debit=None):
    g = scale_value(global_scale)
    sizes, edges = configuration(tuple(g * s for s in BASE_SIZES), EDGES)
    if type(refinement) is not int or refinement not in (1, 2):
        raise ValueError("refinement must be 1 or 2")
    layout = compile_hierarchy(len(sizes), edges, TREE)
    y = initial_state(sizes, edges, g)
    initial = y.copy()
    e0, u0, _, groups0 = measure(y, sizes, edges, layout)
    reserve0 = y[:36].reshape(4, 9)[:, 4].copy()
    dt = 0.01 * g / refinement
    trace = []
    for step in range(100 * refinement + 1):
        derivative = rhs(y, sizes, edges, omitted_debit=omitted_debit)
        energy, potential, incident, groups = measure(y, sizes, edges, layout)
        for path, account in groups.items():
            account["residual_j"] = (
                account["accounted_energy_j"]
                - groups0[path]["accounted_energy_j"]
                - account["boundary_work_j"]
            )
        b = y[:36].reshape(4, 9)
        work = y[36:].reshape(4, 2)
        trace.append(
            dict(
                time_s=step * dt,
                reference_time_s=step * 0.01 / refinement,
                q=b[:, :2].tolist(),
                rates=b[:, 2:4].tolist(),
                mechanical_j=energy.tolist(),
                reserve_j=b[:, 4].tolist(),
                work_j=b[:, 5].tolist(),
                damping_loss_j=b[:, 6].tolist(),
                conversion_loss_j=b[:, 7].tolist(),
                leakage_loss_j=b[:, 8].tolist(),
                edge_potential_j=potential.tolist(),
                edge_work_j=work.tolist(),
                node_mechanical_residual_j=(energy - e0 - b[:, 5] + b[:, 6] - incident).tolist(),
                node_reservoir_residual_j=(
                    b[:, 4] - reserve0 + b[:, 5] + b[:, 7] + b[:, 8]
                ).tolist(),
                edge_residual_j=(potential - u0 + work.sum(axis=1)).tolist(),
                groups=groups,
            )
        )
        if step == 100 * refinement:
            break
        a = derivative
        b = rhs(y + dt * a / 2, sizes, edges, omitted_debit=omitted_debit)
        c = rhs(y + dt * b / 2, sizes, edges, omitted_debit=omitted_debit)
        d = rhs(y + dt * c, sizes, edges, omitted_debit=omitted_debit)
        y += dt * (a + 2 * b + 2 * c + d) / 6
    result = dict(
        settings=dict(
            global_scale=g,
            sizes=sizes,
            edges=edges,
            hierarchy=TREE,
            dt_s=dt,
            duration_s=g,
            steps=100 * refinement,
            omitted_debit=omitted_debit,
        ),
        initial_state=initial.tolist(),
        final_state=y.tolist(),
        initial_accounts=groups0,
        final_accounts=trace[-1]["groups"],
        owners=layout["owners"],
        trace=trace,
    )
    for key in ("node_mechanical_residual_j", "node_reservoir_residual_j", "edge_residual_j"):
        result["max_" + key] = np.max(np.abs([r[key] for r in trace]), axis=0).tolist()
    result["max_group_residual_j"] = {
        p: max(abs(r["groups"][p]["residual_j"]) for r in trace) for p in groups0
    }
    reserves = np.array([r["reserve_j"] for r in trace])
    result["finite_supply"] = dict(
        initial_reserve_j=reserve0.tolist(),
        minimum_reserve_j=reserves.min(axis=0).tolist(),
        maximum_reserve_step_increase_j=np.diff(reserves, axis=0).max(axis=0).tolist(),
        remaining_plus_spent_minus_initial_j=trace[-1]["node_reservoir_residual_j"],
    )
    return result


def comparison(run, reference):
    if reference["settings"]["global_scale"] != 1 or [
        r["reference_time_s"] for r in run["trace"]
    ] != [r["reference_time_s"] for r in reference["trace"]]:
        raise ValueError("comparison requires unit reference and matching time grids")
    g = run["settings"]["global_scale"]
    result = {}
    for key, factor in (
        ("q", 1),
        ("rates", g),
        *(
            (k, g**-3)
            for k in (
                "mechanical_j",
                "reserve_j",
                "work_j",
                "damping_loss_j",
                "conversion_loss_j",
                "leakage_loss_j",
                "edge_potential_j",
                "edge_work_j",
            )
        ),
    ):
        result[key] = np.max(
            abs(
                factor * np.array([r[key] for r in run["trace"]])
                - np.array([r[key] for r in reference["trace"]])
            ),
            axis=0,
        ).tolist()
    return result


def report():
    reference = simulate()
    cases = {}
    for name, g, omission in (
        ("reference", 1, None),
        ("three_quarters", 0.75, None),
        ("half", 0.5, None),
        ("omitted_debit", 1, 1),
    ):
        run = reference if name == "reference" else simulate(g, omitted_debit=omission)
        cases[name] = {k: v for k, v in run.items() if k != "trace"}
        cases[name]["samples"] = run["trace"][::20]
        cases[name]["similarity"] = comparison(run, reference)
    fine = simulate(0.5, refinement=2)
    coarse = cases["half"]
    names = (
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
        scope="Finite unreplenished synthetic reservoirs on four unequal-size modules; conditional similarity only",
        sources={
            f"report_fold_{n}.py": hashlib.sha256(
                Path(__file__).with_name(f"report_fold_{n}.py").read_text(encoding="utf-8").encode()
            ).hexdigest()
            for n in names
        },
        scaling=dict(
            reserve_and_activation="s^3",
            feedback_damping="s^4",
            leakage_rate="0.15/s",
            efficiency=0.8,
            gain=4,
        ),
        cases=cases,
        refinement=dict(
            root_residuals_j=[
                coarse["max_group_residual_j"]["root"],
                fine["max_group_residual_j"]["root"],
            ],
            component_columns=[
                "scale",
                "angle_rad",
                "scale_rate_per_s",
                "angle_rate_rad_per_s",
                "reserve_j",
                "work_j",
                "damping_loss_j",
                "conversion_loss_j",
                "leakage_loss_j",
            ],
            state_component_differences_by_module=abs(
                np.array(coarse["final_state"][:36]).reshape(4, 9)
                - np.array(fine["final_state"][:36]).reshape(4, 9)
            ).tolist(),
        ),
        calibrated_material=False,
        recursive_assembly_validated=False,
        sustained_breathing=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v["max_group_residual_j"] for k, v in result["cases"].items()}))
