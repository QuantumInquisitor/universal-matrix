"""Finite-lattice Weyl operator and determinant diagnostics.

For an overlap Dirac operator D, take:
- a GW-modified right-handed or left-handed Weyl basis V spanning hat_P_chi;
- an ordinary barred chiral basis Vbar spanning Pbar_{-chi}.

The finite Weyl block is

    M = Vbar^dagger D V.

When the two chiral subspaces have equal rank, det(M) is defined.

Under internal basis changes

    V    -> V U
    Vbar -> Vbar Ubar,

the block transforms as

    M -> Ubar^dagger M U,

so

    det(M)
      -> det(Ubar)^* det(M) det(U).

Therefore:
- |det(M)| is basis independent;
- the determinant phase is NOT basis independent by itself;
- a chiral fermion measure prescription is required to fix the physical phase.

This module makes that basis-phase issue explicit. It does not claim anomaly
cancellation.
"""

from __future__ import annotations

import cmath
import math
import numpy as np

try:
    from .u1_overlap_dirac_lattice import (
        gamma5_lattice,
        overlap_dirac_matrix,
    )
    from .weyl_measure_curvature import weyl_basis
except ImportError:
    from u1_overlap_dirac_lattice import (
        gamma5_lattice,
        overlap_dirac_matrix,
    )
    from weyl_measure_curvature import weyl_basis


def ordinary_chiral_basis(
    shape: tuple[int, int, int, int],
    chirality: int = 1,
    tolerance: float = 1e-10,
) -> np.ndarray:
    """Deterministic orthonormal basis of ordinary gamma5 chirality."""
    if chirality not in (-1, 1):
        raise ValueError("chirality must be -1 or +1")
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")

    g5 = gamma5_lattice(shape)
    values, vectors = np.linalg.eigh(g5)
    selected = np.abs(values - chirality) <= tolerance

    if not np.any(selected):
        raise ValueError("requested ordinary chiral subspace is empty")
    return vectors[:, selected]


def weyl_operator_matrix(
    dirac: np.ndarray,
    right_basis: np.ndarray,
    barred_basis: np.ndarray,
) -> np.ndarray:
    d = np.asarray(dirac, dtype=complex)
    v = np.asarray(right_basis, dtype=complex)
    vb = np.asarray(barred_basis, dtype=complex)

    if d.ndim != 2 or d.shape[0] != d.shape[1]:
        raise ValueError("dirac must be square")
    if v.ndim != 2 or vb.ndim != 2:
        raise ValueError("bases must be matrices")
    if v.shape[0] != d.shape[0] or vb.shape[0] != d.shape[0]:
        raise ValueError("basis dimensions must match dirac dimension")

    return vb.conj().T @ d @ v


def u1_overlap_weyl_matrix(
    links: np.ndarray,
    chirality: int = -1,
    rho: float = 1.0,
    wilson_r: float = 1.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (M,V,Vbar) for a compact-U(1) overlap Weyl block.

    The barred basis uses ordinary chirality -chirality.
    """
    if chirality not in (-1, 1):
        raise ValueError("chirality must be -1 or +1")

    a = np.asarray(links, dtype=float)
    shape = a.shape[1:]
    if a.ndim != 5 or a.shape[0] != 4 or len(shape) != 4:
        raise ValueError("links must have shape (4,n0,n1,n2,n3)")

    d = overlap_dirac_matrix(
        a,
        rho=rho,
        wilson_r=wilson_r,
    )
    right = weyl_basis(
        a,
        chirality=chirality,
        rho=rho,
        wilson_r=wilson_r,
    )
    barred = ordinary_chiral_basis(
        shape,
        chirality=-chirality,
    )
    matrix = weyl_operator_matrix(
        d,
        right,
        barred,
    )
    return matrix, right, barred


def determinant_if_square(matrix: np.ndarray) -> complex:
    m = np.asarray(matrix, dtype=complex)
    if m.ndim != 2:
        raise ValueError("matrix must be two-dimensional")
    if m.shape[0] != m.shape[1]:
        raise ValueError(
            "Weyl block is rectangular; determinant requires equal chiral ranks"
        )
    return complex(np.linalg.det(m))


def log_determinant_magnitude(matrix: np.ndarray) -> float:
    """Stable log |det M| for a square nonsingular Weyl block."""
    m = np.asarray(matrix, dtype=complex)
    if m.ndim != 2 or m.shape[0] != m.shape[1]:
        raise ValueError("matrix must be square")

    sign, logabs = np.linalg.slogdet(m)
    if sign == 0:
        return -math.inf
    return float(logabs)


def determinant_phase(matrix: np.ndarray) -> float:
    det = determinant_if_square(matrix)
    if det == 0:
        raise ValueError("determinant phase undefined for singular matrix")
    phase = cmath.phase(det)
    if phase <= -math.pi:
        return math.pi
    return float(phase)


def basis_rotation_prediction(
    determinant: complex,
    right_unitary: np.ndarray,
    barred_unitary: np.ndarray,
) -> complex:
    """Predicted determinant after V->VU, Vbar->Vbar Ubar."""
    ur = np.asarray(right_unitary, dtype=complex)
    ub = np.asarray(barred_unitary, dtype=complex)
    if (
        ur.ndim != 2
        or ub.ndim != 2
        or ur.shape[0] != ur.shape[1]
        or ub.shape[0] != ub.shape[1]
    ):
        raise ValueError("basis rotations must be square")
    return (
        np.conj(np.linalg.det(ub))
        * determinant
        * np.linalg.det(ur)
    )


def rotated_weyl_matrix(
    matrix: np.ndarray,
    right_unitary: np.ndarray,
    barred_unitary: np.ndarray,
) -> np.ndarray:
    m = np.asarray(matrix, dtype=complex)
    ur = np.asarray(right_unitary, dtype=complex)
    ub = np.asarray(barred_unitary, dtype=complex)

    if m.shape[1] != ur.shape[0] or ur.shape[0] != ur.shape[1]:
        raise ValueError("right rotation shape mismatch")
    if m.shape[0] != ub.shape[0] or ub.shape[0] != ub.shape[1]:
        raise ValueError("barred rotation shape mismatch")

    return ub.conj().T @ m @ ur


def determinant_basis_covariance_residual(
    matrix: np.ndarray,
    right_unitary: np.ndarray,
    barred_unitary: np.ndarray,
) -> complex:
    det = determinant_if_square(matrix)
    rotated = rotated_weyl_matrix(
        matrix,
        right_unitary,
        barred_unitary,
    )
    actual = determinant_if_square(rotated)
    predicted = basis_rotation_prediction(
        det,
        right_unitary,
        barred_unitary,
    )
    return actual - predicted


def determinant_magnitude_basis_residual(
    matrix: np.ndarray,
    right_unitary: np.ndarray,
    barred_unitary: np.ndarray,
) -> float:
    original = abs(determinant_if_square(matrix))
    rotated = abs(
        determinant_if_square(
            rotated_weyl_matrix(
                matrix,
                right_unitary,
                barred_unitary,
            )
        )
    )
    return float(rotated - original)
