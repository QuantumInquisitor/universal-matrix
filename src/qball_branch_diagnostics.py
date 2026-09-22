"""Diagnostics for a numerically continued time-harmonic Q-ball branch.

For a smooth family of stationary charged scalar solutions, constrained
variation implies the branch identity

    dE/dQ = omega

in the normalization used by the repository.

A commonly useful classical branch diagnostic is the sign of

    dQ/domega.

For standard one-field Q-ball families, a negative slope is associated with the
candidate stable branch under the usual spectral assumptions.  This module
reports that sign but does not promote it to a general proof of stability.

The implementation uses finite secants between accepted continuation points and
also locates crossings of E/Q with the free-field mass threshold.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from collections.abc import Iterable

from .radial_matter_continuation import ContinuationRecord


@dataclass(frozen=True)
class BranchSecant:
    left_amplitude: float
    right_amplitude: float
    left_omega: float
    right_omega: float
    midpoint_omega: float
    delta_charge: float
    delta_energy: float
    delta_omega: float
    dcharge_domega: float
    denergy_dcharge: float
    variational_relative_error: float
    negative_charge_frequency_slope: bool


@dataclass(frozen=True)
class ThresholdCrossing:
    left_amplitude: float
    right_amplitude: float
    interpolated_amplitude: float
    interpolated_omega: float
    threshold: float


def _accepted(records: Iterable[ContinuationRecord]) -> list[ContinuationRecord]:
    values = [record for record in records if record.accepted_as_seed]
    if len(values) < 2:
        raise ValueError("at least two accepted continuation points are required")
    return values


def branch_secants(
    records: Iterable[ContinuationRecord],
) -> tuple[BranchSecant, ...]:
    """Return nearest-neighbor finite-difference diagnostics along a branch."""
    values = _accepted(records)
    out: list[BranchSecant] = []

    for left, right in zip(values, values[1:]):
        dq = right.solution.charge - left.solution.charge
        de = right.solution.energy - left.solution.energy
        dw = right.solution.omega - left.solution.omega

        if abs(dq) <= 1e-15:
            raise ValueError("neighboring branch points have indistinguishable charge")
        if abs(dw) <= 1e-15:
            raise ValueError("neighboring branch points have indistinguishable omega")

        dedq = de / dq
        dqdomega = dq / dw
        omega_mid = 0.5 * (left.solution.omega + right.solution.omega)
        relative_error = abs(dedq - omega_mid) / max(abs(omega_mid), 1e-15)

        out.append(
            BranchSecant(
                left_amplitude=left.central_amplitude,
                right_amplitude=right.central_amplitude,
                left_omega=left.solution.omega,
                right_omega=right.solution.omega,
                midpoint_omega=omega_mid,
                delta_charge=dq,
                delta_energy=de,
                delta_omega=dw,
                dcharge_domega=dqdomega,
                denergy_dcharge=dedq,
                variational_relative_error=relative_error,
                negative_charge_frequency_slope=dqdomega < 0.0,
            )
        )

    return tuple(out)


def energy_per_charge_threshold_crossings(
    records: Iterable[ContinuationRecord],
    *,
    threshold: float | None = None,
) -> tuple[ThresholdCrossing, ...]:
    """Linearly interpolate crossings of E/Q through a chosen threshold."""
    values = _accepted(records)

    if threshold is None:
        threshold = values[0].solution.potential.free_mass
    threshold = float(threshold)
    if not math.isfinite(threshold) or threshold <= 0:
        raise ValueError("threshold must be finite and positive")

    out: list[ThresholdCrossing] = []
    for left, right in zip(values, values[1:]):
        gl = left.solution.energy_per_charge - threshold
        gr = right.solution.energy_per_charge - threshold

        if gl == 0.0:
            fraction = 0.0
        elif gr == 0.0:
            fraction = 1.0
        elif gl * gr > 0.0:
            continue
        else:
            fraction = -gl / (gr - gl)

        amplitude = (
            left.central_amplitude
            + fraction * (right.central_amplitude - left.central_amplitude)
        )
        omega = (
            left.solution.omega
            + fraction * (right.solution.omega - left.solution.omega)
        )
        out.append(
            ThresholdCrossing(
                left_amplitude=left.central_amplitude,
                right_amplitude=right.central_amplitude,
                interpolated_amplitude=float(amplitude),
                interpolated_omega=float(omega),
                threshold=threshold,
            )
        )

    return tuple(out)


def branch_diagnostic_summary(
    records: Iterable[ContinuationRecord],
) -> dict[str, float | int | bool]:
    """Return compact diagnostics without declaring nonlinear stability."""
    values = _accepted(records)
    secants = branch_secants(values)
    crossings = energy_per_charge_threshold_crossings(values)

    return {
        "accepted_points": len(values),
        "secants": len(secants),
        "omega_strictly_decreasing": all(
            right.solution.omega < left.solution.omega
            for left, right in zip(values, values[1:])
        ),
        "all_negative_dq_domega": all(
            secant.negative_charge_frequency_slope
            for secant in secants
        ),
        "maximum_variational_relative_error": max(
            secant.variational_relative_error
            for secant in secants
        ),
        "energy_per_charge_crossings": len(crossings),
        "minimum_energy_per_charge": min(
            record.solution.energy_per_charge
            for record in values
        ),
        "maximum_energy_per_charge": max(
            record.solution.energy_per_charge
            for record in values
        ),
    }
