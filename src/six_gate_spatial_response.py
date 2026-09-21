"""Six-gate symmetry constraints on spatial response.

The canonical boundary set

    B6 = {+X,-X,+Y,-Y,+Z,-Z}

has signed-permutation symmetry. Consider a linear infinitesimal spatial
response tensor R acting on the three axis directions.

If R commutes with:
- independent sign flips of X, Y, Z, and
- all permutations of X, Y, Z,

then R must be proportional to the identity.

Therefore any content-induced spatial response that preserves the full B6
symmetry has the isotropic form

    R = gamma_M * I

at linear order.

If spatial response also composes multiplicatively under additive scalar
potential increments,

    S(psi1 + psi2) = S(psi1) S(psi2),

continuity gives

    S(psi) = exp(gamma_M * psi).

The symmetry fixes isotropy, but not gamma_M itself.

This module makes that distinction executable.
"""

from __future__ import annotations

import itertools
import math
import numpy as np


def signed_permutation_matrices() -> list[np.ndarray]:
    """Return the 48 signed 3x3 permutation matrices."""
    matrices: list[np.ndarray] = []
    basis = np.eye(3)
    for perm in itertools.permutations(range(3)):
        p = basis[list(perm), :]
        for signs in itertools.product((-1.0, 1.0), repeat=3):
            s = np.diag(signs)
            matrices.append(s @ p)
    return matrices


SIGNED_PERMUTATIONS = signed_permutation_matrices()


def commutator(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a @ b - b @ a


def max_symmetry_commutator(response: np.ndarray) -> float:
    r = np.asarray(response, dtype=float)
    if r.shape != (3, 3):
        raise ValueError("response must be 3x3")
    return max(
        float(np.max(np.abs(commutator(r, g))))
        for g in SIGNED_PERMUTATIONS
    )


def preserves_b6_symmetry(
    response: np.ndarray,
    tolerance: float = 1e-12,
) -> bool:
    return max_symmetry_commutator(response) <= tolerance


def isotropic_projection(response: np.ndarray) -> np.ndarray:
    """Project a 3x3 response onto the B6-invariant scalar subspace."""
    r = np.asarray(response, dtype=float)
    if r.shape != (3, 3):
        raise ValueError("response must be 3x3")
    coefficient = float(np.trace(r)) / 3.0
    return coefficient * np.eye(3)


def symmetry_average(response: np.ndarray) -> np.ndarray:
    """Group-average a tensor over the 48 signed permutations."""
    r = np.asarray(response, dtype=float)
    if r.shape != (3, 3):
        raise ValueError("response must be 3x3")
    total = np.zeros((3, 3), dtype=float)
    for g in SIGNED_PERMUTATIONS:
        total += g @ r @ g.T
    return total / len(SIGNED_PERMUTATIONS)


def invariant_coefficient(response: np.ndarray) -> float:
    return float(np.trace(np.asarray(response, dtype=float))) / 3.0


def spatial_scale_factor(psi: float, gamma_matrix: float) -> float:
    """Multiplicative isotropic spatial scale under additive psi."""
    return math.exp(gamma_matrix * psi)


def spatial_metric_factor(psi: float, gamma_matrix: float) -> float:
    """Isotropic metric coefficient S^2."""
    s = spatial_scale_factor(psi, gamma_matrix)
    return s * s


def linearized_metric_response(psi: float, gamma_matrix: float) -> np.ndarray:
    """First-order isotropic spatial metric perturbation 2 gamma psi I."""
    return 2.0 * gamma_matrix * psi * np.eye(3)
