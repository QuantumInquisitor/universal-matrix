"""Isolate recursive return backreaction by selectively removing deeper edge levels."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .report_fold_material_depth3 import (
        initial_state,
        measure,
        rhs,
        subtree_members,
        tree_configuration,
    )
except ImportError:
    from report_fold_material_depth3 import (
        initial_state,
        measure,
        rhs,
        subtree_members,
        tree_configuration,
    )


DURATION_S = 0.1
DT_S = 0.0005
SAMPLE_TIMES_S = (0.02, 0.05, 0.075, 0.1)
RESPONSE_FLOOR = 1e-12


def configuration_through_level(max_child_level):
    if type(max_child_level) is not int or not 0 <= max_child_level <= 3:
        raise ValueError("max_child_level must be an integer in [0,3]")
    full = tree_configuration(3)
    levels = full["levels"]
    edges = tuple(
        edge for edge in full["edges"] if levels[edge[1]] <= max_child_level
    )
    return {
        "depth": 3,
        "levels": levels,
        "sizes": full["sizes"],
        "edges": edges,
        "connected_through_level": max_child_level,
    }


def _edge_level_metrics(potential, works, edges, levels, initial_potential):
    rows = {}
    for child_level in (1, 2, 3):
        indexes = [
            i
            for i, (_, child, _) in enumerate(edges)
            if levels[child] == child_level
        ]
        if not indexes:
            rows[str(child_level)] = {
                "edge_count": 0,
                "potential_change_j": 0.0,
                "parent_endpoint_work_j": 0.0,
                "child_endpoint_work_j": 0.0,
                "energy_identity_residual_j": 0.0,
                "child_uptake_fraction_of_parent_magnitude": None,
            }
            continue
        parent_work = float(works[indexes, 0].sum())
        child_work = float(works[indexes, 1].sum())
        delta_potential = float(
            potential[indexes].sum() - initial_potential[child_level]
        )
        parent_magnitude = abs(parent_work)
        rows[str(child_level)] = {
            "edge_count": len(indexes),
            "potential_change_j": delta_potential,
            "parent_endpoint_work_j": parent_work,
            "child_endpoint_work_j": child_work,
            "energy_identity_residual_j": delta_potential + parent_work + child_work,
            "child_uptake_fraction_of_parent_magnitude": (
                None if parent_magnitude == 0 else abs(child_work) / parent_magnitude
            ),
        }
    return rows


def simulate(max_child_level):
    cfg = configuration_through_level(max_child_level)
    sizes, edges, levels = cfg["sizes"], cfg["edges"], cfg["levels"]
    groups = subtree_members(len(sizes))
    y = initial_state(sizes, edges)
    e0, u0, _, _, groups0 = measure(y, sizes, edges, groups)
    node_max = np.zeros(len(sizes))
    edge_max = np.zeros(len(edges))
    group_max = dict.fromkeys(groups0, 0.0)
    sample_steps = {round(time / DT_S): time for time in SAMPLE_TIMES_S}
    snapshots = []

    initial_potential = {}
    for level in (1, 2, 3):
        indexes = [
            i for i, (_, child, _) in enumerate(edges) if levels[child] == level
        ]
        initial_potential[level] = (
            0.0 if not indexes else float(u0[indexes].sum())
        )

    def audit(state, step):
        energy, potential, incident, works, accounts = measure(
            state, sizes, edges, groups
        )
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

        if step in sample_steps:
            snapshots.append(
                {
                    "time_s": sample_steps[step],
                    "root_state": blocks[0, :4].tolist(),
                    "edge_levels": _edge_level_metrics(
                        potential,
                        works,
                        edges,
                        levels,
                        initial_potential,
                    ),
                }
            )

    audit(y, 0)
    steps = round(DURATION_S / DT_S)
    for step in range(steps):
        a = rhs(y, sizes, edges)
        b = rhs(y + DT_S * a / 2, sizes, edges)
        c = rhs(y + DT_S * b / 2, sizes, edges)
        d = rhs(y + DT_S * c, sizes, edges)
        y += DT_S * (a + 2 * b + 2 * c + d) / 6
        audit(y, step + 1)

    return {
        "settings": {
            **cfg,
            "duration_s": DURATION_S,
            "dt_s": DT_S,
            "sample_times_s": SAMPLE_TIMES_S,
        },
        "snapshots": snapshots,
        "final_state": y.tolist(),
        "max_node_residual_j": node_max.tolist(),
        "max_edge_residual_j": edge_max.tolist(),
        "max_group_residual_j": group_max,
    }


def _root_state_at(run, time_s):
    for row in run["snapshots"]:
        if row["time_s"] == time_s:
            return np.asarray(row["root_state"])
    raise ValueError("requested time is not present")


def report():
    runs = {str(level): simulate(level) for level in range(4)}
    increments = {}
    for time_s in SAMPLE_TIMES_S:
        row = {}
        for level in (1, 2, 3):
            delta = np.abs(
                _root_state_at(runs[str(level)], time_s)
                - _root_state_at(runs[str(level - 1)], time_s)
            )
            row[str(level)] = {
                "maximum_absolute_root_state_change": float(np.max(delta)),
                "absolute_root_state_change": delta.tolist(),
                "resolved": bool(np.max(delta) > RESPONSE_FLOOR),
            }
        increments[str(time_s)] = row

    full_final = runs["3"]["snapshots"][-1]["edge_levels"]
    return {
        "schema": 1,
        "scope": (
            "causal recursive backreaction audit using the same 15 physical modules "
            "with parent-child edges admitted only through selected levels"
        ),
        "response_floor": RESPONSE_FLOOR,
        "sample_times_s": SAMPLE_TIMES_S,
        "runs": runs,
        "incremental_root_backreaction": increments,
        "full_tree_final_edge_energy_transfer": full_final,
        "sources": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in (
                "report_fold_material_depth_backreaction.py",
                "report_fold_material_depth3.py",
                "report_fold_scale_extension.py",
                "report_fold_constitutive.py",
                "report_fold_mapped.py",
            )
        },
        "module_count_held_fixed": True,
        "connector_coefficients_changed": False,
        "material_scaling_law_changed": False,
        "spatial_parent_child_geometry_validated": False,
        "new_recursive_coupling_introduced": False,
        "arbitrary_depth_validated": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
