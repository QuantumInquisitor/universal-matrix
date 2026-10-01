"""Search fixed port-to-body correspondences in the existing 22-body geometry."""

import argparse
import hashlib
import json
import math
from itertools import product
from pathlib import Path

import numpy as np

try:
    from .report_fold_constitutive import geometry
    from .report_fold_dynamics import Q0
    from .report_fold_mapped import port
except ImportError:
    from report_fold_constitutive import geometry
    from report_fold_dynamics import Q0
    from report_fold_mapped import port


FIT_Q = tuple(
    (scale, theta)
    for scale, theta in product(
        (0.92, 1.0, 1.08),
        (0.04, math.pi / 12, 0.48),
    )
)
VALIDATION_Q = tuple(
    (scale, theta)
    for scale, theta in product(
        (0.9, 0.95, 1.0, 1.05, 1.1),
        (0.0, 0.07, math.pi / 12, 0.4, math.pi / 6),
    )
)
JACOBIAN_Q = tuple(
    (scale, theta)
    for scale, theta in product(
        (0.91, 1.0, 1.09),
        (0.01, math.pi / 12, math.pi / 6 - 0.01),
    )
)
VALIDATION_LENGTHS_M = (0.1, 0.05, 0.025, 0.0125)
FD_STEP = 1e-6
EXACT_DISPLACEMENT_TOLERANCE = 1e-9
EXACT_JACOBIAN_TOLERANCE = 1e-8
SCALED_ORTHOGONAL_TOLERANCE = 1e-8


def catalog():
    rows = geometry(Q0, length_m=1.0)
    result = []
    for body in rows:
        vertices = np.asarray(body["vertices_m"], dtype=float)
        for index in range(len(vertices)):
            result.append(
                {
                    "candidate_id": f"{body['id']}:vertex-{index}",
                    "body_id": body["id"],
                    "vertex_index": index,
                    "body_kind": body["id"].split("-")[0],
                }
            )
    return result


def point(candidate, q, length_m):
    rows = {row["id"]: row for row in geometry(q, length_m=length_m)}
    vertices = np.asarray(rows[candidate["body_id"]]["vertices_m"], dtype=float)
    return vertices[candidate["vertex_index"]]


def point_jacobian(candidate, q, length_m):
    q = np.asarray(q, dtype=float)
    columns = []
    for axis in range(2):
        step = np.zeros(2)
        step[axis] = FD_STEP
        plus = point(candidate, q + step, length_m)
        minus = point(candidate, q - step, length_m)
        columns.append((plus - minus) / (2 * FD_STEP))
    return np.column_stack(columns)


def fit_transform(candidate):
    reference = point(candidate, Q0, 1.0)
    vectors = []
    targets = []
    for q in FIT_Q:
        current = point(candidate, q, 1.0)
        displacement = current - reference
        point_j = point_jacobian(candidate, q, 1.0)
        port_displacement, port_j = port(q, 1.0)
        vectors.extend((displacement, point_j[:, 0], point_j[:, 1]))
        targets.extend((port_displacement, port_j[:, 0], port_j[:, 1]))
    x = np.asarray(vectors, dtype=float)
    y = np.asarray(targets, dtype=float)
    coefficients, _, rank, _ = np.linalg.lstsq(x, y, rcond=None)
    transform = coefficients.T
    return transform, int(rank)


def transform_geometry(transform):
    gram = transform @ transform.T
    scale_squared = float(np.trace(gram) / 2)
    if scale_squared <= 0:
        isotropy_error = math.inf
        uniform_scale = 0.0
        condition = math.inf
    else:
        isotropy_error = float(
            np.linalg.norm(gram - scale_squared * np.eye(2), ord=2) / scale_squared
        )
        uniform_scale = math.sqrt(scale_squared)
        singular = np.linalg.svd(transform, compute_uv=False)
        condition = math.inf if singular[-1] <= 1e-15 else float(singular[0] / singular[-1])
    return {
        "row_gram": gram.tolist(),
        "uniform_projection_scale": uniform_scale,
        "scaled_orthogonal_relative_error": isotropy_error,
        "condition_number": condition,
    }


