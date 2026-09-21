"""Weak-field normalization of the reciprocity scalar coupling.

For the self-consistent reciprocity action, the static weak equation is

    -laplacian psi = kappa * rho_active.

For nonrelativistic rest matter,
    rho_active ~= rho_rest_energy.

For a point source with rest energy
    E = M c_*^2,

the Green-function solution is
    psi(r) = kappa M c_*^2 / (4*pi*r).

The reciprocity metric weak acceleration is
    a = c_*^2 grad(psi),

so
    |a| = kappa c_*^4 M / (4*pi*r^2).

Matching Newton's law
    |a| = G M / r^2

requires
    kappa = 4*pi*G / c_*^4.

Einstein's field-equation coupling is conventionally
    kappa_E = 8*pi*G / c^4.

Therefore the scalar reciprocity normalization is
    kappa = kappa_E / 2

for the source and metric conventions used here.

This is a matching relation, not an independent derivation of G.
"""

from __future__ import annotations

import math


def reciprocity_kappa_from_newton(
    newton_constant: float,
    causal_speed: float,
) -> float:
    if newton_constant <= 0:
        raise ValueError("newton_constant must be positive")
    if causal_speed <= 0:
        raise ValueError("causal_speed must be positive")
    return 4.0 * math.pi * newton_constant / causal_speed**4


def einstein_kappa(
    newton_constant: float,
    causal_speed: float,
) -> float:
    if newton_constant <= 0:
        raise ValueError("newton_constant must be positive")
    if causal_speed <= 0:
        raise ValueError("causal_speed must be positive")
    return 8.0 * math.pi * newton_constant / causal_speed**4


def effective_newton_constant(
    reciprocity_kappa: float,
    causal_speed: float,
) -> float:
    if reciprocity_kappa <= 0:
        raise ValueError("reciprocity_kappa must be positive")
    if causal_speed <= 0:
        raise ValueError("causal_speed must be positive")
    return reciprocity_kappa * causal_speed**4 / (4.0 * math.pi)


def point_source_psi(
    source_mass: float,
    radius: float,
    reciprocity_kappa: float,
    causal_speed: float,
) -> float:
    if source_mass < 0:
        raise ValueError("source_mass must be non-negative")
    if radius <= 0:
        raise ValueError("radius must be positive")
    if reciprocity_kappa <= 0:
        raise ValueError("reciprocity_kappa must be positive")
    if causal_speed <= 0:
        raise ValueError("causal_speed must be positive")

    rest_energy = source_mass * causal_speed**2
    return reciprocity_kappa * rest_energy / (4.0 * math.pi * radius)


def point_source_acceleration(
    source_mass: float,
    radius: float,
    reciprocity_kappa: float,
    causal_speed: float,
) -> float:
    """Weak radial acceleration magnitude c_*^2 |grad psi|."""
    if radius <= 0:
        raise ValueError("radius must be positive")
    return (
        reciprocity_kappa
        * causal_speed**4
        * source_mass
        / (4.0 * math.pi * radius**2)
    )
