"""Direct and perturbed 3D persistence scan across the refined E/Q threshold."""

from __future__ import annotations

from dataclasses import dataclass

from .charged_matter_persistence import (
    SurvivalCriteria,
    evolve_candidate,
    localized_amplitude_perturbation,
    map_candidate_to_3d,
    mapping_consistency,
    passes_survival_window,
)
from .qball_threshold_refinement import (
    ThresholdRefinementResult,
    refine_energy_per_charge_threshold,
    threshold_bracket,
)
from .radial_matter_continuation import ContinuationRecord


@dataclass(frozen=True)
class ThresholdPersistencePoint:
    central_amplitude: float
    omega: float
    radial_energy_per_charge: float
    cartesian_energy_per_charge: float
    mapping_relative_difference: float
    below_free_mass_threshold: bool
    direct_survival: bool
    perturbed_survival: bool
    direct_energy_drift: float
    direct_charge_drift: float
    direct_peak_ratio: float
    direct_radius_ratio: float
    perturbed_energy_drift: float
    perturbed_charge_drift: float
    perturbed_peak_ratio: float
    perturbed_radius_ratio: float


@dataclass(frozen=True)
class ThresholdPersistenceScan:
    refinement: ThresholdRefinementResult
    below_side: ThresholdPersistencePoint
    above_side: ThresholdPersistencePoint


def _run_one(
    record: ContinuationRecord,
    *,
    shape: tuple[int, int, int],
    spacing: float,
    steps: int,
    dt: float,
    perturbation_fraction: float,
    perturbation_width: float,
    criteria: SurvivalCriteria,
) -> ThresholdPersistencePoint:
    base = map_candidate_to_3d(record, shape=shape, spacing=spacing)
    consistency = mapping_consistency(record, base)

    direct_report = evolve_candidate(base, steps=steps, dt=dt)

    perturbed = localized_amplitude_perturbation(
        map_candidate_to_3d(record, shape=shape, spacing=spacing),
        fractional_amplitude=perturbation_fraction,
        width=perturbation_width,
    )
    perturbed_report = evolve_candidate(perturbed, steps=steps, dt=dt)

    return ThresholdPersistencePoint(
        central_amplitude=record.central_amplitude,
        omega=record.solution.omega,
        radial_energy_per_charge=record.solution.energy_per_charge,
        cartesian_energy_per_charge=consistency.cartesian_energy_per_charge,
        mapping_relative_difference=consistency.relative_difference,
        below_free_mass_threshold=record.below_free_mass_threshold,
        direct_survival=passes_survival_window(direct_report, criteria),
        perturbed_survival=passes_survival_window(perturbed_report, criteria),
        direct_energy_drift=direct_report.relative_energy_drift,
        direct_charge_drift=direct_report.relative_charge_drift,
        direct_peak_ratio=direct_report.peak_ratio,
        direct_radius_ratio=direct_report.radius_ratio,
        perturbed_energy_drift=perturbed_report.relative_energy_drift,
        perturbed_charge_drift=perturbed_report.relative_charge_drift,
        perturbed_peak_ratio=perturbed_report.peak_ratio,
        perturbed_radius_ratio=perturbed_report.radius_ratio,
    )


def scan_refined_threshold_persistence(
    *,
    refinement_rounds: int = 2,
    interior_points_per_round: int = 4,
    shape: tuple[int, int, int] = (25, 25, 25),
    spacing: float = 0.5,
    steps: int = 1000,
    dt: float = 0.001,
    perturbation_fraction: float = 0.005,
    perturbation_width: float = 1.0,
    criteria: SurvivalCriteria = SurvivalCriteria(),
) -> ThresholdPersistenceScan:
    """Run direct and perturbed evolution on the two refined threshold neighbors."""
    refinement = refine_energy_per_charge_threshold(
        refinement_rounds=refinement_rounds,
        interior_points_per_round=interior_points_per_round,
    )
    left, right = threshold_bracket(refinement.records)

    left_point = _run_one(
        left,
        shape=shape,
        spacing=spacing,
        steps=steps,
        dt=dt,
        perturbation_fraction=perturbation_fraction,
        perturbation_width=perturbation_width,
        criteria=criteria,
    )
    right_point = _run_one(
        right,
        shape=shape,
        spacing=spacing,
        steps=steps,
        dt=dt,
        perturbation_fraction=perturbation_fraction,
        perturbation_width=perturbation_width,
        criteria=criteria,
    )

    below = left_point if left_point.below_free_mass_threshold else right_point
    above = right_point if left_point.below_free_mass_threshold else left_point

    if not below.below_free_mass_threshold or above.below_free_mass_threshold:
        raise RuntimeError("threshold neighbors do not straddle the energetic threshold")

    return ThresholdPersistenceScan(
        refinement=refinement,
        below_side=below,
        above_side=above,
    )


def format_scan_report(scan: ThresholdPersistenceScan) -> str:
    """Return a stable text report for CI and research logs."""
    crossing = scan.refinement.crossing
    lines = [
        "Q-BALL THRESHOLD PERSISTENCE SCAN",
        f"crossing_amplitude={crossing.interpolated_amplitude:.10f}",
        f"crossing_omega={crossing.interpolated_omega:.10f}",
        f"bracket_width={scan.refinement.bracket_width:.10f}",
    ]
    for label, point in (
        ("below", scan.below_side),
        ("above", scan.above_side),
    ):
        lines.extend(
            [
                f"{label}_amplitude={point.central_amplitude:.10f}",
                f"{label}_omega={point.omega:.10f}",
                f"{label}_radial_E_over_Q={point.radial_energy_per_charge:.10f}",
                f"{label}_cartesian_E_over_Q={point.cartesian_energy_per_charge:.10f}",
                f"{label}_mapping_relative_difference={point.mapping_relative_difference:.6e}",
                f"{label}_direct_survival={point.direct_survival}",
                f"{label}_perturbed_survival={point.perturbed_survival}",
                f"{label}_direct_energy_drift={point.direct_energy_drift:.6e}",
                f"{label}_direct_charge_drift={point.direct_charge_drift:.6e}",
                f"{label}_direct_peak_ratio={point.direct_peak_ratio:.10f}",
                f"{label}_direct_radius_ratio={point.direct_radius_ratio:.10f}",
                f"{label}_perturbed_energy_drift={point.perturbed_energy_drift:.6e}",
                f"{label}_perturbed_charge_drift={point.perturbed_charge_drift:.6e}",
                f"{label}_perturbed_peak_ratio={point.perturbed_peak_ratio:.10f}",
                f"{label}_perturbed_radius_ratio={point.perturbed_radius_ratio:.10f}",
            ]
        )
    return "\n".join(lines)


def main() -> None:
    print(format_scan_report(scan_refined_threshold_persistence()))


if __name__ == "__main__":
    main()
