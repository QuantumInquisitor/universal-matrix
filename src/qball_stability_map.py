"""Evidence-map utilities for the continued charged-matter branch.

This module combines distinct diagnostics without collapsing them into a single
"stability score".  Energetic binding, branch geometry, and finite-time
persistence answer different questions and are therefore recorded separately.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable
import math

from .charged_matter_persistence import SurvivalCriteria, passes_survival_window
from .localized_matter_persistence import PersistenceReport
from .qball_branch_diagnostics import branch_secants
from .radial_matter_continuation import ContinuationRecord


@dataclass(frozen=True)
class StabilityEvidencePoint:
    central_amplitude: float
    omega: float
    energy_per_charge: float
    below_free_mass_threshold: bool
    dq_domega_left: float | None
    dq_domega_right: float | None
    negative_slope_on_available_secants: bool | None
    direct_survival: bool | None = None
    perturbed_survival: bool | None = None

    @property
    def finite_time_persistence_supported(self) -> bool | None:
        values = [
            value
            for value in (self.direct_survival, self.perturbed_survival)
            if value is not None
        ]
        if not values:
            return None
        return all(values)


def _accepted(records: Iterable[ContinuationRecord]) -> list[ContinuationRecord]:
    values = [record for record in records if record.accepted_as_seed]
    if not values:
        raise ValueError("at least one accepted continuation point is required")
    return values


def build_static_evidence_map(
    records: Iterable[ContinuationRecord],
) -> tuple[StabilityEvidencePoint, ...]:
    """Combine branch and energetic diagnostics at accepted continuation points."""
    values = _accepted(records)
    if len(values) == 1:
        record = values[0]
        return (
            StabilityEvidencePoint(
                central_amplitude=record.central_amplitude,
                omega=record.solution.omega,
                energy_per_charge=record.solution.energy_per_charge,
                below_free_mass_threshold=record.below_free_mass_threshold,
                dq_domega_left=None,
                dq_domega_right=None,
                negative_slope_on_available_secants=None,
            ),
        )

    secants = branch_secants(values)
    out: list[StabilityEvidencePoint] = []

    for index, record in enumerate(values):
        left = secants[index - 1] if index > 0 else None
        right = secants[index] if index < len(secants) else None
        slopes = [
            secant.dcharge_domega
            for secant in (left, right)
            if secant is not None
        ]
        negative = all(value < 0.0 for value in slopes) if slopes else None

        out.append(
            StabilityEvidencePoint(
                central_amplitude=record.central_amplitude,
                omega=record.solution.omega,
                energy_per_charge=record.solution.energy_per_charge,
                below_free_mass_threshold=record.below_free_mass_threshold,
                dq_domega_left=None if left is None else left.dcharge_domega,
                dq_domega_right=None if right is None else right.dcharge_domega,
                negative_slope_on_available_secants=negative,
            )
        )

    return tuple(out)


def attach_persistence_evidence(
    points: Iterable[StabilityEvidencePoint],
    *,
    amplitude: float,
    direct_report: PersistenceReport | None = None,
    perturbed_report: PersistenceReport | None = None,
    criteria: SurvivalCriteria = SurvivalCriteria(),
    amplitude_tolerance: float = 1e-12,
) -> tuple[StabilityEvidencePoint, ...]:
    """Attach finite-time persistence results to one existing evidence point."""
    if not math.isfinite(amplitude):
        raise ValueError("amplitude must be finite")
    if not math.isfinite(amplitude_tolerance) or amplitude_tolerance < 0:
        raise ValueError("amplitude_tolerance must be finite and non-negative")
    if direct_report is None and perturbed_report is None:
        raise ValueError("at least one persistence report is required")

    values = list(points)
    matches = [
        index
        for index, point in enumerate(values)
        if abs(point.central_amplitude - amplitude) <= amplitude_tolerance
    ]
    if len(matches) != 1:
        raise ValueError("amplitude must match exactly one evidence point")

    index = matches[0]
    point = values[index]
    values[index] = StabilityEvidencePoint(
        central_amplitude=point.central_amplitude,
        omega=point.omega,
        energy_per_charge=point.energy_per_charge,
        below_free_mass_threshold=point.below_free_mass_threshold,
        dq_domega_left=point.dq_domega_left,
        dq_domega_right=point.dq_domega_right,
        negative_slope_on_available_secants=point.negative_slope_on_available_secants,
        direct_survival=(
            point.direct_survival
            if direct_report is None
            else passes_survival_window(direct_report, criteria)
        ),
        perturbed_survival=(
            point.perturbed_survival
            if perturbed_report is None
            else passes_survival_window(perturbed_report, criteria)
        ),
    )
    return tuple(values)


def select_refinement_amplitudes(
    records: Iterable[ContinuationRecord],
    *,
    threshold: float | None = None,
    interior_points: int = 5,
) -> tuple[float, ...]:
    """Return evenly spaced amplitudes inside the first E/Q threshold bracket."""
    if interior_points < 1:
        raise ValueError("interior_points must be at least one")

    values = _accepted(records)
    if len(values) < 2:
        raise ValueError("at least two accepted continuation points are required")

    if threshold is None:
        threshold = values[0].solution.potential.free_mass
    threshold = float(threshold)
    if not math.isfinite(threshold) or threshold <= 0:
        raise ValueError("threshold must be finite and positive")

    for left, right in zip(values, values[1:]):
        gl = left.solution.energy_per_charge - threshold
        gr = right.solution.energy_per_charge - threshold
        if gl == 0.0 or gr == 0.0 or gl * gr < 0.0:
            width = right.central_amplitude - left.central_amplitude
            return tuple(
                left.central_amplitude
                + width * (index + 1) / (interior_points + 1)
                for index in range(interior_points)
            )

    raise ValueError("no E/Q threshold bracket found")


def evidence_summary(
    points: Iterable[StabilityEvidencePoint],
) -> dict[str, int]:
    """Count independently supported evidence categories."""
    values = tuple(points)
    return {
        "points": len(values),
        "energetically_bound": sum(
            point.below_free_mass_threshold for point in values
        ),
        "negative_slope_candidates": sum(
            point.negative_slope_on_available_secants is True for point in values
        ),
        "direct_survival_supported": sum(
            point.direct_survival is True for point in values
        ),
        "perturbed_survival_supported": sum(
            point.perturbed_survival is True for point in values
        ),
        "both_persistence_tests_supported": sum(
            point.finite_time_persistence_supported is True for point in values
        ),
    }
