"""Restart persistence and deep bookkeeping controls for the powered material graph."""

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.integrate import RK45

try:
    from .report_fold_hierarchy import compile_hierarchy
    from .report_fold_kinematics import scalar
    from .report_fold_material_supply import (
        BASE_SIZES,
        EDGES,
        TREE,
        initial_state,
        measure,
        rhs,
    )
    from .report_fold_multiscale import configuration
    from .report_fold_dynamics import vector
except ImportError:
    from report_fold_hierarchy import compile_hierarchy
    from report_fold_kinematics import scalar
    from report_fold_material_supply import BASE_SIZES, EDGES, TREE, initial_state, measure, rhs
    from report_fold_multiscale import configuration
    from report_fold_dynamics import vector


STATE_SIZE = 48


def advance(initial, duration, *, power_density=6e-6, max_step=0.002, rtol=1e-9):
    """Advance a saved powered-material state while retaining cumulative ledgers."""
    duration = scalar(duration, "duration")
    max_step = scalar(max_step, "max_step")
    rtol = scalar(rtol, "rtol")
    if not 0 < duration <= 1 or not 0 < max_step <= 0.01 or not 1e-12 <= rtol <= 1e-6:
        raise ValueError("invalid duration, max_step or rtol")

    sizes, edges = configuration(BASE_SIZES, EDGES)
    layout = compile_hierarchy(len(sizes), edges, TREE)
    y = vector(initial, STATE_SIZE, "saved powered material state").copy()
    rhs(y, sizes, edges, power_density=power_density)

    e0, u0, incident0, input0, groups0 = measure(y, sizes, edges, layout)
    b0 = y[:36].reshape(4, 9).copy()
    edge_work0 = y[36:44].reshape(4, 2).copy()
    maxima = {
        "node_mechanical_residual_j": np.zeros(4),
        "node_reservoir_residual_j": np.zeros(4),
        "edge_residual_j": np.zeros(4),
    }
    group_max = dict.fromkeys(groups0, 0.0)
    minimum_reserve = b0[:, 4].copy()

    def audit(state):
        nonlocal minimum_reserve
        energy, potential, incident, supplied, groups = measure(state, sizes, edges, layout)
        blocks = state[:36].reshape(4, 9)
        edge_work = state[36:44].reshape(4, 2)
        maxima["node_mechanical_residual_j"] = np.maximum(
            maxima["node_mechanical_residual_j"],
            np.abs(
                energy
                - e0
                - (blocks[:, 5] - b0[:, 5])
                + (blocks[:, 6] - b0[:, 6])
                - (incident - incident0)
            ),
        )
        maxima["node_reservoir_residual_j"] = np.maximum(
            maxima["node_reservoir_residual_j"],
            np.abs(
                blocks[:, 4]
                - b0[:, 4]
                + (blocks[:, 5] - b0[:, 5])
                + (blocks[:, 7] - b0[:, 7])
                + (blocks[:, 8] - b0[:, 8])
                - (supplied - input0)
            ),
        )
        maxima["edge_residual_j"] = np.maximum(
            maxima["edge_residual_j"],
            np.abs(potential - u0 + (edge_work - edge_work0).sum(axis=1)),
        )
        for path, account in groups.items():
            residual = (
                account["accounted_energy_j"]
                - groups0[path]["accounted_energy_j"]
                - (account["boundary_work_j"] - groups0[path]["boundary_work_j"])
                - (account["input_j"] - groups0[path]["input_j"])
            )
            group_max[path] = max(group_max[path], abs(residual))
        minimum_reserve = np.minimum(minimum_reserve, blocks[:, 4])

    audit(y)
    atol = np.r_[np.tile([1e-11] * 4 + [1e-16] * 5, 4), np.full(12, 1e-16)]
    solver = RK45(
        lambda t, state: rhs(state, sizes, edges, power_density=power_density),
        0.0,
        y,
        duration,
        max_step=max_step,
        rtol=rtol,
        atol=atol,
        first_step=min(max_step, duration),
    )
    while solver.status == "running":
        message = solver.step()
        if solver.status == "failed":
            raise RuntimeError(f"persistent material integration failed: {message}")
        y = solver.y.copy()
        audit(y)

    return {
        "duration_s": duration,
        "power_density_w": power_density,
        "max_step_s": max_step,
        "rtol": rtol,
        "initial_state": vector(initial, STATE_SIZE, "saved powered material state").tolist(),
        "final_state": y.tolist(),
        "accepted_steps": solver.nfev,
        "minimum_reserve_j": minimum_reserve.tolist(),
        **{"max_" + key: value.tolist() for key, value in maxima.items()},
        "max_group_residual_j": group_max,
    }


