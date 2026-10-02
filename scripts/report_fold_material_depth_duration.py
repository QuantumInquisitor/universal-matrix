"""Extend the passive depth-three material audit to 0.1 s without changing its laws."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

try:
    from .report_fold_dynamics import vector
    from .report_fold_material_depth3 import (
        initial_state,
        measure,
        rhs,
        subtree_members,
        tree_configuration,
    )
except ImportError:
    from report_fold_dynamics import vector
    from report_fold_material_depth3 import (
        initial_state,
        measure,
        rhs,
        subtree_members,
        tree_configuration,
    )


DT_S = 0.0005
MAX_DURATION_S = 0.1
RESOLUTION = 1e-12
SAMPLE_TIMES_S = (0.05, 0.075, 0.1)


def _state_size(sizes, edges):
    return 5 * len(sizes) + 2 * len(edges)


def advance(initial, depth, duration, *, connected=True, refinement=1):
    """Advance a saved passive recursive-material state with segment-relative ledgers."""
    cfg = tree_configuration(depth, connected=connected)
    sizes, edges = cfg["sizes"], cfg["edges"]
    if type(refinement) is not int or refinement not in (1, 2):
        raise ValueError("refinement must be 1 or 2")
    if isinstance(duration, (bool, complex)):
        raise ValueError("duration must be finite and real")
    try:
        duration = float(duration)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("duration must be finite and real") from error
    if not math.isfinite(duration) or not 0 < duration <= MAX_DURATION_S:
        raise ValueError("duration outside (0,0.1]")

    dt = DT_S / refinement
    steps = round(duration / dt)
    if not np.isclose(steps * dt, duration, rtol=0, atol=1e-14):
        raise ValueError("duration must contain complete integration steps")

    groups = subtree_members(len(sizes))
    y = vector(initial, _state_size(sizes, edges), "saved recursive material state").copy()
    rhs(y, sizes, edges)
    e0, u0, incident0, works0, groups0 = measure(y, sizes, edges, groups)
    b0 = y[: 5 * len(sizes)].reshape(len(sizes), 5).copy()
    node_max = np.zeros(len(sizes))
    edge_max = np.zeros(len(edges))
    group_max = dict.fromkeys(groups0, 0.0)
    coordinate_min = b0[:, :2].copy()
    coordinate_max = b0[:, :2].copy()
    samples = []

    def audit(state, time):
        nonlocal coordinate_min, coordinate_max
        energy, potential, incident, works, accounts = measure(state, sizes, edges, groups)
        blocks = state[: 5 * len(sizes)].reshape(len(sizes), 5)
        node_residual = energy - e0 + (blocks[:, 4] - b0[:, 4]) - (incident - incident0)
        edge_residual = potential - u0 + (works - works0).sum(axis=1)
        node_max[:] = np.maximum(node_max, np.abs(node_residual))
        edge_max[:] = np.maximum(edge_max, np.abs(edge_residual))
        for key, account in accounts.items():
            residual = (
                account["accounted_energy_j"]
                - groups0[key]["accounted_energy_j"]
                - (account["boundary_work_j"] - groups0[key]["boundary_work_j"])
            )
            group_max[key] = max(group_max[key], abs(residual))
        coordinate_min = np.minimum(coordinate_min, blocks[:, :2])
        coordinate_max = np.maximum(coordinate_max, blocks[:, :2])
        samples.append({"time_s": float(time), "root_state": blocks[0, :4].tolist()})

    audit(y, 0.0)
    for step in range(steps):
        a = rhs(y, sizes, edges)
        b = rhs(y + dt * a / 2, sizes, edges)
        c = rhs(y + dt * b / 2, sizes, edges)
        d = rhs(y + dt * c, sizes, edges)
        y += dt * (a + 2 * b + 2 * c + d) / 6
        audit(y, (step + 1) * dt)

    return {
        "settings": {
            **cfg,
            "duration_s": duration,
            "dt_s": dt,
            "steps": steps,
            "refinement": refinement,
        },
        "initial_state": vector(
            initial, _state_size(sizes, edges), "saved recursive material state"
        ).tolist(),
        "final_state": y.tolist(),
        "max_node_residual_j": node_max.tolist(),
        "max_edge_residual_j": edge_max.tolist(),
        "max_group_residual_j": group_max,
        "coordinate_min": coordinate_min.tolist(),
        "coordinate_max": coordinate_max.tolist(),
        "samples": samples,
    }


def run_from_reference(depth, duration, *, connected=True, refinement=1):
    cfg = tree_configuration(depth, connected=connected)
    return advance(
        initial_state(cfg["sizes"], cfg["edges"]),
        depth,
        duration,
        connected=connected,
        refinement=refinement,
    )


def sample_root(run, time_s):
    dt = run["settings"]["dt_s"]
    index = round(time_s / dt)
    row = run["samples"][index]
    if not np.isclose(row["time_s"], time_s, rtol=0, atol=1e-14):
        raise ValueError("requested root sample is off-grid")
    return np.asarray(row["root_state"])


def report():
    depth2 = run_from_reference(2, MAX_DURATION_S)
    depth3 = run_from_reference(3, MAX_DURATION_S)
    fine_depth3 = run_from_reference(3, MAX_DURATION_S, refinement=2)

    first_half = run_from_reference(3, 0.05)
    second_half = advance(first_half["final_state"], 3, 0.05)
    restart_difference = np.abs(
        np.asarray(second_half["final_state"]) - np.asarray(depth3["final_state"])
    )

    transitions = {}
    for time_s in SAMPLE_TIMES_S:
        delta = np.abs(sample_root(depth3, time_s) - sample_root(depth2, time_s))
        transitions[str(time_s)] = {
            "root_absolute_state_change": delta.tolist(),
            "maximum_root_absolute_state_change": float(np.max(delta)),
            "resolved": bool(np.max(delta) > RESOLUTION),
        }

    first_resolved = next(
        (time for time in SAMPLE_TIMES_S if transitions[str(time)]["resolved"]),
        None,
    )
    fine_difference = np.abs(
        np.asarray(depth3["final_state"]) - np.asarray(fine_depth3["final_state"])
    )
    return {
        "schema": 1,
        "scope": (
            "experimental passive depth-three duration extension to 0.1 s; "
            "unchanged material, connector and scale laws"
        ),
        "resolution_threshold": RESOLUTION,
        "sample_times_s": SAMPLE_TIMES_S,
        "cases": {
            "depth_2": depth2,
            "depth_3": depth3,
            "fine_depth_3": fine_depth3,
            "depth_3_first_half": first_half,
            "depth_3_second_half": second_half,
        },
        "depth_2_to_3": {
            "samples": transitions,
            "first_resolved_duration_s": first_resolved,
        },
        "restart": {
            "maximum_absolute_state_difference": float(np.max(restart_difference)),
            "absolute_state_differences": restart_difference.tolist(),
        },
        "refinement": {
            "maximum_absolute_state_difference": float(np.max(fine_difference)),
            "absolute_state_differences": fine_difference.tolist(),
        },
        "sources": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in (
                "report_fold_material_depth_duration.py",
                "report_fold_material_depth3.py",
                "report_fold_scale_extension.py",
                "report_fold_constitutive.py",
                "report_fold_mapped.py",
            )
        },
        "connector_law_changed": False,
        "material_scaling_law_changed": False,
        "production_duration_guard_changed": False,
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
