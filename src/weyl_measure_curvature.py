"""Finite-lattice Weyl subspaces and chiral measure-curvature diagnostics.

This module builds on the Ginsparg-Wilson overlap operator already implemented
for compact U(1) backgrounds.

For an admissible overlap Dirac operator D, define

    hat_gamma5 = gamma5 (I - D/rho)

and the exact chiral projectors

    P_hat(+/-) = (I +/- hat_gamma5)/2.

A Weyl basis is any orthonormal frame spanning one of these projector
subspaces. The frame itself is not unique: V and V U, for unitary U acting
inside the Weyl subspace, represent the same physical subspace.

For a smooth family of gauge backgrounds A(lambda), the basis-independent
curvature of the Weyl projector bundle is

    F_ab
      = i Tr[
          P (partial_a P partial_b P
             - partial_b P partial_a P)
        ].

This is the natural finite-dimensional Berry/measure-curvature diagnostic that
precedes a lattice gauge-anomaly analysis.

Important classification:
- projector covariance and curvature are exact algebraic/geometric diagnostics;
- a nonzero local curvature is NOT by itself a proof of an uncancelled gauge
  anomaly;
- anomaly cancellation requires the complete chiral representation content,
  fermion measure, and global consistency conditions.

The dense overlap matrices used here are correctness references for small
lattices, not production solvers.
"""

from __future__ import annotations

import numpy as np

try:
    from .ginsparg_wilson_chirality import chiral_projectors
    from .u1_overlap_dirac_lattice import (
        gamma5_lattice,
        gauge_matrix,
        gauge_transform_links,
        overlap_dirac_matrix,
    )
except ImportError:
    from ginsparg_wilson_chirality import chiral_projectors
    from u1_overlap_dirac_lattice import (
        gamma5_lattice,
        gauge_matrix,
        gauge_transform_links,
        overlap_dirac_matrix,
    )


def _validate_chirality(chirality: int) -> int:
    if chirality not in (-1, 1):
        raise ValueError("chirality must be -1 or +1")
    return chirality


def weyl_projector(
    links: np.ndarray,
    chirality: int = -1,
    rho: float = 1.0,
    wilson_r: float = 1.0,
) -> np.ndarray:
    """Return the exact GW-modified Weyl projector for a U(1) background."""
    _validate_chirality(chirality)
    a = np.asarray(links, dtype=float)
    shape = a.shape[1:]
    if a.ndim != 5 or a.shape[0] != 4 or len(shape) != 4:
        raise ValueError("links must have shape (4,n0,n1,n2,n3)")

    d = overlap_dirac_matrix(
        a,
        rho=rho,
        wilson_r=wilson_r,
    )
    g5 = gamma5_lattice(shape)
    plus, minus = chiral_projectors(
        d,
        g5,
        rho,
    )
    return plus if chirality > 0 else minus


def weyl_basis_from_projector(
    projector: np.ndarray,
    eigenvalue_tolerance: float = 1e-8,
) -> np.ndarray:
    """Construct an orthonormal frame for a Hermitian projector subspace."""
    p = np.asarray(projector, dtype=complex)
    if p.ndim != 2 or p.shape[0] != p.shape[1]:
        raise ValueError("projector must be square")
    if eigenvalue_tolerance <= 0:
        raise ValueError("eigenvalue_tolerance must be positive")
    if not np.allclose(p, p.conj().T, atol=1e-9, rtol=0):
        raise ValueError("projector must be Hermitian")

    values, vectors = np.linalg.eigh(p)

    distance_to_projector_spectrum = np.minimum(
        np.abs(values),
        np.abs(values - 1.0),
    )
    if np.max(distance_to_projector_spectrum) > eigenvalue_tolerance:
        raise ValueError("matrix is not numerically projector-valued")

    selected = values > 0.5
    return vectors[:, selected]


def weyl_basis(
    links: np.ndarray,
    chirality: int = -1,
    rho: float = 1.0,
    wilson_r: float = 1.0,
) -> np.ndarray:
    return weyl_basis_from_projector(
        weyl_projector(
            links,
            chirality=chirality,
            rho=rho,
            wilson_r=wilson_r,
        )
    )


def basis_projector(basis: np.ndarray) -> np.ndarray:
    v = np.asarray(basis, dtype=complex)
    if v.ndim != 2:
        raise ValueError("basis must be a matrix")
    return v @ v.conj().T


def projector_reconstruction_residual(
    projector: np.ndarray,
    basis: np.ndarray,
) -> float:
    p = np.asarray(projector, dtype=complex)
    reconstructed = basis_projector(basis)
    if p.shape != reconstructed.shape:
        raise ValueError("projector/basis shape mismatch")
    return float(np.linalg.norm(p - reconstructed))


