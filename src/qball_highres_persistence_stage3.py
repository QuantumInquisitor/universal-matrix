"""Stage-3 duration scaling on the threshold-preserving 91^3 Q-ball grid."""

from __future__ import annotations

from dataclasses import dataclass

from .qball_highres_persistence_stage1 import (
    HighResolutionPersistenceStage,
    run_high_resolution_persistence_stage,
)


@dataclass(frozen=True)
class HighResolutionPersistenceStage3:
    result: HighResolutionPersistenceStage
    stage1_reference_steps: int = 25
    stage2_reference_steps: int = 100

    @property
    def duration_multiplier_vs_stage1(self) -> float:
        return self.result.steps / self.stage1_reference_steps

    @property
    def duration_multiplier_vs_stage2(self) -> float:
        return self.result.steps / self.stage2_reference_steps


def run_high_resolution_persistence_stage3(
    *,
    steps: int = 250,
    dt: float = 0.001,
) -> HighResolutionPersistenceStage3:
    """Run the same direct and perturbed test at t=0.25 by default."""
    if steps <= 100:
        raise ValueError("Stage 3 must extend beyond the 100-step Stage-2 duration")
    result = run_high_resolution_persistence_stage(
        steps=steps,
        dt=dt,
    )
    return HighResolutionPersistenceStage3(result=result)


def format_high_resolution_persistence_stage3_report(
    stage: HighResolutionPersistenceStage3,
) -> str:
    result = stage.result
    return "\n".join(
        [
            "Q-BALL HIGH-RESOLUTION PERSISTENCE STAGE 3",
            f"shape={result.shape}",
            f"spacing={result.spacing:.10f}",
            f"steps={result.steps}",
            f"dt={result.dt:.10f}",
            f"duration_multiplier_vs_stage1={stage.duration_multiplier_vs_stage1:.10f}",
            f"duration_multiplier_vs_stage2={stage.duration_multiplier_vs_stage2:.10f}",
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
        format_high_resolution_persistence_stage3_report(
            run_high_resolution_persistence_stage3()
        )
    )


if __name__ == "__main__":
    main()
