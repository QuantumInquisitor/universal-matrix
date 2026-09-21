"""U(1) gauge field on the reciprocity metric.

Natural units c_*=1.

Metric:
    ds^2 = -exp(-2 psi) dt^2 + exp(2 psi) d x^2.

For Maxwell theory

    L = -1/4 sqrt(-g) F_{mu nu} F^{mu nu},

the coordinate-field form is

    L_EM
      = 1/2 exp(2 psi) |E|^2
        - 1/2 exp(-2 psi) |B|^2.

Canonical electric displacement:
    D = dL/dE = exp(2 psi) E.

Hamiltonian density:
    H_EM
      = 1/2 exp(-2 psi) (|D|^2 + |B|^2).

Geometry-source variation:
    dL_EM/dpsi
      = exp(2 psi)|E|^2
        + exp(-2 psi)|B|^2
      = exp(-2 psi)(|D|^2+|B|^2)
      = 2 H_EM.

This is the expected local active source rho + p_x+p_y+p_z for a traceless
Maxwell stress tensor.

For a uniform background psi, Hamilton's equations give gauge-wave coordinate
speed
    c_gauge = exp(-2 psi),

equal to the reciprocity metric null speed and the geometry-scalar
characteristic speed.

A free gauge field by itself is not a stationary localized isolated object.
For a stationary bound composite, confining/binding stresses must be included;
the total von Laue condition then restores integrated active-source = total
energy.
"""

from __future__ import annotations

import math
import numpy as np


def lagrangian_density(
    electric: np.ndarray,
    magnetic: np.ndarray,
    psi: float,
) -> float:
    e = np.asarray(electric, dtype=float)
    b = np.asarray(magnetic, dtype=float)
    return 0.5 * (
        math.exp(2.0*psi) * float(np.dot(e, e))
        - math.exp(-2.0*psi) * float(np.dot(b, b))
    )


def canonical_displacement(
    electric: np.ndarray,
    psi: float,
) -> np.ndarray:
    return math.exp(2.0*psi) * np.asarray(electric, dtype=float)


def electric_from_displacement(
    displacement: np.ndarray,
    psi: float,
) -> np.ndarray:
    return math.exp(-2.0*psi) * np.asarray(displacement, dtype=float)


def hamiltonian_density(
    displacement: np.ndarray,
    magnetic: np.ndarray,
    psi: float,
) -> float:
    d = np.asarray(displacement, dtype=float)
    b = np.asarray(magnetic, dtype=float)
    return 0.5 * math.exp(-2.0*psi) * (
        float(np.dot(d, d))
        + float(np.dot(b, b))
    )


def geometry_source_density_velocity_form(
    electric: np.ndarray,
    magnetic: np.ndarray,
    psi: float,
) -> float:
    e = np.asarray(electric, dtype=float)
    b = np.asarray(magnetic, dtype=float)
    return (
        math.exp(2.0*psi) * float(np.dot(e, e))
        + math.exp(-2.0*psi) * float(np.dot(b, b))
    )


def geometry_source_density_canonical(
    displacement: np.ndarray,
    magnetic: np.ndarray,
    psi: float,
) -> float:
    d = np.asarray(displacement, dtype=float)
    b = np.asarray(magnetic, dtype=float)
    return math.exp(-2.0*psi) * (
        float(np.dot(d, d))
        + float(np.dot(b, b))
    )


def gauge_characteristic_speed(psi: float) -> float:
    return math.exp(-2.0*psi)


def metric_null_speed(psi: float) -> float:
    return math.exp(-2.0*psi)


def geometry_scalar_characteristic_speed(psi: float) -> float:
    return math.exp(-2.0*psi)


def source_to_energy_ratio_for_free_gauge_field(
    displacement: np.ndarray,
    magnetic: np.ndarray,
    psi: float,
) -> float:
    h = hamiltonian_density(displacement, magnetic, psi)
    if h <= 0:
        raise ValueError("gauge energy must be positive")
    return (
        geometry_source_density_canonical(
            displacement,
            magnetic,
            psi,
        )
        / h
    )
