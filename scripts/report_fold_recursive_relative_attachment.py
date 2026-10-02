"""Search physical relative-marker frames for the abstract recursive connector port."""

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path

import numpy as np

try:
    from .report_fold_dynamics import Q0
    from .report_fold_mapped import port
    from .report_fold_recursive_port_body_correspondence import (
        EXACT_DISPLACEMENT_TOLERANCE,
        EXACT_JACOBIAN_TOLERANCE,
        FIT_Q,
        JACOBIAN_Q,
        SCALED_ORTHOGONAL_TOLERANCE,
        VALIDATION_LENGTHS_M,
        VALIDATION_Q,
        catalog,
        point,
        point_jacobian,
        transform_geometry,
    )
except ImportError:
    from report_fold_dynamics import Q0
    from report_fold_mapped import port
    from report_fold_recursive_port_body_correspondence import (
        EXACT_DISPLACEMENT_TOLERANCE,
        EXACT_JACOBIAN_TOLERANCE,
        FIT_Q,
        JACOBIAN_Q,
        SCALED_ORTHOGONAL_TOLERANCE,
        VALIDATION_LENGTHS_M,
        VALIDATION_Q,
        catalog,
        point,
        point_jacobian,
        transform_geometry,
    )


PAIR_EXACT_DISPLACEMENT_TOLERANCE = EXACT_DISPLACEMENT_TOLERANCE
PAIR_EXACT_JACOBIAN_TOLERANCE = EXACT_JACOBIAN_TOLERANCE
PAIR_SCALED_ORTHOGONAL_TOLERANCE = SCALED_ORTHOGONAL_TOLERANCE


def pair_catalog():
    markers = catalog()
    return [
        {
            "candidate_id": f"{a['candidate_id']} -> {b['candidate_id']}",
            "a": a,
            "b": b,
            "same_body": a["body_id"] == b["body_id"],
            "body_kinds": sorted((a["body_kind"], b["body_kind"])),
        }
        for a, b in combinations(markers, 2)
    ]


def _grid_key(q, length_m):
    return (float(q[0]), float(q[1]), float(length_m))


def precompute():
    markers = catalog()
    all_q = sorted(set(FIT_Q + VALIDATION_Q + JACOBIAN_Q + (Q0,)))
    lengths = sorted(set((1.0,) + VALIDATION_LENGTHS_M))
    points = {}
    jacobians = {}
    for q in all_q:
        for length_m in lengths:
            key = _grid_key(q, length_m)
            points[key] = {
                row["candidate_id"]: point(row, q, length_m) for row in markers
            }
        for length_m in VALIDATION_LENGTHS_M + (1.0,):
            key = _grid_key(q, length_m)
            jacobians[key] = {
                row["candidate_id"]: point_jacobian(row, q, length_m)
                for row in markers
            }
    return points, jacobians


def relative_point(candidate, q, length_m, cache):
    rows = cache[_grid_key(q, length_m)]
    return rows[candidate["b"]["candidate_id"]] - rows[candidate["a"]["candidate_id"]]


def relative_jacobian(candidate, q, length_m, cache):
    rows = cache[_grid_key(q, length_m)]
    return rows[candidate["b"]["candidate_id"]] - rows[candidate["a"]["candidate_id"]]


def fit_transform(candidate, point_cache, jacobian_cache):
    reference = relative_point(candidate, Q0, 1.0, point_cache)
    vectors = []
    targets = []
    for q in FIT_Q:
        current = relative_point(candidate, q, 1.0, point_cache)
        source_j = relative_jacobian(candidate, q, 1.0, jacobian_cache)
        target, target_j = port(q, 1.0)
        vectors.extend((current - reference, source_j[:, 0], source_j[:, 1]))
        targets.extend((target, target_j[:, 0], target_j[:, 1]))
    x = np.asarray(vectors, dtype=float)
    y = np.asarray(targets, dtype=float)
    coefficients, _, rank, _ = np.linalg.lstsq(x, y, rcond=None)
    return coefficients.T, int(rank)


def validation_errors(candidate, transform, point_cache, jacobian_cache):
    maximum_displacement = 0.0
    maximum_jacobian = 0.0
    for length_m in VALIDATION_LENGTHS_M:
        reference = relative_point(candidate, Q0, length_m, point_cache)
        for q in VALIDATION_Q:
            current = relative_point(candidate, q, length_m, point_cache)
            target, _ = port(q, length_m)
            predicted = transform @ (current - reference)
            maximum_displacement = max(
                maximum_displacement,
                float(np.linalg.norm(predicted - target) / length_m),
            )
        for q in JACOBIAN_Q:
            source_j = relative_jacobian(candidate, q, length_m, jacobian_cache)
            _, target_j = port(q, length_m)
            predicted_j = transform @ source_j
            maximum_jacobian = max(
                maximum_jacobian,
                float(np.linalg.norm(predicted_j - target_j, ord=2) / length_m),
            )
    return maximum_displacement, maximum_jacobian


