"""Higher-order weak-field comparison with Schwarzschild in isotropic coordinates.

Let
    u = mu/r.

Reciprocity exponential metric:
    g_tt = -exp(-2u)
    g_spatial = exp(2u).

Schwarzschild metric in isotropic radius r:
    g_tt = -[(1-u/2)/(1+u/2)]^2
    g_spatial = (1+u/2)^4.

Series:

Reciprocity:
    g_tt = -1 + 2u - 2u^2 + (4/3)u^3 - (2/3)u^4 + ...
    g_sp = 1 + 2u + 2u^2 + (4/3)u^3 + (2/3)u^4 + ...

Schwarzschild:
    g_tt = -1 + 2u - 2u^2 + (3/2)u^3 - u^4 + ...
    g_sp = 1 + 2u + (3/2)u^2 + (1/2)u^3 + (1/16)u^4.

Thus:
- the standard 1PN coefficients beta=gamma=1 agree;
- the first spatial difference occurs at order u^2;
- the first temporal difference occurs at order u^3.

Using the common isotropic 2PN spatial parametrization

    g_ij = [1 + 2 gamma u + (3/2) delta u^2 + ...] delta_ij,

the exponential metric corresponds to

    delta = 4/3

while Schwarzschild/GR has

    delta = 1.

This module only states the metric-series comparison; it does not claim current
experiments exclude or confirm the value delta=4/3.
"""

from __future__ import annotations

import math


def exponential_gtt(u: float) -> float:
    return -math.exp(-2.0*u)


def exponential_spatial_factor(u: float) -> float:
    return math.exp(2.0*u)


def schwarzschild_isotropic_gtt(u: float) -> float:
    if abs(1.0 + 0.5*u) < 1e-15:
        raise ValueError("isotropic Schwarzschild denominator vanishes")
    return -((1.0 - 0.5*u)/(1.0 + 0.5*u))**2


def schwarzschild_isotropic_spatial_factor(u: float) -> float:
    return (1.0 + 0.5*u)**4


def exponential_series_coefficients() -> dict[str, tuple[float, ...]]:
    return {
        "gtt": (-1.0, 2.0, -2.0, 4.0/3.0, -2.0/3.0),
        "spatial": (1.0, 2.0, 2.0, 4.0/3.0, 2.0/3.0),
    }


def schwarzschild_series_coefficients() -> dict[str, tuple[float, ...]]:
    return {
        "gtt": (-1.0, 2.0, -2.0, 3.0/2.0, -1.0),
        "spatial": (1.0, 2.0, 3.0/2.0, 1.0/2.0, 1.0/16.0),
    }


def ppn_beta_gamma_exponential() -> tuple[float, float]:
    return 1.0, 1.0


def isotropic_2pn_delta_exponential() -> float:
    """Coefficient convention: spatial u^2 coefficient=(3/2) delta."""
    return 4.0/3.0


def isotropic_2pn_delta_schwarzschild() -> float:
    return 1.0


def leading_spatial_difference_coefficient() -> float:
    """Coefficient of u^2 in g_sp(exp)-g_sp(Schwarzschild)."""
    return 0.5


def leading_temporal_difference_coefficient() -> float:
    """Coefficient of u^3 in g_tt(exp)-g_tt(Schwarzschild)."""
    return -1.0/6.0
