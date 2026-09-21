"""Discrete parallel transport and holonomy of finite-lattice Weyl subspaces.

Given orthonormal Weyl frames V_a and V_b with the same rank, define the
overlap

    M_ba = V_b^dagger V_a.

When neighboring subspaces are sufficiently close, M_ba is nonsingular. Its
unitary polar factor

    Q_ba = polar_unitary(M_ba)

is the closest unitary map between coefficient frames and supplies a discrete
parallel-transport step.

Under independent internal basis changes

    V_a -> V_a U_a
    V_b -> V_b U_b,

the transport transforms covariantly,

    Q_ba -> U_b^dagger Q_ba U_a.

For a closed loop of frames V_0,...,V_{N-1}, the ordered product

    H = Q_{0,N-1} ... Q_{2,1} Q_{1,0}

transforms by conjugation at the base point. Therefore its spectrum and

    arg det(H)

are independent of arbitrary choices of Weyl basis inside each subspace.

This determinant phase is a finite-dimensional chiral-measure holonomy
diagnostic. It is not, by itself, a proof of a gauge anomaly.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np

try:
    from .weyl_measure_curvature import weyl_basis
except ImportError:
    from weyl_measure_curvature import weyl_basis


def polar_unitary(
    matrix: np.ndarray,
    singular_tolerance: float = 1e-10,
) -> np.ndarray:
    """Return the unitary polar factor U V^dagger from an SVD."""
    m = np.asarray(matrix, dtype=complex)
    if m.ndim != 2 or m.shape[0] != m.shape[1]:
        raise ValueError("matrix must be square")
    if singular_tolerance <= 0:
        raise ValueError("singular_tolerance must be positive")

    left, singular, right_h = np.linalg.svd(m)
    if np.min(singular) <= singular_tolerance:
        raise ValueError(
            "neighboring Weyl frames have a singular overlap"
        )
    return left @ right_h


def transport_matrix(
    basis_from: np.ndarray,
    basis_to: np.ndarray,
    singular_tolerance: float = 1e-10,
) -> np.ndarray:
    """Unitary coefficient transport from basis_from to basis_to."""
    a = np.asarray(basis_from, dtype=complex)
    b = np.asarray(basis_to, dtype=complex)

    if a.ndim != 2 or b.ndim != 2:
        raise ValueError("bases must be matrices")
    if a.shape != b.shape:
        raise ValueError("Weyl bases must have the same shape")

    overlap = b.conj().T @ a
    return polar_unitary(
        overlap,
        singular_tolerance=singular_tolerance,
    )


def transport_unitarity_residual(
    basis_from: np.ndarray,
    basis_to: np.ndarray,
    singular_tolerance: float = 1e-10,
) -> float:
    q = transport_matrix(
        basis_from,
        basis_to,
        singular_tolerance,
    )
    identity = np.eye(q.shape[0], dtype=complex)
    return float(
        np.linalg.norm(
            q.conj().T @ q - identity
        )
    )


def closed_loop_holonomy_from_bases(
    bases: Sequence[np.ndarray],
    singular_tolerance: float = 1e-10,
) -> np.ndarray:
    """Return ordered coefficient holonomy around a closed frame loop.

    The sequence lists distinct loop vertices. Closure back to bases[0] is
    inserted automatically.
    """
    frames = [
        np.asarray(v, dtype=complex)
        for v in bases
    ]
    if len(frames) < 2:
        raise ValueError("at least two loop vertices are required")

    shape = frames[0].shape
    if any(v.ndim != 2 or v.shape != shape for v in frames):
        raise ValueError("all Weyl bases must have the same matrix shape")

    rank = shape[1]
    holonomy = np.eye(rank, dtype=complex)

    for i in range(len(frames)):
        source = frames[i]
        target = frames[(i + 1) % len(frames)]
        q = transport_matrix(
            source,
            target,
            singular_tolerance,
        )
        holonomy = q @ holonomy

    return holonomy


def holonomy_unitarity_residual(
    holonomy: np.ndarray,
) -> float:
    h = np.asarray(holonomy, dtype=complex)
    if h.ndim != 2 or h.shape[0] != h.shape[1]:
        raise ValueError("holonomy must be square")
    identity = np.eye(h.shape[0], dtype=complex)
    return float(
        np.linalg.norm(
            h.conj().T @ h - identity
        )
    )


def determinant_phase(
    unitary: np.ndarray,
) -> float:
    """Principal phase arg(det U) in (-pi,pi]."""
    u = np.asarray(unitary, dtype=complex)
    if u.ndim != 2 or u.shape[0] != u.shape[1]:
        raise ValueError("matrix must be square")
    det = np.linalg.det(u)
    phase = math.atan2(
        float(det.imag),
        float(det.real),
    )
    if phase <= -math.pi:
        return math.pi
    return phase


def closed_loop_measure_phase_from_bases(
    bases: Sequence[np.ndarray],
    singular_tolerance: float = 1e-10,
) -> float:
    return determinant_phase(
        closed_loop_holonomy_from_bases(
            bases,
            singular_tolerance,
        )
    )


def weyl_loop_bases(
    link_path: Sequence[np.ndarray],
    chirality: int = -1,
    rho: float = 1.0,
    wilson_r: float = 1.0,
) -> list[np.ndarray]:
    if len(link_path) < 2:
        raise ValueError("link_path must contain at least two vertices")
    return [
        weyl_basis(
            links,
            chirality=chirality,
            rho=rho,
            wilson_r=wilson_r,
        )
        for links in link_path
    ]


def closed_loop_measure_phase(
    link_path: Sequence[np.ndarray],
    chirality: int = -1,
    rho: float = 1.0,
    wilson_r: float = 1.0,
    singular_tolerance: float = 1e-10,
) -> float:
    """Compute basis-independent determinant holonomy for a gauge-field loop."""
    return closed_loop_measure_phase_from_bases(
        weyl_loop_bases(
            link_path,
            chirality,
            rho,
            wilson_r,
        ),
        singular_tolerance,
    )


def rectangular_link_loop(
    base_links: np.ndarray,
    direction_a: np.ndarray,
    direction_b: np.ndarray,
    side_a: float,
    side_b: float,
) -> list[np.ndarray]:
    """Four vertices of an oriented rectangle in link-field space."""
    base = np.asarray(base_links, dtype=float)
    da = np.asarray(direction_a, dtype=float)
    db = np.asarray(direction_b, dtype=float)

    if da.shape != base.shape or db.shape != base.shape:
        raise ValueError("direction shapes must match base_links")

    return [
        base.copy(),
        base + side_a * da,
        base + side_a * da + side_b * db,
        base + side_b * db,
    ]


def principal_phase_difference(
    phase_a: float,
    phase_b: float,
) -> float:
    """Return wrapped phase_a-phase_b in (-pi,pi]."""
    value = (phase_a - phase_b + math.pi) % (
        2.0 * math.pi
    ) - math.pi
    if value <= -math.pi:
        return math.pi
    return value
