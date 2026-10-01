"""Audit explicit 22-body placement inside candidate recursive Seed-axis vessels."""

import argparse
import hashlib
import json
import math
from itertools import combinations
from pathlib import Path

import numpy as np

try:
    from .report_fold_constitutive import geometry
    from .report_fold_mapped import port
    from .report_fold_recursive_seed_correspondence import (
        RECIPROCAL_RING_PAIRS,
        binary_axis_tree,
    )
except ImportError:
    from report_fold_constitutive import geometry
    from report_fold_mapped import port
    from report_fold_recursive_seed_correspondence import (
        RECIPROCAL_RING_PAIRS,
        binary_axis_tree,
    )


BASE_MODULE_LENGTH_M = 0.1
Q_GRID = tuple(
    (scale_coordinate, theta)
    for scale_coordinate in (0.9, 1.0, 1.1)
    for theta in (0.0, math.pi / 12, math.pi / 6)
)


def rotation(angle):
    cosine, sine = math.cos(angle), math.sin(angle)
    return np.array(((cosine, -sine), (sine, cosine)))


def body_rows(q, length_m):
    return {
        row["id"]: np.asarray(row["vertices_m"], dtype=float)
        for row in geometry(q, length_m=length_m)
    }


def candidate_nodes(pair):
    candidate = binary_axis_tree(pair)
    first = np.asarray(candidate["levels"][1]["nodes"][0]["center"], dtype=float)
    axis_angle = math.atan2(first[1], first[0])
    nodes = {}
    for level in candidate["levels"]:
        for row in level["nodes"]:
            path = tuple(row["path"])
            nodes[path] = {
                "path": path,
                "depth": level["depth"],
                "scale": 0.5 ** level["depth"],
                "center_normalized": np.asarray(row["center"], dtype=float),
                "vessel_radius_normalized": float(row["radius"]),
                "orientation_rad": axis_angle + (sum(path) % 2) * math.pi,
            }
    return axis_angle, nodes


def transformed_bodies(node, q, vessel_ratio):
    length = BASE_MODULE_LENGTH_M * node["scale"]
    center = vessel_ratio * BASE_MODULE_LENGTH_M * node["center_normalized"]
    transform = rotation(node["orientation_rad"])
    result = {}
    for body_id, vertices in body_rows(q, length).items():
        xy = center + vertices[:, :2] @ transform.T
        result[body_id] = np.c_[xy, vertices[:, 2]]
    return result


def footprint_requirements():
    maximum_planar = 0.0
    maximum_spherical = 0.0
    governing_planar = None
    governing_spherical = None
    for q in Q_GRID:
        rows = body_rows(q, 1.0)
        for body_id, vertices in rows.items():
            planar = float(np.max(np.linalg.norm(vertices[:, :2], axis=1)))
            spherical = float(np.max(np.linalg.norm(vertices, axis=1)))
            if planar > maximum_planar:
                maximum_planar = planar
                governing_planar = {"q": list(q), "body_id": body_id}
            if spherical > maximum_spherical:
                maximum_spherical = spherical
                governing_spherical = {"q": list(q), "body_id": body_id}
    return {
        "minimum_vessel_radius_per_module_length_planar": maximum_planar,
        "minimum_spherical_bound_per_module_length": maximum_spherical,
        "governing_planar": governing_planar,
        "governing_spherical": governing_spherical,
    }


def pair_clearance_requirement(nodes, radius_coefficient, *, siblings_only=False):
    rows = []
    for path_a, path_b in combinations(nodes, 2):
        if siblings_only and (
            len(path_a) != len(path_b) or not path_a or path_a[:-1] != path_b[:-1]
        ):
            continue
        a, b = nodes[path_a], nodes[path_b]
        center_distance = float(np.linalg.norm(a["center_normalized"] - b["center_normalized"]))
        if center_distance == 0:
            required = math.inf
        else:
            required = radius_coefficient * (a["scale"] + b["scale"]) / center_distance
        rows.append(
            {
                "path_a": list(path_a),
                "path_b": list(path_b),
                "required_vessel_radius_per_module_length": required,
                "normalized_center_distance": center_distance,
            }
        )
    maximum = max(row["required_vessel_radius_per_module_length"] for row in rows)
    governing = max(
        rows,
        key=lambda row: row["required_vessel_radius_per_module_length"],
    )
    return maximum, governing


