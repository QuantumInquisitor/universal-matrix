"""Weak-field clock/spatial-response consistency bridge.

Let psi > 0 denote the dimensionless weak content potential near a positive
source, chosen so the modeled clock-rate ratio is

    r_local / r_ref = exp(-psi) ~= 1 - psi.

Introduce an independent spatial-response coefficient gamma_M:

    spatial_scale = exp(gamma_M * psi).

For null propagation in the resulting static isotropic clock/space response,
the coordinate travel-time index is

    n = spatial_scale / clock_rate_ratio
      = exp((1 + gamma_M) * psi).

For a point source

    psi(r) = mu / r,

the leading small-angle deflection at impact parameter b is

    alpha = 2 * (1 + gamma_M) * mu / b.

Thus:
    gamma_M = 0 -> clock-only scalar result, alpha = 2 mu/b
    gamma_M = 1 -> alpha = 4 mu/b

This mirrors the PPN structure in which gamma measures the spatial-curvature
contribution to light deflection.

The module is a correspondence diagnostic. It does not derive gamma_M=1.
"""

from __future__ import annotations

import math


def clock_rate_ratio_from_psi(psi: float) -> float:
    return math.exp(-psi)


def spatial_scale_factor(psi: float, gamma_matrix: float) -> float:
    return math.exp(gamma_matrix * psi)


def optical_index_from_psi(psi: float, gamma_matrix: float) -> float:
    return math.exp((1.0 + gamma_matrix) * psi)


def point_source_deflection(
    mu: float,
    impact_parameter: float,
    gamma_matrix: float,
) -> float:
    """Leading weak-field deflection for psi=mu/r."""
    if mu < 0:
        raise ValueError("mu must be non-negative")
    if impact_parameter <= 0:
        raise ValueError("impact_parameter must be positive")
    return (
        2.0
        * (1.0 + gamma_matrix)
        * mu
        / impact_parameter
    )


def effective_ppn_gamma(gamma_matrix: float) -> float:
    """The Matrix spatial-response coefficient maps directly to PPN gamma here."""
    return gamma_matrix


def gamma_deviation(gamma_matrix: float) -> float:
    return gamma_matrix - 1.0


def satisfies_gamma_bound(
    gamma_matrix: float,
    central_deviation: float,
    one_sigma_uncertainty: float,
    sigma: float = 1.0,
) -> bool:
    """Check gamma_M-1 against an externally supplied experimental interval."""
    if one_sigma_uncertainty < 0:
        raise ValueError("uncertainty must be non-negative")
    if sigma < 0:
        raise ValueError("sigma must be non-negative")
    deviation = gamma_deviation(gamma_matrix)
    lo = central_deviation - sigma * one_sigma_uncertainty
    hi = central_deviation + sigma * one_sigma_uncertainty
    return lo <= deviation <= hi
