"""Conditional uniqueness of the reciprocity exponential metric.

This module isolates the assumptions that lead to the static isotropic metric

    ds^2 = -exp(-2 psi) c_*^2 dt^2
           + exp(+2 psi) d x^2.

Assumptions:

A1. Spatial response preserves full B6 signed-permutation symmetry.
    Therefore the spatial response is isotropic:
        h_ij = S(psi)^2 delta_ij.

A2. Scalar potential increments compose additively and spatial response
    composes multiplicatively:
        S(psi1 + psi2) = S(psi1) S(psi2),
        S(0)=1,
    with continuity.
    Therefore:
        S(psi) = exp(gamma psi).

A3. The local clock-rate ratio is
        N(psi) = exp(-psi),
    so the local tick-duration lapse is
        L_t = exp(+psi).

A4. One local causal propagation unit remains one responded spatial unit per
    one responded local tick, so
        S(psi)/L_t(psi) = 1
    for arbitrary psi.

Then gamma=1 and
    S(psi)=exp(psi).

The result is unique only conditional on A1-A4. The canonical finite kernel by
itself does not prove A2-A4 as physical laws.
"""

from __future__ import annotations

import math
import numpy as np


def clock_rate_ratio(psi: float) -> float:
    return math.exp(-psi)


def tick_duration_lapse(psi: float) -> float:
    return 1.0 / clock_rate_ratio(psi)


def multiplicative_spatial_scale(
    psi: float,
    gamma: float,
) -> float:
    return math.exp(gamma * psi)


def local_causal_speed_ratio(
    psi: float,
    gamma: float,
) -> float:
    return multiplicative_spatial_scale(
        psi,
        gamma,
    ) / tick_duration_lapse(psi)


def gamma_from_local_causal_invariance() -> float:
    """Unique exponential-response coefficient satisfying A4 for all psi."""
    return 1.0


def reciprocity_spatial_scale(psi: float) -> float:
    return math.exp(psi)


def reciprocity_metric_diagonal(
    psi: float,
    causal_speed: float = 1.0,
) -> np.ndarray:
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


def composition_residual(
    psi1: float,
    psi2: float,
    gamma: float,
) -> float:
    return (
        multiplicative_spatial_scale(
            psi1 + psi2,
            gamma,
        )
        - multiplicative_spatial_scale(psi1, gamma)
        * multiplicative_spatial_scale(psi2, gamma)
    )


def b6_invariant_metric(
    spatial_scale: float,
) -> np.ndarray:
    """Return the unique isotropic 3-metric for a chosen scale factor."""
    if spatial_scale <= 0:
        raise ValueError("spatial_scale must be positive")
    return spatial_scale**2 * np.eye(3)


def isotropic_under_signed_permutations(
    spatial_metric: np.ndarray,
    tolerance: float = 1e-12,
) -> bool:
    h = np.asarray(spatial_metric, dtype=float)
    if h.shape != (3, 3):
        raise ValueError("spatial_metric must be 3x3")

    basis = np.eye(3)
    import itertools

    for perm in itertools.permutations(range(3)):
        p = basis[list(perm), :]
        for signs in itertools.product((-1.0, 1.0), repeat=3):
            g = np.diag(signs) @ p
            if not np.allclose(
                g @ h @ g.T,
                h,
                atol=tolerance,
                rtol=0,
            ):
                return False
    return True
