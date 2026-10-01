"""Replicated passive material modules in a bounded binary parent-child tree."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .fold_material_multiscale import measure, rhs
    from .report_fold_hierarchy import compile_hierarchy
    from .report_fold_kinematics import scalar
    from .report_fold_multiscale import configuration, initial_state
except ImportError:
    from fold_material_multiscale import measure, rhs
    from report_fold_hierarchy import compile_hierarchy
    from report_fold_kinematics import scalar
    from report_fold_multiscale import configuration, initial_state


SCALE_RATIO = 0.5


def recursive_configuration(depth, *, connected=True):
    """Build one, three or seven separate dynamical modules in a binary tree."""
    if type(depth) is not int or not 0 <= depth <= 2:
        raise ValueError("depth must be an integer in [0,2]")
    if type(connected) is not bool:
        raise ValueError("connected must be boolean")

    levels = []
    for level in range(depth + 1):
        levels.extend([level] * (2**level))
    sizes = tuple(SCALE_RATIO**level for level in levels)

    edges = []
    if connected:
        for child in range(1, len(sizes)):
            parent = (child - 1) // 2
            edges.append((parent, child, 1.0))

    def subtree(node, level):
        if level == depth:
            return node
        left = 2 * node + 1
        right = 2 * node + 2
        return [node, subtree(left, level + 1), subtree(right, level + 1)]

    tree = [0] if depth == 0 else subtree(0, 0)
    sizes, edges = configuration(sizes, tuple(edges))
    return {
        "depth": depth,
        "sizes": sizes,
        "levels": tuple(levels),
        "edges": edges,
        "tree": tree,
        "connected": connected,
    }


def simulate(depth, *, refinement=1, connected=True, broken_edge=None, duration=0.1):
    """Integrate a short passive replicated-material tree with owned energies."""
    cfg = recursive_configuration(depth, connected=connected)
    sizes, edges = cfg["sizes"], cfg["edges"]
    if type(refinement) is not int or refinement not in (1, 2):
        raise ValueError("refinement must be 1 or 2")
    if broken_edge is not None and (
        type(broken_edge) is not int or not 0 <= broken_edge < len(edges)
    ):
        raise ValueError("broken edge must identify an existing edge")
    duration = scalar(duration, "duration")
    dt = 0.001 / refinement
    steps = round(duration / dt)
    if not 0 < duration <= 0.1 or not np.isclose(steps * dt, duration, rtol=0, atol=1e-14):
        raise ValueError("duration must be complete .001/refinement steps in (0,.1]")

    layout = compile_hierarchy(len(sizes), edges, cfg["tree"])
    y = initial_state(sizes, edges)
    initial = y.copy()
    e0, u0, _, groups0 = measure(y, sizes, edges, layout)
    node_max = np.zeros(len(sizes))
    edge_max = np.zeros(len(edges))
    group_max = dict.fromkeys(groups0, 0.0)
    root_trace = []

    def audit(state, time):
        nonlocal node_max, edge_max
        energy, potential, incident, groups = measure(state, sizes, edges, layout)
        blocks = state[: 5 * len(sizes)].reshape(len(sizes), 5)
        work = state[5 * len(sizes) :].reshape(len(edges), 2)
        node_residual = energy - e0 + blocks[:, 4] - incident
        edge_residual = potential - u0 + work.sum(axis=1)
        node_max = np.maximum(node_max, np.abs(node_residual))
        edge_max = np.maximum(edge_max, np.abs(edge_residual))
        for path, account in groups.items():
            residual = (
                account["accounted_energy_j"]
                - groups0[path]["accounted_energy_j"]
                - account["boundary_work_j"]
            )
            account["residual_j"] = residual
            group_max[path] = max(group_max[path], abs(residual))
        root_trace.append(
            {
                "time_s": time,
                "q": blocks[0, :2].tolist(),
                "rates": blocks[0, 2:4].tolist(),
                "mechanical_j": float(energy[0]),
            }
        )

    audit(y, 0.0)
    for step in range(steps):
        a = rhs(y, sizes, edges, broken_edge=broken_edge)
        b = rhs(y + dt * a / 2, sizes, edges, broken_edge=broken_edge)
        c = rhs(y + dt * b / 2, sizes, edges, broken_edge=broken_edge)
        d = rhs(y + dt * c, sizes, edges, broken_edge=broken_edge)
        y += dt * (a + 2 * b + 2 * c + d) / 6
        audit(y, (step + 1) * dt)

    return {
        "settings": {
            **cfg,
            "dt_s": dt,
            "duration_s": duration,
            "steps": steps,
            "refinement": refinement,
            "broken_edge": broken_edge,
        },
        "initial_state": initial.tolist(),
        "final_state": y.tolist(),
        "max_node_residual_j": node_max.tolist(),
        "max_edge_residual_j": edge_max.tolist(),
        "max_group_residual_j": group_max,
        "root_trace": root_trace,
    }


def root_state(run):
    return np.asarray(run["final_state"][:4])


def report():
    depth0 = simulate(0)
    depth1 = simulate(1)
    depth2 = simulate(2)
    disconnected = simulate(2, connected=False)
    broken = simulate(2, broken_edge=0)
    fine = simulate(2, refinement=2)

    increment_01 = np.abs(root_state(depth1) - root_state(depth0))
    increment_12 = np.abs(root_state(depth2) - root_state(depth1))
    refinement = np.abs(np.asarray(depth2["final_state"]) - np.asarray(fine["final_state"]))
    disconnected_root = np.abs(root_state(disconnected) - root_state(depth0))

    sources = {}
    for name in (
        "report_fold_material_recursive_tree.py",
        "fold_material_multiscale.py",
        "report_fold_multiscale.py",
        "report_fold_hierarchy.py",
    ):
        path = Path(__file__).with_name(name)
        sources[name] = hashlib.sha256(path.read_bytes()).hexdigest()

    return {
        "schema": 1,
        "scope": (
            "passive replicated dynamical material modules through binary depth 2; "
            "synthetic mapped connectors, no spatial embedding"
        ),
        "scale_ratio": SCALE_RATIO,
        "cases": {
            "depth_0": depth0,
            "depth_1": depth1,
            "depth_2": depth2,
            "disconnected_depth_2": disconnected,
            "broken_depth_2": broken,
            "fine_depth_2": fine,
        },
        "depth_response": {
            "depth_0_to_1_root_absolute_state_change": increment_01.tolist(),
            "depth_1_to_2_root_absolute_state_change": increment_12.tolist(),
            "disconnected_depth_2_to_depth_0_root_absolute_state_change": disconnected_root.tolist(),
        },
        "refinement": {
            "depth_2_absolute_state_differences": refinement.tolist(),
            "maximum_absolute_state_difference": float(np.max(refinement)),
        },
        "sources": sources,
        "replicated_dynamical_modules": True,
        "maximum_physical_modules_tested": 7,
        "physical_depths_tested": [0, 1, 2],
        "arbitrary_depth_validated": False,
        "spatial_parent_child_geometry_validated": False,
        "powered_recursive_tree_validated": False,
        "stable_recursive_limit_cycle_validated": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
