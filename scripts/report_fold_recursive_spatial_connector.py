"""Audit energy-derived spatial attachment adapters for recursive mirror placement."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

try:
    from .report_fold_mapped import PORT_STIFFNESS, port
    from .report_fold_scale_extension import audit_scale
    from .report_fold_scale_extension import connector as local_connector
except ImportError:
    from report_fold_mapped import PORT_STIFFNESS, port
    from report_fold_scale_extension import audit_scale
    from report_fold_scale_extension import connector as local_connector


PARENT_SCALES = (1.0, 0.5, 0.25)
VESSEL_RATIOS = (2.193830551297614, 5.0, 19.744474961678524)
STATE_PAIRS = (
    ((1.0, math.pi / 12), (1.0, math.pi / 12)),
    ((1.05, math.pi / 8), (0.95, math.pi / 10)),
    ((1.1, math.pi / 6), (0.9, 0.0)),
)
GRADIENT_PAIR = ((1.03, 0.2), (0.97, 0.35))
MODES = ("parent_aligned", "body_following")
FD_STEP = 1e-7
BASE_LENGTH_M = 0.1


def branch_rotation(child_bit, mode):
    if child_bit not in (0, 1) or type(child_bit) is not int:
        raise ValueError("child_bit must be integer 0 or 1")
    if mode not in MODES:
        raise ValueError("mode must be parent_aligned or body_following")
    if mode == "parent_aligned" or child_bit == 0:
        return np.eye(2)
    return -np.eye(2)


def spatial_connector(
    qa,
    qb,
    parent_scale,
    child_bit,
    vessel_ratio,
    *,
    mode="parent_aligned",
    weight=1.0,
):
    parent_scale = audit_scale(parent_scale)
    if parent_scale not in PARENT_SCALES:
        raise ValueError("parent scale must be 1, 1/2 or 1/4")
    child_scale = audit_scale(parent_scale / 2)
    vessel_ratio = float(vessel_ratio)
    if not np.isfinite(vessel_ratio) or vessel_ratio <= 0:
        raise ValueError("vessel_ratio must be positive and finite")
    if not np.isfinite(weight) or not 0 < weight <= 10:
        raise ValueError("weight outside (0,10]")

    attachment_rotation = branch_rotation(child_bit, mode)
    parent_length = BASE_LENGTH_M * parent_scale
    child_length = BASE_LENGTH_M * child_scale
    sign = 1.0 if child_bit == 0 else -1.0
    child_center = np.array((sign * vessel_ratio * parent_length / 2, 0.0))
    rest_vector = -child_center

    parent_port, parent_jacobian = port(qa, parent_length)
    child_port, child_jacobian = port(qb, child_length)

    actual_relative_vector = -child_center + parent_port - attachment_rotation @ child_port
    delta = actual_relative_vector - rest_vector
    stiffness = weight * parent_scale * PORT_STIFFNESS
    stress = stiffness @ delta
    energy = float(delta @ stress / 2)
    parent_force = -parent_jacobian.T @ stress
    child_force = (attachment_rotation @ child_jacobian).T @ stress

    return {
        "energy_j": energy,
        "parent_generalized_force": parent_force,
        "child_generalized_force": child_force,
        "delta_parent_frame_m": delta,
        "actual_relative_vector_m": actual_relative_vector,
        "rest_vector_parent_frame_m": rest_vector,
        "rest_offset_parent_lengths": float(np.linalg.norm(rest_vector) / parent_length),
        "translation_cancellation_error_m": float(
            np.linalg.norm(delta - (parent_port - attachment_rotation @ child_port))
        ),
        "relative_attachment_orientation_rad": (
            0.0 if np.allclose(attachment_rotation, np.eye(2)) else math.pi
        ),
    }


def gradient_errors(parent_scale, child_bit, vessel_ratio, mode):
    qa = np.asarray(GRADIENT_PAIR[0], dtype=float)
    qb = np.asarray(GRADIENT_PAIR[1], dtype=float)
    base = spatial_connector(qa, qb, parent_scale, child_bit, vessel_ratio, mode=mode)
    numerical_parent = np.zeros(2)
    numerical_child = np.zeros(2)
    for axis in range(2):
        step = np.zeros(2)
        step[axis] = FD_STEP
        plus = spatial_connector(qa + step, qb, parent_scale, child_bit, vessel_ratio, mode=mode)[
            "energy_j"
        ]
        minus = spatial_connector(qa - step, qb, parent_scale, child_bit, vessel_ratio, mode=mode)[
            "energy_j"
        ]
        numerical_parent[axis] = -(plus - minus) / (2 * FD_STEP)

        plus = spatial_connector(qa, qb + step, parent_scale, child_bit, vessel_ratio, mode=mode)[
            "energy_j"
        ]
        minus = spatial_connector(qa, qb - step, parent_scale, child_bit, vessel_ratio, mode=mode)[
            "energy_j"
        ]
        numerical_child[axis] = -(plus - minus) / (2 * FD_STEP)

    return {
        "parent_force_gradient_error": float(
            np.max(np.abs(numerical_parent - base["parent_generalized_force"]))
        ),
        "child_force_gradient_error": float(
            np.max(np.abs(numerical_child - base["child_generalized_force"]))
        ),
    }


def comparison_metrics(parent_scale, child_bit, mode):
    rows = []
    for vessel_ratio in VESSEL_RATIOS:
        for qa, qb in STATE_PAIRS:
            spatial = spatial_connector(
                qa,
                qb,
                parent_scale,
                child_bit,
                vessel_ratio,
                mode=mode,
            )
            reference_energy, reference_parent, reference_child = local_connector(
                qa,
                qb,
                parent_scale,
                parent_scale / 2,
            )
            rows.append(
                {
                    "vessel_ratio": vessel_ratio,
                    "qa": list(qa),
                    "qb": list(qb),
                    "spatial_energy_j": spatial["energy_j"],
                    "reference_energy_j": reference_energy,
                    "energy_difference_j": spatial["energy_j"] - reference_energy,
                    "parent_force_difference": (
                        np.asarray(spatial["parent_generalized_force"])
                        - np.asarray(reference_parent)
                    ).tolist(),
                    "child_force_difference": (
                        np.asarray(spatial["child_generalized_force"]) - np.asarray(reference_child)
                    ).tolist(),
                    "translation_cancellation_error_m": spatial["translation_cancellation_error_m"],
                    "rest_offset_parent_lengths": spatial["rest_offset_parent_lengths"],
                    "relative_attachment_orientation_rad": spatial[
                        "relative_attachment_orientation_rad"
                    ],
                }
            )

    gradient = {
        str(vessel_ratio): gradient_errors(parent_scale, child_bit, vessel_ratio, mode)
        for vessel_ratio in VESSEL_RATIOS
    }
    return {
        "rows": rows,
        "max_abs_energy_difference_j": max(abs(row["energy_difference_j"]) for row in rows),
        "max_abs_parent_force_difference": max(
            max(abs(value) for value in row["parent_force_difference"]) for row in rows
        ),
        "max_abs_child_force_difference": max(
            max(abs(value) for value in row["child_force_difference"]) for row in rows
        ),
        "max_translation_cancellation_error_m": max(
            row["translation_cancellation_error_m"] for row in rows
        ),
        "rest_offset_parent_lengths": sorted({row["rest_offset_parent_lengths"] for row in rows}),
        "gradient_errors": gradient,
    }


def scale_similarity(mode, child_bit):
    normalized = {}
    for parent_scale in PARENT_SCALES:
        values = []
        for qa, qb in STATE_PAIRS:
            row = spatial_connector(
                qa,
                qb,
                parent_scale,
                child_bit,
                VESSEL_RATIOS[0],
                mode=mode,
            )
            values.append(
                {
                    "energy": row["energy_j"] / parent_scale**3,
                    "parent_force": (np.asarray(row["parent_generalized_force"]) / parent_scale**3),
                    "child_force": (np.asarray(row["child_generalized_force"]) / parent_scale**3),
                }
            )
        normalized[str(parent_scale)] = values

    reference = normalized["1.0"]
    maximum = 0.0
    for parent_scale in PARENT_SCALES[1:]:
        rows = normalized[str(parent_scale)]
        for current, baseline in zip(rows, reference, strict=True):
            maximum = max(
                maximum,
                abs(current["energy"] - baseline["energy"]),
                float(np.max(np.abs(current["parent_force"] - baseline["parent_force"]))),
                float(np.max(np.abs(current["child_force"] - baseline["child_force"]))),
            )
    return maximum


def vessel_ratio_invariance(mode, child_bit, parent_scale):
    maximum = 0.0
    for qa, qb in STATE_PAIRS:
        rows = [
            spatial_connector(
                qa,
                qb,
                parent_scale,
                child_bit,
                ratio,
                mode=mode,
            )
            for ratio in VESSEL_RATIOS
        ]
        reference = rows[0]
        for current in rows[1:]:
            maximum = max(
                maximum,
                abs(current["energy_j"] - reference["energy_j"]),
                float(
                    np.max(
                        np.abs(
                            np.asarray(current["parent_generalized_force"])
                            - np.asarray(reference["parent_generalized_force"])
                        )
                    )
                ),
                float(
                    np.max(
                        np.abs(
                            np.asarray(current["child_generalized_force"])
                            - np.asarray(reference["child_generalized_force"])
                        )
                    )
                ),
            )
    return maximum


def report():
    cases = {}
    for mode in MODES:
        mode_cases = {}
        for child_bit in (0, 1):
            per_scale = {
                str(scale): comparison_metrics(scale, child_bit, mode) for scale in PARENT_SCALES
            }
            mode_cases[str(child_bit)] = {
                "per_scale": per_scale,
                "maximum_scale_similarity_error": scale_similarity(mode, child_bit),
                "maximum_vessel_ratio_invariance_error": max(
                    vessel_ratio_invariance(mode, child_bit, scale) for scale in PARENT_SCALES
                ),
            }
        cases[mode] = mode_cases

    return {
        "schema": 1,
        "scope": (
            "energy-derived recursive spatial connector attachment audit; exact "
            "geometric rest offset with either parent-aligned or body-following "
            "child attachment frames"
        ),
        "parent_scales": PARENT_SCALES,
        "vessel_ratios": VESSEL_RATIOS,
        "state_pairs": [
            {"parent": list(parent), "child": list(child)} for parent, child in STATE_PAIRS
        ],
        "cases": cases,
        "sources": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in (
                "report_fold_recursive_spatial_connector.py",
                "report_fold_recursive_material_placement.py",
                "report_fold_scale_extension.py",
                "report_fold_mapped.py",
            )
        },
        "connector_stiffness_changed": False,
        "material_coefficients_changed": False,
        "geometric_rest_offset_added": True,
        "attachment_frame_choice_is_physical_input": True,
        "abstract_port_mapped_to_specific_body_site": False,
        "physical_attachment_convention_selected": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
