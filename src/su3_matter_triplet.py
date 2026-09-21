"""Classical SU(3) matter-triplet lattice prototype.

Matter:
    Psi(x) in C^3

Local gauge transformation:
    Psi(x) -> G(x) Psi(x)

Covariant forward difference:
    D_i Psi(x)
      = U_i(x) Psi(x+i) - Psi(x).

Matter energy:
    E =
      sum_{x,i} ||D_i Psi||^2
      + sum_x [m2 rho + lambda4 rho^2]

with
    rho = Psi^dagger Psi.

This is a classical fundamental-representation SU(3) matter field. It is not
yet identified with quarks or QCD matter.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

try:
    from .su3_lattice_gauge import AXES, forward_index
except ImportError:
    from su3_lattice_gauge import AXES, forward_index


def matter_density(psi: np.ndarray) -> np.ndarray:
    field = np.asarray(psi, dtype=complex)
    if field.ndim != 4 or field.shape[-1] != 3:
        raise ValueError("psi must have shape (nx, ny, nz, 3)")
    return np.sum(np.abs(field)**2, axis=-1)


def gauge_transform_matter(
    psi: np.ndarray,
    site_transform: np.ndarray,
) -> np.ndarray:
    field = np.asarray(psi, dtype=complex)
    shape = field.shape[:3]
    if site_transform.shape != shape + (3,3):
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
    if links.shape != (3,) + shape + (3,3):
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
                np.abs(covariant_forward_difference(psi, links, axis))**2
            )
            for axis in AXES
        )
    )


@dataclass(frozen=True)
class SU3MatterPotential:
    mass2: float = 1.0
    lambda4: float = 0.0


def potential_energy(
    psi: np.ndarray,
    potential: SU3MatterPotential,
) -> float:
    rho = matter_density(psi)
    return float(
        np.sum(
            potential.mass2*rho
            + potential.lambda4*rho**2
        )
    )


def total_matter_energy(
    psi: np.ndarray,
    links: np.ndarray,
    potential: SU3MatterPotential = SU3MatterPotential(),
) -> float:
    return hopping_energy(psi, links) + potential_energy(psi, potential)


def gauge_invariant_norm(psi: np.ndarray) -> float:
    return float(np.sum(matter_density(psi)))
