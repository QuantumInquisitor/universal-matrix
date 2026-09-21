"""Timelike circular orbits and ISCO in the reciprocity exterior.

Metric:
    ds^2 = -A(r) dt^2 + B(r) dr^2 + C(r) dphi^2

with
    A = exp(-2 mu/r)
    B = exp( 2 mu/r)
    C = exp( 2 mu/r) r^2

in the equatorial plane.

For static circular timelike geodesics,

    Omega^2 = A'/C'

and

    E^2 = A^2 C' / (A C' - C A')
    L^2 = C^2 A' / (A C' - C A').

For the exponential exterior:

    A C' - C A' = 2(r - 2 mu),

so timelike circular orbits require
    r > 2 mu.

Exact formulas:

    Omega^2
      = mu exp(-4 mu/r) / [r^2 (r-mu)]

    E^2
      = exp(-2 mu/r) (r-mu)/(r-2mu)

    L^2
      = mu exp(2 mu/r) r^2/(r-2mu).

Marginal stability is given by d(L^2)/dr=0, which reduces to

    r^2 - 6 mu r + 4 mu^2 = 0.

The physical root outside the photon orbit is

    r_ISCO = (3 + sqrt(5)) mu.

Areal radius:
    R = r exp(mu/r),

so
    R_ISCO ~= 6.337940264856347 mu.

Schwarzschild has R_ISCO = 6 mu.

The dimensionless orbital frequency at the reciprocity ISCO is

    Omega_ISCO * mu ~= 0.06333263135,

versus Schwarzschild

    1/(6 sqrt(6)) ~= 0.06804138174.
"""

from __future__ import annotations

import math


def lapse_squared(radius: float, mu: float) -> float:
    _validate(radius, mu)
    return math.exp(-2.0*mu/radius)


def angular_metric(radius: float, mu: float) -> float:
    _validate(radius, mu)
    return math.exp(2.0*mu/radius)*radius**2


def circular_orbit_energy_squared(radius: float, mu: float) -> float:
    _validate_timelike_radius(radius, mu)
    return (
        math.exp(-2.0*mu/radius)
        * (radius-mu)
        / (radius-2.0*mu)
    )


def circular_orbit_angular_momentum_squared(
    radius: float,
    mu: float,
) -> float:
    _validate_timelike_radius(radius, mu)
    return (
        mu
        * math.exp(2.0*mu/radius)
        * radius**2
        / (radius-2.0*mu)
    )


def circular_orbit_omega_squared(radius: float, mu: float) -> float:
    _validate_timelike_radius(radius, mu)
    return (
        mu
        * math.exp(-4.0*mu/radius)
        / (radius**2 * (radius-mu))
    )


def circular_orbit_omega(radius: float, mu: float) -> float:
    return math.sqrt(circular_orbit_omega_squared(radius, mu))


def photon_orbit_isotropic_radius(mu: float) -> float:
    if mu <= 0:
        raise ValueError("mu must be positive")
    return 2.0*mu


def isco_isotropic_radius(mu: float) -> float:
    if mu <= 0:
        raise ValueError("mu must be positive")
    return (3.0+math.sqrt(5.0))*mu


def areal_radius(radius: float, mu: float) -> float:
    _validate(radius, mu)
    return radius*math.exp(mu/radius)


def isco_areal_radius(mu: float) -> float:
    r = isco_isotropic_radius(mu)
    return areal_radius(r, mu)


def isco_dimensionless_frequency() -> float:
    """Return Omega_ISCO * mu."""
    x = 3.0+math.sqrt(5.0)
    return math.sqrt(
        math.exp(-4.0/x)
        / (x*x*(x-1.0))
    )


def schwarzschild_isco_areal_radius(mu: float) -> float:
    if mu <= 0:
        raise ValueError("mu must be positive")
    return 6.0*mu


def schwarzschild_isco_dimensionless_frequency() -> float:
    return 1.0/(6.0*math.sqrt(6.0))


def isco_areal_fractional_difference_from_schwarzschild() -> float:
    return isco_areal_radius(1.0)/6.0 - 1.0


def isco_frequency_fractional_difference_from_schwarzschild() -> float:
    return (
        isco_dimensionless_frequency()
        / schwarzschild_isco_dimensionless_frequency()
        - 1.0
    )


def _validate(radius: float, mu: float) -> None:
    if radius <= 0:
        raise ValueError("radius must be positive")
    if mu <= 0:
        raise ValueError("mu must be positive")


def _validate_timelike_radius(radius: float, mu: float) -> None:
    _validate(radius, mu)
    if radius <= 2.0*mu:
        raise ValueError(
            "timelike circular orbit requires radius > 2 mu"
        )
