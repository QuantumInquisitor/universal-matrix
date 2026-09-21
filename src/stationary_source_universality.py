"""Stationary-source universality from the von Laue condition.

The reciprocity matter coupling sources the geometry scalar through the active
stress-energy density

    s(x) = T^{00}(x) + T^{11}(x) + T^{22}(x) + T^{33}(x)

in a local weak/background-flat frame.

For a stationary isolated system with conserved stress-energy,

    partial_mu T^{mu nu} = 0,

stationarity implies

    partial_k T^{k j} = 0.

Then

    partial_k (x^i T^{k j})
      = T^{i j} + x^i partial_k T^{k j}
      = T^{i j}.

Integrating over all space gives

    int T^{ij} d^3x
      = surface integral x^i T^{k j} n_k dA.

For a sufficiently localized isolated system, the surface term vanishes.
Therefore

    int T^{ij} d^3x = 0.

This is the von Laue condition.

Consequently,

    M_active
      = int [T^{00} + sum_i T^{ii}] d^3x
      = int T^{00} d^3x
      = E.

Thus the reciprocity scalar source is universally equal to total rest energy
for any stationary isolated system satisfying stress-energy conservation and
the required boundary falloff, regardless of internal composition.

This theorem does NOT apply automatically to nonstationary radiation escaping
to infinity, externally stressed systems, or configurations with nonvanishing
boundary stress flux.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np


def integrated_active_source(
    energy: float,
    integrated_spatial_stress: np.ndarray,
) -> float:
    stress = np.asarray(integrated_spatial_stress, dtype=float)
    if stress.shape != (3, 3):
        raise ValueError("integrated_spatial_stress must be 3x3")
    return float(energy + np.trace(stress))


def laue_residual(
    integrated_spatial_stress: np.ndarray,
) -> float:
    stress = np.asarray(integrated_spatial_stress, dtype=float)
    if stress.shape != (3, 3):
        raise ValueError("integrated_spatial_stress must be 3x3")
    return float(np.max(np.abs(stress)))


def source_energy_difference(
    integrated_spatial_stress: np.ndarray,
) -> float:
    stress = np.asarray(integrated_spatial_stress, dtype=float)
    if stress.shape != (3, 3):
        raise ValueError("integrated_spatial_stress must be 3x3")
    return float(np.trace(stress))


def source_energy_ratio(
    energy: float,
    integrated_spatial_stress: np.ndarray,
) -> float:
    if energy <= 0:
        raise ValueError("energy must be positive")
    return integrated_active_source(
        energy,
        integrated_spatial_stress,
    ) / energy


def satisfies_laue_condition(
    integrated_spatial_stress: np.ndarray,
    tolerance: float = 1e-12,
) -> bool:
    return laue_residual(integrated_spatial_stress) <= tolerance


def isotropic_integrated_stress(
    integrated_pressure: float,
) -> np.ndarray:
    return integrated_pressure * np.eye(3)


def boundary_surface_term_to_stress_integral(
    boundary_moment_flux: np.ndarray,
) -> np.ndarray:
    """The divergence-theorem identity ∫T^ij = boundary moment flux."""
    boundary = np.asarray(boundary_moment_flux, dtype=float)
    if boundary.shape != (3, 3):
        raise ValueError("boundary_moment_flux must be 3x3")
    return boundary.copy()


@dataclass(frozen=True)
class StationarySourceDiagnostic:
    energy: float
    integrated_spatial_stress: np.ndarray

    def __post_init__(self) -> None:
        if self.energy <= 0:
            raise ValueError("energy must be positive")
        stress = np.asarray(self.integrated_spatial_stress, dtype=float)
        if stress.shape != (3, 3):
            raise ValueError("integrated_spatial_stress must be 3x3")
        object.__setattr__(self, "integrated_spatial_stress", stress)

    @property
    def active_source(self) -> float:
        return integrated_active_source(
            self.energy,
            self.integrated_spatial_stress,
        )

    @property
    def difference(self) -> float:
        return self.active_source - self.energy

    @property
    def ratio(self) -> float:
        return self.active_source / self.energy

    @property
    def laue_residual(self) -> float:
        return laue_residual(self.integrated_spatial_stress)

    @property
    def universal_on_stationary_shell(self) -> bool:
        return math.isclose(
            self.active_source,
            self.energy,
            rel_tol=0,
            abs_tol=1e-12,
        ) and satisfies_laue_condition(
            self.integrated_spatial_stress,
        )
