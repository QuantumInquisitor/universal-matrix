"""Free 4D overlap-Dirac / Ginsparg-Wilson reference.

This module provides a mathematically correct chiral lattice-fermion target.

Euclidean massless Wilson kernel:
    D_W(p)
      = i sum_mu gamma_mu sin(p_mu)
        + r sum_mu [1-cos(p_mu)] I.

Define
    A = D_W - rho I

with
    0 < rho < 2r.

For the free operator,
    A^dagger A
      = [sum sin^2(p_mu) + (W-rho)^2] I.

The overlap operator is

    D_ov
      = rho [
          I + A / sqrt(A^dagger A)
        ].

It obeys the Ginsparg-Wilson relation

    gamma5 D + D gamma5
      = (1/rho) D gamma5 D.

At p=0:
    D_ov = 0.

At nonzero Brillouin-zone corners with p_mu in {0,pi}, choosing 0<rho<2r
gives
    D_ov = 2 rho I,

so the Wilson doublers are lifted.

This is a free Euclidean reference operator. It is not yet a full interacting
chiral gauge theory and does not by itself establish anomaly cancellation.
"""

from __future__ import annotations

import itertools
import math
import numpy as np


I2 = np.eye(2, dtype=complex)
I4 = np.eye(4, dtype=complex)
ZERO2 = np.zeros((2,2), dtype=complex)

SIGMA = (
    np.array([[0,1],[1,0]], dtype=complex),
    np.array([[0,-1j],[1j,0]], dtype=complex),
    np.array([[1,0],[0,-1]], dtype=complex),
)


def _block(a,b,c,d):
    return np.block([[a,b],[c,d]])


GAMMA = (
    _block(ZERO2, -1j*SIGMA[0], 1j*SIGMA[0], ZERO2),
    _block(ZERO2, -1j*SIGMA[1], 1j*SIGMA[1], ZERO2),
    _block(ZERO2, -1j*SIGMA[2], 1j*SIGMA[2], ZERO2),
    _block(ZERO2, I2, I2, ZERO2),
)

GAMMA5 = GAMMA[0] @ GAMMA[1] @ GAMMA[2] @ GAMMA[3]


def wilson_term(
    momentum: tuple[float,float,float,float] | np.ndarray,
    wilson_r: float = 1.0,
) -> float:
    p = np.asarray(momentum, dtype=float)
    if p.shape != (4,):
        raise ValueError("momentum must have four components")
    if wilson_r <= 0:
        raise ValueError("wilson_r must be positive")
    return float(wilson_r*np.sum(1.0-np.cos(p)))


def wilson_dirac(
    momentum: tuple[float,float,float,float] | np.ndarray,
    wilson_r: float = 1.0,
) -> np.ndarray:
    p = np.asarray(momentum, dtype=float)
    if p.shape != (4,):
        raise ValueError("momentum must have four components")

    out = wilson_term(p, wilson_r)*I4
    for mu in range(4):
        out = out + 1j*GAMMA[mu]*math.sin(float(p[mu]))
    return out


def overlap_denominator(
    momentum: tuple[float,float,float,float] | np.ndarray,
    rho: float = 1.0,
    wilson_r: float = 1.0,
) -> float:
    if not 0 < rho < 2.0*wilson_r:
        raise ValueError("require 0 < rho < 2*wilson_r")
    p = np.asarray(momentum, dtype=float)
    s2 = float(np.sum(np.sin(p)**2))
    w = wilson_term(p, wilson_r)
    return math.sqrt(s2 + (w-rho)**2)


def overlap_dirac(
    momentum: tuple[float,float,float,float] | np.ndarray,
    rho: float = 1.0,
    wilson_r: float = 1.0,
) -> np.ndarray:
    denom = overlap_denominator(momentum, rho, wilson_r)
    if denom == 0:
        raise ValueError("singular overlap kernel")
    a = wilson_dirac(momentum, wilson_r) - rho*I4
    return rho*(I4 + a/denom)


def ginsparg_wilson_residual(
    momentum: tuple[float,float,float,float] | np.ndarray,
    rho: float = 1.0,
    wilson_r: float = 1.0,
) -> np.ndarray:
    d = overlap_dirac(momentum, rho, wilson_r)
    return (
        GAMMA5@d
        + d@GAMMA5
        - (1.0/rho)*d@GAMMA5@d
    )


def gamma5_hermiticity_residual(
    momentum: tuple[float,float,float,float] | np.ndarray,
    rho: float = 1.0,
    wilson_r: float = 1.0,
) -> np.ndarray:
    d = overlap_dirac(momentum, rho, wilson_r)
    return d.conj().T - GAMMA5@d@GAMMA5


def brillouin_corners() -> list[tuple[float,float,float,float]]:
    return [
        tuple(float(v) for v in p)
        for p in itertools.product((0.0, math.pi), repeat=4)
    ]


def zero_corners(
    rho: float = 1.0,
    wilson_r: float = 1.0,
    tolerance: float = 1e-12,
) -> list[tuple[float,float,float,float]]:
    zeros=[]
    for p in brillouin_corners():
        d=overlap_dirac(p,rho,wilson_r)
        if float(np.linalg.norm(d)) <= tolerance:
            zeros.append(p)
    return zeros


def modified_chiral_matrix(
    momentum: tuple[float,float,float,float] | np.ndarray,
    rho: float = 1.0,
    wilson_r: float = 1.0,
) -> np.ndarray:
    """hat(gamma5)=gamma5*(1-D/rho), the GW-modified chirality operator."""
    d=overlap_dirac(momentum,rho,wilson_r)
    return GAMMA5@(I4-d/rho)
