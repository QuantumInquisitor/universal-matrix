"""Classical SU(2) matter-doublet lattice prototype.

Matter field:
    Psi(x) in C^2

Local gauge transformation:
    Psi(x) -> G(x) Psi(x)

Link transformation:
    U_i(x) -> G(x) U_i(x) G^dagger(x+i)

Gauge-covariant forward difference:
    D_i Psi(x)
      = U_i(x) Psi(x+i) - Psi(x).

Matter energy:
    E =
      sum_{x,i} ||D_i Psi||^2
      + sum_x V(Psi^dagger Psi).

The first potential implemented is
    V(rho) = m2 rho + lambda4 rho^2.

This is a classical non-Abelian matter prototype. It is not a Standard Model
Higgs or fermion sector.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

try:
    from .su2_lattice_gauge import AXES, forward_index
except ImportError:
    from su2_lattice_gauge import AXES, forward_index


def matter_density(psi: np.ndarray) -> np.ndarray:
    field = np.asarray(psi, dtype=complex)
    if field.ndim != 4 or field.shape[-1] != 2:
        raise ValueError("psi must have shape (nx, ny, nz, 2)")
    return np.sum(np.abs(field) ** 2, axis=-1)


def gauge_transform_matter(
    psi: np.ndarray,
    site_transform: np.ndarray,
) -> np.ndarray:
    field = np.asarray(psi, dtype=complex)
    shape = field.shape[:3]
    if field.shape != shape + (2,):
        raise ValueError("psi must have shape (nx, ny, nz, 2)")
    if site_transform.shape != shape + (2, 2):
        raise ValueError("site transform shape mismatch")

    out = np.empty_like(field)
    for idx in np.ndindex(shape):
        out[idx] = site_transform[idx] @ field[idx]
    return out


def covariant_forward_difference(
    psi: np.ndarray,
    links: np.ndarray,
    axis: int,
) -> np.ndarray:
    field = np.asarray(psi, dtype=complex)
    shape = field.shape[:3]
    if axis not in AXES:
        raise ValueError("axis must be 0,1,2")
    if links.shape != (3,) + shape + (2, 2):
        raise ValueError("link shape mismatch")

    out = np.empty_like(field)
    for idx in np.ndindex(shape):
        xp = forward_index(idx, axis, shape)
        out[idx] = links[(axis,) + idx] @ field[xp] - field[idx]
    return out


def hopping_energy(psi: np.ndarray, links: np.ndarray) -> float:
    return float(
        sum(
            np.sum(
                np.abs(
                    covariant_forward_difference(
                        psi,
                        links,
                        axis,
                    )
                ) ** 2
            )
            for axis in AXES
        )
    )


@dataclass(frozen=True)
class SU2MatterPotential:
    mass2: float = 1.0
    lambda4: float = 0.0


def potential_energy(
    psi: np.ndarray,
    potential: SU2MatterPotential,
) -> float:
    rho = matter_density(psi)
    return float(
        np.sum(
            potential.mass2 * rho
            + potential.lambda4 * rho**2
        )
    )


def total_matter_energy(
    psi: np.ndarray,
    links: np.ndarray,
    potential: SU2MatterPotential = SU2MatterPotential(),
) -> float:
    return hopping_energy(psi, links) + potential_energy(psi, potential)


def gauge_invariant_norm(psi: np.ndarray) -> float:
    return float(np.sum(matter_density(psi)))
