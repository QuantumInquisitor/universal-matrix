"""Free spatial Wilson-Dirac reference Hamiltonian.

This module is a lattice-fermion correctness bridge, not a derived Matrix
fermion theory.

For three discretized spatial directions and continuous time, define

    H(p)
      = sum_i alpha_i sin(p_i)
        + beta M_W(p)

with

    M_W(p)
      = m
        + r sum_i [1 - cos(p_i)].

The matrices alpha_i and beta are the standard 4x4 Dirac Hamiltonian matrices.

Spectrum:

    E(p)
      = +/- sqrt(
          sum_i sin^2(p_i)
          + M_W(p)^2
        )

with double degeneracy.

Naive lattice fermion:
    r = 0, m = 0

has zero-energy modes at every Brillouin-zone corner
    p_i in {0, pi},

giving 2^3 = 8 species.

Wilson fermion:
    r > 0

gives the corner with n_pi components equal to pi an effective Wilson mass
    2 r n_pi,

so only p=(0,0,0) remains massless when m=0.

This explicitly audits the fermion-doubling problem before any physical
fermion identification is attempted.
"""

from __future__ import annotations

import itertools
import math
import numpy as np


SIGMA_X = np.array([[0, 1], [1, 0]], dtype=complex)
SIGMA_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
SIGMA_Z = np.array([[1, 0], [0, -1]], dtype=complex)
I2 = np.eye(2, dtype=complex)
ZERO2 = np.zeros((2,2), dtype=complex)


def _block(a, b, c, d) -> np.ndarray:
    return np.block([[a, b], [c, d]])


BETA = _block(I2, ZERO2, ZERO2, -I2)

ALPHA = (
    _block(ZERO2, SIGMA_X, SIGMA_X, ZERO2),
    _block(ZERO2, SIGMA_Y, SIGMA_Y, ZERO2),
    _block(ZERO2, SIGMA_Z, SIGMA_Z, ZERO2),
)


def wilson_mass(
    momentum: tuple[float, float, float] | np.ndarray,
    mass: float = 0.0,
    wilson_r: float = 1.0,
) -> float:
    p = np.asarray(momentum, dtype=float)
    if p.shape != (3,):
        raise ValueError("momentum must have three components")
    if wilson_r < 0:
        raise ValueError("wilson_r must be non-negative")
    return float(
        mass
        + wilson_r * np.sum(1.0 - np.cos(p))
    )


def hamiltonian(
    momentum: tuple[float, float, float] | np.ndarray,
    mass: float = 0.0,
    wilson_r: float = 1.0,
) -> np.ndarray:
    p = np.asarray(momentum, dtype=float)
    if p.shape != (3,):
        raise ValueError("momentum must have three components")

    h = BETA * wilson_mass(p, mass, wilson_r)
    for i in range(3):
        h = h + ALPHA[i] * math.sin(float(p[i]))
    return h


def analytic_positive_energy(
    momentum: tuple[float, float, float] | np.ndarray,
    mass: float = 0.0,
    wilson_r: float = 1.0,
) -> float:
    p = np.asarray(momentum, dtype=float)
    kinetic = float(np.sum(np.sin(p)**2))
    wm = wilson_mass(p, mass, wilson_r)
    return math.sqrt(kinetic + wm*wm)


def eigenvalues(
    momentum: tuple[float, float, float] | np.ndarray,
    mass: float = 0.0,
    wilson_r: float = 1.0,
) -> np.ndarray:
    return np.linalg.eigvalsh(hamiltonian(momentum, mass, wilson_r))


def brillouin_corners() -> list[tuple[float, float, float]]:
    return [
        tuple(float(v) for v in corner)
        for corner in itertools.product((0.0, math.pi), repeat=3)
    ]


def zero_energy_corners(
    mass: float = 0.0,
    wilson_r: float = 0.0,
    tolerance: float = 1e-12,
) -> list[tuple[float, float, float]]:
    out = []
    for p in brillouin_corners():
        if analytic_positive_energy(p, mass, wilson_r) <= tolerance:
            out.append(p)
    return out


def doubler_corner_mass(
    number_of_pi_components: int,
    mass: float = 0.0,
    wilson_r: float = 1.0,
) -> float:
    if not 0 <= number_of_pi_components <= 3:
        raise ValueError("number_of_pi_components must be 0..3")
    return abs(mass + 2.0*wilson_r*number_of_pi_components)
