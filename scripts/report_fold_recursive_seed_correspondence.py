"""Audit correspondence between binary material recursion and Seed/Vesica recursion."""

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path

import numpy as np

from src.sevenfold_seed_contract import mirror_vesica_index, seed_vesicas
from src.universe_port_engine import (
    CONTAINED_RECURSION_SCALE,
    SEED_CIRCLE_SCALE,
    VESICAS_PER_SEED,
    CircleVessel,
    central_mirror_point,
    seed_circles,
)

try:
    from .report_fold_material_depth3 import SCALE_RATIO
except ImportError:
    from report_fold_material_depth3 import SCALE_RATIO
RECIPROCAL_RING_PAIRS = ((1, 4), (2, 5), (3, 6))
MAX_AUDIT_DEPTH = 3


def material_exact_level(depth):
    if type(depth) is not int or not 0 <= depth <= MAX_AUDIT_DEPTH:
        raise ValueError("depth must be an integer in [0,3]")
    return {
        "depth": depth,
        "module_count": 2**depth,
        "linear_scale": SCALE_RATIO**depth,
    }


def contained_vesica_exact_depth(depth):
    if type(depth) is not int or depth < 0:
        raise ValueError("depth must be a nonnegative integer")
    return {
        "depth": depth,
        "address_count": VESICAS_PER_SEED**depth,
        "vessel_scale": CONTAINED_RECURSION_SCALE**depth,
    }


def alternating_seed_stage(material_depth):
    """Map material scale only onto vessel/Seed-circle stages, not topology."""
    row = material_exact_level(material_depth)
    universe_depth, parity = divmod(material_depth, 2)
    if parity == 0:
        stage = "contained_vessel"
        geometric_scale = CONTAINED_RECURSION_SCALE**universe_depth
    else:
        stage = "seed_circle"
        geometric_scale = (
            CONTAINED_RECURSION_SCALE**universe_depth * SEED_CIRCLE_SCALE
        )
    return {
        **row,
        "universe_depth": universe_depth,
        "stage": stage,
        "geometric_scale": geometric_scale,
        "scale_error": abs(row["linear_scale"] - geometric_scale),
    }


def vesica_mirror_pairs():
    pairs = []
    seen = set()
    for index in range(len(seed_vesicas())):
        mirror = mirror_vesica_index(index)
        pair = tuple(sorted((index, mirror)))
        if pair not in seen:
            seen.add(pair)
            pairs.append(pair)
    return tuple(sorted(pairs))


def mirror_closed_four_address_subsets():
    """All four-address subsets closed under the central Vesica mirror."""
    mirror_pairs = vesica_mirror_pairs()
    return tuple(
        tuple(sorted(left + right))
        for left, right in combinations(mirror_pairs, 2)
    )


def binary_axis_tree(pair, depth=MAX_AUDIT_DEPTH):
    """Build a candidate material-container tree from one opposite Seed axis."""
    if pair not in RECIPROCAL_RING_PAIRS:
        raise ValueError("pair must be one of the three reciprocal Seed axes")
    if type(depth) is not int or not 0 <= depth <= MAX_AUDIT_DEPTH:
        raise ValueError("depth must be an integer in [0,3]")

    root = CircleVessel()
    levels = [[{"path": (), "vessel": root}]]
    containment_errors = []
    mirror_errors = []
    radius_errors = []

    for _level in range(depth):
        children = []
        for parent in levels[-1]:
            vessel = parent["vessel"]
            circles = seed_circles(vessel)
            left, right = (circles[index] for index in pair)
            expected_radius = vessel.radius * SCALE_RATIO
            radius_errors.extend(
                (abs(left.radius - expected_radius), abs(right.radius - expected_radius))
            )
            containment_errors.extend(
                (
                    0.0 if vessel.contains_circle(left) else 1.0,
                    0.0 if vessel.contains_circle(right) else 1.0,
                )
            )
            mirrored_left = central_mirror_point(left.center, vessel.center)
            mirrored_right = central_mirror_point(right.center, vessel.center)
            mirror_errors.extend(
                (
                    float(np.linalg.norm(np.asarray(mirrored_left) - np.asarray(right.center))),
                    float(np.linalg.norm(np.asarray(mirrored_right) - np.asarray(left.center))),
                )
            )
            children.extend(
                (
                    {"path": parent["path"] + (0,), "vessel": left},
                    {"path": parent["path"] + (1,), "vessel": right},
                )
            )
        levels.append(children)

    serialized = []
    for level, nodes in enumerate(levels):
        serialized.append(
            {
                "depth": level,
                "count": len(nodes),
                "expected_count": 2**level,
                "expected_scale": SCALE_RATIO**level,
                "nodes": [
                    {
                        "path": list(node["path"]),
                        "center": list(node["vessel"].center),
                        "radius": node["vessel"].radius,
                    }
                    for node in nodes
                ],
            }
        )

    return {
        "axis_pair": list(pair),
        "levels": serialized,
        "maximum_containment_failure": max(containment_errors, default=0.0),
        "maximum_mirror_center_error": max(mirror_errors, default=0.0),
        "maximum_radius_error": max(radius_errors, default=0.0),
    }


