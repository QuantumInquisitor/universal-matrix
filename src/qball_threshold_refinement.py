"""Adaptive local refinement of the charged-matter E/Q threshold.

The coarse continuation establishes that the tracked branch crosses the free
mass threshold.  This module repeatedly inserts interior amplitudes inside the
current accepted crossing bracket and resolves the branch on the combined
ordered amplitude set.

No stability conclusion is inferred from the crossing itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable
import math

from .localized_matter_variational import MatterPotential
from .qball_branch_diagnostics import (
    ThresholdCrossing,
    branch_secants,
    energy_per_charge_threshold_crossings,
)
from .radial_matter_continuation import ContinuationRecord, continue_radial_branch


@dataclass(frozen=True)
class ThresholdRefinementResult:
    records: tuple[ContinuationRecord, ...]
    crossing: ThresholdCrossing
    bracket_width: float
    rounds_completed: int

    @property
    def accepted_points(self) -> int:
        return sum(record.accepted_as_seed for record in self.records)


def _accepted(records: Iterable[ContinuationRecord]) -> list[ContinuationRecord]:
    values = [record for record in records if record.accepted_as_seed]
    if len(values) < 2:
        raise ValueError("at least two accepted points are required")
    return values


def threshold_bracket(
    records: Iterable[ContinuationRecord],
    *,
    threshold: float | None = None,
) -> tuple[ContinuationRecord, ContinuationRecord]:
    """Return the first accepted neighboring pair that brackets E/Q threshold."""
    values = _accepted(records)
    if threshold is None:
        threshold = values[0].solution.potential.free_mass
    threshold = float(threshold)
    if not math.isfinite(threshold) or threshold <= 0:
        raise ValueError("threshold must be finite and positive")

    for left, right in zip(values, values[1:]):
        gl = left.solution.energy_per_charge - threshold
        gr = right.solution.energy_per_charge - threshold
        if gl == 0.0 or gr == 0.0 or gl * gr < 0.0:
            return left, right
    raise ValueError("no accepted E/Q threshold bracket found")


def _interior_points(left: float, right: float, count: int) -> tuple[float, ...]:
    if count < 1:
        raise ValueError("count must be at least one")
    width = right - left
    if width <= 0:
        raise ValueError("right amplitude must exceed left amplitude")
    return tuple(
        left + width * (index + 1) / (count + 1)
        for index in range(count)
    )


def refine_energy_per_charge_threshold(
    coarse_amplitudes: Iterable[float] = (0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    *,
    potential: MatterPotential = MatterPotential(
        mass2=1.0,
        lambda4=-2.0,
        lambda6=1.0,
    ),
    omega_guess: float = 0.95,
    radius_max: float = 20.0,
    radial_points: int = 300,
    tolerance: float = 2e-5,
    max_nodes: int = 10000,
    virial_tolerance: float = 1e-3,
    refinement_rounds: int = 2,
    interior_points_per_round: int = 4,
) -> ThresholdRefinementResult:
    """Refine the first accepted E/Q crossing by repeated seeded continuation."""
    if refinement_rounds < 1:
        raise ValueError("refinement_rounds must be at least one")
    if interior_points_per_round < 1:
        raise ValueError("interior_points_per_round must be at least one")

    amplitudes = sorted({float(value) for value in coarse_amplitudes})
    if len(amplitudes) < 2:
        raise ValueError("at least two coarse amplitudes are required")

    records: list[ContinuationRecord] = []
    crossing: ThresholdCrossing | None = None

    for round_index in range(refinement_rounds + 1):
        records = continue_radial_branch(
            amplitudes,
            potential=potential,
            omega_guess=omega_guess,
            radius_max=radius_max,
            radial_points=radial_points,
            tolerance=tolerance,
            max_nodes=max_nodes,
            virial_tolerance=virial_tolerance,
        )
        crossings = energy_per_charge_threshold_crossings(records)
        if not crossings:
            raise RuntimeError("accepted branch no longer contains an E/Q crossing")
        crossing = crossings[0]

        if round_index == refinement_rounds:
            break

        left, right = threshold_bracket(records)
        amplitudes = sorted(
            set(amplitudes).union(
                _interior_points(
                    left.central_amplitude,
                    right.central_amplitude,
                    interior_points_per_round,
                )
            )
        )

    assert crossing is not None
    left, right = threshold_bracket(records)
    return ThresholdRefinementResult(
        records=tuple(records),
        crossing=crossing,
        bracket_width=right.central_amplitude - left.central_amplitude,
        rounds_completed=refinement_rounds,
    )


def local_slope_diagnostics(
    result: ThresholdRefinementResult,
) -> dict[str, float | bool]:
    """Summarize branch slopes immediately adjacent to the refined crossing."""
    accepted = _accepted(result.records)
    secants = branch_secants(accepted)
    crossing = result.crossing

    relevant = [
        secant
        for secant in secants
        if (
            secant.left_amplitude <= crossing.interpolated_amplitude
            <= secant.right_amplitude
        )
    ]
    if len(relevant) != 1:
        raise RuntimeError("refined crossing must fall inside exactly one secant")

    secant = relevant[0]
    return {
        "dcharge_domega": secant.dcharge_domega,
        "denergy_dcharge": secant.denergy_dcharge,
        "midpoint_omega": secant.midpoint_omega,
        "variational_relative_error": secant.variational_relative_error,
        "negative_charge_frequency_slope": (
            secant.negative_charge_frequency_slope
        ),
    }
