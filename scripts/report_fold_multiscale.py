"""Passive mixed-size graph with mapped ports and explicit group energy accounts."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .report_fold_dynamics import Q0, vector
    from .report_fold_hierarchy import compile_hierarchy
    from .report_fold_mapped import PORT_STIFFNESS, port
    from .report_fold_network import topology
    from .report_fold_scaling import rhs as body_rhs
    from .report_fold_scaling import scale_value, scaled_mechanical
except ImportError:
    from report_fold_dynamics import Q0, vector
    from report_fold_hierarchy import compile_hierarchy
    from report_fold_mapped import PORT_STIFFNESS, port
    from report_fold_network import topology
    from report_fold_scaling import rhs as body_rhs
    from report_fold_scaling import scale_value, scaled_mechanical

BASE_SIZES = (1.0, 0.75, 0.5, 0.5)
EDGES = ((0, 1, 1.0), (1, 2, 0.7), (2, 3, 1.0), (3, 0, 0.5))
TREE = [[0, 1], [2, 3]]


def configuration(sizes, edges):
    if not isinstance(sizes, (list, tuple)) or not 1 <= len(sizes) <= 8:
        raise ValueError("sizes must contain one to eight body scales")
    return tuple(scale_value(s) for s in sizes), topology(len(sizes), edges)


def connector(qa, qb, size_a, size_b, weight=1.0):
    sizes, edges = configuration((size_a, size_b), ((0, 1, weight),))
    pa, ja = port(qa, 0.1 * sizes[0])
    pb, jb = port(qb, 0.1 * sizes[1])
    delta = pa - pb
    force = edges[0][2] * max(sizes) * PORT_STIFFNESS @ delta
    return float(delta @ force / 2), -ja.T @ force, jb.T @ force


def initial_state(sizes, edges, global_scale=1.0):
    sizes, edges = configuration(sizes, edges)
    global_scale = scale_value(global_scale)
    blocks = np.zeros((len(sizes), 5))
    blocks[:, :2] = Q0
    blocks[0, :4] = np.r_[Q0 + (0.005, -0.008), np.array((0.002, 0.004)) / global_scale]
    return np.r_[blocks.ravel(), np.zeros(2 * len(edges))]


def rhs(y, sizes, edges, *, broken_edge=None):
    sizes, edges = configuration(sizes, edges)
    if broken_edge is not None and (
        type(broken_edge) is not int or not 0 <= broken_edge < len(edges)
    ):
        raise ValueError("broken edge must identify an existing edge")
    n = len(sizes)
    y = vector(y, 5 * n + 2 * len(edges), "mixed-size graph state")
    blocks = y[: 5 * n].reshape(n, 5)
    result = np.zeros_like(y)
    forces = np.zeros((n, 2))
    for i, block in enumerate(blocks):
        result[5 * i : 5 * i + 5] = body_rhs(block, sizes[i])
    for e, (a, b, w) in enumerate(edges):
        _, fa, fb = connector(blocks[a, :2], blocks[b, :2], sizes[a], sizes[b], w)
        if e == broken_edge:
            fb = -fb
        forces[a] += fa
        forces[b] += fb
        result[5 * n + 2 * e : 5 * n + 2 * e + 2] = [fa @ blocks[a, 2:4], fb @ blocks[b, 2:4]]
    for i, block in enumerate(blocks):
        mass = scaled_mechanical(block[:2], block[2:4], sizes[i])[0]["mass_matrix"]
        result[5 * i + 2 : 5 * i + 4] += np.linalg.solve(mass, forces[i])
    return result


def measure(y, sizes, edges, layout):
    n = len(sizes)
    blocks = np.asarray(y[: 5 * n]).reshape(n, 5)
    energies = np.array(
        [scaled_mechanical(b[:2], b[2:4], sizes[i])[2] for i, b in enumerate(blocks)]
    )
    potentials = np.array(
        [connector(blocks[a, :2], blocks[b, :2], sizes[a], sizes[b], w)[0] for a, b, w in edges]
    )
    works = np.asarray(y[5 * n :]).reshape(len(edges), 2)
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
        accounted = float(
            sum(energies[members]) + sum(blocks[members, 4]) + sum(potentials[internal])
        )
        groups[path] = dict(
            accounted_energy_j=accounted, boundary_work_j=float(boundary), internal_edges=internal
        )
    return energies, potentials, incident, groups


def simulate(global_scale=1.0, *, refinement=1, broken_edge=None):
    global_scale = scale_value(global_scale)
    sizes, edges = configuration(tuple(global_scale * s for s in BASE_SIZES), EDGES)
    if type(refinement) is not int or refinement not in (1, 2):
        raise ValueError("refinement must be 1 or 2")
    layout = compile_hierarchy(len(sizes), edges, TREE)
    y = initial_state(sizes, edges, global_scale)
    initial = y.tolist()
    e0, u0, _, groups0 = measure(y, sizes, edges, layout)
    dt = 0.01 * global_scale / refinement
    trace = []
    for step in range(100 * refinement + 1):
        derivative = rhs(y, sizes, edges, broken_edge=broken_edge)
        energy, potential, incident, groups = measure(y, sizes, edges, layout)
        for path, account in groups.items():
            account["residual_j"] = (
                account["accounted_energy_j"]
                - groups0[path]["accounted_energy_j"]
                - account["boundary_work_j"]
            )
        blocks = y[:20].reshape(4, 5)
        work = y[20:].reshape(4, 2)
        trace.append(
            dict(
                time_s=step * dt,
                reference_time_s=step * 0.01 / refinement,
                q=blocks[:, :2].tolist(),
                rates=blocks[:, 2:4].tolist(),
                mechanical_j=energy.tolist(),
                damping_loss_j=blocks[:, 4].tolist(),
                edge_potential_j=potential.tolist(),
                edge_work_j=work.tolist(),
                node_residual_j=(energy - e0 + blocks[:, 4] - incident).tolist(),
                edge_residual_j=(potential - u0 + work.sum(axis=1)).tolist(),
                groups=groups,
            )
        )
        if step == 100 * refinement:
            break
        a = derivative
        b = rhs(y + dt * a / 2, sizes, edges, broken_edge=broken_edge)
        c = rhs(y + dt * b / 2, sizes, edges, broken_edge=broken_edge)
        d = rhs(y + dt * c, sizes, edges, broken_edge=broken_edge)
        y += dt * (a + 2 * b + 2 * c + d) / 6
    return dict(
        settings=dict(
            global_scale=global_scale,
            sizes=list(sizes),
            edges=edges,
            hierarchy=TREE,
            dt_s=dt,
            duration_s=global_scale,
            steps=100 * refinement,
            broken_edge=broken_edge,
        ),
        initial_state=initial,
        final_state=y.tolist(),
        initial_accounts=groups0,
        final_accounts=trace[-1]["groups"],
        owners=layout["owners"],
        max_node_residual_j=np.max(np.abs([r["node_residual_j"] for r in trace]), axis=0).tolist(),
        max_edge_residual_j=np.max(np.abs([r["edge_residual_j"] for r in trace]), axis=0).tolist(),
        max_group_residual_j={
            p: max(abs(r["groups"][p]["residual_j"]) for r in trace) for p in groups0
        },
        trace=trace,
    )


def comparison(run, reference):
    if [r["reference_time_s"] for r in run["trace"]] != [
        r["reference_time_s"] for r in reference["trace"]
    ]:
        raise ValueError("comparison requires matching reference-time grids")
    if reference["settings"]["global_scale"] != 1:
        raise ValueError("reference must have unit global scale")
    g = run["settings"]["global_scale"]

    def values(key, source):
        return np.array([r[key] for r in source["trace"]])

    return dict(
        coordinate_max_differences=np.max(
            abs(values("q", run) - values("q", reference)), axis=0
        ).tolist(),
        rescaled_rate_max_differences=np.max(
            abs(g * values("rates", run) - values("rates", reference)), axis=0
        ).tolist(),
        rescaled_node_energy_differences_j=np.max(
            abs(values("mechanical_j", run) / g**3 - values("mechanical_j", reference)), axis=0
        ).tolist(),
        rescaled_edge_energy_differences_j=np.max(
            abs(values("edge_potential_j", run) / g**3 - values("edge_potential_j", reference)),
            axis=0,
        ).tolist(),
    )


def report():
    reference = simulate()
    cases = {}
    for name, scale, broken in (
        ("reference", 1.0, None),
        ("three_quarters", 0.75, None),
        ("half", 0.5, None),
        ("wrong_reaction", 1.0, 1),
    ):
        run = reference if name == "reference" else simulate(scale, broken_edge=broken)
        cases[name] = {k: v for k, v in run.items() if k != "trace"}
        cases[name]["samples"] = run["trace"][::20]
        cases[name]["similarity"] = comparison(run, reference)
    fine = simulate(0.5, refinement=2)
    coarse = cases["half"]
    names = (
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
        scope="Four passive unequal-size modules, synthetic mapped connectors; conditional homothetic similarity, not a material or recursive assembly validation",
        sources={
            f"report_fold_{name}.py": hashlib.sha256(
                Path(__file__)
                .with_name(f"report_fold_{name}.py")
                .read_text(encoding="utf-8")
                .encode()
            ).hexdigest()
            for name in names
        },
        connector_rule="weight * max(endpoint absolute sizes) * PORT_STIFFNESS",
        cases=cases,
        refinement=dict(
            residuals_j=[
                coarse["max_group_residual_j"]["root"],
                fine["max_group_residual_j"]["root"],
            ],
            component_columns=["scale", "angle_rad", "scale_rate_per_s", "angle_rate_rad_per_s"],
            state_component_differences_by_module=abs(
                np.array(coarse["final_state"][:20]).reshape(4, 5)[:, :4]
                - np.array(fine["final_state"][:20]).reshape(4, 5)[:, :4]
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
