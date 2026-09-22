"""Stage-4 duration scaling at t=0.5 on the threshold-preserving 91^3 Q-ball grid."""

from __future__ import annotations

from dataclasses import dataclass

from .qball_highres_persistence_stage1 import (
    HighResolutionPersistenceStage,
    run_high_resolution_persistence_stage,
)
from .qball_highres_time_scaling import analyze_stage_scaling


@dataclass(frozen=True)
class HighResolutionPersistenceStage4:
    result: HighResolutionPersistenceStage
    projected_direct_peak_deviation: float
    projected_perturbed_peak_deviation: float
    projected_direct_radius_deviation: float
    projected_perturbed_radius_deviation: float

    @property
    def direct_peak_projection_ratio(self) -> float:
        return (1.0 - self.result.direct_peak_ratio) / self.projected_direct_peak_deviation

    @property
    def perturbed_peak_projection_ratio(self) -> float:
        return (1.0 - self.result.perturbed_peak_ratio) / self.projected_perturbed_peak_deviation

    @property
    def direct_radius_projection_ratio(self) -> float:
        return (self.result.direct_radius_ratio - 1.0) / self.projected_direct_radius_deviation

    @property
    def perturbed_radius_projection_ratio(self) -> float:
        return (self.result.perturbed_radius_ratio - 1.0) / self.projected_perturbed_radius_deviation


def _projection_map() -> dict[str, float]:
    return {
        channel.name: channel.projected_value_at_0p5
        for channel in analyze_stage_scaling()
    }


def run_high_resolution_persistence_stage4(
    *,
    steps: int = 500,
    dt: float = 0.001,
) -> HighResolutionPersistenceStage4:
    """Run the same direct and perturbed test at t=0.5 by default."""
    if steps != 500:
        raise ValueError("Stage 4 is defined specifically at 500 steps")
    if dt != 0.001:
        raise ValueError("Stage 4 keeps dt fixed at 0.001")

    result = run_high_resolution_persistence_stage(
        steps=steps,
        dt=dt,
    )
    projections = _projection_map()
    return HighResolutionPersistenceStage4(
        result=result,
        projected_direct_peak_deviation=projections["direct_peak_deviation"],
        projected_perturbed_peak_deviation=projections["perturbed_peak_deviation"],
        projected_direct_radius_deviation=projections["direct_radius_deviation"],
        projected_perturbed_radius_deviation=projections["perturbed_radius_deviation"],
    )


def format_high_resolution_persistence_stage4_report(
    stage: HighResolutionPersistenceStage4,
) -> str:
    result = stage.result
    return "\n".join(
        [
            "Q-BALL HIGH-RESOLUTION PERSISTENCE STAGE 4",
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
            f"projected_direct_peak_deviation={stage.projected_direct_peak_deviation:.10e}",
            f"measured_to_projected_direct_peak={stage.direct_peak_projection_ratio:.10f}",
            f"projected_perturbed_peak_deviation={stage.projected_perturbed_peak_deviation:.10e}",
            f"measured_to_projected_perturbed_peak={stage.perturbed_peak_projection_ratio:.10f}",
            f"projected_direct_radius_deviation={stage.projected_direct_radius_deviation:.10e}",
            f"measured_to_projected_direct_radius={stage.direct_radius_projection_ratio:.10f}",
            f"projected_perturbed_radius_deviation={stage.projected_perturbed_radius_deviation:.10e}",
            f"measured_to_projected_perturbed_radius={stage.perturbed_radius_projection_ratio:.10f}",
        ]
    )


def main() -> None:
    print(
        format_high_resolution_persistence_stage4_report(
            run_high_resolution_persistence_stage4()
        )
    )


if __name__ == "__main__":
    main()
