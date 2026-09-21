"""Experimental scalar potential sourced by conserved content density.

Distinguish:
    rho_C >= 0 : local conserved-content source density
    chi        : long-range scalar content potential

Choose the static field functional

    E[chi] = integral [ |grad chi|^2 / (2*kappa_C) - rho_C * chi ] dV

for kappa_C > 0.

Variation gives

    -laplacian(chi) = kappa_C * rho_C.

In unbounded 3D space, the Green function satisfies

    -laplacian(1/(4*pi*r)) = delta^3(r),

so a positive point source generates

    chi(r) = kappa_C * Q_C / (4*pi*r).

Thus a 1/r potential and 1/r^2 gradient follow from the field equation and
three-dimensional Green function rather than being directly inserted as a
force law.

The finite numerical adapter reuses the open Neumann solver. Its additive
constant is fixed by the solver's mean-zero convention. Physical lapse models
must therefore use potential differences or an explicitly chosen reference
potential.

This is experimental and is not a gravitational field equation.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np

try:
    from .open_boundary_solver import (
        GateFieldFlux,
        balanced_gate_flux,
        solve_open_gauss,
    )
except ImportError:
    from open_boundary_solver import (
        GateFieldFlux,
        balanced_gate_flux,
        solve_open_gauss,
    )


def validate_source_density(source_density: np.ndarray) -> np.ndarray:
    rho = np.asarray(source_density, dtype=float)
    if rho.ndim != 3:
        raise ValueError("source_density must be a 3D array")
    if np.any(rho < 0):
        raise ValueError("content source density must be non-negative")
    return rho


def solve_content_potential(
    source_density: np.ndarray,
    coupling: float,
    boundary_flux: GateFieldFlux | None = None,
    tolerance: float = 1e-11,
):
    """Solve -laplacian(chi)=coupling*rho_C on the finite open domain."""
    if coupling < 0:
        raise ValueError("coupling must be non-negative")
    rho = validate_source_density(source_density)
    effective_source = coupling * rho

    if boundary_flux is None:
        boundary_flux = balanced_gate_flux(float(np.sum(effective_source)))

    return solve_open_gauss(
        effective_source,
        boundary_flux,
        tolerance=tolerance,
    )


def point_source_potential_3d(
    radius: float,
    source_strength: float,
    coupling: float,
) -> float:
    """Infinite-space 3D Green-function potential outside a point source."""
    if radius <= 0:
        raise ValueError("radius must be positive")
    if source_strength < 0 or coupling < 0:
        raise ValueError("source_strength and coupling must be non-negative")
    return coupling * source_strength / (4.0 * math.pi * radius)


def point_source_gradient_3d(
    position: Sequence[float],
    source_strength: float,
    coupling: float,
) -> np.ndarray:
    """Gradient of chi=KQ/(4*pi*r), pointing toward the positive source."""
    x = np.asarray(position, dtype=float)
    if x.ndim != 1:
        raise ValueError("position must be a 1D vector")
    r = float(np.linalg.norm(x))
    if r <= 0:
        raise ValueError("position must be away from the point source")
    if source_strength < 0 or coupling < 0:
        raise ValueError("source_strength and coupling must be non-negative")

    prefactor = -coupling * source_strength / (4.0 * math.pi * r**3)
    return prefactor * x


def field_energy_density(
    potential_gradient: Sequence[float],
    coupling: float,
) -> float:
    """Positive gradient-energy density |grad chi|^2/(2*kappa_C)."""
    if coupling <= 0:
        raise ValueError("coupling must be positive")
    grad = np.asarray(potential_gradient, dtype=float)
    return float(np.dot(grad, grad)) / (2.0 * coupling)


def potential_lapse(
    potential: float,
    clock_coupling: float,
    reference_potential: float = 0.0,
) -> float:
    """Positive clock/travel-time lapse from scalar potential difference."""
    if clock_coupling < 0:
        raise ValueError("clock_coupling must be non-negative")
    return math.exp(clock_coupling * (potential - reference_potential))


def potential_clock_rate_ratio(
    potential: float,
    clock_coupling: float,
    reference_potential: float = 0.0,
) -> float:
    return 1.0 / potential_lapse(
        potential,
        clock_coupling,
        reference_potential,
    )


@dataclass(frozen=True)
class PointContentSource:
    source_strength: float
    field_coupling: float

    def __post_init__(self) -> None:
        if self.source_strength < 0:
            raise ValueError("source_strength must be non-negative")
        if self.field_coupling < 0:
            raise ValueError("field_coupling must be non-negative")

    def potential(self, radius: float) -> float:
        return point_source_potential_3d(
            radius,
            self.source_strength,
            self.field_coupling,
        )

    def gradient(self, position: Sequence[float]) -> np.ndarray:
        return point_source_gradient_3d(
            position,
            self.source_strength,
            self.field_coupling,
        )
