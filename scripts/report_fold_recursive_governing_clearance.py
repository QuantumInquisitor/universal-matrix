"""Densify the governing root/depth-3 recursive clearance state neighborhood."""

import argparse
import hashlib
import json
import math
from itertools import product
from pathlib import Path

import numpy as np

try:
    from . import report_fold_recursive_exact_clearance as exact_clearance
except ImportError:
    import report_fold_recursive_exact_clearance as exact_clearance


DENSE_SCALE_VALUES = (1.07, 1.08, 1.09, 1.095, 1.1)
DENSE_THETA_VALUES = (0.0, 0.0025, 0.005, 0.01, 0.02, 0.04)
DENSE_Q = tuple(product(DENSE_SCALE_VALUES, DENSE_THETA_VALUES))

BROAD_GRID_LOWER = 14.945470630714992
BROAD_GRID_UPPER = 14.979749233079017
UPPER_GUARDS = (
    15.014027835443041,
    15.048306437807067,
    15.082585040171093,
)
BISECTION_STEPS = 8

ROOT_PATH = ()
DEPTH3_PATH = (0, 1, 1)
CORNER_Q = (1.1, 0.0)


def is_corner_q(q):
    return tuple(float(value) for value in q) == CORNER_Q


def custom_module(node):
    transform = exact_clearance.rotation(node["orientation_rad"])
    states = []
    for q_index, q in enumerate(DENSE_Q):
        bodies = []
        radius = 0.0
        for row in exact_clearance.geometry(
            q,
            length_m=exact_clearance.BASE_MODULE_LENGTH_M * node["scale"],
        ):
            vertices = np.asarray(row["vertices_m"], dtype=float)
            rotated = vertices.copy()
            rotated[:, :2] = vertices[:, :2] @ transform.T
            radius = max(
                radius,
                float(np.max(np.linalg.norm(rotated, axis=1))),
            )
            bodies.append(
                {
                    "id": row["id"],
                    "kind": exact_clearance.body_kind(row["id"]),
                    "vertices": rotated,
                    "aabb_min": np.min(rotated, axis=0),
                    "aabb_max": np.max(rotated, axis=0),
                }
            )
        states.append(
            {
                "q_index": q_index,
                "q": list(q),
                "bodies": bodies,
                "radius": radius,
            }
        )

    return {
        "path": node["path"],
        "scale": node["scale"],
        "center_coefficient": np.r_[
            exact_clearance.BASE_MODULE_LENGTH_M * node["center_normalized"],
            0.0,
        ],
        "states": states,
    }


def scan_governing_pair(module_a, module_b, ratio):
    best = math.inf
    best_interior = math.inf
    governing = None
    governing_interior = None
    collision_state_pairs = 0

    for state_a, state_b in product(module_a["states"], module_b["states"]):
        corner_pair = is_corner_q(state_a["q"]) and is_corner_q(state_b["q"])
        search_limit = best if corner_pair else best_interior
        detail = exact_clearance.module_pair_clearance(
            module_a,
            state_a,
            module_b,
            state_b,
            ratio,
            search_limit,
        )
        if detail is None:
            continue

        distance = detail["distance_m"]
        row = {
            **detail,
            "q_a": state_a["q"],
            "q_b": state_b["q"],
            "corner_pair": corner_pair,
        }

        if not corner_pair and distance < best_interior:
            best_interior = distance
            governing_interior = row
        if distance < best:
            best = distance
            governing = row
        if distance <= exact_clearance.COLLISION_TOLERANCE_M:
            collision_state_pairs += 1

    if not math.isfinite(best):
        raise RuntimeError("dense governing-pair scan produced no finite distance")
    if not math.isfinite(best_interior):
        raise RuntimeError("dense interior governing-pair scan produced no finite distance")

    return {
        "ratio": float(ratio),
        "collision_free": collision_state_pairs == 0,
        "collision_state_pair_count": collision_state_pairs,
        "minimum_clearance_m": best,
        "minimum_clearance_per_root_module_length": (best / exact_clearance.BASE_MODULE_LENGTH_M),
        "governing_case": governing,
        "minimum_interior_clearance_m": best_interior,
        "interior_governing_case": governing_interior,
        "corner_clearance_advantage_m": best_interior - best,
    }


