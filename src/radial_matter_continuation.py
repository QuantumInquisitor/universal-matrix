"""Numerical continuation for the existing radial charged-matter solver.

The original radial solver treats each central amplitude as an independent BVP
with a generic Gaussian initial guess.  That is useful for isolated solves but
can jump between mathematical branches as amplitude changes.

This module adds branch continuation:

1. solve one trusted starting point;
2. interpolate and rescale the previous converged profile;
3. seed the next BVP with that profile and previous omega;
4. reject solutions outside the analytic Q-ball window;
5. retain only converged, nodeless, low-virial-residual points as future seeds.

The continuation machinery does not prove nonlinear stability.  It improves
branch identity and numerical reliability before persistence tests.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from collections.abc import Iterable

import numpy as np
from scipy.integrate import simpson, solve_bvp

from .localized_matter_variational import MatterPotential
from .qball_existence_window import qball_existence_window
from .radial_matter_solver import (
    RadialMatterSolution,
    radial_rhs,
    solve_radial_matter,
)


@dataclass(frozen=True)
class ContinuationRecord:
    central_amplitude: float
    solution: RadialMatterSolution
    converged: bool
    nodeless: bool
    in_frequency_window: bool
    relative_virial_residual: float
    accepted_as_seed: bool
    rejection_reason: str

    @property
    def omega(self) -> float:
        return self.solution.omega

    @property
    def energy_per_charge(self) -> float:
        return self.solution.energy_per_charge

    @property
    def below_free_mass_threshold(self) -> bool:
        return self.solution.below_free_mass_threshold


def _assemble_solution(
    *,
    solver,
    potential: MatterPotential,
) -> RadialMatterSolution:
    rr = solver.x
    f = solver.y[0]
    fp = solver.y[1]
    omega = float(solver.p[0])

    rho2 = f * f
    potential_density = (
        potential.mass2 * rho2
        + potential.lambda4 * rho2**2
        + potential.lambda6 * rho2**3
    )
    volume_weight = 4.0 * math.pi * rr * rr

    i2 = float(simpson(volume_weight * rho2, x=rr))
    charge = 2.0 * omega * i2
    time_kinetic_integral = omega**2 * i2
    gradient_integral = float(
        simpson(volume_weight * fp * fp, x=rr)
    )
    potential_integral = float(
        simpson(volume_weight * potential_density, x=rr)
    )
    energy = (
        time_kinetic_integral
        + gradient_integral
        + potential_integral
    )

    return RadialMatterSolution(
        radius=rr,
        profile=f,
        derivative=fp,
        omega=omega,
        energy=energy,
        charge=charge,
        time_kinetic_integral=time_kinetic_integral,
        gradient_integral=gradient_integral,
        potential_integral=potential_integral,
        potential=potential,
        solver_status=int(solver.status),
        solver_message=str(solver.message),
    )


def solve_radial_matter_seeded(
    central_amplitude: float,
    seed: RadialMatterSolution,
    *,
    potential: MatterPotential | None = None,
    radius_max: float = 20.0,
    radial_points: int = 300,
    tolerance: float = 2e-5,
    max_nodes: int = 10000,
) -> RadialMatterSolution:
    """Solve one neighboring branch point using a previous solution as seed."""
    if central_amplitude <= 0:
        raise ValueError("central_amplitude must be positive")
    if radius_max <= 0:
        raise ValueError("radius_max must be positive")
    if radial_points < 50:
        raise ValueError("radial_points must be at least 50")
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    if max_nodes < radial_points:
        raise ValueError("max_nodes must be >= radial_points")

    p = seed.potential if potential is None else potential
    if p != seed.potential:
        raise ValueError("seed potential must match continuation potential")

    r0 = 1e-4
    r = np.linspace(r0, radius_max, radial_points)

    profile = np.interp(
        r,
        seed.radius,
        seed.profile,
        left=float(seed.profile[0]),
        right=0.0,
    )
    derivative = np.interp(
        r,
        seed.radius,
        seed.derivative,
        left=float(seed.derivative[0]),
        right=0.0,
    )

    seed_center = float(seed.profile[0])
    if abs(seed_center) < 1e-14:
        raise ValueError("seed central amplitude is too small for rescaling")

    scale = central_amplitude / seed_center
    y_guess = np.vstack(
        [
            profile * scale,
            derivative * scale,
        ]
    )

    def fun(x: np.ndarray, y: np.ndarray, params: np.ndarray) -> np.ndarray:
        return radial_rhs(
            x,
            y,
            float(params[0]),
            p,
        )

    def bc(
        ya: np.ndarray,
        yb: np.ndarray,
        params: np.ndarray,
    ) -> np.ndarray:
        omega = float(params[0])
        regular_force = (
            (p.mass2 - omega**2) * central_amplitude
            + 2.0 * p.lambda4 * central_amplitude**3
            + 3.0 * p.lambda6 * central_amplitude**5
        )
        regular_derivative = regular_force * r0 / 3.0
        return np.array(
            [
                ya[0] - central_amplitude,
                ya[1] - regular_derivative,
                yb[0],
            ]
        )

    solver = solve_bvp(
        fun,
        bc,
        r,
        y_guess,
        p=np.array([seed.omega], dtype=float),
        tol=tolerance,
        max_nodes=max_nodes,
    )
    return _assemble_solution(
        solver=solver,
        potential=p,
    )


def classify_continuation_solution(
    central_amplitude: float,
    solution: RadialMatterSolution,
    *,
    virial_tolerance: float = 1e-3,
) -> ContinuationRecord:
    """Classify whether a solution is reliable enough to seed its neighbor."""
    if central_amplitude <= 0:
        raise ValueError("central_amplitude must be positive")
    if not math.isfinite(virial_tolerance) or virial_tolerance < 0:
        raise ValueError("virial_tolerance must be finite and non-negative")

    window = qball_existence_window(solution.potential)
    converged = solution.solver_status == 0
    nodeless = solution.nodeless
    in_window = window.allows_omega(solution.omega)
    relative_virial = (
        abs(solution.virial_residual)
        / max(abs(solution.energy), 1e-15)
    )

    reasons: list[str] = []
    if not converged:
        reasons.append("solver_not_converged")
    if not nodeless:
        reasons.append("profile_has_node")
    if not in_window:
        reasons.append("omega_outside_analytic_window")
    if relative_virial > virial_tolerance:
        reasons.append("virial_residual_too_large")

    accepted = not reasons
    return ContinuationRecord(
        central_amplitude=float(central_amplitude),
        solution=solution,
        converged=converged,
        nodeless=nodeless,
        in_frequency_window=in_window,
        relative_virial_residual=float(relative_virial),
        accepted_as_seed=accepted,
        rejection_reason="accepted" if accepted else ",".join(reasons),
    )


def continue_radial_branch(
    central_amplitudes: Iterable[float],
    *,
    potential: MatterPotential = MatterPotential(),
    omega_guess: float = 0.95,
    radius_max: float = 20.0,
    radial_points: int = 300,
    tolerance: float = 2e-5,
    max_nodes: int = 10000,
    virial_tolerance: float = 1e-3,
) -> list[ContinuationRecord]:
    """Track one nodeless branch across ordered central amplitudes."""
    amplitudes = [float(a) for a in central_amplitudes]
    if not amplitudes:
        raise ValueError("central_amplitudes must be non-empty")
    if any(a <= 0 or not math.isfinite(a) for a in amplitudes):
        raise ValueError("central amplitudes must be finite and positive")

    records: list[ContinuationRecord] = []
    seed: RadialMatterSolution | None = None

    for amplitude in amplitudes:
        if seed is None:
            solution = solve_radial_matter(
                central_amplitude=amplitude,
                potential=potential,
                omega_guess=omega_guess,
                radius_max=radius_max,
                radial_points=radial_points,
                tolerance=tolerance,
            )
        else:
            solution = solve_radial_matter_seeded(
                amplitude,
                seed,
                potential=potential,
                radius_max=radius_max,
                radial_points=radial_points,
                tolerance=tolerance,
                max_nodes=max_nodes,
            )

        record = classify_continuation_solution(
            amplitude,
            solution,
            virial_tolerance=virial_tolerance,
        )
        records.append(record)

        if record.accepted_as_seed:
            seed = solution

    return records


def accepted_records(
    records: Iterable[ContinuationRecord],
) -> list[ContinuationRecord]:
    return [record for record in records if record.accepted_as_seed]


def below_threshold_records(
    records: Iterable[ContinuationRecord],
) -> list[ContinuationRecord]:
    return [
        record
        for record in accepted_records(records)
        if record.below_free_mass_threshold
    ]
