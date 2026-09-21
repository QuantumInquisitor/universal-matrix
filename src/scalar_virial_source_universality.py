"""Virial universality of active geometry source for stationary scalar lumps.

Consider a stationary localized time-harmonic complex scalar in three spatial
dimensions,

    Phi(t,x) = exp(-i omega t) f(x),

with flat weak-background matter Lagrangian

    L = |Phi_t|^2 - |grad Phi|^2 - U(|Phi|^2).

Define integrated quantities

    K = int |Phi_t|^2 d^3x
    G = int |grad Phi|^2 d^3x
    V = int U d^3x.

Total energy:

    E = K + G + V.

The reciprocity-geometry source from variation of the matter action is

    M_active = int (rho + p_x + p_y + p_z) d^3x
             = 4 K - 2 V.

For a stationary localized solution, Derrick scaling of the reduced
time-harmonic action gives the 3D virial identity

    G + 3(V - K) = 0.

Equivalently,

    K - V = G/3.

Substituting into M_active gives

    M_active
      = 4K - 2V
      = 2K + 2(K-V)
      = 2K + 2G/3.

Using the same virial identity in E,

    E
      = K + G + V
      = 2K + 2G/3.

Therefore

    M_active = E.

So any exact stationary localized scalar solution satisfying the virial
identity sources the weak reciprocity geometry in proportion to its total rest
energy, independent of detailed profile shape.

This is a weak-background stationary theorem. It does not automatically extend
to strongly gravitating, time-dependent, radiating, or non-scalar matter.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


def virial_residual(
    time_kinetic: float,
    gradient: float,
    potential: float,
) -> float:
    _validate_nonnegative(time_kinetic, gradient)
    return gradient + 3.0 * (potential - time_kinetic)


def total_energy(
    time_kinetic: float,
    gradient: float,
    potential: float,
) -> float:
    _validate_nonnegative(time_kinetic, gradient)
    return time_kinetic + gradient + potential


def active_geometry_source(
    time_kinetic: float,
    potential: float,
) -> float:
    if time_kinetic < 0:
        raise ValueError("time_kinetic must be non-negative")
    return 4.0 * time_kinetic - 2.0 * potential


def source_energy_difference(
    time_kinetic: float,
    gradient: float,
    potential: float,
) -> float:
    """M_active - E."""
    return (
        active_geometry_source(time_kinetic, potential)
        - total_energy(time_kinetic, gradient, potential)
    )


def difference_from_virial(
    time_kinetic: float,
    gradient: float,
    potential: float,
) -> float:
    """Identity: M_active - E = -virial_residual."""
    return -virial_residual(time_kinetic, gradient, potential)


def potential_required_by_virial(
    time_kinetic: float,
    gradient: float,
) -> float:
    _validate_nonnegative(time_kinetic, gradient)
    return time_kinetic - gradient / 3.0


def universal_source_ratio_on_virial_shell(
    time_kinetic: float,
    gradient: float,
) -> float:
    potential = potential_required_by_virial(
        time_kinetic,
        gradient,
    )
    energy = total_energy(
        time_kinetic,
        gradient,
        potential,
    )
    if energy <= 0:
        raise ValueError("virial-shell total energy must be positive")
    source = active_geometry_source(
        time_kinetic,
        potential,
    )
    return source / energy


@dataclass(frozen=True)
class VirialSourceDiagnostic:
    time_kinetic: float
    gradient: float
    potential: float

    @property
    def virial_residual(self) -> float:
        return virial_residual(
            self.time_kinetic,
            self.gradient,
            self.potential,
        )

    @property
    def energy(self) -> float:
        return total_energy(
            self.time_kinetic,
            self.gradient,
            self.potential,
        )

    @property
    def active_source(self) -> float:
        return active_geometry_source(
            self.time_kinetic,
            self.potential,
        )

    @property
    def source_energy_difference(self) -> float:
        return self.active_source - self.energy

    @property
    def source_energy_ratio(self) -> float:
        if self.energy == 0:
            return math.inf
        return self.active_source / self.energy


def _validate_nonnegative(
    time_kinetic: float,
    gradient: float,
) -> None:
    if time_kinetic < 0:
        raise ValueError("time_kinetic must be non-negative")
    if gradient < 0:
        raise ValueError("gradient must be non-negative")
