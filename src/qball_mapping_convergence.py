"""Convergence audit for radial-to-Cartesian Q-ball mapping near E/Q thresholds."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable
import math

from .charged_matter_persistence import map_candidate_to_3d, mapping_consistency
from .qball_threshold_refinement import refine_energy_per_charge_threshold, threshold_bracket
from .radial_matter_continuation import ContinuationRecord


@dataclass(frozen=True)
class MappingGrid:
    shape: tuple[int, int, int]
    spacing: float

    def __post_init__(self) -> None:
        if len(self.shape) != 3 or any(n < 3 for n in self.shape):
            raise ValueError("shape must contain three dimensions >= 3")
        if any(n % 2 == 0 for n in self.shape):
            raise ValueError("odd shape dimensions are required for a centered origin")
        if not math.isfinite(self.spacing) or self.spacing <= 0:
            raise ValueError("spacing must be finite and positive")

    @property
    def minimum_half_width(self) -> float:
        return 0.5 * (min(self.shape) - 1) * self.spacing


@dataclass(frozen=True)
class MappingConvergencePoint:
    shape: tuple[int, int, int]
    spacing: float
    minimum_half_width: float
    radial_energy_per_charge: float
    cartesian_energy_per_charge: float
    relative_difference: float
    radial_below_threshold: bool
    cartesian_below_threshold: bool
    threshold_side_preserved: bool


def audit_mapping_convergence(
    record: ContinuationRecord,
    grids: Iterable[MappingGrid] = (
        MappingGrid((25, 25, 25), 0.5),
        MappingGrid((33, 33, 33), 0.4),
        MappingGrid((41, 41, 41), 0.3),
    ),
) -> tuple[MappingConvergencePoint, ...]:
    """Evaluate E/Q mapping error across increasingly resolved Cartesian grids."""
    if not record.accepted_as_seed:
        raise ValueError("record must be an accepted continuation point")

    threshold = record.solution.potential.free_mass
    radial_eq = record.solution.energy_per_charge
    values: list[MappingConvergencePoint] = []

    for grid in grids:
        state = map_candidate_to_3d(
            record,
            shape=grid.shape,
            spacing=grid.spacing,
        )
        consistency = mapping_consistency(record, state)
        cartesian_eq = consistency.cartesian_energy_per_charge
        values.append(
            MappingConvergencePoint(
                shape=grid.shape,
                spacing=grid.spacing,
                minimum_half_width=grid.minimum_half_width,
                radial_energy_per_charge=radial_eq,
                cartesian_energy_per_charge=cartesian_eq,
                relative_difference=consistency.relative_difference,
                radial_below_threshold=radial_eq < threshold,
                cartesian_below_threshold=cartesian_eq < threshold,
                threshold_side_preserved=(radial_eq < threshold) == (cartesian_eq < threshold),
            )
        )

    return tuple(values)


def best_mapping_point(
    points: Iterable[MappingConvergencePoint],
) -> MappingConvergencePoint:
    """Select the configuration with the smallest absolute relative E/Q error."""
    values = tuple(points)
    if not values:
        raise ValueError("at least one mapping point is required")
    return min(values, key=lambda point: abs(point.relative_difference))


def threshold_side_stabilized(
    points: Iterable[MappingConvergencePoint],
    *,
    tail: int = 2,
) -> bool:
    """Return whether the final mapping levels agree with the radial threshold side."""
    values = tuple(points)
    if tail < 1 or len(values) < tail:
        raise ValueError("tail must be positive and no larger than the point count")
    return all(point.threshold_side_preserved for point in values[-tail:])


def format_mapping_convergence_report(
    points: Iterable[MappingConvergencePoint],
) -> str:
    values = tuple(points)
    if not values:
        raise ValueError("at least one mapping point is required")
    best = best_mapping_point(values)
    lines = [
        "Q-BALL MAPPING CONVERGENCE AUDIT",
        f"radial_E_over_Q={values[0].radial_energy_per_charge:.10f}",
    ]
    for index, point in enumerate(values):
        lines.extend(
            [
                f"grid_{index}_shape={point.shape}",
                f"grid_{index}_spacing={point.spacing:.10f}",
                f"grid_{index}_half_width={point.minimum_half_width:.10f}",
                f"grid_{index}_cartesian_E_over_Q={point.cartesian_energy_per_charge:.10f}",
                f"grid_{index}_relative_difference={point.relative_difference:.6e}",
                f"grid_{index}_threshold_side_preserved={point.threshold_side_preserved}",
            ]
        )
    lines.extend(
        [
            f"best_spacing={best.spacing:.10f}",
            f"best_relative_difference={best.relative_difference:.6e}",
            f"threshold_side_stabilized={threshold_side_stabilized(values)}",
        ]
    )
    return "\n".join(lines)


def run_refined_above_threshold_mapping_audit(
    grids: Iterable[MappingGrid] = (
        MappingGrid((25, 25, 25), 0.5),
        MappingGrid((33, 33, 33), 0.4),
        MappingGrid((41, 41, 41), 0.3),
    ),
) -> tuple[MappingConvergencePoint, ...]:
    """Audit the refined radial point immediately above E/Q=m_free."""
    refinement = refine_energy_per_charge_threshold(
        refinement_rounds=2,
        interior_points_per_round=4,
    )
    left, right = threshold_bracket(refinement.records)
    above = left if not left.below_free_mass_threshold else right
    if above.below_free_mass_threshold:
        raise RuntimeError("refined bracket does not contain an above-threshold point")
    return audit_mapping_convergence(above, grids=grids)


def main() -> None:
    points = run_refined_above_threshold_mapping_audit()
    print(format_mapping_convergence_report(points))


if __name__ == "__main__":
    main()