def mirror_placement_error(nodes, vessel_ratio, q):
    maximum_xy_error = 0.0
    maximum_z_error = 0.0
    for parent_path, parent in nodes.items():
        left_path, right_path = parent_path + (0,), parent_path + (1,)
        if left_path not in nodes or right_path not in nodes:
            continue
        left = transformed_bodies(nodes[left_path], q, vessel_ratio)
        right = transformed_bodies(nodes[right_path], q, vessel_ratio)
        parent_center = vessel_ratio * BASE_MODULE_LENGTH_M * parent["center_normalized"]
        for body_id in left:
            a, b = left[body_id], right[body_id]
            if a.shape != b.shape:
                raise ValueError("mirror body vertex count mismatch")
            xy_error = np.max(np.linalg.norm(a[:, :2] + b[:, :2] - 2 * parent_center, axis=1))
            z_error = np.max(np.abs(a[:, 2] - b[:, 2]))
            maximum_xy_error = max(maximum_xy_error, float(xy_error))
            maximum_z_error = max(maximum_z_error, float(z_error))
    return maximum_xy_error, maximum_z_error


def axis_equivalence_error(pair, canonical_pair, vessel_ratio, q):
    canonical_angle, canonical_nodes = candidate_nodes(canonical_pair)
    angle, nodes = candidate_nodes(pair)
    undo = rotation(canonical_angle - angle)
    maximum = 0.0
    for path, canonical in canonical_nodes.items():
        current = nodes[path]
        canonical_bodies = transformed_bodies(canonical, q, vessel_ratio)
        current_bodies = transformed_bodies(current, q, vessel_ratio)
        for body_id in canonical_bodies:
            target = canonical_bodies[body_id]
            candidate = current_bodies[body_id].copy()
            candidate[:, :2] = candidate[:, :2] @ undo.T
            maximum = max(
                maximum,
                float(np.max(np.linalg.norm(candidate - target, axis=1))),
            )
    return maximum


def connector_spatial_compatibility(nodes):
    rows = []
    mismatch_by_child_bit = {0: 0.0, 1: 0.0}
    rest_coefficients = []
    for child_path, child in nodes.items():
        if not child_path:
            continue
        parent_path = child_path[:-1]
        parent = nodes[parent_path]
        parent_rotation = rotation(parent["orientation_rad"])
        child_rotation = rotation(child["orientation_rad"])
        relative_rotation = parent_rotation.T @ child_rotation
        center_distance = float(
            np.linalg.norm(child["center_normalized"] - parent["center_normalized"])
        )
        rest_per_parent_length_per_vessel_ratio = center_distance / parent["scale"]
        rest_coefficients.append(rest_per_parent_length_per_vessel_ratio)

        maximum_mismatch = 0.0
        maximum_local_delta = 0.0
        for q in Q_GRID:
            parent_port = port(q, BASE_MODULE_LENGTH_M * parent["scale"])[0]
            child_port = port(q, BASE_MODULE_LENGTH_M * child["scale"])[0]
            existing_delta = parent_port - child_port
            spatial_rest_corrected_delta = parent_port - relative_rotation @ child_port
            parent_length = BASE_MODULE_LENGTH_M * parent["scale"]
            maximum_mismatch = max(
                maximum_mismatch,
                float(
                    np.linalg.norm(spatial_rest_corrected_delta - existing_delta) / parent_length
                ),
            )
            maximum_local_delta = max(
                maximum_local_delta,
                float(np.linalg.norm(existing_delta) / parent_length),
            )

        child_bit = child_path[-1]
        mismatch_by_child_bit[child_bit] = max(mismatch_by_child_bit[child_bit], maximum_mismatch)
        rows.append(
            {
                "parent_path": list(parent_path),
                "child_path": list(child_path),
                "child_bit": child_bit,
                "relative_orientation_rad": float(
                    (child["orientation_rad"] - parent["orientation_rad"]) % (2 * math.pi)
                ),
                "rest_offset_per_parent_length_per_vessel_ratio": (
                    rest_per_parent_length_per_vessel_ratio
                ),
                "maximum_frame_mismatch_per_parent_length": maximum_mismatch,
                "maximum_existing_local_delta_per_parent_length": (maximum_local_delta),
            }
        )
    return {
        "edges": rows,
        "rest_offset_coefficient_min": min(rest_coefficients),
        "rest_offset_coefficient_max": max(rest_coefficients),
        "maximum_frame_mismatch_by_child_bit": mismatch_by_child_bit,
    }


