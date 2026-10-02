"""Solve the governing recursive panel contact over the dense local state box."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import shgo

try:
    from . import report_fold_recursive_exact_clearance as exact_clearance
except ImportError:
    import report_fold_recursive_exact_clearance as exact_clearance


ROOT_PATH = ()
DEPTH3_PATH = (0, 1, 1)
ROOT_BODY = "panel-0"
CHILD_BODY = "panel-5"

LOCAL_ROOT_SCALE_BOUNDS = (1.07, 1.1)
LOCAL_CHILD_SCALE_BOUNDS = (1.07, 1.1)
LOCAL_CHILD_THETA_BOUNDS = (0.0, 0.04)

START_LOWER = 14.963948939801849
START_UPPER = 14.964082840592333
UPPER_GUARDS = (
    15.014027835443041,
    15.048306437807067,
    15.082585040171093,
)
BISECTION_STEPS = 18
SHGO_SAMPLES = 96
SHGO_ITERS = 2


def transformed_panel(node, q, ratio, body_id):
    row = next(
        item
        for item in exact_clearance.geometry(
            q,
            length_m=exact_clearance.BASE_MODULE_LENGTH_M * node["scale"],
        )
        if item["id"] == body_id
    )
    vertices = np.asarray(row["vertices_m"], dtype=float)
    transform = exact_clearance.rotation(node["orientation_rad"])
    world = vertices.copy()
    world[:, :2] = vertices[:, :2] @ transform.T
    world[:, :2] += (
        ratio
        * exact_clearance.BASE_MODULE_LENGTH_M
        * node["center_normalized"]
    )
    return world


def governing_nodes():
    pair = exact_clearance.RECIPROCAL_RING_PAIRS[0]
    _, nodes = exact_clearance.candidate_nodes(pair)
    return nodes[ROOT_PATH], nodes[DEPTH3_PATH], pair


def governing_distance(
    ratio,
    root_scale,
    child_scale,
    child_theta,
    *,
    root_theta=0.0,
):
    root, child, _ = governing_nodes()
    root_vertices = transformed_panel(
        root,
        (root_scale, root_theta),
        ratio,
        ROOT_BODY,
    )
    child_vertices = transformed_panel(
        child,
        (child_scale, child_theta),
        ratio,
        CHILD_BODY,
    )
    return exact_clearance.body_distance(
        {"kind": "panel", "vertices": root_vertices},
        {"kind": "panel", "vertices": child_vertices},
    )


def optimize_local_state(ratio):
    def objective(state):
        return governing_distance(
            ratio,
            root_scale=state[0],
            child_scale=state[1],
            child_theta=state[2],
        )

    result = shgo(
        objective,
        (
            LOCAL_ROOT_SCALE_BOUNDS,
            LOCAL_CHILD_SCALE_BOUNDS,
            LOCAL_CHILD_THETA_BOUNDS,
        ),
        n=SHGO_SAMPLES,
        iters=SHGO_ITERS,
        sampling_method="simplicial",
    )
    if not result.success or not math.isfinite(float(result.fun)):
        raise RuntimeError("local governing-state optimizer failed")
    return {
        "minimum_clearance_m": float(result.fun),
        "state": {
            "root_scale": float(result.x[0]),
            "child_scale": float(result.x[1]),
            "child_theta": float(result.x[2]),
        },
        "function_evaluations": int(result.nfev),
        "collision_free": float(result.fun) > exact_clearance.COLLISION_TOLERANCE_M,
    }


def monotonicity(values, distances):
    values = np.asarray(values, dtype=float)
    distances = np.asarray(distances, dtype=float)
    if len(values) != len(distances) or len(values) < 2:
        raise ValueError("monotonicity requires aligned sequences with at least two points")
    if np.any(np.diff(values) <= 0):
        raise ValueError("monotonicity axis must increase strictly")
    differences = np.diff(distances)
    tolerance = exact_clearance.COLLISION_TOLERANCE_M
    return {
        "nondecreasing": bool(np.all(differences >= -tolerance)),
        "nonincreasing": bool(np.all(differences <= tolerance)),
        "minimum_difference_m": float(np.min(differences)),
        "maximum_difference_m": float(np.max(differences)),
    }


def axis_audits(ratio):
    root_scales = np.linspace(*LOCAL_ROOT_SCALE_BOUNDS, 31)
    child_scales = np.linspace(*LOCAL_CHILD_SCALE_BOUNDS, 31)
    child_thetas = np.linspace(*LOCAL_CHILD_THETA_BOUNDS, 41)

    root_distances = [
        governing_distance(ratio, scale, 1.1, 0.0)
        for scale in root_scales
    ]
    child_scale_distances = [
        governing_distance(ratio, 1.1, scale, 0.0)
        for scale in child_scales
    ]
    child_theta_distances = [
        governing_distance(ratio, 1.1, 1.1, theta)
        for theta in child_thetas
    ]

    return {
        "root_scale": {
            "axis": root_scales.tolist(),
            "distances_m": root_distances,
            **monotonicity(root_scales, root_distances),
        },
        "child_scale": {
            "axis": child_scales.tolist(),
            "distances_m": child_scale_distances,
            **monotonicity(child_scales, child_scale_distances),
        },
        "child_theta": {
            "axis": child_thetas.tolist(),
            "distances_m": child_theta_distances,
            **monotonicity(child_thetas, child_theta_distances),
        },
    }


def root_theta_invariance(ratio):
    samples = np.linspace(0.0, math.pi / 6, 13)
    reference = governing_distance(ratio, 1.1, 1.1, 0.0, root_theta=0.0)
    distances = [
        governing_distance(ratio, 1.1, 1.1, 0.0, root_theta=theta)
        for theta in samples
    ]
    return {
        "theta_samples": samples.tolist(),
        "distances_m": distances,
        "maximum_distance_difference_m": float(
            np.max(np.abs(np.asarray(distances) - reference))
        ),
    }


def report():
    cache = {}

    def optimized(ratio):
        key = float(ratio)
        if key not in cache:
            cache[key] = optimize_local_state(key)
        return cache[key]

    lower = START_LOWER
    lower_row = optimized(lower)
    if lower_row["collision_free"]:
        raise ValueError("starting lower ratio must remain colliding in local optimization")

    upper = None
    for candidate in (START_UPPER, *UPPER_GUARDS):
        row = optimized(candidate)
        if row["collision_free"]:
            upper = candidate
            break
    if upper is None:
        raise RuntimeError("no collision-free local upper guard found")

    bisection = []
    for step in range(BISECTION_STEPS):
        midpoint = (lower + upper) / 2
        row = optimized(midpoint)
        bisection.append(
            {
                "step": step + 1,
                "lower_before": lower,
                "upper_before": upper,
                "midpoint": midpoint,
                **row,
            }
        )
        if row["collision_free"]:
            upper = midpoint
        else:
            lower = midpoint

    final_lower = optimized(lower)
    final_upper = optimized(upper)

    root, child, axis_pair = governing_nodes()
    broad_cache = exact_clearance.local_geometry_cache(
        exact_clearance.candidate_nodes(axis_pair)[1]
    )
    broad_control = exact_clearance.scan_ratio(broad_cache, upper)

    fixed_corner_distance = governing_distance(
        upper,
        root_scale=1.1,
        child_scale=1.1,
        child_theta=0.0,
    )
    invariance = root_theta_invariance(upper)
    axes = axis_audits(upper)

    return {
        "schema": 1,
        "scope": (
            "continuous numerical local-state solve for the identified root-panel0 / "
            "depth3-panel5 zero-thickness contact family"
        ),
        "axis_pair": list(axis_pair),
        "root_path": list(ROOT_PATH),
        "depth3_path": list(DEPTH3_PATH),
        "root_body": ROOT_BODY,
        "child_body": CHILD_BODY,
        "local_bounds": {
            "root_scale": list(LOCAL_ROOT_SCALE_BOUNDS),
            "child_scale": list(LOCAL_CHILD_SCALE_BOUNDS),
            "child_theta": list(LOCAL_CHILD_THETA_BOUNDS),
        },
        "collision_tolerance_m": exact_clearance.COLLISION_TOLERANCE_M,
        "bisection_steps": BISECTION_STEPS,
        "starting_bracket": [START_LOWER, START_UPPER],
        "upper_guards": list(UPPER_GUARDS),
        "final_lower_colliding_ratio": lower,
        "final_upper_collision_free_ratio": upper,
        "final_width": upper - lower,
        "final_lower_optimized": final_lower,
        "final_upper_optimized": final_upper,
        "bisection": bisection,
        "fixed_corner_clearance_at_final_upper_m": fixed_corner_distance,
        "root_theta_invariance": invariance,
        "axis_audits_at_final_upper": axes,
        "broad_grid_control_at_final_upper": broad_control,
        "unique_optimized_ratio_count": len(cache),
        "source_node_scales": {
            "root": root["scale"],
            "depth3": child["scale"],
        },
        "sources": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in (
                "report_fold_recursive_governing_contact.py",
                "report_fold_recursive_governing_clearance.py",
                "report_fold_recursive_exact_clearance.py",
                "report_fold_recursive_material_placement.py",
                "report_fold_constitutive.py",
            )
        },
        "continuous_collision_theorem": False,
        "global_q_domain_optimized": False,
        "local_state_box_optimized": True,
        "body_geometry_changed": False,
        "collision_tolerance_changed": False,
        "physical_body_thickness_modeled": False,
        "manufacturing_margin_modeled": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
