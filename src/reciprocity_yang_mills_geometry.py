"""Generic Yang-Mills gauge sector on the reciprocity geometry.

For a compact gauge group with adjoint index a, the classical action is

    L_YM = -1/4 sqrt(-g) F^a_{mu nu} F^{a mu nu}.

On the reciprocity metric

    ds^2 = -exp(-2 psi) dt^2 + exp(2 psi) d x^2,

the local color-electric and color-magnetic form is

    L_YM
      = 1/2 exp(2 psi) sum_a |E_a|^2
        - 1/2 exp(-2 psi) sum_a |B_a|^2.

Canonical displacement for each adjoint component:

    D_a = exp(2 psi) E_a.

Hamiltonian:

    H_YM
      = 1/2 exp(-2 psi)
        sum_a (|D_a|^2 + |B_a|^2).

Geometry-source variation:

    dL_YM/dpsi
      = exp(-2 psi)
        sum_a (|D_a|^2 + |B_a|^2)
      = 2 H_YM.

The principal propagation cone is therefore the same as the U(1) case:

    c_YM = exp(-2 psi).

This module treats the spacetime/metric coupling only. It does not implement
the non-Abelian commutator dynamics, structure constants, or lattice electric
Gauss law.
"""

from __future__ import annotations

import math
import numpy as np


def _validate_components(field: np.ndarray) -> np.ndarray:
    a = np.asarray(field, dtype=float)
    if a.ndim != 2 or a.shape[1] != 3:
        raise ValueError(
            "field must have shape (adjoint_components, 3)"
        )
    return a


def lagrangian_density(
    electric_components: np.ndarray,
    magnetic_components: np.ndarray,
    psi: float,
) -> float:
    e = _validate_components(electric_components)
    b = _validate_components(magnetic_components)
    if e.shape != b.shape:
        raise ValueError("electric and magnetic shapes must match")
    return 0.5 * (
        math.exp(2.0*psi) * float(np.sum(e*e))
        - math.exp(-2.0*psi) * float(np.sum(b*b))
    )


def canonical_displacement(
    electric_components: np.ndarray,
    psi: float,
) -> np.ndarray:
    e = _validate_components(electric_components)
    return math.exp(2.0*psi) * e


def electric_from_displacement(
    displacement_components: np.ndarray,
    psi: float,
) -> np.ndarray:
    d = _validate_components(displacement_components)
    return math.exp(-2.0*psi) * d


def hamiltonian_density(
    displacement_components: np.ndarray,
    magnetic_components: np.ndarray,
    psi: float,
) -> float:
    d = _validate_components(displacement_components)
    b = _validate_components(magnetic_components)
    if d.shape != b.shape:
        raise ValueError("displacement and magnetic shapes must match")
    return 0.5 * math.exp(-2.0*psi) * float(
        np.sum(d*d) + np.sum(b*b)
    )


def geometry_source_density(
    displacement_components: np.ndarray,
    magnetic_components: np.ndarray,
    psi: float,
) -> float:
    d = _validate_components(displacement_components)
    b = _validate_components(magnetic_components)
    if d.shape != b.shape:
        raise ValueError("displacement and magnetic shapes must match")
    return math.exp(-2.0*psi) * float(
        np.sum(d*d) + np.sum(b*b)
    )


def characteristic_speed(psi: float) -> float:
    return math.exp(-2.0*psi)


def source_energy_ratio(
    displacement_components: np.ndarray,
    magnetic_components: np.ndarray,
    psi: float,
) -> float:
    energy = hamiltonian_density(
        displacement_components,
        magnetic_components,
        psi,
    )
    if energy <= 0:
        raise ValueError("Yang-Mills energy must be positive")
    return (
        geometry_source_density(
            displacement_components,
            magnetic_components,
            psi,
        )
        / energy
    )


def adjoint_dimension_su(n: int) -> int:
    if n < 2:
        raise ValueError("SU(n) requires n>=2")
    return n*n - 1
