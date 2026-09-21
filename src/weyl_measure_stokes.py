"""Local curvature versus small-loop Weyl measure holonomy.

The projector formulation gives the local chiral measure curvature

    F_ab = i Tr(P [partial_a P, partial_b P]).

The discrete transport formulation gives a closed-loop determinant phase

    Theta = arg det(H).

For a sufficiently small positively oriented rectangular loop with side
parameters da and db,

    Theta = F_ab * da * db + higher-order terms

for the transport orientation used in this repository.

This module compares those independently constructed quantities. Agreement in
the shrinking-loop limit is a discrete Stokes consistency check. It does not
constitute an anomaly-cancellation theorem.
"""

from __future__ import annotations

import math
import numpy as np

try:
    from .weyl_measure_curvature import measure_curvature
    from .weyl_measure_holonomy import (
        closed_loop_measure_phase,
        principal_phase_difference,
        rectangular_link_loop,
    )
except ImportError:
    from weyl_measure_curvature import measure_curvature
    from weyl_measure_holonomy import (
        closed_loop_measure_phase,
        principal_phase_difference,
        rectangular_link_loop,
    )


def curvature_flux(
    links: np.ndarray,
    direction_a: np.ndarray,
    direction_b: np.ndarray,
    side_a: float,
    side_b: float,
    chirality: int = -1,
    rho: float = 1.0,
    wilson_r: float = 1.0,
    derivative_epsilon: float = 1e-5,
) -> float:
    curvature = measure_curvature(
        links,
        direction_a,
        direction_b,
        chirality=chirality,
        rho=rho,
        wilson_r=wilson_r,
        epsilon=derivative_epsilon,
    )
    return curvature * side_a * side_b


def rectangular_holonomy_phase(
    links: np.ndarray,
    direction_a: np.ndarray,
    direction_b: np.ndarray,
    side_a: float,
    side_b: float,
    chirality: int = -1,
    rho: float = 1.0,
    wilson_r: float = 1.0,
) -> float:
    loop = rectangular_link_loop(
        links,
        direction_a,
        direction_b,
        side_a,
        side_b,
    )
    return closed_loop_measure_phase(
        loop,
        chirality=chirality,
        rho=rho,
        wilson_r=wilson_r,
    )


def stokes_phase_residual(
    links: np.ndarray,
    direction_a: np.ndarray,
    direction_b: np.ndarray,
    side_a: float,
    side_b: float,
    chirality: int = -1,
    rho: float = 1.0,
    wilson_r: float = 1.0,
    derivative_epsilon: float = 1e-5,
) -> float:
    """Wrapped Theta_loop - F_ab*area."""
    phase = rectangular_holonomy_phase(
        links,
        direction_a,
        direction_b,
        side_a,
        side_b,
        chirality,
        rho,
        wilson_r,
    )
    flux = curvature_flux(
        links,
        direction_a,
        direction_b,
        side_a,
        side_b,
        chirality,
        rho,
        wilson_r,
        derivative_epsilon,
    )
    return principal_phase_difference(
        phase,
        flux,
    )


def normalized_stokes_residual(
    links: np.ndarray,
    direction_a: np.ndarray,
    direction_b: np.ndarray,
    side_a: float,
    side_b: float,
    chirality: int = -1,
    rho: float = 1.0,
    wilson_r: float = 1.0,
    derivative_epsilon: float = 1e-5,
) -> float:
    area = abs(side_a * side_b)
    if area == 0:
        raise ValueError("rectangle area must be nonzero")
    return stokes_phase_residual(
        links,
        direction_a,
        direction_b,
        side_a,
        side_b,
        chirality,
        rho,
        wilson_r,
        derivative_epsilon,
    ) / area


def shrinking_loop_diagnostics(
    links: np.ndarray,
    direction_a: np.ndarray,
    direction_b: np.ndarray,
    sizes: tuple[float, ...],
    chirality: int = -1,
    rho: float = 1.0,
    wilson_r: float = 1.0,
    derivative_epsilon: float = 1e-5,
) -> list[dict[str, float]]:
    if not sizes:
        raise ValueError("sizes must be non-empty")
    if any(size <= 0 for size in sizes):
        raise ValueError("loop sizes must be positive")

    curvature = measure_curvature(
        links,
        direction_a,
        direction_b,
        chirality=chirality,
        rho=rho,
        wilson_r=wilson_r,
        epsilon=derivative_epsilon,
    )

    out = []
    for size in sizes:
        phase = rectangular_holonomy_phase(
            links,
            direction_a,
            direction_b,
            size,
            size,
            chirality,
            rho,
            wilson_r,
        )
        flux = curvature * size * size
        residual = principal_phase_difference(
            phase,
            flux,
        )
        out.append(
            {
                "size": size,
                "area": size * size,
                "curvature": curvature,
                "phase": phase,
                "curvature_flux": flux,
                "residual": residual,
                "residual_per_area": residual / (size * size),
            }
        )
    return out
