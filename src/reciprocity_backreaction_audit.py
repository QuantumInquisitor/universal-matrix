"""Backreaction audit for the reciprocity exponential metric.

Metric:
    g_tt = -c_*^2 exp(-2 psi)
    g_ij = exp(+2 psi) delta_ij

Then
    det(g) = -c_*^2 exp(4 psi)
    sqrt(-g) = c_* exp(2 psi)

and
    g^ij = exp(-2 psi) delta^ij.

Therefore
    sqrt(-g) g^ij = c_* delta^ij,

independent of psi.

For a static test scalar f on this prescribed geometry,

    box_g f
      = 1/sqrt(-g) * d_i(sqrt(-g) g^ij d_j f)
      = exp(-2 psi) * laplacian(f).

In particular, if f=psi is treated only as a test scalar on the already
specified metric, vacuum box_g psi=0 implies flat laplacian(psi)=0.

This does NOT complete a self-consistent scalar-gravity theory because varying
an action in which g=g(psi) produces additional dependence through the metric.
The module exists to mark that distinction explicitly.
"""

from __future__ import annotations

import math
import numpy as np


def metric_diagonal(psi: float, causal_speed: float = 1.0) -> np.ndarray:
    if causal_speed <= 0:
        raise ValueError("causal_speed must be positive")
    return np.array(
        [
            -causal_speed**2 * math.exp(-2.0 * psi),
            math.exp(2.0 * psi),
            math.exp(2.0 * psi),
            math.exp(2.0 * psi),
        ],
        dtype=float,
    )


def metric_determinant(psi: float, causal_speed: float = 1.0) -> float:
    if causal_speed <= 0:
        raise ValueError("causal_speed must be positive")
    return -causal_speed**2 * math.exp(4.0 * psi)


def sqrt_minus_g(psi: float, causal_speed: float = 1.0) -> float:
    if causal_speed <= 0:
        raise ValueError("causal_speed must be positive")
    return causal_speed * math.exp(2.0 * psi)


def inverse_spatial_factor(psi: float) -> float:
    return math.exp(-2.0 * psi)


def spatial_flux_prefactor(psi: float, causal_speed: float = 1.0) -> float:
    """sqrt(-g) * g^ii for any spatial diagonal component."""
    return sqrt_minus_g(psi, causal_speed) * inverse_spatial_factor(psi)


def static_covariant_box_from_flat_laplacian(
    psi_background: float,
    flat_laplacian_value: float,
) -> float:
    """box_g f for static f on the prescribed reciprocity background."""
    return math.exp(-2.0 * psi_background) * flat_laplacian_value


def temporal_flux_prefactor(psi: float, causal_speed: float = 1.0) -> float:
    """sqrt(-g) g^tt."""
    if causal_speed <= 0:
        raise ValueError("causal_speed must be positive")
    return -math.exp(4.0 * psi) / causal_speed
