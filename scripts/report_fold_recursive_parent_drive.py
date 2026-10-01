"""Audit the actual recursive parent drive against scale-corresponding isolated pairs."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

try:
    from .report_fold_dynamics import Q0
    from .report_fold_mapped import port
    from .report_fold_recursive_drive_load_replay import (
        REPRESENTATIVE,
        SAMPLE_TIMES_S,
        capture_full_tree,
    )
    from .report_fold_recursive_pair_dynamics import sample_reference_time, simulate_pair
    from .report_fold_scale_extension import connector
except ImportError:
    from report_fold_dynamics import Q0
    from report_fold_mapped import port
    from report_fold_recursive_drive_load_replay import REPRESENTATIVE, SAMPLE_TIMES_S, capture_full_tree
    from report_fold_recursive_pair_dynamics import sample_reference_time, simulate_pair
    from report_fold_scale_extension import connector


def _power_factor(force, velocity):
    force = np.asarray(force, dtype=float)
    velocity = np.asarray(velocity, dtype=float)
    denominator = np.linalg.norm(force) * np.linalg.norm(velocity)
    if denominator == 0:
        return None
    return float(np.clip(force @ velocity / denominator, -1.0, 1.0))


def drive_metrics(parent_scale, parent_q, parent_v, child_q, child_v):
    parent_q = np.asarray(parent_q, dtype=float)
    parent_v = np.asarray(parent_v, dtype=float)
    child_q = np.asarray(child_q, dtype=float)
    child_v = np.asarray(child_v, dtype=float)
    child_scale = parent_scale / 2

    parent_port, _ = port(parent_q, 0.1 * parent_scale)
    child_port, _ = port(child_q, 0.1 * child_scale)
    potential, parent_force, child_force = connector(
        parent_q, child_q, parent_scale, child_scale
    )
    parent_power = float(parent_force @ parent_v)
    child_power = float(child_force @ child_v)
    return {
        "parent_displacement_norm": float(np.linalg.norm(parent_q - Q0)),
        "parent_scaled_rate_norm": float(parent_scale * np.linalg.norm(parent_v)),
        "child_displacement_norm": float(np.linalg.norm(child_q - Q0)),
        "child_scaled_rate_norm": float(child_scale * np.linalg.norm(child_v)),
        "relative_port_displacement_m": float(np.linalg.norm(parent_port - child_port)),
        "connector_potential_j": float(potential),
        "parent_force_norm": float(np.linalg.norm(parent_force)),
        "child_force_norm": float(np.linalg.norm(child_force)),
        "parent_power_w": parent_power,
        "child_power_w": child_power,
        "parent_power_factor": _power_factor(parent_force, parent_v),
        "child_power_factor": _power_factor(child_force, child_v),
    }


def _ratio(embedded, isolated):
    if isolated == 0:
        return None
    return abs(embedded) / abs(isolated)


def report():
    full = capture_full_tree()
    isolated = {str(scale): simulate_pair(scale) for scale in (1.0, 0.5, 0.25)}
    cases = {}

    for child_level in (1, 2, 3):
        rep = REPRESENTATIVE[child_level]
        parent_scale = rep["parent_scale"]
        isolated_run = isolated[str(parent_scale)]
        rows = {}

        for physical_time in SAMPLE_TIMES_S:
            full_index = round(physical_time / full["settings"]["dt_s"])
            full_row = full["trace"][full_index]
            embedded = drive_metrics(
                parent_scale,
                full_row["q"][rep["parent"]],
                full_row["rates"][rep["parent"]],
                full_row["q"][rep["child"]],
                full_row["rates"][rep["child"]],
            )
            reference_time = physical_time / parent_scale
            isolated_row = sample_reference_time(isolated_run, reference_time)
            reference = drive_metrics(
                parent_scale,
                isolated_row["q"][0],
                isolated_row["rates"][0],
                isolated_row["q"][1],
                isolated_row["rates"][1],
            )

            ratio_keys = (
                "parent_displacement_norm",
                "parent_scaled_rate_norm",
                "child_displacement_norm",
                "child_scaled_rate_norm",
                "relative_port_displacement_m",
                "connector_potential_j",
                "parent_force_norm",
                "child_force_norm",
                "parent_power_w",
                "child_power_w",
            )
            ratios = {key: _ratio(embedded[key], reference[key]) for key in ratio_keys}
            rows[str(physical_time)] = {
                "physical_time_s": physical_time,
                "reference_time_s": reference_time,
                "embedded": embedded,
                "isolated": reference,
                "magnitude_ratios": ratios,
                "parent_power_factor_difference": (
                    None
                    if embedded["parent_power_factor"] is None
                    or reference["parent_power_factor"] is None
                    else embedded["parent_power_factor"] - reference["parent_power_factor"]
                ),
                "child_power_factor_difference": (
                    None
                    if embedded["child_power_factor"] is None
                    or reference["child_power_factor"] is None
                    else embedded["child_power_factor"] - reference["child_power_factor"]
                ),
            }

        cases[str(child_level)] = {
            "parent_node": rep["parent"],
            "child_node": rep["child"],
            "parent_scale": parent_scale,
            "rows": rows,
        }

    return {
        "schema": 1,
        "scope": (
            "embedded recursive parent-drive amplitude and power alignment versus "
            "scale-corresponding isolated pair trajectories under unchanged laws"
        ),
        "sample_times_s": SAMPLE_TIMES_S,
        "cases": cases,
        "full_tree_energy": {
            "max_node_residual_j": full["max_node_residual_j"],
            "max_edge_residual_j": full["max_edge_residual_j"],
            "max_group_residual_j": full["max_group_residual_j"],
        },
        "sources": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in (
                "report_fold_recursive_parent_drive.py",
                "report_fold_recursive_drive_load_replay.py",
                "report_fold_recursive_pair_dynamics.py",
                "report_fold_material_depth3.py",
                "report_fold_scale_extension.py",
                "report_fold_mapped.py",
            )
        },
        "power_factor_is_generalized_coordinate_diagnostic": True,
        "connector_coefficients_changed": False,
        "material_scaling_law_changed": False,
        "new_recursive_coupling_introduced": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
