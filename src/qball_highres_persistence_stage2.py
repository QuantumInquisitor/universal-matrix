"""Stage-2 duration scaling on the threshold-preserving 91^3 Q-ball grid."""

from __future__ import annotations

from dataclasses import dataclass

from .qball_highres_persistence_stage1 import (
    HighResolutionPersistenceStage,
    run_high_resolution_persistence_stage,
)


@dataclass(frozen=True)
class HighResolutionPersistenceStage2:
    result: HighResolutionPersistenceStage
    stage1_reference_steps: int = 25

    @property
    def duration_multiplier(self) -> float:
        return self.result.steps / self.stage1_reference_steps


def run_high_resolution_persistence_stage2(
    *,
    steps: int = 100,
    dt: float = 0.001,
) -> HighResolutionPersistenceStage2:
    """Run the same direct and perturbed test at four times the Stage-1 duration."""
    if steps <= 25:
        raise ValueError("Stage 2 must extend beyond the 25-step Stage-1 duration")
    result = run_high_resolution_persistence_stage(
        steps=steps,
        dt=dt,
    )
    return HighResolutionPersistenceStage2(result=result)


def format_high_resolution_persistence_stage2_report(
    stage: HighResolutionPersistenceStage2,
) -> str:
    result = stage.result
    return "\n".join(
        [
            "Q-BALL HIGH-RESOLUTION PERSISTENCE STAGE 2",
            f"shape={result.shape}",
            f"spacing={result.spacing:.10f}",
            f"steps={result.steps}",
            f"dt={result.dt:.10f}",
            f"duration_multiplier_vs_stage1={stage.duration_multiplier:.10f}",
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
    print(
        format_high_resolution_persistence_stage2_report(
            run_high_resolution_persistence_stage2()
        )
    )


if __name__ == "__main__":
    main()
