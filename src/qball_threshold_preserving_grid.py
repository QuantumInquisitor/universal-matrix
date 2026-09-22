"""Confirm a finite Cartesian grid that preserves the refined radial E/Q threshold side."""

from __future__ import annotations

from dataclasses import dataclass

from .charged_matter_persistence import map_candidate_to_3d, mapping_consistency
from .qball_joint_mapping_extrapolation import run_joint_mapping_extrapolation
from .qball_threshold_refinement import (
    refine_energy_per_charge_threshold,
    threshold_bracket,
)


@dataclass(frozen=True)
class ThresholdPreservingGridResult:
    shape: tuple[int, int, int]
    spacing: float
    half_width: float
    radial_energy_per_charge: float
    cartesian_energy_per_charge: float
    mapping_relative_difference: float
    radial_above_threshold: bool
    cartesian_above_threshold: bool
    threshold_side_preserved: bool
    joint_fit_prediction: float
    prediction_absolute_error: float


TARGET_SHAPE = (91, 91, 91)
TARGET_SPACING = 0.175


def target_half_width(
    shape: tuple[int, int, int] = TARGET_SHAPE,
    spacing: float = TARGET_SPACING,
) -> float:
    if len(shape) != 3 or any(n < 3 or n % 2 == 0 for n in shape):
        raise ValueError("shape must contain three odd dimensions >= 3")
    return 0.5 * (min(shape) - 1) * spacing


def confirm_threshold_preserving_grid() -> ThresholdPreservingGridResult:
    """Map the refined radial point above E/Q=m_free onto the target finite grid."""
    refinement = refine_energy_per_charge_threshold(
        refinement_rounds=2,
        interior_points_per_round=4,
    )
    left, right = threshold_bracket(refinement.records)
    above = left if not left.below_free_mass_threshold else right
    if above.below_free_mass_threshold:
        raise RuntimeError("refined bracket does not contain an above-threshold point")

    state = map_candidate_to_3d(
        above,
        shape=TARGET_SHAPE,
        spacing=TARGET_SPACING,
    )
    consistency = mapping_consistency(above, state)

    threshold = above.solution.potential.free_mass
    radial_above = above.solution.energy_per_charge > threshold
    cartesian_above = consistency.cartesian_energy_per_charge > threshold

    joint = run_joint_mapping_extrapolation()
    half_width = target_half_width()
    prediction = (
        joint.continuum_infinite_volume_energy_per_charge
        + joint.spacing_coefficient * TARGET_SPACING**2
    )
    from .qball_joint_mapping_extrapolation import asymptotic_tail_basis
    prediction += (
        joint.tail_coefficient
        * asymptotic_tail_basis(half_width, joint.mu)
    )

    return ThresholdPreservingGridResult(
        shape=TARGET_SHAPE,
        spacing=TARGET_SPACING,
        half_width=half_width,
        radial_energy_per_charge=above.solution.energy_per_charge,
        cartesian_energy_per_charge=consistency.cartesian_energy_per_charge,
        mapping_relative_difference=consistency.relative_difference,
        radial_above_threshold=radial_above,
        cartesian_above_threshold=cartesian_above,
        threshold_side_preserved=radial_above == cartesian_above,
        joint_fit_prediction=float(prediction),
        prediction_absolute_error=abs(
            consistency.cartesian_energy_per_charge - prediction
        ),
    )


def format_threshold_preserving_grid_report(
    result: ThresholdPreservingGridResult,
) -> str:
    return "\n".join(
        [
            "Q-BALL THRESHOLD-PRESERVING GRID CONFIRMATION",
            f"shape={result.shape}",
            f"spacing={result.spacing:.10f}",
            f"half_width={result.half_width:.10f}",
            f"radial_E_over_Q={result.radial_energy_per_charge:.10f}",
            f"cartesian_E_over_Q={result.cartesian_energy_per_charge:.10f}",
            f"mapping_relative_difference={result.mapping_relative_difference:.6e}",
            f"radial_above_threshold={result.radial_above_threshold}",
            f"cartesian_above_threshold={result.cartesian_above_threshold}",
            f"threshold_side_preserved={result.threshold_side_preserved}",
            f"joint_fit_prediction={result.joint_fit_prediction:.10f}",
            f"prediction_absolute_error={result.prediction_absolute_error:.6e}",
        ]
    )


def main() -> None:
    print(format_threshold_preserving_grid_report(confirm_threshold_preserving_grid()))


if __name__ == "__main__":
    main()
