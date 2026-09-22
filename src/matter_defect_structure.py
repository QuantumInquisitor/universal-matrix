"""Exact defect structure and Derrick constraint for the default matter potential.

For the repository default

    U(rho) = rho - 2 rho^2 + rho^3,

a real amplitude f has

    U(f^2) = f^2 (1 - f^2)^2.

The vacua f=0 and f=1 are degenerate.  A one-dimensional static wall obeys

    f' = f(1-f^2)

and therefore has the exact profile

    f(x) = [1 + exp(-2(x-x0))]^{-1/2}.

Its tension in the repository's energy normalization,

    E = int [(f')^2 + U(f^2)] dx,

is exactly 1/2.

The same nonnegative scalar energy cannot support a nontrivial static,
finite-energy localized solution in three spatial dimensions.  Derrick
scaling gives

    dE(lambda)/d lambda |_(1)
      = (2-d) T - d V

for f_lambda(x)=f(lambda x).  In d=3 with T>=0 and V>=0 this is strictly
negative for every nontrivial configuration, so no static scalar lump can be
a stationary finite-size particle.

Time dependence, conserved charge, gauge fields, topology, higher derivatives,
or another nonredundant ingredient is therefore required for 3D localization.
"""

from __future__ import annotations

import math

import numpy as np

from .localized_matter_variational import MatterPotential


DEFAULT_DEFECT_POTENTIAL = MatterPotential(
    mass2=1.0,
    lambda4=-2.0,
    lambda6=1.0,
)


def default_potential_energy_from_amplitude(amplitude: np.ndarray | float):
    """Return U(|f|^2)=f^2(1-f^2)^2 for a real amplitude."""
    f = np.asarray(amplitude, dtype=float)
    return f * f * (1.0 - f * f) ** 2


def domain_wall_profile(
    coordinate: np.ndarray | float,
    *,
    center: float = 0.0,
) -> np.ndarray:
    """Exact monotone wall connecting f=0 to f=1."""
    x = np.asarray(coordinate, dtype=float)
    if not math.isfinite(center):
        raise ValueError("center must be finite")
    return 1.0 / np.sqrt(1.0 + np.exp(-2.0 * (x - center)))


def domain_wall_derivative(
    coordinate: np.ndarray | float,
    *,
    center: float = 0.0,
) -> np.ndarray:
    """Exact first derivative f'=f(1-f^2)."""
    f = domain_wall_profile(coordinate, center=center)
    return f * (1.0 - f * f)


def domain_wall_second_derivative(
    coordinate: np.ndarray | float,
    *,
    center: float = 0.0,
) -> np.ndarray:
    """Exact second derivative f''=f(1-4f^2+3f^4)."""
    f = domain_wall_profile(coordinate, center=center)
    return f * (1.0 - 4.0 * f * f + 3.0 * f**4)


def static_field_equation_residual(
    coordinate: np.ndarray | float,
    *,
    center: float = 0.0,
) -> np.ndarray:
    """Residual of f'' - U'(f^2) f for the exact wall."""
    f = domain_wall_profile(coordinate, center=center)
    fpp = domain_wall_second_derivative(coordinate, center=center)
    nonlinear = (1.0 - 4.0 * f * f + 3.0 * f**4) * f
    return fpp - nonlinear


def domain_wall_energy_density(
    coordinate: np.ndarray | float,
    *,
    center: float = 0.0,
) -> np.ndarray:
    """Return (f')^2 + U(f^2)."""
    f = domain_wall_profile(coordinate, center=center)
    fp = domain_wall_derivative(coordinate, center=center)
    return fp * fp + default_potential_energy_from_amplitude(f)


def domain_wall_tension_exact() -> float:
    """Exact wall tension in the repository's scalar normalization."""
    return 0.5


def derrick_scaled_energy(
    scale: float,
    gradient_energy: float,
    potential_energy: float,
    *,
    dimension: int = 3,
) -> float:
    """Energy of f_lambda(x)=f(lambda x) under Derrick scaling."""
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError("scale must be finite and positive")
    if not isinstance(dimension, int) or isinstance(dimension, bool) or dimension < 1:
        raise ValueError("dimension must be a positive integer")
    if not math.isfinite(gradient_energy) or gradient_energy < 0:
        raise ValueError("gradient_energy must be finite and non-negative")
    if not math.isfinite(potential_energy) or potential_energy < 0:
        raise ValueError("potential_energy must be finite and non-negative")

    return (
        scale ** (2 - dimension) * gradient_energy
        + scale ** (-dimension) * potential_energy
    )


def derrick_stationarity_residual(
    gradient_energy: float,
    potential_energy: float,
    *,
    dimension: int = 3,
) -> float:
    """Return dE/dlambda at lambda=1."""
    if not isinstance(dimension, int) or isinstance(dimension, bool) or dimension < 1:
        raise ValueError("dimension must be a positive integer")
    if not math.isfinite(gradient_energy) or gradient_energy < 0:
        raise ValueError("gradient_energy must be finite and non-negative")
    if not math.isfinite(potential_energy) or potential_energy < 0:
        raise ValueError("potential_energy must be finite and non-negative")

    return (
        (2 - dimension) * gradient_energy
        - dimension * potential_energy
    )


def static_scalar_lump_allowed_by_derrick(
    gradient_energy: float,
    potential_energy: float,
    *,
    dimension: int = 3,
    tolerance: float = 1e-12,
) -> bool:
    """Return whether Derrick stationarity is possible for supplied T,V."""
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be finite and non-negative")
    residual = derrick_stationarity_residual(
        gradient_energy,
        potential_energy,
        dimension=dimension,
    )
    return abs(residual) <= tolerance
