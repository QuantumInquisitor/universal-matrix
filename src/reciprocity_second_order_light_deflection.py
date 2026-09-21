"""Second-order light deflection in the reciprocity exponential exterior.

Metric:
    ds^2 = -exp(-2 mu/r) dt^2
           + exp(2 mu/r)(dr^2 + r^2 dOmega^2).

For an equatorial null geodesic with conserved asymptotic impact parameter
    b = L/E,

define
    x = b/r
    epsilon = mu/b.

Because A*B=1 for the exponential metric, the first integral reduces to

    (dx/dphi)^2 = exp(4 epsilon x) - x^2.

Differentiating gives the exact orbit equation

    x'' + x = 2 epsilon exp(4 epsilon x).

Use
    x = x0 + epsilon x1 + epsilon^2 x2 + ...

with symmetry about closest approach.

Turning point:
    x_t^2 = exp(4 epsilon x_t)

gives
    x_t
      = 1 + 2 epsilon + 6 epsilon^2
        + (64/3) epsilon^3 + ...

Orders:

    x0'' + x0 = 0
    x0 = cos(phi)

    x1'' + x1 = 2
    x1 = 2

    x2'' + x2 = 8 cos(phi)
    x2 = 6 cos(phi) + 4 phi sin(phi).

The outgoing asymptote occurs at
    phi = pi/2 + s

with
    s = 2 epsilon + 2 pi epsilon^2 + ...

Total deflection is twice the one-sided shift:

    alpha_exp
      = 4 epsilon + 4 pi epsilon^2 + O(epsilon^3).

Schwarzschild/GR reference:

    alpha_GR
      = 4 epsilon + (15 pi/4) epsilon^2 + O(epsilon^3).

Difference:

    alpha_exp - alpha_GR
      = (pi/4) epsilon^2 + O(epsilon^3).

This gives a coordinate-invariant observable distinction at second order.
"""

from __future__ import annotations

import math


def turning_point_series(epsilon: float) -> float:
    """Turning-point series with a cubic remainder-control term.

    The observable deflection calculation remains second order. Including the
    exact cubic turning-point coefficient suppresses the O(epsilon^3)
    residual in the algebraic turning-point constraint.
    """
    return (
        1.0
        + 2.0*epsilon
        + 6.0*epsilon**2
        + (64.0/3.0)*epsilon**3
    )


def orbit_x0(phi: float) -> float:
    return math.cos(phi)


def orbit_x1(phi: float) -> float:
    _ = phi
    return 2.0


def orbit_x2(phi: float) -> float:
    return (
        6.0*math.cos(phi)
        + 4.0*phi*math.sin(phi)
    )


def orbit_series(phi: float, epsilon: float) -> float:
    return (
        orbit_x0(phi)
        + epsilon*orbit_x1(phi)
        + epsilon**2*orbit_x2(phi)
    )


def reciprocity_deflection_second_order(
    mu: float,
    impact_parameter: float,
) -> float:
    _validate(mu, impact_parameter)
    epsilon = mu/impact_parameter
    return 4.0*epsilon + 4.0*math.pi*epsilon**2


def schwarzschild_deflection_second_order(
    mu: float,
    impact_parameter: float,
) -> float:
    _validate(mu, impact_parameter)
    epsilon = mu/impact_parameter
    return (
        4.0*epsilon
        + 15.0*math.pi*epsilon**2/4.0
    )


def second_order_coefficient_reciprocity() -> float:
    return 4.0*math.pi


def second_order_coefficient_schwarzschild() -> float:
    return 15.0*math.pi/4.0


def second_order_difference_coefficient() -> float:
    return math.pi/4.0


def one_sided_asymptotic_shift_series(epsilon: float) -> float:
    return 2.0*epsilon + 2.0*math.pi*epsilon**2


def exact_orbit_rhs(x: float, epsilon: float) -> float:
    """Right-hand side of x''+x = RHS."""
    return 2.0*epsilon*math.exp(4.0*epsilon*x)


def _validate(mu: float, impact_parameter: float) -> None:
    if mu < 0:
        raise ValueError("mu must be non-negative")
    if impact_parameter <= 0:
        raise ValueError("impact_parameter must be positive")
