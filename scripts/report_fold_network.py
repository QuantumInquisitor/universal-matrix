"""Small synthetic fold graph with single-owner connection energy."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

try:
    from .report_fold_coupling import spring
    from .report_fold_dynamics import Q0, mechanical, vector
    from .report_fold_kinematics import scalar
    from .report_fold_reservoir import rhs as reservoir_rhs
except ImportError:
    from report_fold_coupling import spring
    from report_fold_dynamics import Q0, mechanical, vector
    from report_fold_kinematics import scalar
    from report_fold_reservoir import rhs as reservoir_rhs


def topology(nodes, edges):
    if type(nodes) is not int or not 1 <= nodes <= 8:
        raise ValueError("nodes must be an integer in [1,8]")
    if not isinstance(edges, (list, tuple)):
        raise ValueError("edges must be a list or tuple")
    seen, result = set(), []
    for edge in edges:
        if not isinstance(edge, (list, tuple)) or len(edge) != 3:
            raise ValueError("edge must be (node a, node b, stiffness multiplier)")
        a, b, weight = edge
        if (
            type(a) is not int
            or type(b) is not int
            or not 0 <= a < nodes
            or not 0 <= b < nodes
            or a == b
        ):
            raise ValueError("invalid edge endpoints")
        key = tuple(sorted((a, b)))
        if key in seen:
            raise ValueError("duplicate undirected edge")
        weight = scalar(weight, "edge weight")
        if not 0 < weight <= 10:
            raise ValueError("edge weight outside (0,10]")
        seen.add(key)
        result.append((a, b, weight))
    return tuple(result)


def initial_state(nodes, edges, fueled=True):
    edges = topology(nodes, edges)
    blocks = np.zeros((nodes, 9))
    blocks[:, :2] = Q0
    blocks[0, :4] = np.r_[Q0 + (0.02, -0.03), 0.01, 0.02]
    blocks[0, 4] = 2e-5 if fueled else 0
    return np.r_[blocks.ravel(), np.zeros(2 * len(edges))]


def rhs(y, nodes, edges, *, gain=4.0, damping=1.0, leakage=0.15, efficiency=0.8, broken_edge=None):
    edges = topology(nodes, edges)
    if broken_edge is not None and (
        type(broken_edge) is not int or not 0 <= broken_edge < len(edges)
    ):
        raise ValueError("broken edge must identify an existing edge")
    y = vector(y, 9 * nodes + 2 * len(edges), "network state")
    blocks = y[: 9 * nodes].reshape(nodes, 9)
    result = np.zeros_like(y)
    masses, forces = [], np.zeros((nodes, 2))
    for i, block in enumerate(blocks):
        result[9 * i : 9 * i + 9] = reservoir_rhs(
            block, gain=gain, damping=damping, leakage=leakage, efficiency=efficiency
        )
        masses.append(mechanical(block[:2], block[2:4])[0]["mass_matrix"])
    for e, (a, b, weight) in enumerate(edges):
        _, fa, fb = spring(blocks[a, :2], blocks[b, :2], weight)
        if e == broken_edge:
            fb = -fb
        forces[a] += fa
        forces[b] += fb
        result[9 * nodes + 2 * e : 9 * nodes + 2 * e + 2] = [
            fa @ blocks[a, 2:4],
            fb @ blocks[b, 2:4],
        ]
    for i in range(nodes):
        result[9 * i + 2 : 9 * i + 4] += np.linalg.solve(masses[i], forces[i])
    return result


def measure(y, nodes, edges):
    edges = topology(nodes, edges)
    blocks = np.asarray(y[: 9 * nodes]).reshape(nodes, 9)
    energies = np.array([mechanical(b[:2], b[2:4])[2] for b in blocks])
    potentials = np.array([spring(blocks[a, :2], blocks[b, :2], w)[0] for a, b, w in edges])
    incident = np.zeros(nodes)
    works = np.asarray(y[9 * nodes :]).reshape(len(edges), 2)
    for e, (a, b, _) in enumerate(edges):
        incident[a] += works[e, 0]
        incident[b] += works[e, 1]
    total = float(sum(energies) + sum(potentials) + np.sum(blocks[:, 4]) + np.sum(blocks[:, 6:]))
    return energies, potentials, incident, total


def simulate(
    nodes,
    edges,
    *,
    duration=4.0,
    dt=0.02,
    fueled=True,
    initial=None,
    gain=4.0,
    damping=1.0,
    leakage=0.15,
    efficiency=0.8,
    broken_edge=None,
):
    edges = topology(nodes, edges)
    duration, dt = scalar(duration, "duration"), scalar(dt, "dt")
    if not 0 < duration <= 10 or not 0 < dt <= 0.1:
        raise ValueError("integration settings outside numerical scope")
    steps = round(duration / dt)
    if not 1 <= steps <= 10000 or not math.isclose(steps * dt, duration, abs_tol=1e-12):
        raise ValueError("duration must contain complete steps")
    y = (
        initial_state(nodes, edges, fueled)
        if initial is None
        else vector(initial, 9 * nodes + 2 * len(edges), "initial")
    )
    blocks = y[: 9 * nodes].reshape(nodes, 9)
    if np.any(blocks[:, 5:] != 0) or np.any(y[9 * nodes :] != 0):
        raise ValueError("initial ledgers must be zero")
    if np.any(blocks[:, 4] > 1e-4):
        raise ValueError("initial reserve outside numerical scope")
    initial_snapshot = y.tolist()
    settings = dict(
        gain=gain, damping=damping, leakage=leakage, efficiency=efficiency, broken_edge=broken_edge
    )
    rhs(y, nodes, edges, **settings)
    e0, u0, _, total0 = measure(y, nodes, edges)
    trace = []
    for step in range(steps + 1):
        derivative = rhs(y, nodes, edges, **settings)
        energies, potentials, incident, total = measure(y, nodes, edges)
        blocks = y[: 9 * nodes].reshape(nodes, 9)
        works = y[9 * nodes :].reshape(len(edges), 2)
        trace.append(
            dict(
                time_s=step * dt,
                q=blocks[:, :2].tolist(),
                mechanical_j=energies.tolist(),
                reserve_j=blocks[:, 4].tolist(),
                edge_potential_j=potentials.tolist(),
                edge_work_j=works.tolist(),
                node_residual_j=(energies - e0 - blocks[:, 5] + blocks[:, 6] - incident).tolist(),
                edge_residual_j=(potentials - u0 + works.sum(axis=1)).tolist(),
                total_residual_j=total - total0,
            )
        )
        if step == steps:
            break
        a = derivative
        b = rhs(y + dt * a / 2, nodes, edges, **settings)
        c = rhs(y + dt * b / 2, nodes, edges, **settings)
        d = rhs(y + dt * c, nodes, edges, **settings)
        y = y + dt * (a + 2 * b + 2 * c + d) / 6
    return dict(
        nodes=nodes,
        edges=edges,
        initial_state=initial_snapshot,
        settings=dict(duration_s=duration, dt_s=dt, **settings),
        initial_total_j=total0,
        final_state=y.tolist(),
        max_total_residual_j=max(abs(r["total_residual_j"]) for r in trace),
        max_node_residual_j=max(max(map(abs, r["node_residual_j"])) for r in trace),
        max_edge_residuals_j=[
            max(abs(r["edge_residual_j"][e]) for r in trace) for e in range(len(edges))
        ],
        trace=trace,
    )


def report():
    chain = [(0, 1, 1.0), (1, 2, 1.0), (2, 3, 1.0)]
    cases = {}
    for name, edges, settings in [
        ("chain", chain, {}),
        ("star", [(0, 1, 1.0), (0, 2, 1.0), (0, 3, 1.0)], {}),
        ("cycle", chain + [(3, 0, 1.0)], {}),
        ("disconnected", [], {}),
        ("broken_chain", chain, dict(broken_edge=1)),
        ("conservative_chain", chain, dict(fueled=False, gain=0, damping=0, leakage=0)),
    ]:
        run = simulate(4, edges, **settings)
        run["samples"] = run.pop("trace")[::25]
        cases[name] = run
    fine = simulate(4, chain, dt=0.01)
    return dict(
        schema=1,
        scope="Four-node synthetic generalized-coordinate graph; no spatial recursive assembly validation",
        sources={
            name: hashlib.sha256(
                Path(__file__).with_name(name).read_text(encoding="utf-8").encode()
            ).hexdigest()
            for name in (
                "report_fold_network.py",
                "report_fold_coupling.py",
                "report_fold_reservoir.py",
                "report_fold_dynamics.py",
                "report_fold_kinematics.py",
            )
        },
        cases=cases,
        refinement=dict(
            dt_s=[0.02, 0.01],
            residuals_j=[cases["chain"]["max_total_residual_j"], fine["max_total_residual_j"]],
            per_node_coordinate_absolute_differences=[
                np.abs(
                    np.array(cases["chain"]["final_state"][9 * i : 9 * i + 4])
                    - fine["final_state"][9 * i : 9 * i + 4]
                ).tolist()
                for i in range(4)
            ],
        ),
        full_recursive_structure_validated=False,
        sustained_breathing=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v["max_total_residual_j"] for k, v in result["cases"].items()}))
