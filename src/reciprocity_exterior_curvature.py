"""Exact curvature diagnostics for the reciprocity exponential exterior.

Metric in isotropic spherical coordinates:

    ds^2
      = -exp(-2 mu/r) dt^2
        + exp(2 mu/r)
          [dr^2 + r^2 dOmega^2].

The exact Ricci tensor has only one nonzero coordinate component:

    R_rr = -2 mu^2 / r^4.

The Ricci scalar is

    R
      = -2 mu^2 exp(-2 mu/r) / r^4.

Ricci-tensor square:

    R_{mu nu} R^{mu nu}
      = 4 mu^4 exp(-4 mu/r) / r^8.

Kretschmann scalar:

    R_{abcd} R^{abcd}
      = 4 mu^2
        (7 mu^2 - 16 mu r + 12 r^2)
        exp(-4 mu/r)
        / r^8.

Therefore the exterior is not Ricci-flat for finite r and mu != 0, even
though psi=mu/r solves the scalar vacuum equation laplacian psi=0.

This is not a contradiction because the proposed theory does not impose the
Einstein vacuum equation G_{mu nu}=0. It is a direct way to distinguish the
reciprocity scalar geometry from GR vacuum geometry.

At large r:
    K ~ 48 mu^2/r^6 + higher orders,

matching the leading Schwarzschild Kretschmann scaling, while the Ricci scalar
remains nonzero at second order:
    R ~ -2 mu^2/r^4 + ...

At r -> 0+, the exponential suppression dominates all inverse powers and these
curvature invariants tend to zero.
"""

from __future__ import annotations

import math


def ricci_rr(radius: float, mu: float) -> float:
    _validate(radius, mu)
    return -2.0 * mu**2 / radius**4


def ricci_scalar(radius: float, mu: float) -> float:
    _validate(radius, mu)
    return (
        -2.0
        * mu**2
        * math.exp(-2.0 * mu / radius)
        / radius**4
    )


def ricci_tensor_square(radius: float, mu: float) -> float:
    _validate(radius, mu)
    return (
        4.0
        * mu**4
        * math.exp(-4.0 * mu / radius)
        / radius**8
    )


def kretschmann_scalar(radius: float, mu: float) -> float:
    _validate(radius, mu)
    polynomial = (
        7.0 * mu**2
        - 16.0 * mu * radius
        + 12.0 * radius**2
    )
    return (
        4.0
        * mu**2
        * polynomial
        * math.exp(-4.0 * mu / radius)
        / radius**8
    )


def schwarzschild_kretschmann(radius_areal: float, mu: float) -> float:
    """GR Schwarzschild reference in areal radius R: K=48 mu^2/R^6."""
    if radius_areal <= 0:
        raise ValueError("radius_areal must be positive")
    if mu < 0:
        raise ValueError("mu must be non-negative")
    return 48.0 * mu**2 / radius_areal**6


def leading_large_radius_kretschmann(radius: float, mu: float) -> float:
    _validate(radius, mu)
    return 48.0 * mu**2 / radius**6


def einstein_tensor_coordinate_diagonal(
    radius: float,
    mu: float,
    theta: float,
) -> tuple[float, float, float, float]:
    """Coordinate components (G_tt,G_rr,G_thth,G_phph), c_*=1."""
    _validate(radius, mu)
    return (
        -mu**2 * math.exp(-4.0 * mu / radius) / radius**4,
        -mu**2 / radius**4,
        mu**2 / radius**2,
        mu**2 * math.sin(theta)**2 / radius**2,
    )


def is_ricci_flat(
    radius: float,
    mu: float,
    tolerance: float = 1e-15,
) -> bool:
    return abs(ricci_scalar(radius, mu)) <= tolerance and abs(
        ricci_rr(radius, mu)
    ) <= tolerance


def _validate(radius: float, mu: float) -> None:
    if radius <= 0:
        raise ValueError("radius must be positive")
    if mu < 0:
        raise ValueError("mu must be non-negative")
