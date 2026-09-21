"""Controlled parameter scan for nonlinear radial matter branches.

This utility wraps solve_radial_matter over a bounded set of central amplitudes
and records:
- solver convergence;
- solved frequency omega;
- nodelessness;
- energy;
- U(1) charge;
- E/Q;
- whether E/Q lies below the free-field mass threshold.

It is intended for explicit offline/research scans. Normal CI should only test
small deterministic helper behavior, not large parameter sweeps.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable

try:
    from .localized_matter_variational import MatterPotential
    from .radial_matter_solver import solve_radial_matter
except ImportError:
    from localized_matter_variational import MatterPotential
    from radial_matter_solver import solve_radial_matter


@dataclass(frozen=True)
class BranchPoint:
    central_amplitude: float
    omega: float
    solver_status: int
    nodeless: bool
    energy: float
    charge: float
    energy_per_charge: float
    below_free_mass_threshold: bool
    solver_message: str


def scan_radial_branch(
    central_amplitudes: Iterable[float],
    potential: MatterPotential = MatterPotential(),
    omega_guess: float = 0.95,
    radius_max: float = 20.0,
    radial_points: int = 300,
    tolerance: float = 2e-5,
) -> list[BranchPoint]:
    points: list[BranchPoint] = []

    for amplitude in central_amplitudes:
        solution = solve_radial_matter(
            central_amplitude=float(amplitude),
            potential=potential,
            omega_guess=omega_guess,
            radius_max=radius_max,
            radial_points=radial_points,
            tolerance=tolerance,
        )
        points.append(
            BranchPoint(
                central_amplitude=float(amplitude),
                omega=solution.omega,
                solver_status=solution.solver_status,
                nodeless=solution.nodeless,
                energy=solution.energy,
                charge=solution.charge,
                energy_per_charge=solution.energy_per_charge,
                below_free_mass_threshold=solution.below_free_mass_threshold,
                solver_message=solution.solver_message,
            )
        )

    return points


def converged_nodeless(points: Iterable[BranchPoint]) -> list[BranchPoint]:
    return [
        point
        for point in points
        if point.solver_status == 0 and point.nodeless
    ]


def stable_candidates(points: Iterable[BranchPoint]) -> list[BranchPoint]:
    return [
        point
        for point in converged_nodeless(points)
        if point.below_free_mass_threshold
    ]


def lowest_energy_per_charge(
    points: Iterable[BranchPoint],
) -> BranchPoint | None:
    candidates = converged_nodeless(points)
    if not candidates:
        return None
    return min(candidates, key=lambda point: point.energy_per_charge)
