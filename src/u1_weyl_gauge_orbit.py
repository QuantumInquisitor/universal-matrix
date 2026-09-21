"""Gauge-orbit holonomy of a charged U(1) Weyl subspace.

For a charge-q overlap fermion, the background seen by the Dirac operator is

    q A_mu(x).

Under an underlying compact-U(1) gauge transformation

    A_mu(x)
      -> A_mu(x)
         + alpha(x)
         - alpha(x+mu),

the charged overlap operator transforms with the site gauge matrix

    G_q(alpha) = exp(i q alpha).

A path along the gauge orbit connects gauge-equivalent backgrounds. To form a
closed loop in gauge-orbit space:

1. parallel transport the Weyl basis along the gauge path;
2. identify the endpoint with the start using the exact charge-q gauge
   transformation.

If H_open maps coefficient vectors from the initial Weyl frame to the endpoint
frame, and Q_g is the unitary coefficient map induced by G_q from the initial
frame to the endpoint frame, then the quotient-space holonomy is

    H_gauge = Q_g^dagger H_open.

Its determinant phase is invariant under arbitrary internal Weyl-basis changes
at every path point.

This phase is a chiral-measure gauge-orbit diagnostic. It is not by itself the
consistent gauge anomaly.
"""

from __future__ import annotations

import math

import numpy as np

try:
    from .u1_overlap_dirac_lattice import gauge_matrix
    from .weyl_measure_curvature import weyl_basis
    from .weyl_measure_holonomy import (
        determinant_phase,
        polar_unitary,
        transport_matrix,
    )
except ImportError:
    from u1_overlap_dirac_lattice import gauge_matrix
    from weyl_measure_curvature import weyl_basis
    from weyl_measure_holonomy import (
        determinant_phase,
        polar_unitary,
        transport_matrix,
    )


def gauge_link_increment(
    alpha: np.ndarray,
) -> np.ndarray:
    """Return delta A_mu = alpha(x)-alpha(x+mu)."""
    phase = np.asarray(alpha, dtype=float)
    if phase.ndim != 4:
        raise ValueError("alpha must be a 4D lattice field")

    out = np.empty((4,) + phase.shape, dtype=float)
    for mu in range(4):
        out[mu] = (
            phase
            - np.roll(phase, -1, axis=mu)
        )
    return out


def charged_weyl_basis(
    links: np.ndarray,
    charge: float,
    chirality: int = -1,
    rho: float = 1.0,
    wilson_r: float = 1.0,
) -> np.ndarray:
    """Weyl frame for the charge-q background q*A."""
    if not math.isfinite(charge):
        raise ValueError("charge must be finite")
    return weyl_basis(
        charge * np.asarray(links, dtype=float),
        chirality=chirality,
        rho=rho,
        wilson_r=wilson_r,
    )


def gauge_orbit_link_path(
    links: np.ndarray,
    alpha: np.ndarray,
    steps: int,
) -> list[np.ndarray]:
    """Discretize A(t)=A+t*dalpha for t in [0,1]."""
    if steps < 1:
        raise ValueError("steps must be at least one")

    a = np.asarray(links, dtype=float)
    phase = np.asarray(alpha, dtype=float)
    if a.ndim != 5 or a.shape[0] != 4:
        raise ValueError("links must have shape (4,n0,n1,n2,n3)")
    if phase.shape != a.shape[1:]:
        raise ValueError("alpha shape mismatch")

    increment = gauge_link_increment(phase)
    return [
        a + (k / steps) * increment
        for k in range(steps + 1)
    ]


def gauge_orbit_weyl_bases(
    links: np.ndarray,
    alpha: np.ndarray,
    charge: float,
    chirality: int = -1,
    steps: int = 8,
    rho: float = 1.0,
    wilson_r: float = 1.0,
) -> list[np.ndarray]:
    return [
        charged_weyl_basis(
            point,
            charge,
            chirality,
            rho,
            wilson_r,
        )
        for point in gauge_orbit_link_path(
            links,
            alpha,
            steps,
        )
    ]


def open_path_transport(
    bases: list[np.ndarray],
    singular_tolerance: float = 1e-10,
) -> np.ndarray:
    """Ordered parallel transport from bases[0] to bases[-1]."""
    if len(bases) < 2:
        raise ValueError("at least two bases are required")

    rank = bases[0].shape[1]
    if any(
        basis.ndim != 2
        or basis.shape[1] != rank
        for basis in bases
    ):
        raise ValueError("all bases must have the same rank")

    transport = np.eye(rank, dtype=complex)
    for source, target in zip(
        bases[:-1],
        bases[1:],
    ):
        q = transport_matrix(
            source,
            target,
            singular_tolerance,
        )
        transport = q @ transport
    return transport


