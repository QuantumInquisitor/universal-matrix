"""Direct 3D persistence workflow for the continued charged matter branch.

This module composes existing, separately tested pieces:

1. seeded continuation of the radial time-harmonic branch;
2. spacing-consistent radial-to-Cartesian mapping;
3. real-time classical matter evolution;
4. persistence diagnostics for energy, charge, peak amplitude, and RMS radius.

The purpose is to test dynamical survival of a controlled below-threshold branch
point.  A finite persistence window is evidence about that numerical model only.
It is not proof of an elementary particle, quantum stability, or experimental
reality.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from collections.abc import Iterable

import numpy as np

from .classical_matter_dynamics import ClassicalMatterDynamics
from .localized_matter_persistence import (
    PersistenceReport,
    cartesian_radius_grid,
    evolve_persistence,
    radial_solution_to_dynamics,
)
from .localized_matter_variational import MatterPotential
from .radial_matter_continuation import (
    ContinuationRecord,
    continue_radial_branch,
)


@dataclass(frozen=True)
class MappingConsistency:
    radial_energy_per_charge: float
    cartesian_energy_per_charge: float
    relative_difference: float


@dataclass(frozen=True)
class SurvivalCriteria:
    max_relative_energy_drift: float = 1e-5
    max_relative_charge_drift: float = 1e-10
    min_peak_ratio: float = 0.9
    max_peak_ratio: float = 1.1
    min_radius_ratio: float = 0.9
    max_radius_ratio: float = 1.1

    def __post_init__(self) -> None:
        values = (
            self.max_relative_energy_drift,
            self.max_relative_charge_drift,
            self.min_peak_ratio,
            self.max_peak_ratio,
            self.min_radius_ratio,
            self.max_radius_ratio,
        )
        if not all(math.isfinite(v) for v in values):
            raise ValueError("survival criteria must be finite")
        if self.max_relative_energy_drift < 0:
            raise ValueError("energy drift tolerance must be non-negative")
        if self.max_relative_charge_drift < 0:
            raise ValueError("charge drift tolerance must be non-negative")
        if not 0 < self.min_peak_ratio <= self.max_peak_ratio:
            raise ValueError("invalid peak-ratio interval")
        if not 0 < self.min_radius_ratio <= self.max_radius_ratio:
            raise ValueError("invalid radius-ratio interval")


def default_continued_candidate(
    *,
    amplitudes: Iterable[float] = (0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    potential: MatterPotential = MatterPotential(
        mass2=1.0,
        lambda4=-2.0,
        lambda6=1.0,
    ),
    omega_guess: float = 0.95,
    radius_max: float = 20.0,
    radial_points: int = 300,
    tolerance: float = 2e-5,
) -> ContinuationRecord:
    """Return the final accepted point of the controlled default branch."""
    records = continue_radial_branch(
        amplitudes,
        potential=potential,
        omega_guess=omega_guess,
        radius_max=radius_max,
        radial_points=radial_points,
        tolerance=tolerance,
    )
    final = records[-1]
    if not final.accepted_as_seed:
        raise RuntimeError(
            "final continuation point is not an accepted branch point: "
            + final.rejection_reason
        )
    if not final.below_free_mass_threshold:
        raise RuntimeError(
            "final continuation point is not below the free-mass threshold"
        )
    return final


def map_candidate_to_3d(
    record: ContinuationRecord,
    *,
    shape: tuple[int, int, int] = (25, 25, 25),
    spacing: float = 0.5,
) -> ClassicalMatterDynamics:
    """Map an accepted radial continuation point onto a 3D lattice."""
    if not record.accepted_as_seed:
        raise ValueError("record must be an accepted continuation point")
    return radial_solution_to_dynamics(
        record.solution,
        shape=shape,
        spacing=spacing,
    )


def mapping_consistency(
    record: ContinuationRecord,
    state: ClassicalMatterDynamics,
) -> MappingConsistency:
    """Compare radial and Cartesian E/Q before real-time evolution."""
    radial_eq = record.solution.energy_per_charge
    if state.charge == 0:
        raise ValueError("Cartesian state has zero charge")
    cartesian_eq = state.energy / state.charge
    relative = abs(cartesian_eq - radial_eq) / abs(radial_eq)
    return MappingConsistency(
        radial_energy_per_charge=float(radial_eq),
        cartesian_energy_per_charge=float(cartesian_eq),
        relative_difference=float(relative),
    )


def localized_amplitude_perturbation(
    state: ClassicalMatterDynamics,
    *,
    fractional_amplitude: float = 0.005,
    width: float = 1.0,
) -> ClassicalMatterDynamics:
    """Return a copy with a smooth localized radial amplitude perturbation.

    The same real multiplicative envelope is applied to Phi and Pi so their
    local phase relation is retained.  The perturbed state has its own initial
    charge and energy, which are then tested for conservation during evolution.
    """
    if not math.isfinite(fractional_amplitude):
        raise ValueError("fractional_amplitude must be finite")
    if abs(fractional_amplitude) >= 0.25:
        raise ValueError("fractional_amplitude must have magnitude < 0.25")
    if not math.isfinite(width) or width <= 0:
        raise ValueError("width must be finite and positive")

    radii = cartesian_radius_grid(
        state.phi.shape,
        state.lattice_spacing,
    )
    envelope = np.exp(
        -0.5 * (radii / width) ** 2
    )
    factor = 1.0 + fractional_amplitude * envelope

    return ClassicalMatterDynamics(
        phi=state.phi * factor,
        momentum=state.momentum * factor,
        links=state.links.copy(),
        potential=state.potential,
        time=state.time,
        lattice_spacing=state.lattice_spacing,
    )


def passes_survival_window(
    report: PersistenceReport,
    criteria: SurvivalCriteria = SurvivalCriteria(),
) -> bool:
    """Apply explicit finite-window survival criteria to one report."""
    return (
        abs(report.relative_energy_drift)
        <= criteria.max_relative_energy_drift
        and abs(report.relative_charge_drift)
        <= criteria.max_relative_charge_drift
        and criteria.min_peak_ratio
        <= report.peak_ratio
        <= criteria.max_peak_ratio
        and criteria.min_radius_ratio
        <= report.radius_ratio
        <= criteria.max_radius_ratio
    )


def evolve_candidate(
    state: ClassicalMatterDynamics,
    *,
    steps: int = 1000,
    dt: float = 0.001,
) -> PersistenceReport:
    """Run the spacing-consistent persistence diagnostic."""
    return evolve_persistence(
        state,
        steps=steps,
        dt=dt,
    )
