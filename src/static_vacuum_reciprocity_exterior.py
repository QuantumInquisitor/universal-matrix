"""Exact static spherical vacuum exterior of the reciprocity scalar action.

For the self-consistent reciprocity action,

    L_psi
      = exp(4 psi) psi_t^2/(2 kappa)
        - |grad psi|^2/(2 kappa).

The full scalar equation has principal form

    exp(4 psi) [psi_tt + 2 psi_t^2]
      - laplacian psi
      = kappa * S_matter,

where S_matter is the matter source obtained from action variation.

For a static vacuum exterior,

    psi_t = 0
    S_matter = 0,

so the equation reduces EXACTLY to

    laplacian psi = 0.

For a spherically symmetric solution in 3D,

    psi(r) = A + B/r.

Asymptotic flatness requires A=0, leaving

    psi(r) = mu/r.

Distributionally,

    -laplacian(mu/r) = 4*pi*mu delta^3(x).

Therefore for a point source of active energy E,

    mu = kappa E/(4*pi).

This makes the exponential metric with psi=mu/r the exact static spherical
vacuum exterior of this scalar action, conditional on the reciprocity metric
ansatz and scalar action.
"""

from __future__ import annotations

import math


def spherical_vacuum_profile(
    radius: float,
    mu: float,
    asymptotic_constant: float = 0.0,
) -> float:
    if radius <= 0:
        raise ValueError("radius must be positive")
    return asymptotic_constant + mu / radius


def spherical_profile_derivative(
    radius: float,
    mu: float,
) -> float:
    if radius <= 0:
        raise ValueError("radius must be positive")
    return -mu / radius**2


def spherical_laplacian_from_radial_derivatives(
    radius: float,
    first_derivative: float,
    second_derivative: float,
) -> float:
    if radius <= 0:
        raise ValueError("radius must be positive")
    return second_derivative + 2.0 * first_derivative / radius


def point_profile_laplacian(
    radius: float,
    mu: float,
) -> float:
    """Classical Laplacian for r>0; distributional origin excluded."""
    if radius <= 0:
        raise ValueError("radius must be positive")
    first = -mu / radius**2
    second = 2.0 * mu / radius**3
    return spherical_laplacian_from_radial_derivatives(
        radius,
        first,
        second,
    )


def outward_flux(
    radius: float,
    mu: float,
) -> float:
    """Integral of grad(psi).dA on a sphere."""
    if radius <= 0:
        raise ValueError("radius must be positive")
    return (
        4.0
        * math.pi
        * radius**2
        * spherical_profile_derivative(radius, mu)
    )


def mu_from_active_energy(
    active_energy: float,
    kappa: float,
) -> float:
    if active_energy < 0:
        raise ValueError("active_energy must be non-negative")
    if kappa <= 0:
        raise ValueError("kappa must be positive")
    return kappa * active_energy / (4.0 * math.pi)


def active_energy_from_mu(
    mu: float,
    kappa: float,
) -> float:
    if mu < 0:
        raise ValueError("mu must be non-negative")
    if kappa <= 0:
        raise ValueError("kappa must be positive")
    return 4.0 * math.pi * mu / kappa


def full_static_metric_diagonal(
    radius: float,
    mu: float,
    causal_speed: float = 1.0,
) -> tuple[float, float, float, float]:
    if causal_speed <= 0:
        raise ValueError("causal_speed must be positive")
    psi = spherical_vacuum_profile(radius, mu)
    return (
        -causal_speed**2 * math.exp(-2.0 * psi),
        math.exp(2.0 * psi),
        math.exp(2.0 * psi),
        math.exp(2.0 * psi),
    )