def exact_gauge_identification(
    initial_basis: np.ndarray,
    endpoint_basis: np.ndarray,
    alpha: np.ndarray,
    charge: float,
    singular_tolerance: float = 1e-10,
) -> np.ndarray:
    """Coefficient map induced by G_q from initial to endpoint frame."""
    vi = np.asarray(initial_basis, dtype=complex)
    vf = np.asarray(endpoint_basis, dtype=complex)

    if vi.ndim != 2 or vf.ndim != 2 or vi.shape != vf.shape:
        raise ValueError("initial and endpoint bases must match")

    phase = np.asarray(alpha, dtype=float)
    gq = gauge_matrix(charge * phase)
    overlap = vf.conj().T @ gq @ vi
    return polar_unitary(
        overlap,
        singular_tolerance,
    )


def gauge_endpoint_subspace_residual(
    links: np.ndarray,
    alpha: np.ndarray,
    charge: float,
    chirality: int = -1,
    rho: float = 1.0,
    wilson_r: float = 1.0,
) -> float:
    """Check that endpoint Weyl subspace equals G_q acting on the start."""
    path = gauge_orbit_link_path(
        links,
        alpha,
        steps=1,
    )
    vi = charged_weyl_basis(
        path[0],
        charge,
        chirality,
        rho,
        wilson_r,
    )
    vf = charged_weyl_basis(
        path[-1],
        charge,
        chirality,
        rho,
        wilson_r,
    )
    gq = gauge_matrix(
        charge * np.asarray(alpha, dtype=float)
    )

    pi = vi @ vi.conj().T
    pf = vf @ vf.conj().T
    expected = gq @ pi @ gq.conj().T
    return float(np.linalg.norm(pf - expected))


def gauge_orbit_holonomy_from_bases(
    bases: list[np.ndarray],
    alpha: np.ndarray,
    charge: float,
    singular_tolerance: float = 1e-10,
) -> np.ndarray:
    """Return quotient-space holonomy Q_g^dagger H_open."""
    transport = open_path_transport(
        bases,
        singular_tolerance,
    )
    gauge_id = exact_gauge_identification(
        bases[0],
        bases[-1],
        alpha,
        charge,
        singular_tolerance,
    )
    return gauge_id.conj().T @ transport


def gauge_orbit_holonomy(
    links: np.ndarray,
    alpha: np.ndarray,
    charge: float,
    chirality: int = -1,
    steps: int = 8,
    rho: float = 1.0,
    wilson_r: float = 1.0,
    singular_tolerance: float = 1e-10,
) -> np.ndarray:
    bases = gauge_orbit_weyl_bases(
        links,
        alpha,
        charge,
        chirality,
        steps,
        rho,
        wilson_r,
    )
    return gauge_orbit_holonomy_from_bases(
        bases,
        alpha,
        charge,
        singular_tolerance,
    )


def gauge_orbit_measure_phase(
    links: np.ndarray,
    alpha: np.ndarray,
    charge: float,
    chirality: int = -1,
    steps: int = 8,
    rho: float = 1.0,
    wilson_r: float = 1.0,
    singular_tolerance: float = 1e-10,
) -> float:
    return determinant_phase(
        gauge_orbit_holonomy(
            links,
            alpha,
            charge,
            chirality,
            steps,
            rho,
            wilson_r,
            singular_tolerance,
        )
    )


def infinitesimal_gauge_measure_response(
    links: np.ndarray,
    alpha: np.ndarray,
    charge: float,
    chirality: int = -1,
    epsilon: float = 1e-3,
    steps: int = 8,
    rho: float = 1.0,
    wilson_r: float = 1.0,
    singular_tolerance: float = 1e-10,
) -> float:
    """Symmetric derivative of the gauge-orbit measure phase at alpha=0."""
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")

    plus = gauge_orbit_measure_phase(
        links,
        epsilon * np.asarray(alpha, dtype=float),
        charge,
        chirality,
        steps,
        rho,
        wilson_r,
        singular_tolerance,
    )
    minus = gauge_orbit_measure_phase(
        links,
        -epsilon * np.asarray(alpha, dtype=float),
        charge,
        chirality,
        steps,
        rho,
        wilson_r,
        singular_tolerance,
    )

    delta = (
        plus - minus + math.pi
    ) % (2.0 * math.pi) - math.pi
    return delta / (2.0 * epsilon)


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
