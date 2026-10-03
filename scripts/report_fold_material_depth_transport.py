"""Trace recursive material response and connector work by physical level."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .report_fold_dynamics import Q0, vector
    from .report_fold_material_depth3 import (
        initial_state,
        measure,
        rhs,
        subtree_members,
        tree_configuration,
    )
except ImportError:
    from report_fold_dynamics import Q0, vector
    from report_fold_material_depth3 import (
        initial_state,
        measure,
        rhs,
        subtree_members,
        tree_configuration,
    )


DURATION_S = 0.1
DT_S = 0.0005
RESPONSE_FLOOR = 1e-12
SAMPLE_TIMES_S = (0.0, 0.005, 0.01, 0.02, 0.04, 0.05, 0.075, 0.1)


def simulate_transport(*, connected=True):
    if type(connected) is not bool:
        raise ValueError("connected must be boolean")
    cfg = tree_configuration(3, connected=connected)
    sizes = np.asarray(cfg["sizes"], dtype=float)
    levels = np.asarray(cfg["levels"], dtype=int)
    edges = cfg["edges"]
    groups = subtree_members(len(sizes))
    y = initial_state(cfg["sizes"], edges)
    y = vector(y, 5 * len(sizes) + 2 * len(edges), "transport state")
    rhs(y, cfg["sizes"], edges)

    e0, u0, _, _, groups0 = measure(y, cfg["sizes"], edges, groups)
    node_max = np.zeros(len(sizes))
    edge_max = np.zeros(len(edges))
    group_max = dict.fromkeys(groups0, 0.0)
    first_resolved = {str(level): None for level in range(4)}
    sample_steps = {round(time / DT_S): time for time in SAMPLE_TIMES_S}
    snapshots = []

    def level_metrics(blocks, energy, level):
        members = np.flatnonzero(levels == level)
        coordinate = np.abs(blocks[members, :2] - Q0)
        normalized_rate = np.abs(sizes[members, None] * blocks[members, 2:4])
        maximum_coordinate = float(np.max(coordinate))
        maximum_rate = float(np.max(normalized_rate))
        return {
            "members": members.tolist(),
            "module_count": len(members),
            "maximum_coordinate_response": maximum_coordinate,
            "maximum_scale_normalized_rate": maximum_rate,
            "mechanical_energy_j": float(energy[members].sum()),
            "damping_loss_j": float(blocks[members, 4].sum()),
            "coordinate_resolved": bool(maximum_coordinate > RESPONSE_FLOOR),
        }

    def edge_metrics(potential, works, child_level):
        indexes = [
            edge_index
            for edge_index, (_, child, _) in enumerate(edges)
            if levels[child] == child_level
        ]
        if not indexes:
            return {
                "edge_count": 0,
                "connector_potential_j": 0.0,
                "signed_parent_endpoint_work_j": 0.0,
                "signed_child_endpoint_work_j": 0.0,
                "sum_abs_child_endpoint_work_j": 0.0,
                "maximum_abs_child_endpoint_work_j": 0.0,
            }
        child_work = works[indexes, 1]
        return {
            "edge_count": len(indexes),
            "connector_potential_j": float(potential[indexes].sum()),
            "signed_parent_endpoint_work_j": float(works[indexes, 0].sum()),
            "signed_child_endpoint_work_j": float(child_work.sum()),
            "sum_abs_child_endpoint_work_j": float(np.abs(child_work).sum()),
            "maximum_abs_child_endpoint_work_j": float(np.max(np.abs(child_work))),
        }

    def audit(state, step):
        energy, potential, incident, works, accounts = measure(state, cfg["sizes"], edges, groups)
        blocks = state[: 5 * len(sizes)].reshape(len(sizes), 5)
        node_residual = energy - e0 + blocks[:, 4] - incident
        edge_residual = potential - u0 + works.sum(axis=1)
        node_max[:] = np.maximum(node_max, np.abs(node_residual))
        edge_max[:] = np.maximum(edge_max, np.abs(edge_residual))
        for key, account in accounts.items():
            residual = (
                account["accounted_energy_j"]
                - groups0[key]["accounted_energy_j"]
                - account["boundary_work_j"]
            )
            group_max[key] = max(group_max[key], abs(residual))

        current_levels = {}
        for level in range(4):
            metrics = level_metrics(blocks, energy, level)
            current_levels[str(level)] = metrics
            if first_resolved[str(level)] is None and metrics["coordinate_resolved"]:
                first_resolved[str(level)] = step * DT_S

        if step in sample_steps:
            snapshots.append(
                {
                    "time_s": sample_steps[step],
                    "levels": current_levels,
                    "edges_by_child_level": {
                        str(level): edge_metrics(potential, works, level) for level in (1, 2, 3)
                    },
                }
            )

    audit(y, 0)
    steps = round(DURATION_S / DT_S)
    for step in range(steps):
        a = rhs(y, cfg["sizes"], edges)
        b = rhs(y + DT_S * a / 2, cfg["sizes"], edges)
        c = rhs(y + DT_S * b / 2, cfg["sizes"], edges)
        d = rhs(y + DT_S * c, cfg["sizes"], edges)
        y += DT_S * (a + 2 * b + 2 * c + d) / 6
        audit(y, step + 1)

    return {
        "settings": {
            **cfg,
            "duration_s": DURATION_S,
            "dt_s": DT_S,
            "response_floor": RESPONSE_FLOOR,
            "sample_times_s": SAMPLE_TIMES_S,
        },
        "first_coordinate_resolution_s": first_resolved,
        "snapshots": snapshots,
        "final_state": y.tolist(),
        "max_node_residual_j": node_max.tolist(),
        "max_edge_residual_j": edge_max.tolist(),
        "max_group_residual_j": group_max,
    }


def report():
    connected = simulate_transport()
    disconnected = simulate_transport(connected=False)
    disconnected_descendant_max = max(
        snapshot["levels"][str(level)]["maximum_coordinate_response"]
        for snapshot in disconnected["snapshots"]
        for level in (1, 2, 3)
    )
    return {
        "schema": 1,
        "scope": (
            "passive depth-three per-level response and connector-work diagnostics through "
            "0.1 s under unchanged recursive material laws"
        ),
        "connected": connected,
        "disconnected": disconnected,
        "disconnected_descendant_maximum_coordinate_response": disconnected_descendant_max,
        "sources": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in (
                "report_fold_material_depth_transport.py",
                "report_fold_material_depth3.py",
                "report_fold_scale_extension.py",
                "report_fold_constitutive.py",
                "report_fold_mapped.py",
            )
        },
        "connector_law_changed": False,
        "material_scaling_law_changed": False,
        "response_floor_tuned_to_result": False,
        "spatial_parent_child_geometry_validated": False,
        "arbitrary_depth_validated": False,
        "infinite_depth_limit_validated": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