def gauge_transport_projector_residual(
    links: np.ndarray,
    alpha: np.ndarray,
    chirality: int = -1,
    rho: float = 1.0,
    wilson_r: float = 1.0,
) -> float:
    """Check P[A^g] = G P[A] G^dagger."""
    a = np.asarray(links, dtype=float)
    gauge_phase = np.asarray(alpha, dtype=float)
    if gauge_phase.shape != a.shape[1:]:
        raise ValueError("alpha shape mismatch")

    p = weyl_projector(
        a,
        chirality,
        rho,
        wilson_r,
    )
    transformed_links = gauge_transform_links(
        a,
        gauge_phase,
    )
    p2 = weyl_projector(
        transformed_links,
        chirality,
        rho,
        wilson_r,
    )
    g = gauge_matrix(gauge_phase)
    return float(
        np.linalg.norm(
            p2 - g @ p @ g.conj().T
        )
    )


def gauge_transport_singular_values(
    links: np.ndarray,
    alpha: np.ndarray,
    chirality: int = -1,
    rho: float = 1.0,
    wilson_r: float = 1.0,
) -> np.ndarray:
    """Principal-angle diagnostic between gauge-related Weyl subspaces.

    If the subspaces transform covariantly, all singular values of

        V[A^g]^dagger G V[A]

    equal one, regardless of the arbitrary internal basis convention chosen by
    eigensolvers.
    """
    a = np.asarray(links, dtype=float)
    gauge_phase = np.asarray(alpha, dtype=float)
    if gauge_phase.shape != a.shape[1:]:
        raise ValueError("alpha shape mismatch")

    v = weyl_basis(
        a,
        chirality,
        rho,
        wilson_r,
    )
    transformed_links = gauge_transform_links(
        a,
        gauge_phase,
    )
    v2 = weyl_basis(
        transformed_links,
        chirality,
        rho,
        wilson_r,
    )
    if v.shape[1] != v2.shape[1]:
        raise ValueError("gauge-related Weyl ranks do not match")

    g = gauge_matrix(gauge_phase)
    overlap = v2.conj().T @ g @ v
    return np.linalg.svd(
        overlap,
        compute_uv=False,
    )


def projector_directional_derivative(
    links: np.ndarray,
    direction: np.ndarray,
    chirality: int = -1,
    rho: float = 1.0,
    wilson_r: float = 1.0,
    epsilon: float = 1e-5,
) -> np.ndarray:
    """Symmetric finite-difference derivative of the Weyl projector."""
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")

    a = np.asarray(links, dtype=float)
    tangent = np.asarray(direction, dtype=float)
    if tangent.shape != a.shape:
        raise ValueError("direction shape must match links")

    plus = weyl_projector(
        a + epsilon * tangent,
        chirality,
        rho,
        wilson_r,
    )
    minus = weyl_projector(
        a - epsilon * tangent,
        chirality,
        rho,
        wilson_r,
    )
    return (plus - minus) / (2.0 * epsilon)


def measure_curvature(
    links: np.ndarray,
    direction_a: np.ndarray,
    direction_b: np.ndarray,
    chirality: int = -1,
    rho: float = 1.0,
    wilson_r: float = 1.0,
    epsilon: float = 1e-5,
) -> float:
    """Return i Tr(P [d_a P, d_b P]).

    For a Hermitian projector family this is real up to numerical error.
    """
    p = weyl_projector(
        links,
        chirality,
        rho,
        wilson_r,
    )
    dpa = projector_directional_derivative(
        links,
        direction_a,
        chirality,
        rho,
        wilson_r,
        epsilon,
    )
    dpb = projector_directional_derivative(
        links,
        direction_b,
        chirality,
        rho,
        wilson_r,
        epsilon,
    )
    commutator = dpa @ dpb - dpb @ dpa
    value = 1j * np.trace(p @ commutator)
    return float(np.real(value))


def curvature_imaginary_residual(
    links: np.ndarray,
    direction_a: np.ndarray,
    direction_b: np.ndarray,
    chirality: int = -1,
    rho: float = 1.0,
    wilson_r: float = 1.0,
    epsilon: float = 1e-5,
) -> float:
    """Numerical imaginary residue before taking the real curvature."""
    p = weyl_projector(
        links,
        chirality,
        rho,
        wilson_r,
    )
    dpa = projector_directional_derivative(
        links,
        direction_a,
        chirality,
        rho,
        wilson_r,
        epsilon,
    )
    dpb = projector_directional_derivative(
        links,
        direction_b,
        chirality,
        rho,
        wilson_r,
        epsilon,
    )
    value = 1j * np.trace(
        p @ (dpa @ dpb - dpb @ dpa)
    )
    return float(np.imag(value))


def curvature_gauge_invariance_residual(
    links: np.ndarray,
    alpha: np.ndarray,
    direction_a: np.ndarray,
    direction_b: np.ndarray,
    chirality: int = -1,
    rho: float = 1.0,
    wilson_r: float = 1.0,
    epsilon: float = 1e-5,
) -> float:
    """Gauge-invariance residual for the projector-bundle curvature.

    For compact U(1), a fixed gauge transformation shifts the background links
    affinely, so additive tangent directions are unchanged.
    """
    original = measure_curvature(
        links,
        direction_a,
        direction_b,
        chirality,
        rho,
        wilson_r,
        epsilon,
    )
    transformed = gauge_transform_links(
        links,
        alpha,
    )
    after = measure_curvature(
        transformed,
        direction_a,
        direction_b,
        chirality,
        rho,
        wilson_r,
        epsilon,
    )
    return after - original
