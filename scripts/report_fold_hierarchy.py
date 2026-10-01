"""Regrouping invariance and boundary work for a synthetic fold hierarchy."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .report_fold_coupling import spring
    from .report_fold_dynamics import mechanical, vector
    from .report_fold_kinematics import scalar
    from .report_fold_network import initial_state, measure, topology
    from .report_fold_network import rhs as flat_rhs
    from .report_fold_reservoir import rhs as reservoir_rhs
except ImportError:
    from report_fold_coupling import spring
    from report_fold_dynamics import mechanical, vector
    from report_fold_kinematics import scalar
    from report_fold_network import initial_state, measure, topology
    from report_fold_network import rhs as flat_rhs
    from report_fold_reservoir import rhs as reservoir_rhs


def compile_hierarchy(nodes, edges, tree):
    edges = topology(nodes, edges)
    groups, children, leaves = {}, {}, []

    def visit(item, path, depth):
        if depth > 8:
            raise ValueError("hierarchy exceeds depth 8")
        if type(item) is int:
            if not 0 <= item < nodes or item in leaves:
                raise ValueError("invalid or duplicate leaf")
            leaves.append(item)
            return [item]
        if not isinstance(item, (list, tuple)) or not item:
            raise ValueError("group must be a nonempty list or tuple")
        members = []
        children[path] = []
        for i, child in enumerate(item):
            child_path = path + "/" + str(i)
            members.extend(visit(child, child_path, depth + 1))
            children[path].append(child if type(child) is int else child_path)
        groups[path] = members
        return members

    if not isinstance(tree, (list, tuple)):
        raise ValueError("root must be a group")
    visit(tree, "root", 0)
    if sorted(leaves) != list(range(nodes)):
        raise ValueError("hierarchy must cover every node exactly once")
    owners = {path: [] for path in groups}
    for e, (a, b, _) in enumerate(edges):
        path = max(
            (p for p, members in groups.items() if a in members and b in members),
            key=lambda p: p.count("/"),
        )
        owners[path].append(e)
    return dict(
        nodes=nodes, edges=edges, tree=tree, groups=groups, children=children, owners=owners
    )


def rhs(y, layout):
    nodes, edges = layout["nodes"], layout["edges"]
    y = vector(y, 9 * nodes + 2 * len(edges), "hierarchy state")
    blocks = y[: 9 * nodes].reshape(nodes, 9)
    result = np.zeros_like(y)
    forces = np.zeros((nodes, 2))

    def visit(path):
        for child in layout["children"][path]:
            if type(child) is int:
                result[9 * child : 9 * child + 9] = reservoir_rhs(blocks[child])
            else:
                visit(child)
        for e in layout["owners"][path]:
            a, b, w = edges[e]
            _, fa, fb = spring(blocks[a, :2], blocks[b, :2], w)
            forces[a] += fa
            forces[b] += fb
            result[9 * nodes + 2 * e : 9 * nodes + 2 * e + 2] = [
                fa @ blocks[a, 2:4],
                fb @ blocks[b, 2:4],
            ]

    visit("root")
    for i in range(nodes):
        mass = mechanical(blocks[i, :2], blocks[i, 2:4])[0]["mass_matrix"]
        result[9 * i + 2 : 9 * i + 4] += np.linalg.solve(mass, forces[i])
    return result


def accounts(y, layout):
    nodes, edges = layout["nodes"], layout["edges"]
    energies, potentials, _, _ = measure(y, nodes, edges)
    blocks = np.asarray(y[: 9 * nodes]).reshape(nodes, 9)
    works = np.asarray(y[9 * nodes :]).reshape(len(edges), 2)
    result = {}
    for path, members in layout["groups"].items():
        total = float(
            sum(energies[members]) + sum(blocks[members, 4]) + np.sum(blocks[members, 6:])
        )
        boundary = 0.0
        internal = []
        for e, (a, b, _) in enumerate(edges):
            inside_a, inside_b = a in members, b in members
            if inside_a and inside_b:
                total += potentials[e]
                internal.append(e)
            elif inside_a:
                boundary += works[e, 0]
            elif inside_b:
                boundary += works[e, 1]
        result[path] = dict(
            accounted_energy_j=total, boundary_work_j=float(boundary), internal_edges=internal
        )
    return result


def integrate(layout, *, hierarchical=True, steps=100, dt=0.02):
    # A fixed bounded comparison, not a general solver configuration API.
    if type(steps) is not int or not 1 <= steps <= 200:
        raise ValueError("steps must be integer in [1,200]")
    dt = scalar(dt, "dt")
    if not 0 < dt <= 0.02:
        raise ValueError("dt must be finite in (0,.02]")
    n, edges = layout["nodes"], layout["edges"]
    y = initial_state(n, edges)
    initial = accounts(y, layout)
    evaluate = (
        (lambda value: rhs(value, layout))
        if hierarchical
        else (lambda value: flat_rhs(value, n, edges))
    )
    states = [y.copy()]
    residuals = {p: 0.0 for p in initial}
    for _ in range(steps):
        a = evaluate(y)
        b = evaluate(y + dt * a / 2)
        c = evaluate(y + dt * b / 2)
        d = evaluate(y + dt * c)
        y = y + dt * (a + 2 * b + 2 * c + d) / 6
        evaluate(y)  # endpoint validation, including reserve/domain
        states.append(y.copy())
        for p, acc in accounts(y, layout).items():
            residuals[p] = max(
                residuals[p],
                abs(
                    acc["accounted_energy_j"]
                    - initial[p]["accounted_energy_j"]
                    - acc["boundary_work_j"]
                ),
            )
    return dict(
        states=np.array(states),
        group_max_residual_j=residuals,
        initial_accounts=initial,
        final_accounts=accounts(y, layout),
    )


def report():
    edges = [(0, 1, 1.0), (1, 2, 0.7), (2, 3, 1.2), (3, 0, 0.5)]
    trees = dict(
        flat=[0, 1, 2, 3],
        balanced=[[0, 1], [2, 3]],
        deep=[0, [1, [2, 3]]],
        reordered=[[3, 1], [2, 0]],
    )
    reference_layout = compile_hierarchy(4, edges, trees["flat"])
    reference = integrate(reference_layout, hierarchical=False)
    cases = {}
    for name, tree in trees.items():
        layout = compile_hierarchy(4, edges, tree)
        run = integrate(layout)
        differences = np.abs(run["states"] - reference["states"])
        cases[name] = dict(
            tree=tree,
            owners=layout["owners"],
            groups=layout["groups"],
            group_max_residual_j=run["group_max_residual_j"],
            initial_accounts=run["initial_accounts"],
            final_accounts=run["final_accounts"],
            maximum_coordinate_differences_per_node=[
                differences[:, 9 * i : 9 * i + 4].max(axis=0).tolist() for i in range(4)
            ],
            maximum_energy_state_difference_j=float(
                np.max(
                    np.c_[
                        differences[:, [i * 9 + j for i in range(4) for j in range(4, 9)]],
                        differences[:, 36:],
                    ]
                )
            ),
            final_state=run["states"][-1].tolist(),
        )
    y0 = reference["states"][0]
    u0 = measure(y0, 4, edges)[1]
    yend = reference["states"][-1]
    uend = measure(yend, 4, edges)[1]
    return dict(
        schema=1,
        nodes=4,
        edges=edges,
        duration_s=2.0,
        dt_s=0.02,
        initial_state=y0.tolist(),
        sources={
            name: hashlib.sha256(
                Path(__file__).with_name(name).read_text(encoding="utf-8").encode()
            ).hexdigest()
            for name in (
                "report_fold_hierarchy.py",
                "report_fold_network.py",
                "report_fold_coupling.py",
                "report_fold_reservoir.py",
                "report_fold_dynamics.py",
                "report_fold_kinematics.py",
            )
        },
        cases=cases,
        duplicate_edge_accounting_control=dict(
            edge=0,
            initial_total_overcount_j=float(u0[0]),
            final_total_overcount_j=float(uend[0]),
            spurious_energy_change_j=float(uend[0] - u0[0]),
        ),
        scope="Hierarchy is exact regrouping of fixed physical degrees of freedom and fixed laws; no coarse graining or new cross-scale physics",
        full_recursive_physical_validation=False,
        sustained_breathing=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(
        json.dumps({k: max(v["group_max_residual_j"].values()) for k, v in result["cases"].items()})
    )
