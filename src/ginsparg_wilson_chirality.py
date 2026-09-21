"""Ginsparg-Wilson chirality and index diagnostics.

For a lattice Dirac operator D obeying

    gamma5 D + D gamma5 = (1/rho) D gamma5 D

and gamma5 Hermiticity,

    D^dagger = gamma5 D gamma5,

define the modified chirality operator

    hat_gamma5 = gamma5 (I - D/rho).

The Ginsparg-Wilson relation implies

    hat_gamma5^dagger = hat_gamma5
    hat_gamma5^2 = I.

Therefore

    hat_P_plus  = (I + hat_gamma5)/2
    hat_P_minus = (I - hat_gamma5)/2

are exact orthogonal projectors on an admissible finite lattice.

For finite matrices with Tr(gamma5)=0, the overlap index can be written as

    index(D)
      = (1/2) Tr(hat_gamma5)
      = Tr[gamma5 (I - D/(2 rho))].

This module is algebraic. It does not construct the fermion measure, Weyl
determinant, or anomaly-cancellation conditions.
"""

from __future__ import annotations

import numpy as np


def _validate(
    dirac: np.ndarray,
    gamma5: np.ndarray,
    rho: float,
) -> tuple[np.ndarray, np.ndarray]:
    d = np.asarray(dirac, dtype=complex)
    g5 = np.asarray(gamma5, dtype=complex)

    if d.ndim != 2 or d.shape[0] != d.shape[1]:
        raise ValueError("dirac must be a square matrix")
    if g5.shape != d.shape:
        raise ValueError("gamma5 shape must match dirac")
    if rho <= 0:
        raise ValueError("rho must be positive")
    return d, g5


def modified_gamma5(
    dirac: np.ndarray,
    gamma5: np.ndarray,
    rho: float,
) -> np.ndarray:
    d, g5 = _validate(dirac, gamma5, rho)
    identity = np.eye(d.shape[0], dtype=complex)
    return g5 @ (identity - d / rho)


def chiral_projectors(
    dirac: np.ndarray,
    gamma5: np.ndarray,
    rho: float,
) -> tuple[np.ndarray, np.ndarray]:
    gh = modified_gamma5(dirac, gamma5, rho)
    identity = np.eye(gh.shape[0], dtype=complex)
    return (
        0.5 * (identity + gh),
        0.5 * (identity - gh),
    )


def modified_gamma5_hermiticity_residual(
    dirac: np.ndarray,
    gamma5: np.ndarray,
    rho: float,
) -> np.ndarray:
    gh = modified_gamma5(dirac, gamma5, rho)
    return gh - gh.conj().T


def modified_gamma5_involution_residual(
    dirac: np.ndarray,
    gamma5: np.ndarray,
    rho: float,
) -> np.ndarray:
    gh = modified_gamma5(dirac, gamma5, rho)
    identity = np.eye(gh.shape[0], dtype=complex)
    return gh @ gh - identity


def projector_residuals(
    dirac: np.ndarray,
    gamma5: np.ndarray,
    rho: float,
) -> dict[str, float]:
    plus, minus = chiral_projectors(dirac, gamma5, rho)
    identity = np.eye(plus.shape[0], dtype=complex)

    return {
        "plus_idempotency": float(
            np.linalg.norm(plus @ plus - plus)
        ),
        "minus_idempotency": float(
            np.linalg.norm(minus @ minus - minus)
        ),
        "orthogonality": float(
            np.linalg.norm(plus @ minus)
        ),
        "completeness": float(
            np.linalg.norm(plus + minus - identity)
        ),
        "plus_hermiticity": float(
            np.linalg.norm(plus - plus.conj().T)
        ),
        "minus_hermiticity": float(
            np.linalg.norm(minus - minus.conj().T)
        ),
    }


def overlap_index(
    dirac: np.ndarray,
    gamma5: np.ndarray,
    rho: float,
) -> float:
    """Return the finite-matrix GW index diagnostic.

    For exact admissible overlap matrices this should be integer-valued up to
    floating arithmetic.
    """
    d, g5 = _validate(dirac, gamma5, rho)
    identity = np.eye(d.shape[0], dtype=complex)
    value = np.trace(
        g5 @ (identity - d / (2.0 * rho))
    )
    return float(np.real_if_close(value).real)


def overlap_index_from_modified_gamma5(
    dirac: np.ndarray,
    gamma5: np.ndarray,
    rho: float,
) -> float:
    gh = modified_gamma5(dirac, gamma5, rho)
    value = 0.5 * np.trace(gh)
    return float(np.real_if_close(value).real)


def index_identity_residual(
    dirac: np.ndarray,
    gamma5: np.ndarray,
    rho: float,
) -> float:
    return (
        overlap_index(dirac, gamma5, rho)
        - overlap_index_from_modified_gamma5(
            dirac,
            gamma5,
            rho,
        )
    )


def covariance_residual(
    dirac: np.ndarray,
    transformed_dirac: np.ndarray,
    gauge_matrix: np.ndarray,
    gamma5: np.ndarray,
    rho: float,
) -> np.ndarray:
    """Check hat_gamma5[D'] = G hat_gamma5[D] G^dagger."""
    d, g5 = _validate(dirac, gamma5, rho)
    d2 = np.asarray(transformed_dirac, dtype=complex)
    g = np.asarray(gauge_matrix, dtype=complex)

    if d2.shape != d.shape or g.shape != d.shape:
        raise ValueError("matrix shapes must match")

    lhs = modified_gamma5(d2, g5, rho)
    rhs = g @ modified_gamma5(d, g5, rho) @ g.conj().T
    return lhs - rhs