def wrapped_tree(wrappers):
    """Add unary bookkeeping layers without adding physical modules."""
    if type(wrappers) is not int or not 0 <= wrappers <= 6:
        raise ValueError("wrappers must be an integer in [0,6]")
    tree = TREE
    for _ in range(wrappers):
        tree = [tree]
    return tree


def hierarchy_audit(state):
    """Verify that extra bookkeeping depth does not manufacture new energy."""
    sizes, edges = configuration(BASE_SIZES, EDGES)
    state = vector(state, STATE_SIZE, "saved powered material state")
    cases = {}
    reference = None
    for wrappers in (0, 1, 3, 6):
        tree = wrapped_tree(wrappers)
        layout = compile_hierarchy(4, edges, tree)
        _, _, _, _, groups = measure(state, sizes, edges, layout)
        root = groups["root"]
        current = {
            "wrappers": wrappers,
            "group_count": len(layout["groups"]),
            "deepest_path_separators": max(path.count("/") for path in layout["groups"]),
            "root_accounted_energy_j": root["accounted_energy_j"],
            "root_boundary_work_j": root["boundary_work_j"],
            "root_input_j": root["input_j"],
            "owned_edge_count": sum(len(values) for values in layout["owners"].values()),
        }
        if reference is None:
            reference = current
        current["root_energy_difference_j"] = (
            current["root_accounted_energy_j"] - reference["root_accounted_energy_j"]
        )
        current["root_input_difference_j"] = current["root_input_j"] - reference["root_input_j"]
        cases[str(wrappers)] = current
    return {
        "cases": cases,
        "interpretation": (
            "Additional hierarchy depth is bookkeeping over the same four physical modules; "
            "it does not create new degrees of freedom, energy, or cross-scale dynamics."
        ),
        "physical_recursive_replication_tested": False,
    }


def report():
    start = initial_state()
    first = advance(start, 0.4)
    saved_text = json.dumps(first["final_state"], allow_nan=False)
    restored = json.loads(saved_text)
    second = advance(restored, 0.4)
    continuous = advance(start, 0.8)
    source_off_first = advance(start, 0.4, power_density=0)
    source_off_second = advance(source_off_first["final_state"], 0.4, power_density=0)
    source_off_continuous = advance(start, 0.8, power_density=0)

    powered_difference = np.abs(
        np.asarray(second["final_state"]) - np.asarray(continuous["final_state"])
    )
    source_off_difference = np.abs(
        np.asarray(source_off_second["final_state"])
        - np.asarray(source_off_continuous["final_state"])
    )
    return {
        "schema": 1,
        "scope": (
            "0.8 second restart persistence and bookkeeping-depth controls for the "
            "four-module powered material graph"
        ),
        "segments": {
            "powered_first": first,
            "powered_second": second,
            "powered_continuous": continuous,
            "source_off_first": source_off_first,
            "source_off_second": source_off_second,
            "source_off_continuous": source_off_continuous,
        },
        "restart": {
            "serialization": "JSON finite-number round trip of the complete 48-component state",
            "powered_maximum_absolute_state_difference": float(np.max(powered_difference)),
            "powered_absolute_state_differences": powered_difference.tolist(),
            "source_off_maximum_absolute_state_difference": float(np.max(source_off_difference)),
            "source_off_absolute_state_differences": source_off_difference.tolist(),
        },
        "hierarchy": hierarchy_audit(second["final_state"]),
        "persistent_state_demonstrated_over_s": 0.8,
        "arbitrary_physical_depth_demonstrated": False,
        "stable_limit_cycle_demonstrated": False,
        "measured_material_calibration": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
