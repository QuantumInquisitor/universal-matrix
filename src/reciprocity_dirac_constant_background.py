"""Constant-psi Dirac bridge for the reciprocity metric.

For a spatially uniform reciprocity potential psi,

    ds^2 = -exp(-2 psi) dt^2 + exp(2 psi) d x^2,

the tetrad is constant and the spin connection vanishes.

With lapse
    N = exp(-psi)

and spatial scale
    a = exp(+psi),

the coordinate-time Dirac Hamiltonian is

    H_psi(p)
      = (N/a) alpha.p + N beta m

      = exp(-2 psi) alpha.p
        + exp(-psi) beta m.

The positive-energy dispersion is

    E_+(p,psi)
      = sqrt(
          exp(-4 psi) |p|^2
          + exp(-2 psi) m^2
        ).

Consequences:

- massless / ultrarelativistic coordinate group speed:
      c_coord = exp(-2 psi)

- rest coordinate energy:
      E_rest = m exp(-psi)

- local static-observer energy:
      E_local = E_coord / N

  so at p=0:
      E_local = m.

This module is a controlled constant-background correspondence bridge. A
spatially varying psi requires a position-dependent tetrad and spin connection
and is not implemented here.
"""

from __future__ import annotations

import math
import numpy as np

try:
    from .wilson_dirac_reference import ALPHA, BETA
except ImportError:
    from wilson_dirac_reference import ALPHA, BETA


def lapse(psi: float) -> float:
    return math.exp(-psi)


def spatial_scale(psi: float) -> float:
    return math.exp(psi)


def kinetic_speed_factor(psi: float) -> float:
    return math.exp(-2.0 * psi)


def mass_redshift_factor(psi: float) -> float:
    return math.exp(-psi)


def hamiltonian(
    momentum: tuple[float, float, float] | np.ndarray,
    mass: float,
    psi: float,
) -> np.ndarray:
    p = np.asarray(momentum, dtype=float)
    if p.shape != (3,):
        raise ValueError("momentum must have three components")
    if mass < 0:
        raise ValueError("mass must be non-negative")

    h = mass_redshift_factor(psi) * mass * BETA
    for axis in range(3):
        h = h + kinetic_speed_factor(psi) * p[axis] * ALPHA[axis]
    return h


def positive_energy(
    momentum: tuple[float, float, float] | np.ndarray,
    mass: float,
    psi: float,
) -> float:
    p = np.asarray(momentum, dtype=float)
    if p.shape != (3,):
        raise ValueError("momentum must have three components")
    if mass < 0:
        raise ValueError("mass must be non-negative")
    return math.sqrt(
        math.exp(-4.0 * psi) * float(np.dot(p, p))
        + math.exp(-2.0 * psi) * mass * mass
    )


def group_speed_magnitude(
    momentum_magnitude: float,
    mass: float,
    psi: float,
) -> float:
    if momentum_magnitude < 0 or mass < 0:
        raise ValueError("momentum and mass must be non-negative")
    if momentum_magnitude == 0:
        return 0.0

    energy = math.sqrt(
        math.exp(-4.0 * psi) * momentum_magnitude**2
        + math.exp(-2.0 * psi) * mass**2
    )
    return (
        math.exp(-4.0 * psi)
        * momentum_magnitude
        / energy
    )


def massless_group_speed(psi: float) -> float:
    return math.exp(-2.0 * psi)


def metric_null_coordinate_speed(psi: float) -> float:
    return math.exp(-2.0 * psi)


def rest_coordinate_energy(mass: float, psi: float) -> float:
    if mass < 0:
        raise ValueError("mass must be non-negative")
    return mass * math.exp(-psi)


def local_static_observer_energy(
    coordinate_energy: float,
    psi: float,
) -> float:
    return coordinate_energy / lapse(psi)


def rest_local_energy(mass: float, psi: float) -> float:
    return local_static_observer_energy(
        rest_coordinate_energy(mass, psi),
        psi,
    )


def geometry_source_from_stationary_total(
    total_rest_energy: float,
    integrated_spatial_stress: np.ndarray,
) -> float:
    """General stationary source T00 + trace(Tij), integrated.

    For a localized stationary spinor composite obeying the von Laue
    condition, integrated_spatial_stress vanishes and source=energy.
    """
    stress = np.asarray(integrated_spatial_stress, dtype=float)
    if stress.shape != (3, 3):
        raise ValueError("integrated_spatial_stress must be 3x3")
    return float(total_rest_energy + np.trace(stress))
