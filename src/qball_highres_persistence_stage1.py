"""Stage-1 persistence test on the threshold-preserving 91^3 Q-ball grid.

This is intentionally a short-duration sanity run before any longer high-cost
evolution. It keeps energetic classification and finite-time persistence as
separate diagnostics.
"""

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
from .qball_threshold_preserving_grid import TARGET_SHAPE, TARGET_SPACING
from .qball_threshold_refinement import (
    refine_energy_per_charge_threshold,
    threshold_bracket,
)


@dataclass(frozen=True)
class HighResolutionPersistenceStage:
    shape: tuple[int, int, int]
    spacing: float
    steps: int
    dt: float
    radial_energy_per_charge: float
    cartesian_energy_per_charge: float
    threshold_side_preserved: bool
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


def refined_above_threshold_record():
    refinement = refine_energy_per_charge_threshold(
        refinement_rounds=2,
        interior_points_per_round=4,
    )
    left, right = threshold_bracket(refinement.records)
    above = left if not left.below_free_mass_threshold else right
    if above.below_free_mass_threshold:
        raise RuntimeError("refined bracket does not contain an above-threshold point")
    return above


def run_high_resolution_persistence_stage(
    *,
    steps: int = 25,
    dt: float = 0.001,
    perturbation_fraction: float = 0.005,
    perturbation_width: float = 1.0,
    criteria: SurvivalCriteria = SurvivalCriteria(),
) -> HighResolutionPersistenceStage:
    """Run short direct and perturbed persistence on the confirmed 91^3 grid."""
    if steps < 1:
        raise ValueError("steps must be positive")
    if dt <= 0:
        raise ValueError("dt must be positive")

    record = refined_above_threshold_record()

    direct_state = map_candidate_to_3d(
        record,
        shape=TARGET_SHAPE,
        spacing=TARGET_SPACING,
    )
    consistency = mapping_consistency(record, direct_state)
    threshold = record.solution.potential.free_mass
    threshold_side_preserved = (
        record.solution.energy_per_charge > threshold
        and consistency.cartesian_energy_per_charge > threshold
    )
    if not threshold_side_preserved:
        raise RuntimeError(
            "high-resolution persistence stage requires an above-threshold "
            "Cartesian mapping"
        )

    direct_report = evolve_candidate(
        direct_state,
        steps=steps,
        dt=dt,
    )

    perturbed_state = localized_amplitude_perturbation(
        map_candidate_to_3d(
            record,
            shape=TARGET_SHAPE,
            spacing=TARGET_SPACING,
        ),
        fractional_amplitude=perturbation_fraction,
        width=perturbation_width,
    )
    perturbed_report = evolve_candidate(
        perturbed_state,
        steps=steps,
        dt=dt,
    )

    return HighResolutionPersistenceStage(
        shape=TARGET_SHAPE,
        spacing=TARGET_SPACING,
        steps=steps,
        dt=dt,
        radial_energy_per_charge=record.solution.energy_per_charge,
        cartesian_energy_per_charge=consistency.cartesian_energy_per_charge,
        threshold_side_preserved=threshold_side_preserved,
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


def format_high_resolution_persistence_report(
    result: HighResolutionPersistenceStage,
) -> str:
    return "\n".join(
        [
            "Q-BALL HIGH-RESOLUTION PERSISTENCE STAGE 1",
            f"shape={result.shape}",
            f"spacing={result.spacing:.10f}",
            f"steps={result.steps}",
            f"dt={result.dt:.10f}",
            f"radial_E_over_Q={result.radial_energy_per_charge:.10f}",
            f"cartesian_E_over_Q={result.cartesian_energy_per_charge:.10f}",
            f"threshold_side_preserved={result.threshold_side_preserved}",
            f"direct_survival={result.direct_survival}",
            f"direct_energy_drift={result.direct_energy_drift:.6e}",
            f"direct_charge_drift={result.direct_charge_drift:.6e}",
            f"direct_peak_ratio={result.direct_peak_ratio:.10f}",
            f"direct_radius_ratio={result.direct_radius_ratio:.10f}",
            f"perturbed_survival={result.perturbed_survival}",
            f"perturbed_energy_drift={result.perturbed_energy_drift:.6e}",
            f"perturbed_charge_drift={result.perturbed_charge_drift:.6e}",
            f"perturbed_peak_ratio={result.perturbed_peak_ratio:.10f}",
            f"perturbed_radius_ratio={result.perturbed_radius_ratio:.10f}",
        ]
    )


def main() -> None:
    print(format_high_resolution_persistence_report(
        run_high_resolution_persistence_stage()
    ))


if __name__ == "__main__":
    main()