def report():
    material = [material_exact_level(depth) for depth in range(MAX_AUDIT_DEPTH + 1)]
    vesica = [contained_vesica_exact_depth(depth) for depth in range(3)]
    cadence = [alternating_seed_stage(depth) for depth in range(MAX_AUDIT_DEPTH + 1)]
    axis_candidates = [binary_axis_tree(pair) for pair in RECIPROCAL_RING_PAIRS]
    mirror_pairs = vesica_mirror_pairs()
    four_subsets = mirror_closed_four_address_subsets()

    depth_two_material = material_exact_level(2)
    depth_one_vesica = contained_vesica_exact_depth(1)

    return {
        "schema": 1,
        "scope": (
            "correspondence audit only: binary half-scale material recursion versus "
            "full twelve-way quarter-scale contained Vesica recursion and a mirror-axis "
            "Seed-circle slice candidate"
        ),
        "constants": {
            "material_scale_ratio": SCALE_RATIO,
            "seed_circle_scale": SEED_CIRCLE_SCALE,
            "contained_vesica_recursion_scale": CONTAINED_RECURSION_SCALE,
            "vesicas_per_seed": VESICAS_PER_SEED,
        },
        "material_exact_levels": material,
        "vesica_exact_depths": vesica,
        "alternating_scale_cadence": cadence,
        "direct_topology_comparison": {
            "material_children_per_node": 2,
            "vesica_children_per_vessel": VESICAS_PER_SEED,
            "direct_edge_scale_match": SCALE_RATIO == CONTAINED_RECURSION_SCALE,
            "same_recursive_graph": False,
        },
        "two_material_levels_vs_one_vesica_step": {
            "material_descendants": depth_two_material["module_count"],
            "vesica_addresses": depth_one_vesica["address_count"],
            "scale_match": abs(
                depth_two_material["linear_scale"] - depth_one_vesica["vessel_scale"]
            )
            < 1e-15,
            "count_match": depth_two_material["module_count"]
            == depth_one_vesica["address_count"],
        },
        "vesica_mirror_pairs": [list(pair) for pair in mirror_pairs],
        "vesica_mirror_pair_count": len(mirror_pairs),
        "mirror_closed_four_address_subsets": [list(row) for row in four_subsets],
        "mirror_closed_four_address_subset_count": len(four_subsets),
        "binary_seed_axis_candidates": axis_candidates,
        "binary_seed_axis_candidate_count": len(axis_candidates),
        "binary_axis_candidate_is_canonical": False,
        "full_vesica_recursion_replaced": False,
        "material_tree_identified_with_full_vesica_recursion": False,
        "spatial_material_body_placement_validated": False,
        "physical_joint_correspondence_validated": False,
        "sources": {
            "report_fold_recursive_seed_correspondence.py": hashlib.sha256(
                Path(__file__).read_bytes()
            ).hexdigest(),
            "report_fold_material_depth3.py": hashlib.sha256(
                Path(__file__).with_name("report_fold_material_depth3.py").read_bytes()
            ).hexdigest(),
        },
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
