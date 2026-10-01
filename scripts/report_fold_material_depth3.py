"""Depth-three replicated material tree using the independently audited one-eighth scale."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .report_fold_dynamics import Q0, vector
    from .report_fold_scale_extension import audit_scale, connector, mechanical
    from .report_fold_scale_extension import rhs as body_rhs
except ImportError:
    from report_fold_dynamics import Q0, vector
    from report_fold_scale_extension import audit_scale, connector, mechanical
    from report_fold_scale_extension import rhs as body_rhs


MAX_DEPTH = 3
SCALE_RATIO = 0.5


def tree_configuration(depth, *, connected=True):
    if type(depth) is not int or not 0 <= depth <= MAX_DEPTH:
        raise ValueError("depth must be an integer in [0,3]")
    if type(connected) is not bool:
        raise ValueError("connected must be boolean")

    levels = []
    for level in range(depth + 1):
        levels.extend([level] * (2**level))
    sizes = tuple(audit_scale(SCALE_RATIO**level) for level in levels)
    edges = ()
    if connected:
        edges = tuple(((child - 1) // 2, child, 1.0) for child in range(1, len(sizes)))
    return dict(depth=depth, levels=tuple(levels), sizes=sizes, edges=edges, connected=connected)


def subtree_members(nodes):
    """Return descendant membership for every node in the complete binary tree."""
    if type(nodes) is not int or nodes not in (1, 3, 7, 15):
        raise ValueError("nodes must be a complete binary tree size through 15")
    result = {}
    for root in range(nodes):
        members = []
        stack = [root]
        while stack:
            node = stack.pop()
            if node >= nodes:
                continue
            members.append(node)
            stack.extend((2 * node + 1, 2 * node + 2))
        result[root] = tuple(sorted(members))
    return result


def initial_state(sizes, edges):
    blocks = np.zeros((len(sizes), 5))
    blocks[:, :2] = Q0
    blocks[0, :4] = np.r_[Q0 + (0.005, -0.008), (0.002, 0.004)]
    return np.r_[blocks.ravel(), np.zeros(2 * len(edges))]


def rhs(y, sizes, edges, *, broken_edge=None):
    n = len(sizes)
    if broken_edge is not None and (
        type(broken_edge) is not int or not 0 <= broken_edge < len(edges)
    ):
        raise ValueError("broken edge must identify an existing edge")
    y = vector(y, 5 * n + 2 * len(edges), "extended recursive material state")
    blocks = y[: 5 * n].reshape(n, 5)
    result = np.zeros_like(y)
    forces = np.zeros((n, 2))
    masses = []

    for index, (block, size) in enumerate(zip(blocks, sizes, strict=True)):
        result[5 * index : 5 * index + 5] = body_rhs(block, size)
        masses.append(mechanical(block[:2], block[2:4], size)[0]["mass_matrix"])

    for edge_index, (a, b, weight) in enumerate(edges):
        _, force_a, force_b = connector(
            blocks[a, :2], blocks[b, :2], sizes[a], sizes[b], weight
        )
        if edge_index == broken_edge:
            force_b = -force_b
        forces[a] += force_a
        forces[b] += force_b
        result[5 * n + 2 * edge_index : 5 * n + 2 * edge_index + 2] = [
            force_a @ blocks[a, 2:4],
            force_b @ blocks[b, 2:4],
        ]

    for index in range(n):
        result[5 * index + 2 : 5 * index + 4] += np.linalg.solve(
            masses[index], forces[index]
        )
    return result


def measure(y, sizes, edges, groups):
    n = len(sizes)
    y = vector(y, 5 * n + 2 * len(edges), "extended recursive material state")
    blocks = y[: 5 * n].reshape(n, 5)
    energies = np.asarray(
        [mechanical(block[:2], block[2:4], sizes[i])[2] for i, block in enumerate(blocks)]
    )
    potentials = np.asarray(
        [
            connector(blocks[a, :2], blocks[b, :2], sizes[a], sizes[b], weight)[0]
            for a, b, weight in edges
        ]
    )
    works = y[5 * n :].reshape(len(edges), 2)
    incident = np.zeros(n)
    for edge_index, (a, b, _) in enumerate(edges):
        incident[a] += works[edge_index, 0]
        incident[b] += works[edge_index, 1]

    accounts = {}
    for root, members_tuple in groups.items():
        members = set(members_tuple)
        internal = []
        boundary = 0.0
        for edge_index, (a, b, _) in enumerate(edges):
            if a in members and b in members:
                internal.append(edge_index)
            elif a in members:
                boundary += works[edge_index, 0]
            elif b in members:
                boundary += works[edge_index, 1]
        accounts[str(root)] = dict(
            members=list(members_tuple),
            accounted_energy_j=float(
                energies[list(members_tuple)].sum()
                + blocks[list(members_tuple), 4].sum()
                + potentials[internal].sum()
            ),
            boundary_work_j=float(boundary),
            internal_edges=internal,
        )
    return energies, potentials, incident, works, accounts


def simulate(
    depth,
    *,
    connected=True,
    broken_edge=None,
    refinement=1,
    duration=0.04,
):
    cfg = tree_configuration(depth, connected=connected)
    sizes, edges = cfg["sizes"], cfg["edges"]
    if type(refinement) is not int or refinement not in (1, 2):
        raise ValueError("refinement must be 1 or 2")
    duration = float(duration)
    if not np.isfinite(duration) or not 0 < duration <= 0.05:
        raise ValueError("duration outside (0,0.05]")
    dt = 0.0005 / refinement
    steps = round(duration / dt)
    if not np.isclose(steps * dt, duration, rtol=0, atol=1e-14):
        raise ValueError("duration must contain complete integration steps")
    if broken_edge is not None and (
        type(broken_edge) is not int or not 0 <= broken_edge < len(edges)
    ):
        raise ValueError("broken edge must identify an existing edge")

    groups = subtree_members(len(sizes))
    y = initial_state(sizes, edges)
    initial = y.copy()
    e0, u0, _, _, groups0 = measure(y, sizes, edges, groups)
    node_max = np.zeros(len(sizes))
    edge_max = np.zeros(len(edges))
    group_max = {key: 0.0 for key in groups0}
    root_trace = []

    def audit(state, time):
        nonlocal node_max, edge_max
        energy, potential, incident, works, accounts = measure(
            state, sizes, edges, groups
        )
        blocks = state[: 5 * len(sizes)].reshape(len(sizes), 5)
        node_residual = energy - e0 + blocks[:, 4] - incident
        edge_residual = potential - u0 + works.sum(axis=1)
        node_max = np.maximum(node_max, np.abs(node_residual))
        edge_max = np.maximum(edge_max, np.abs(edge_residual))
        for key, account in accounts.items():
            residual = (
                account["accounted_energy_j"]
                - groups0[key]["accounted_energy_j"]
                - account["boundary_work_j"]
            )
            group_max[key] = max(group_max[key], abs(residual))
        root_trace.append(
            dict(
                time_s=float(time),
                q=blocks[0, :2].tolist(),
                rates=blocks[0, 2:4].tolist(),
            )
        )

    audit(y, 0.0)
    for step in range(steps):
        a = rhs(y, sizes, edges, broken_edge=broken_edge)
        b = rhs(y + dt * a / 2, sizes, edges, broken_edge=broken_edge)
        c = rhs(y + dt * b / 2, sizes, edges, broken_edge=broken_edge)
        d = rhs(y + dt * c, sizes, edges, broken_edge=broken_edge)
        y += dt * (a + 2 * b + 2 * c + d) / 6
        audit(y, (step + 1) * dt)

    return dict(
        settings=dict(
            **cfg,
            duration_s=duration,
            dt_s=dt,
            steps=steps,
            refinement=refinement,
            broken_edge=broken_edge,
        ),
        initial_state=initial.tolist(),
        final_state=y.tolist(),
        max_node_residual_j=node_max.tolist(),
        max_edge_residual_j=edge_max.tolist(),
        max_group_residual_j=group_max,
        root_trace=root_trace,
    )


def root_state(run):
    return np.asarray(run["final_state"][:4])


def report():
    depth2 = simulate(2)
    depth3 = simulate(3)
    disconnected = simulate(3, connected=False)
    broken = simulate(3, broken_edge=0)
    fine = simulate(3, refinement=2)
    single = simulate(0)

    return dict(
        schema=1,
        scope=(
            "experimental depth-three passive material tree using independently audited "
            "scale 0.125; production scale/topology guards unchanged"
        ),
        cases=dict(
            depth_2=depth2,
            depth_3=depth3,
            disconnected_depth_3=disconnected,
            broken_depth_3=broken,
            fine_depth_3=fine,
            single=single,
        ),
        depth_response=dict(
            depth_2_to_3_root_absolute_state_change=abs(
                root_state(depth3) - root_state(depth2)
            ).tolist(),
            disconnected_depth_3_to_single_root_absolute_state_change=abs(
                root_state(disconnected) - root_state(single)
            ).tolist(),
            resolved_root_backreaction_threshold=1e-12,
            depth_3_root_backreaction_resolved=bool(
                np.max(abs(root_state(depth3) - root_state(depth2))) > 1e-12
            ),
        ),
        refinement=dict(
            maximum_absolute_state_difference=float(
                np.max(
                    abs(
                        np.asarray(depth3["final_state"])
                        - np.asarray(fine["final_state"])
                    )
                )
            )
        ),
        sources={
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in (
                "report_fold_material_depth3.py",
                "report_fold_scale_extension.py",
                "report_fold_constitutive.py",
                "report_fold_kinematics.py",
                "report_fold_mapped.py",
            )
        },
        production_scale_guard_changed=False,
        production_topology_guard_changed=False,
        physical_depth_three_executed=True,
        maximum_modules_tested=15,
        smallest_scale_tested=0.125,
        spatial_parent_child_geometry_validated=False,
        powered_depth_three_validated=False,
        arbitrary_depth_validated=False,
        infinite_depth_convergence_validated=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
