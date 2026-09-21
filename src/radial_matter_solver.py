"""Nonlinear radial solver for time-harmonic classical matter lumps.

Matter ansatz:
    Phi(t,r) = exp(i omega t) f(r)

Potential:
    U(f) = m2 f^2 + lambda4 f^4 + lambda6 f^6.

For the classical Lagrangian normalization used in the variational module, the
radial Euler-Lagrange equation is

    f'' + (2/r) f'
      = (m2 - omega^2) f
        + 2 lambda4 f^3
        + 3 lambda6 f^5.

Boundary conditions for a localized nodeless profile are approximately

    f(0) = A0
    f'(0) = 0
    f(Rmax) = 0.

This solver fixes A0 and treats omega as an unknown BVP parameter.

The output distinguishes:
- existence/convergence of a localized field-equation solution;
- energetic stability diagnostic E/Q < sqrt(m2).

Those are not the same statement.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np
from scipy.integrate import simpson, solve_bvp

try:
    from .localized_matter_variational import MatterPotential
except ImportError:
    from localized_matter_variational import MatterPotential


@dataclass(frozen=True)
class RadialMatterSolution:
    radius: np.ndarray
    profile: np.ndarray
    derivative: np.ndarray
    omega: float
    energy: float
    charge: float
    time_kinetic_integral: float
    gradient_integral: float
    potential_integral: float
    potential: MatterPotential
    solver_status: int
    solver_message: str

    @property
    def energy_per_charge(self) -> float:
        return self.energy / self.charge

    @property
    def below_free_mass_threshold(self) -> bool:
        return self.energy_per_charge < self.potential.free_mass

    @property
    def virial_residual(self) -> float:
        return (
            self.gradient_integral
            + 3.0
            * (
                self.potential_integral
                - self.time_kinetic_integral
            )
        )

    @property
    def active_geometry_source(self) -> float:
        return (
            4.0 * self.time_kinetic_integral
            - 2.0 * self.potential_integral
        )

    @property
    def source_energy_difference(self) -> float:
        return self.active_geometry_source - self.energy

    @property
    def source_energy_ratio(self) -> float:
        if self.energy == 0:
            return math.inf
        return self.active_geometry_source / self.energy

    @property
    def nodeless(self) -> bool:
        tolerance = 1e-7 * max(1.0, float(np.max(np.abs(self.profile))))
        return float(np.min(self.profile)) >= -tolerance

    def snapshot(self) -> dict[str, float | bool | int | str]:
        return {
            "omega": self.omega,
            "energy": self.energy,
            "charge": self.charge,
            "energy_per_charge": self.energy_per_charge,
            "free_mass": self.potential.free_mass,
            "below_free_mass_threshold": self.below_free_mass_threshold,
            "time_kinetic_integral": self.time_kinetic_integral,
            "gradient_integral": self.gradient_integral,
            "potential_integral": self.potential_integral,
            "virial_residual": self.virial_residual,
            "active_geometry_source": self.active_geometry_source,
            "source_energy_difference": self.source_energy_difference,
            "source_energy_ratio": self.source_energy_ratio,
            "nodeless": self.nodeless,
            "solver_status": self.solver_status,
            "solver_message": self.solver_message,
            "model_status": "classical_nonlinear_radial_matter_solution",
        }


def radial_rhs(
    radius: np.ndarray,
    y: np.ndarray,
    omega: float,
    potential: MatterPotential,
) -> np.ndarray:
    f = y[0]
    fp = y[1]
    r = np.asarray(radius, dtype=float)

    nonlinear = (
        (potential.mass2 - omega**2) * f
        + 2.0 * potential.lambda4 * f**3
        + 3.0 * potential.lambda6 * f**5
    )
    return np.vstack(
        [
            fp,
            nonlinear - 2.0 * fp / r,
        ]
    )


def solve_radial_matter(
    central_amplitude: float,
    potential: MatterPotential = MatterPotential(),
    omega_guess: float = 0.9,
    radius_max: float = 20.0,
    radial_points: int = 350,
    tolerance: float = 1e-5,
) -> RadialMatterSolution:
    if central_amplitude <= 0:
        raise ValueError("central_amplitude must be positive")
    if not 0 < omega_guess < potential.free_mass * 2.0:
        raise ValueError("omega_guess must be positive and finite")
    if radius_max <= 0:
        raise ValueError("radius_max must be positive")
    if radial_points < 50:
        raise ValueError("radial_points must be at least 50")

    r0 = 1e-4
    r = np.linspace(r0, radius_max, radial_points)
    width_guess = max(1.0, radius_max / 5.0)
    f_guess = central_amplitude * np.exp(
        -0.5 * (r / width_guess) ** 2
    )
    fp_guess = -(r / width_guess**2) * f_guess
    y_guess = np.vstack([f_guess, fp_guess])

    def fun(x: np.ndarray, y: np.ndarray, p: np.ndarray) -> np.ndarray:
        return radial_rhs(x, y, float(p[0]), potential)

    def bc(ya: np.ndarray, yb: np.ndarray, p: np.ndarray) -> np.ndarray:
        omega = float(p[0])
        regular_force = (
            (potential.mass2 - omega**2) * central_amplitude
            + 2.0 * potential.lambda4 * central_amplitude**3
            + 3.0 * potential.lambda6 * central_amplitude**5
        )
        regular_derivative = regular_force * r0 / 3.0
        return np.array(
            [
                ya[0] - central_amplitude,
                ya[1] - regular_derivative,
                yb[0],
            ]
        )

    solution = solve_bvp(
        fun,
        bc,
        r,
        y_guess,
        p=np.array([omega_guess], dtype=float),
        tol=tolerance,
        max_nodes=10000,
    )

    rr = solution.x
    f = solution.y[0]
    fp = solution.y[1]
    omega = float(solution.p[0])

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
        solver_status=int(solution.status),
        solver_message=str(solution.message),
    )