def report():
    canonical_pair = exact_clearance.RECIPROCAL_RING_PAIRS[0]
    _, nodes = exact_clearance.candidate_nodes(canonical_pair)
    root = custom_module(nodes[ROOT_PATH])
    depth3 = custom_module(nodes[DEPTH3_PATH])

    scan_cache = {}

    def scan(value):
        key = float(value)
        if key not in scan_cache:
            scan_cache[key] = scan_governing_pair(root, depth3, key)
        return scan_cache[key]

    lower = BROAD_GRID_LOWER
    lower_row = scan(lower)
    if lower_row["collision_free"]:
        raise ValueError("dense lower endpoint unexpectedly became collision-free")

    candidate_uppers = (BROAD_GRID_UPPER, *UPPER_GUARDS)
    upper = None
    for candidate in candidate_uppers:
        if scan(candidate)["collision_free"]:
            upper = candidate
            break
    if upper is None:
        return {
            "schema": 1,
            "resolved_bracket": False,
            "lower_colliding_ratio": lower,
            "tested_upper_guards": list(candidate_uppers),
            "scan_cache": [scan_cache[key] for key in sorted(scan_cache)],
            "dense_q": [list(q) for q in DENSE_Q],
            "continuous_clearance_theorem": False,
        }

    bisection_rows = []
    for step in range(BISECTION_STEPS):
        midpoint = (lower + upper) / 2
        row = scan(midpoint)
        bisection_rows.append(
            {
                "step": step + 1,
                "lower_before": lower,
                "upper_before": upper,
                "midpoint": midpoint,
                "midpoint_collision_free": row["collision_free"],
                "midpoint_collision_state_pair_count": row["collision_state_pair_count"],
                "midpoint_governing_case": row["governing_case"],
            }
        )
        if row["collision_free"]:
            upper = midpoint
        else:
            lower = midpoint

    final_lower = scan(lower)
    final_upper = scan(upper)

    broad_cache = exact_clearance.local_geometry_cache(nodes)
    broad_control = exact_clearance.scan_ratio(broad_cache, upper)

    return {
        "schema": 1,
        "scope": (
            "dense root/depth-3 state-neighborhood clearance refinement near the "
            "scale=1.1, theta=0 governing corner"
        ),
        "resolved_bracket": True,
        "canonical_axis_pair": list(canonical_pair),
        "root_path": list(ROOT_PATH),
        "depth3_path": list(DEPTH3_PATH),
        "dense_scale_values": list(DENSE_SCALE_VALUES),
        "dense_theta_values": list(DENSE_THETA_VALUES),
        "dense_state_count_per_module": len(DENSE_Q),
        "dense_independent_state_pair_count": len(DENSE_Q) ** 2,
        "corner_q": list(CORNER_Q),
        "starting_broad_grid_bracket": [
            BROAD_GRID_LOWER,
            BROAD_GRID_UPPER,
        ],
        "upper_guards": list(UPPER_GUARDS),
        "bisection_steps": BISECTION_STEPS,
        "bisection_rows": bisection_rows,
        "final_lower_colliding_ratio": lower,
        "final_upper_collision_free_ratio": upper,
        "final_width": upper - lower,
        "final_lower_row": final_lower,
        "final_upper_row": final_upper,
        "corner_is_governing_at_final_upper": bool(final_upper["governing_case"]["corner_pair"]),
        "interior_clearance_margin_at_final_upper_m": final_upper["corner_clearance_advantage_m"],
        "broad_grid_control_at_final_upper": broad_control,
        "unique_dense_ratio_scan_count": len(scan_cache),
        "sources": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in (
                "report_fold_recursive_governing_clearance.py",
                "report_fold_recursive_exact_clearance.py",
                "report_fold_recursive_material_placement.py",
                "report_fold_constitutive.py",
            )
        },
        "body_geometry_changed": False,
        "collision_tolerance_changed": False,
        "physical_body_thickness_modeled": False,
        "continuous_clearance_theorem": False,
        "common_vessel_to_module_ratio_selected": False,
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
