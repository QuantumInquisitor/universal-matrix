"""Clock-space reciprocity and the resulting exponential effective metric.

Inputs already established in the experimental extension:
- clock-rate ratio N(psi) = exp(-psi)
- B6 symmetry -> isotropic spatial response S(psi)=exp(gamma_M*psi)

Additional reciprocity postulate:
A local canonical propagation event remains one responded spatial link per one
responded canonical tick, so the locally measured causal speed is independent
of psi.

Then
    v_local / v_ref = S / L_t
where L_t=exp(psi) is the tick-duration lapse.

Thus
    exp((gamma_M - 1)*psi) = 1
for arbitrary psi, forcing
    gamma_M = 1.

The corresponding static isotropic effective line element is

    ds^2 = -exp(-2 psi) c_*^2 dt^2
           + exp(+2 psi) (dx^2+dy^2+dz^2).

This metric form is historically known as an exponential metric. The module
does not claim novelty for the metric itself and does not assert that it is the
physical spacetime metric of nature.

Weak-field expansion:
    g_00 = -1 + 2 psi - 2 psi^2 + O(psi^3)
    g_ij = (1 + 2 psi + O(psi^2)) delta_ij

which corresponds to PPN beta=1 and gamma=1 at the displayed orders when psi
is identified with the positive Newtonian-potential magnitude U/c^2.
"""

from __future__ import annotations

import math
from typing import Sequence
import numpy as np


def tick_duration_lapse(psi: float) -> float:
    return math.exp(psi)


def clock_rate_ratio(psi: float) -> float:
    return math.exp(-psi)


def spatial_scale(psi: float, gamma_matrix: float) -> float:
    return math.exp(gamma_matrix * psi)


def local_causal_speed_ratio(psi: float, gamma_matrix: float) -> float:
    """Responded link length divided by responded tick duration."""
    return spatial_scale(psi, gamma_matrix) / tick_duration_lapse(psi)


def reciprocity_gamma() -> float:
    """Unique coefficient preserving local causal speed for arbitrary psi."""
    return 1.0


def reciprocity_metric_diagonal(
    psi: float,
    causal_speed: float = 1.0,
) -> np.ndarray:
    if causal_speed <= 0:
        raise ValueError("causal_speed must be positive")
    return np.array(
        [
            -(causal_speed**2) * math.exp(-2.0 * psi),
            math.exp(2.0 * psi),
            math.exp(2.0 * psi),
            math.exp(2.0 * psi),
        ],
        dtype=float,
    )


def optical_index(psi: float) -> float:
    """Static isotropic null travel-time index S/N = exp(2 psi)."""
    return math.exp(2.0 * psi)


def weak_field_ppn_parameters() -> tuple[float, float]:
    """Return (beta, gamma) from the exponential metric Taylor coefficients."""
    return 1.0, 1.0


def weak_massive_acceleration(
    grad_psi: Sequence[float],
    causal_speed: float = 1.0,
) -> np.ndarray:
    """Newtonian-order geodesic acceleration a = c_*^2 grad(psi).

    With psi=mu/r > 0, grad(psi) points toward the source.
    """
    if causal_speed <= 0:
        raise ValueError("causal_speed must be positive")
    return causal_speed**2 * np.asarray(grad_psi, dtype=float)


def point_source_light_deflection(
    mu: float,
    impact_parameter: float,
) -> float:
    """Weak leading deflection for psi=mu/r under reciprocity."""
    if mu < 0:
        raise ValueError("mu must be non-negative")
    if impact_parameter <= 0:
        raise ValueError("impact_parameter must be positive")
    return 4.0 * mu / impact_parameter
