"""Refine the exact recursive collision/free vessel-ratio bracket."""

import argparse
import hashlib
import json
from pathlib import Path

from .report_fold_recursive_exact_clearance import (
    RECIPROCAL_RING_PAIRS,
    candidate_nodes,
    footprint_requirements,
    local_geometry_cache,
    pair_clearance_requirement,
    scan_ratio,
)


SUBDIVISIONS = 4
REFINEMENT_STAGES = 4


def refinement_axis(lower, upper, subdivisions=SUBDIVISIONS):
    lower, upper = float(lower), float(upper)
    if not lower > 0 or not upper > lower:
        raise ValueError("refinement bracket must be positive and ordered")
    if type(subdivisions) is not int or subdivisions < 2:
        raise ValueError("subdivisions must be an integer >= 2")
    width = upper - lower
    return tuple(lower + width * index / subdivisions for index in range(subdivisions + 1))


def classify_mask(mask):
    mask = tuple(bool(value) for value in mask)
    if len(mask) < 2:
        raise ValueError("clearance mask must contain at least two samples")
    transitions = sum(a != b for a, b in zip(mask, mask[1:], strict=True))
    first_free = next((index for index, free in enumerate(mask) if free), None)
    reentrant = False
    if first_free is not None:
        reentrant = any(not free for free in mask[first_free + 1 :])
    return {
        "transition_count": transitions,
        "first_free_index": first_free,
        "reentrant_collision": reentrant,
    }


def report():
    footprint = footprint_requirements()
    canonical_pair = RECIPROCAL_RING_PAIRS[0]
    _, nodes = candidate_nodes(canonical_pair)
    geometry_cache = local_geometry_cache(nodes)

    local_ratio = footprint["minimum_spherical_bound_per_module_length"]
    lower = local_ratio * 5.0
    upper, _ = pair_clearance_requirement(nodes, local_ratio)

    scan_cache = {}

    def scan(value):
        key = float(value)
        if key not in scan_cache:
            scan_cache[key] = scan_ratio(geometry_cache, key)
        return scan_cache[key]

    lower_row, upper_row = scan(lower), scan(upper)
    if lower_row["collision_free"]:
        raise ValueError("refinement lower endpoint must remain colliding")
    if not upper_row["collision_free"]:
        raise ValueError("refinement upper endpoint must remain collision-free")

    stages = []
    current_lower, current_upper = lower, upper
    stopped_for_reentrant = False

    for stage_index in range(REFINEMENT_STAGES):
        axis = refinement_axis(current_lower, current_upper)
        rows = [scan(value) for value in axis]
        classification = classify_mask(row["collision_free"] for row in rows)
        stage = {
            "stage": stage_index + 1,
            "lower": current_lower,
            "upper": current_upper,
            "width": current_upper - current_lower,
            "axis": list(axis),
            "rows": rows,
            **classification,
        }
        stages.append(stage)

        first_free = classification["first_free_index"]
        if (
            classification["reentrant_collision"]
            or classification["transition_count"] != 1
            or first_free is None
            or first_free == 0
        ):
            stopped_for_reentrant = True
            break

        current_lower = axis[first_free - 1]
        current_upper = axis[first_free]

    final_lower = current_lower
    final_upper = current_upper
    final_lower_row = scan(final_lower)
    final_upper_row = scan(final_upper)

    return {
        "schema": 1,
        "scope": (
            "staged finite-grid refinement of the exact zero-thickness recursive "
            "collision/free vessel-ratio bracket"
        ),
        "canonical_axis_pair": list(canonical_pair),
        "subdivisions": SUBDIVISIONS,
        "requested_refinement_stages": REFINEMENT_STAGES,
        "completed_refinement_stages": len(stages),
        "coarse_lower_colliding_ratio": lower,
        "coarse_upper_collision_free_ratio": upper,
        "coarse_width": upper - lower,
        "stages": stages,
        "stopped_for_reentrant_or_multiple_transition": stopped_for_reentrant,
        "final_lower_colliding_ratio": final_lower,
        "final_upper_collision_free_ratio": final_upper,
        "final_width": final_upper - final_lower,
        "final_lower_row": final_lower_row,
        "final_upper_row": final_upper_row,
        "unique_ratio_scan_count": len(scan_cache),
        "sources": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in (
                "report_fold_recursive_exact_clearance_refinement.py",
                "report_fold_recursive_exact_clearance.py",
                "report_fold_recursive_material_placement.py",
                "report_fold_constitutive.py",
            )
        },
        "continuous_clearance_theorem": False,
        "body_geometry_changed": False,
        "collision_tolerance_changed": False,
        "q_state_grid_changed": False,
        "physical_body_thickness_modeled": False,
        "common_vessel_to_module_ratio_selected": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