def report():
    footprint = footprint_requirements()
    canonical_pair = RECIPROCAL_RING_PAIRS[0]
    axes = []
    all_pair_requirements = []
    all_sibling_requirements = []

    for pair in RECIPROCAL_RING_PAIRS:
        _, nodes = candidate_nodes(pair)
        sibling_requirement, sibling_governing = pair_clearance_requirement(
            nodes,
            footprint["minimum_spherical_bound_per_module_length"],
            siblings_only=True,
        )
        all_requirement, all_governing = pair_clearance_requirement(
            nodes,
            footprint["minimum_spherical_bound_per_module_length"],
        )
        all_pair_requirements.append(all_requirement)
        all_sibling_requirements.append(sibling_requirement)

        mirror_xy = 0.0
        mirror_z = 0.0
        axis_error = 0.0
        for q in Q_GRID:
            x_error, z_error = mirror_placement_error(
                nodes,
                footprint["minimum_vessel_radius_per_module_length_planar"],
                q,
            )
            mirror_xy = max(mirror_xy, x_error)
            mirror_z = max(mirror_z, z_error)
            axis_error = max(
                axis_error,
                axis_equivalence_error(
                    pair,
                    canonical_pair,
                    footprint["minimum_vessel_radius_per_module_length_planar"],
                    q,
                ),
            )

        axes.append(
            {
                "axis_pair": list(pair),
                "module_count": len(nodes),
                "minimum_conservative_sibling_nonoverlap_ratio": (sibling_requirement),
                "sibling_governing_pair": sibling_governing,
                "minimum_conservative_all_module_nonoverlap_ratio": (all_requirement),
                "all_module_governing_pair": all_governing,
                "maximum_recursive_mirror_xy_error_m": mirror_xy,
                "maximum_recursive_mirror_z_error_m": mirror_z,
                "maximum_rigid_axis_equivalence_error_m": axis_error,
                "connector_spatial_compatibility": (connector_spatial_compatibility(nodes)),
            }
        )

    minimum_planar = footprint["minimum_vessel_radius_per_module_length_planar"]
    minimum_spherical = footprint["minimum_spherical_bound_per_module_length"]
    conservative_all = max(all_pair_requirements)
    conservative_sibling = max(all_sibling_requirements)

    return {
        "schema": 1,
        "scope": (
            "candidate 22-body local-frame placement envelope inside the three "
            "symmetry-related binary Seed-axis vessel slices; no physical vessel/module "
            "size ratio selected"
        ),
        "base_module_length_m": BASE_MODULE_LENGTH_M,
        "q_grid": [list(q) for q in Q_GRID],
        "footprint": footprint,
        "common_scale_envelope": {
            "minimum_ratio_for_planar_vertex_containment": minimum_planar,
            "minimum_ratio_for_spherical_vertex_containment": minimum_spherical,
            "minimum_ratio_for_conservative_sibling_sphere_nonoverlap": (conservative_sibling),
            "minimum_ratio_for_conservative_all_module_sphere_nonoverlap": (conservative_all),
            "minimum_root_vessel_radius_m_if_planar_containment_only": (
                minimum_planar * BASE_MODULE_LENGTH_M
            ),
            "minimum_root_vessel_radius_m_if_conservative_all_module_nonoverlap": (
                conservative_all * BASE_MODULE_LENGTH_M
            ),
        },
        "axes": axes,
        "sources": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in (
                "report_fold_recursive_material_placement.py",
                "report_fold_recursive_seed_correspondence.py",
                "report_fold_constitutive.py",
                "report_fold_kinematics.py",
                "report_fold_mapped.py",
            )
        },
        "common_vessel_to_module_ratio_selected": False,
        "canonical_seed_axis_selected": False,
        "conservative_bounding_sphere_is_exact_collision_certificate": False,
        "direct_existing_connector_spatially_compatible": False,
        "spatial_rest_offset_adapter_required": True,
        "branch_orientation_adapter_required_for_mirror_placement": True,
        "physical_spatial_assembly_validated": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
