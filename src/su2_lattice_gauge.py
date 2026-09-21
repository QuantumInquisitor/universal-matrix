"""Minimal exact SU(2) lattice gauge prototype.

Links are 2x2 complex SU(2) matrices U_i(x).

Local gauge transformation:
    U_i(x) -> G(x) U_i(x) G^dagger(x+i)

Plaquette:
    P_ij(x)
      = U_i(x)
        U_j(x+i)
        U_i^dagger(x+j)
        U_j^dagger(x)

Wilson action:
    S_W
      = beta * sum_p [
          1 - 1/2 Re Tr P_p
        ].

The implementation uses periodic cubic boundaries for this first prototype.

This is a non-Abelian mathematical gauge sector. It is not yet identified with
the Standard Model weak interaction.
"""

from __future__ import annotations

import math
import numpy as np


AXES = (0, 1, 2)
IDENTITY2 = np.eye(2, dtype=complex)


def su2_from_quaternion(
    a0: float,
    a1: float,
    a2: float,
    a3: float,
) -> np.ndarray:
    """Map a unit quaternion to SU(2)."""
    norm = math.sqrt(a0*a0 + a1*a1 + a2*a2 + a3*a3)
    if norm <= 0:
        raise ValueError("quaternion norm must be positive")
    a0, a1, a2, a3 = (
        a0/norm,
        a1/norm,
        a2/norm,
        a3/norm,
    )
    return np.array(
        [
            [a0 + 1j*a3, a2 + 1j*a1],
            [-a2 + 1j*a1, a0 - 1j*a3],
        ],
        dtype=complex,
    )


def random_su2(rng: np.random.Generator) -> np.ndarray:
    q = rng.normal(size=4)
    return su2_from_quaternion(*q)


def is_su2(matrix: np.ndarray, tolerance: float = 1e-12) -> bool:
    u = np.asarray(matrix, dtype=complex)
    if u.shape != (2, 2):
        return False
    unitary = np.allclose(
        u.conj().T @ u,
        IDENTITY2,
        atol=tolerance,
        rtol=0,
    )
    determinant = np.linalg.det(u)
    return unitary and abs(determinant - 1.0) <= tolerance


def identity_links(shape: tuple[int, int, int]) -> np.ndarray:
    links = np.empty((3,) + shape + (2, 2), dtype=complex)
    links[...] = IDENTITY2
    return links


def random_links(
    shape: tuple[int, int, int],
    rng: np.random.Generator,
) -> np.ndarray:
    links = np.empty((3,) + shape + (2, 2), dtype=complex)
    for axis in AXES:
        for idx in np.ndindex(shape):
            links[(axis,) + idx] = random_su2(rng)
    return links


def forward_index(
    idx: tuple[int, int, int],
    axis: int,
    shape: tuple[int, int, int],
) -> tuple[int, int, int]:
    out = list(idx)
    out[axis] = (out[axis] + 1) % shape[axis]
    return tuple(out)


def plaquette(
    links: np.ndarray,
    idx: tuple[int, int, int],
    i: int,
    j: int,
) -> np.ndarray:
    if i == j or i not in AXES or j not in AXES:
        raise ValueError("plaquette axes must be distinct")
    shape = links.shape[1:4]
    xi = forward_index(idx, i, shape)
    xj = forward_index(idx, j, shape)

    ui = links[(i,) + idx]
    uj_at_i = links[(j,) + xi]
    ui_at_j = links[(i,) + xj]
    uj = links[(j,) + idx]

    return (
        ui
        @ uj_at_i
        @ ui_at_j.conj().T
        @ uj.conj().T
    )


def wilson_action(links: np.ndarray, beta: float = 1.0) -> float:
    if beta < 0:
        raise ValueError("beta must be non-negative")
    shape = links.shape[1:4]
    total = 0.0
    for idx in np.ndindex(shape):
        for i, j in ((0, 1), (1, 2), (2, 0)):
            p = plaquette(links, idx, i, j)
            total += 1.0 - 0.5*float(np.trace(p).real)
    return beta*total


def gauge_transform(
    links: np.ndarray,
    site_transform: np.ndarray,
) -> np.ndarray:
    shape = links.shape[1:4]
    if site_transform.shape != shape + (2, 2):
        raise ValueError("site transform shape mismatch")

    out = np.empty_like(links)
    for axis in AXES:
        for idx in np.ndindex(shape):
            xp = forward_index(idx, axis, shape)
            out[(axis,) + idx] = (
                site_transform[idx]
                @ links[(axis,) + idx]
                @ site_transform[xp].conj().T
            )
    return out


def random_site_gauge_transform(
    shape: tuple[int, int, int],
    rng: np.random.Generator,
) -> np.ndarray:
    out = np.empty(shape + (2, 2), dtype=complex)
    for idx in np.ndindex(shape):
        out[idx] = random_su2(rng)
    return out


def plaquette_trace(
    links: np.ndarray,
    idx: tuple[int, int, int],
    i: int,
    j: int,
) -> float:
    return float(np.trace(plaquette(links, idx, i, j)).real)
