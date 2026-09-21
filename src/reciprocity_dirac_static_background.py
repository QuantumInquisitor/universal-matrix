"""Static spatially varying Dirac operator on the reciprocity metric.

For a static isotropic metric written as

    ds^2 = -V(x)^2 dt^2 + W(x)^2 d x^2,

the exact Hermitian Dirac Hamiltonian in the standard rescaled representation
is

    H = beta m V + 1/2 {alpha.p, F},

where

    F = V/W.

For the reciprocity metric,

    V = exp(-psi)
    W = exp(+psi)
    F = exp(-2 psi).

Therefore

    H
      = beta m exp(-psi)
        + 1/2 {alpha.p, exp(-2 psi)}.

Expanding the anticommutator gives

    H
      = beta m exp(-psi)
        - i alpha.[
            F grad + (1/2) grad F
          ].

The grad(F) contribution is the static geometry/spin-connection term in this
Hermitian representation.

This module discretizes p_i with the periodic central Hermitian difference

    p_i psi(x)
      = -i [psi(x+i)-psi(x-i)]/2

and evaluates the anticommutator directly. This preserves Hermiticity on the
finite periodic lattice up to floating arithmetic.

It is a curved-background single-particle Dirac operator, not a
second-quantized fermion theory.
"""

from __future__ import annotations

import numpy as np

try:
    from .wilson_dirac_reference import ALPHA, BETA
except ImportError:
    from wilson_dirac_reference import ALPHA, BETA


AXES = (0, 1, 2)


def lapse_field(psi: np.ndarray) -> np.ndarray:
    return np.exp(-np.asarray(psi, dtype=float))


def spatial_scale_field(psi: np.ndarray) -> np.ndarray:
    return np.exp(np.asarray(psi, dtype=float))


def kinetic_factor_field(psi: np.ndarray) -> np.ndarray:
    return np.exp(-2.0 * np.asarray(psi, dtype=float))


def central_momentum(
    spinor: np.ndarray,
    axis: int,
    spacing: float = 1.0,
) -> np.ndarray:
    field = np.asarray(spinor, dtype=complex)
    if field.ndim != 4 or field.shape[-1] != 4:
        raise ValueError("spinor must have shape (nx,ny,nz,4)")
    if axis not in AXES:
        raise ValueError("axis must be 0,1,2")
    if spacing <= 0:
        raise ValueError("spacing must be positive")

    forward = np.roll(field, -1, axis=axis)
    backward = np.roll(field, 1, axis=axis)
    return -1j * (forward - backward) / (2.0 * spacing)


def apply_static_reciprocity_dirac(
    spinor: np.ndarray,
    psi: np.ndarray,
    mass: float,
    spacing: float = 1.0,
) -> np.ndarray:
    field = np.asarray(spinor, dtype=complex)
    potential = np.asarray(psi, dtype=float)
    shape = field.shape[:3]

    if field.shape != shape + (4,):
        raise ValueError("spinor must have shape (nx,ny,nz,4)")
    if potential.shape != shape:
        raise ValueError("psi shape must match spinor spatial shape")
    if mass < 0:
        raise ValueError("mass must be non-negative")
    if spacing <= 0:
        raise ValueError("spacing must be positive")

    v = lapse_field(potential)
    f = kinetic_factor_field(potential)

    out = mass * v[..., None] * np.einsum(
        "ab,...b->...a",
        BETA,
        field,
    )

    for axis in AXES:
        p_field = central_momentum(field, axis, spacing)
        p_f_field = central_momentum(
            f[..., None] * field,
            axis,
            spacing,
        )
        anticommutator = 0.5 * (
            p_f_field + f[..., None] * p_field
        )
        out += np.einsum(
            "ab,...b->...a",
            ALPHA[axis],
            anticommutator,
        )

    return out


def inner_product(a: np.ndarray, b: np.ndarray) -> complex:
    return np.vdot(
        np.asarray(a, dtype=complex),
        np.asarray(b, dtype=complex),
    )


def local_principal_speed(psi: np.ndarray | float) -> np.ndarray:
    return np.exp(-2.0 * np.asarray(psi, dtype=float))


def metric_null_coordinate_speed(
    psi: np.ndarray | float,
) -> np.ndarray:
    return np.exp(-2.0 * np.asarray(psi, dtype=float))


def gradient_connection_factor(
    psi: np.ndarray,
    axis: int,
    spacing: float = 1.0,
) -> np.ndarray:
    """Continuum-limit coefficient (1/2) d_i F for diagnostics."""
    f = kinetic_factor_field(psi)
    return (
        np.roll(f, -1, axis=axis)
        - np.roll(f, 1, axis=axis)
    ) / (4.0 * spacing)