def reference_frame_metrics(candidate, point_cache):
    vector = relative_point(candidate, Q0, 1.0, point_cache)
    norm = float(np.linalg.norm(vector))
    return {
        "reference_segment_length_per_module_length": norm,
        "reference_segment_unit_vector": (
            None if norm <= 1e-15 else (vector / norm).tolist()
        ),
    }


def evaluate(candidate, point_cache, jacobian_cache):
    transform, fit_rank = fit_transform(candidate, point_cache, jacobian_cache)
    displacement_error, jacobian_error = validation_errors(
        candidate,
        transform,
        point_cache,
        jacobian_cache,
    )
    shape = transform_geometry(transform)
    exact_linear = (
        displacement_error < PAIR_EXACT_DISPLACEMENT_TOLERANCE
        and jacobian_error < PAIR_EXACT_JACOBIAN_TOLERANCE
    )
    scaled_orthogonal = (
        exact_linear
        and shape["scaled_orthogonal_relative_error"]
        < PAIR_SCALED_ORTHOGONAL_TOLERANCE
    )
    unit_projection = (
        scaled_orthogonal
        and abs(shape["uniform_projection_scale"] - 1.0) < 1e-8
    )
    return {
        **candidate,
        "fit_rank": fit_rank,
        "transform_2x3": transform.tolist(),
        **reference_frame_metrics(candidate, point_cache),
        **shape,
        "maximum_normalized_displacement_error": displacement_error,
        "maximum_normalized_jacobian_error": jacobian_error,
        "score": max(displacement_error, jacobian_error),
        "exact_fixed_linear_match": exact_linear,
        "exact_scaled_orthogonal_match": scaled_orthogonal,
        "exact_unit_orthogonal_projection_match": unit_projection,
    }


def report():
    point_cache, jacobian_cache = precompute()
    rows = [
        evaluate(candidate, point_cache, jacobian_cache)
        for candidate in pair_catalog()
    ]
    rows.sort(key=lambda row: (row["score"], row["candidate_id"]))
    exact_linear = [
        row["candidate_id"] for row in rows if row["exact_fixed_linear_match"]
    ]
    exact_scaled = [
        row["candidate_id"]
        for row in rows
        if row["exact_scaled_orthogonal_match"]
    ]
    exact_unit = [
        row["candidate_id"]
        for row in rows
        if row["exact_unit_orthogonal_projection_match"]
    ]
    same_body_scaled = [
        row["candidate_id"]
        for row in rows
        if row["same_body"] and row["exact_scaled_orthogonal_match"]
    ]

    return {
        "schema": 1,
        "scope": (
            "fixed relative-marker search across all unordered pairs of existing "
            "panel vertices, bridge endpoints and hub markers; no state-dependent fit"
        ),
        "marker_count": len(catalog()),
        "pair_candidate_count": len(rows),
        "thresholds": {
            "exact_displacement": PAIR_EXACT_DISPLACEMENT_TOLERANCE,
            "exact_jacobian": PAIR_EXACT_JACOBIAN_TOLERANCE,
            "scaled_orthogonal": PAIR_SCALED_ORTHOGONAL_TOLERANCE,
        },
        "exact_fixed_linear_candidates": exact_linear,
        "exact_scaled_orthogonal_candidates": exact_scaled,
        "exact_unit_orthogonal_projection_candidates": exact_unit,
        "same_body_scaled_orthogonal_candidates": same_body_scaled,
        "best_candidates": rows[:20],
        "best_scaled_orthogonal_candidates": [
            row for row in rows if row["exact_scaled_orthogonal_match"]
        ][:20],
        "sources": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in (
                "report_fold_recursive_relative_attachment.py",
                "report_fold_recursive_port_body_correspondence.py",
                "report_fold_constitutive.py",
                "report_fold_kinematics.py",
                "report_fold_mapped.py",
            )
        },
        "state_dependent_transform_used": False,
        "relative_physical_segment_searched": True,
        "specific_physical_attachment_selected": False,
        "anisotropic_linear_transform_counts_as_literal_frame": False,
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
