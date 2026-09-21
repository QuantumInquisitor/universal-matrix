"""Charged U(1) overlap index density and anomaly-coefficient ledger.

This module separates two related but distinct objects.

1. Finite-lattice overlap index density

For a fermion of U(1) charge q, the compact link phase entering the Wilson
kernel is q*A_mu(x). Using the overlap operator D_q[A], define

    q_index(x)
      = tr_spin[
          gamma5 (I - D_q/(2*rho))
        ]_{x,x}.

Its lattice sum is the overlap index:

    sum_x q_index(x)
      = Tr[
          Gamma5 (I - D_q/(2*rho))
        ].

This is a local index/topological-density diagnostic for the overlap operator.
It is gauge invariant under the corresponding charge-q U(1) transformation.

2. Representation anomaly coefficients

For a collection of Weyl species with handedness chi_i in {-1,+1} and charges
q_i, the standard four-dimensional Abelian group-theory coefficients are

    C_U1^3 = sum_i chi_i q_i^3

and

    C_grav-U1 = sum_i chi_i q_i.

These coefficients are exact representation bookkeeping. Their vanishing is a
necessary perturbative anomaly-cancellation condition, but by itself does not
construct a globally consistent lattice fermion measure and does not address
global anomalies.

The local finite-lattice density and the representation coefficients are kept
explicitly separate in this module.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from collections.abc import Sequence

import numpy as np

try:
    from .u1_overlap_dirac_lattice import (
        gamma5_lattice,
        overlap_dirac_matrix,
        gauge_transform_links,
    )
except ImportError:
    from u1_overlap_dirac_lattice import (
        gamma5_lattice,
        overlap_dirac_matrix,
        gauge_transform_links,
    )


def charged_link_phases(
    links: np.ndarray,
    charge: float,
) -> np.ndarray:
    """Return the link phases seen by a charge-q fermion."""
    if not math.isfinite(charge):
        raise ValueError("charge must be finite")
    a = np.asarray(links, dtype=float)
    if a.ndim != 5 or a.shape[0] != 4:
        raise ValueError("links must have shape (4,n0,n1,n2,n3)")
    return charge * a


def charged_overlap_dirac_matrix(
    links: np.ndarray,
    charge: float,
    rho: float = 1.0,
    wilson_r: float = 1.0,
    spectral_tolerance: float = 1e-10,
) -> np.ndarray:
    return overlap_dirac_matrix(
        charged_link_phases(links, charge),
        rho=rho,
        wilson_r=wilson_r,
        spectral_tolerance=spectral_tolerance,
    )


def local_overlap_index_density(
    links: np.ndarray,
    charge: float,
    rho: float = 1.0,
    wilson_r: float = 1.0,
    spectral_tolerance: float = 1e-10,
) -> np.ndarray:
    """Return tr_spin[gamma5(1-D/(2rho))] on every lattice site."""
    if rho <= 0:
        raise ValueError("rho must be positive")

    a = np.asarray(links, dtype=float)
    if a.ndim != 5 or a.shape[0] != 4:
        raise ValueError("links must have shape (4,n0,n1,n2,n3)")
    shape = a.shape[1:]

    d = charged_overlap_dirac_matrix(
        a,
        charge,
        rho,
        wilson_r,
        spectral_tolerance,
    )
    g5 = gamma5_lattice(shape)
    identity = np.eye(d.shape[0], dtype=complex)
    operator = g5 @ (
        identity - d / (2.0 * rho)
    )

    density = np.zeros(shape, dtype=float)
    for coord in np.ndindex(shape):
        site = int(np.ravel_multi_index(coord, shape))
        block = operator[
            4 * site : 4 * site + 4,
            4 * site : 4 * site + 4,
        ]
        value = np.trace(block)
        density[coord] = float(np.real_if_close(value).real)
    return density


def integrated_overlap_index(
    links: np.ndarray,
    charge: float,
    rho: float = 1.0,
    wilson_r: float = 1.0,
    spectral_tolerance: float = 1e-10,
) -> float:
    return float(
        np.sum(
            local_overlap_index_density(
                links,
                charge,
                rho,
                wilson_r,
                spectral_tolerance,
            )
        )
    )


def direct_overlap_index(
    links: np.ndarray,
    charge: float,
    rho: float = 1.0,
    wilson_r: float = 1.0,
    spectral_tolerance: float = 1e-10,
) -> float:
    a = np.asarray(links, dtype=float)
    shape = a.shape[1:]
    d = charged_overlap_dirac_matrix(
        a,
        charge,
        rho,
        wilson_r,
        spectral_tolerance,
    )
    g5 = gamma5_lattice(shape)
    identity = np.eye(d.shape[0], dtype=complex)
    value = np.trace(
        g5 @ (identity - d / (2.0 * rho))
    )
    return float(np.real_if_close(value).real)


def index_sum_residual(
    links: np.ndarray,
    charge: float,
    rho: float = 1.0,
    wilson_r: float = 1.0,
    spectral_tolerance: float = 1e-10,
) -> float:
    return (
        integrated_overlap_index(
            links,
            charge,
            rho,
            wilson_r,
            spectral_tolerance,
        )
        - direct_overlap_index(
            links,
            charge,
            rho,
            wilson_r,
            spectral_tolerance,
        )
    )


def charged_gauge_transform_links(
    links: np.ndarray,
    alpha: np.ndarray,
) -> np.ndarray:
    """Transform the underlying unit-charge gauge potential.

    The charge factor is applied only when constructing D_q[A].
    """
    return gauge_transform_links(
        np.asarray(links, dtype=float),
        np.asarray(alpha, dtype=float),
    )


def local_index_gauge_residual(
    links: np.ndarray,
    alpha: np.ndarray,
    charge: float,
    rho: float = 1.0,
    wilson_r: float = 1.0,
    spectral_tolerance: float = 1e-10,
) -> np.ndarray:
    before = local_overlap_index_density(
        links,
        charge,
        rho,
        wilson_r,
        spectral_tolerance,
    )
    transformed = charged_gauge_transform_links(
        links,
        alpha,
    )
    after = local_overlap_index_density(
        transformed,
        charge,
        rho,
        wilson_r,
        spectral_tolerance,
    )
    return after - before


@dataclass(frozen=True)
class WeylSpecies:
    charge: float
    handedness: int

    def __post_init__(self) -> None:
        if not math.isfinite(self.charge):
            raise ValueError("charge must be finite")
        if self.handedness not in (-1, 1):
            raise ValueError("handedness must be -1 or +1")


def cubic_u1_anomaly_coefficient(
    species: Sequence[WeylSpecies],
) -> float:
    """Return sum chi_i q_i^3."""
    return float(
        sum(
            item.handedness * item.charge**3
            for item in species
        )
    )


def mixed_gravitational_u1_coefficient(
    species: Sequence[WeylSpecies],
) -> float:
    """Return sum chi_i q_i."""
    return float(
        sum(
            item.handedness * item.charge
            for item in species
        )
    )


def anomaly_ledger(
    species: Sequence[WeylSpecies],
    tolerance: float = 1e-12,
) -> dict[str, float | bool | int]:
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")

    cubic = cubic_u1_anomaly_coefficient(species)
    mixed = mixed_gravitational_u1_coefficient(species)

    return {
        "species_count": len(species),
        "u1_cubic": cubic,
        "mixed_gravitational_u1": mixed,
        "u1_cubic_cancels": abs(cubic) <= tolerance,
        "mixed_gravitational_u1_cancels": abs(mixed) <= tolerance,
        "perturbative_abelian_conditions_cancel": (
            abs(cubic) <= tolerance
            and abs(mixed) <= tolerance
        ),
    }


def covariant_local_anomaly_density_candidate(
    links: np.ndarray,
    species: WeylSpecies,
    rho: float = 1.0,
    wilson_r: float = 1.0,
    spectral_tolerance: float = 1e-10,
) -> np.ndarray:
    """Charge-weighted overlap index density.

    Convention:
        A_cov(x) = chi * q * q_index(x).

    This is a lattice covariant-anomaly diagnostic candidate. It is not the
    consistent anomaly and is not a substitute for a full fermion-measure
    construction.
    """
    return (
        species.handedness
        * species.charge
        * local_overlap_index_density(
            links,
            species.charge,
            rho,
            wilson_r,
            spectral_tolerance,
        )
    )


def total_covariant_local_anomaly_candidate(
    links: np.ndarray,
    species: Sequence[WeylSpecies],
    rho: float = 1.0,
    wilson_r: float = 1.0,
    spectral_tolerance: float = 1e-10,
) -> np.ndarray:
    a = np.asarray(links, dtype=float)
    total = np.zeros(a.shape[1:], dtype=float)
    for item in species:
        total += covariant_local_anomaly_density_candidate(
            a,
            item,
            rho,
            wilson_r,
            spectral_tolerance,
        )
    return total