def validation_errors(candidate, transform):
    maximum_displacement = 0.0
    maximum_jacobian = 0.0
    maximum_scale_displacement = 0.0
    maximum_scale_jacobian = 0.0

    for length_m in VALIDATION_LENGTHS_M:
        reference = point(candidate, Q0, length_m)
        for q in VALIDATION_Q:
            current = point(candidate, q, length_m)
            target, _ = port(q, length_m)
            predicted = transform @ (current - reference)
            error = float(np.linalg.norm(predicted - target) / length_m)
            maximum_displacement = max(maximum_displacement, error)
            if length_m != VALIDATION_LENGTHS_M[0]:
                maximum_scale_displacement = max(maximum_scale_displacement, error)

        for q in JACOBIAN_Q:
            source_j = point_jacobian(candidate, q, length_m)
            _, target_j = port(q, length_m)
            predicted_j = transform @ source_j
            error = float(np.linalg.norm(predicted_j - target_j, ord=2) / length_m)
            maximum_jacobian = max(maximum_jacobian, error)
            if length_m != VALIDATION_LENGTHS_M[0]:
                maximum_scale_jacobian = max(maximum_scale_jacobian, error)

    return {
        "maximum_normalized_displacement_error": maximum_displacement,
        "maximum_normalized_jacobian_error": maximum_jacobian,
        "maximum_other_scale_displacement_error": maximum_scale_displacement,
        "maximum_other_scale_jacobian_error": maximum_scale_jacobian,
    }


def theta_sensitivity(candidate):
    maximum = 0.0
    for q in JACOBIAN_Q:
        jacobian = point_jacobian(candidate, q, 1.0)
        maximum = max(maximum, float(np.linalg.norm(jacobian[:, 1])))
    return maximum


def evaluate(candidate):
    transform, fit_rank = fit_transform(candidate)
    errors = validation_errors(candidate, transform)
    transform_shape = transform_geometry(transform)
    exact_linear = (
        errors["maximum_normalized_displacement_error"] < EXACT_DISPLACEMENT_TOLERANCE
        and errors["maximum_normalized_jacobian_error"] < EXACT_JACOBIAN_TOLERANCE
    )
    exact_scaled_orthogonal = (
        exact_linear
        and transform_shape["scaled_orthogonal_relative_error"] < SCALED_ORTHOGONAL_TOLERANCE
    )
    exact_unit_projection = (
        exact_scaled_orthogonal and abs(transform_shape["uniform_projection_scale"] - 1) < 1e-8
    )
    score = max(
        errors["maximum_normalized_displacement_error"],
        errors["maximum_normalized_jacobian_error"],
    )
    return {
        **candidate,
        "fit_rank": fit_rank,
        "transform_2x3": transform.tolist(),
        "theta_sensitivity": theta_sensitivity(candidate),
        **transform_shape,
        **errors,
        "score": score,
        "exact_fixed_linear_match": exact_linear,
        "exact_scaled_orthogonal_match": exact_scaled_orthogonal,
        "exact_unit_orthogonal_projection_match": exact_unit_projection,
    }


def report():
    candidates = [evaluate(candidate) for candidate in catalog()]
    candidates.sort(key=lambda row: (row["score"], row["candidate_id"]))
    exact_linear = [row["candidate_id"] for row in candidates if row["exact_fixed_linear_match"]]
    exact_scaled_orthogonal = [
        row["candidate_id"] for row in candidates if row["exact_scaled_orthogonal_match"]
    ]
    exact_unit_projection = [
        row["candidate_id"] for row in candidates if row["exact_unit_orthogonal_projection_match"]
    ]

    body_counts = {}
    for row in candidates:
        body_counts[row["body_kind"]] = body_counts.get(row["body_kind"], 0) + 1

    return {
        "schema": 1,
        "scope": (
            "fixed-transform correspondence search from every named source body point "
            "to the abstract two-component mapped connector port"
        ),
        "fit_q_grid": [list(q) for q in FIT_Q],
        "validation_q_grid": [list(q) for q in VALIDATION_Q],
        "jacobian_q_grid": [list(q) for q in JACOBIAN_Q],
        "validation_lengths_m": VALIDATION_LENGTHS_M,
        "candidate_count": len(candidates),
        "candidate_counts_by_body_kind": body_counts,
        "thresholds": {
            "exact_displacement": EXACT_DISPLACEMENT_TOLERANCE,
            "exact_jacobian": EXACT_JACOBIAN_TOLERANCE,
            "scaled_orthogonal": SCALED_ORTHOGONAL_TOLERANCE,
        },
        "exact_fixed_linear_candidates": exact_linear,
        "exact_scaled_orthogonal_candidates": exact_scaled_orthogonal,
        "exact_unit_orthogonal_projection_candidates": exact_unit_projection,
        "best_candidates": candidates[:12],
        "candidates": candidates,
        "sources": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in (
                "report_fold_recursive_port_body_correspondence.py",
                "report_fold_constitutive.py",
                "report_fold_kinematics.py",
                "report_fold_mapped.py",
            )
        },
        "state_dependent_transform_used": False,
        "candidate_specific_fixed_transform_allowed": True,
        "anisotropic_linear_transform_counts_as_literal_projection": False,
        "specific_physical_attachment_selected": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
