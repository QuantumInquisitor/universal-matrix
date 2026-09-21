"""Spatially varying reciprocity geometry weights for lattice Yang-Mills.

For the reciprocity metric, continuum Yang-Mills Hamiltonian density is

    H_YM = (1/2) exp(-2 psi) (D^2 + B^2).

A gauge-invariant lattice discretization must attach the scalar geometry weight
to gauge-invariant geometric objects without altering their internal group
transformation law.

Convention used here:

Link weight:
    w_l(x,i)
      = exp[-2 * mean(psi(x), psi(x+i))].

Plaquette weight:
    w_p(x,i,j)
      = exp[-2 * mean(
          psi(x),
          psi(x+i),
          psi(x+j),
          psi(x+i+j)
        )].

Weighted Hamiltonian:

    H =
      1/2 sum_links w_l E_i^a E_i^a
      + beta sum_plaquettes w_p [
          1 - (1/N) ReTr P_ij
        ].

Because the weights are ordinary gauge-invariant scalars, local SU(N) gauge
invariance remains exact.

The local geometry source is defined by

    S_psi(x) = - dH / d psi(x).

Since every weight is exp(-2 * arithmetic_mean(psi)), each link contribution
deposits equal source to its two endpoints and each plaquette contribution
deposits equal source to its four corners.

Summing over all sites gives the exact lattice identity

    sum_x S_psi(x) = 2 H.

This matches the continuum free Yang-Mills active-source relation.

The endpoint/corner arithmetic mean is a discretization convention, not a
unique consequence of the canonical 108-state kernel.
"""

from __future__ import annotations

import numpy as np


AXES = (0, 1, 2)
PLANES = ((0, 1), (1, 2), (2, 0))


def shift(
    array: np.ndarray,
    axis: int,
    step: int = 1,
) -> np.ndarray:
    return np.roll(array, -step, axis=axis)


def link_psi_average(
    psi: np.ndarray,
    axis: int,
) -> np.ndarray:
    p = np.asarray(psi, dtype=float)
    if p.ndim != 3:
        raise ValueError("psi must be 3D")
    if axis not in AXES:
        raise ValueError("axis must be 0,1,2")
    return 0.5 * (p + shift(p, axis))


def link_weight(
    psi: np.ndarray,
    axis: int,
) -> np.ndarray:
    return np.exp(-2.0 * link_psi_average(psi, axis))


def plaquette_psi_average(
    psi: np.ndarray,
    axis_i: int,
    axis_j: int,
) -> np.ndarray:
    if axis_i == axis_j:
        raise ValueError("plaquette axes must be distinct")
    p = np.asarray(psi, dtype=float)
    pi = shift(p, axis_i)
    pj = shift(p, axis_j)
    pij = shift(pi, axis_j)
    return 0.25 * (p + pi + pj + pij)


def plaquette_weight(
    psi: np.ndarray,
    axis_i: int,
    axis_j: int,
) -> np.ndarray:
    return np.exp(
        -2.0
        * plaquette_psi_average(
            psi,
            axis_i,
            axis_j,
        )
    )


def su2_plaquette(
    links: np.ndarray,
    axis_i: int,
    axis_j: int,
) -> np.ndarray:
    ui = links[axis_i]
    uj = links[axis_j]
    uj_i = shift(uj, axis_i)
    ui_j = shift(ui, axis_j)
    return (
        ui
        @ uj_i
        @ np.swapaxes(ui_j.conj(), -1, -2)
        @ np.swapaxes(uj.conj(), -1, -2)
    )


def weighted_sun_energy(
    links: np.ndarray,
    electric: np.ndarray,
    psi: np.ndarray,
    beta: float,
    group_dimension: int,
) -> float:
    """Weighted SU(N) Hamiltonian for N=2 or N=3."""
    if beta < 0:
        raise ValueError("beta must be non-negative")
    if group_dimension not in (2, 3):
        raise ValueError("group_dimension must be 2 or 3")

    p = np.asarray(psi, dtype=float)
    shape = p.shape
    if links.shape[:4] != (3,) + shape:
        raise ValueError("link shape mismatch")
    if links.shape[-2:] != (
        group_dimension,
        group_dimension,
    ):
        raise ValueError("link matrix dimension mismatch")
    if electric.shape[:4] != (3,) + shape:
        raise ValueError("electric shape mismatch")

    energy = 0.0

    for axis in AXES:
        e2 = np.sum(
            np.asarray(electric[axis], dtype=float) ** 2,
            axis=-1,
        )
        energy += 0.5 * float(
            np.sum(link_weight(p, axis) * e2)
        )

    for i, j in PLANES:
        plaquette = su2_plaquette(links, i, j)
        trace = np.trace(
            plaquette,
            axis1=-2,
            axis2=-1,
        ).real
        density = (
            1.0
            - trace / float(group_dimension)
        )
        energy += beta * float(
            np.sum(
                plaquette_weight(p, i, j)
                * density
            )
        )

    return energy


def weighted_su2_energy(
    links: np.ndarray,
    electric: np.ndarray,
    psi: np.ndarray,
    beta: float,
) -> float:
    return weighted_sun_energy(
        links,
        electric,
        psi,
        beta,
        group_dimension=2,
    )


def weighted_su3_energy(
    links: np.ndarray,
    electric: np.ndarray,
    psi: np.ndarray,
    beta: float,
) -> float:
    return weighted_sun_energy(
        links,
        electric,
        psi,
        beta,
        group_dimension=3,
    )


def local_geometry_source(
    links: np.ndarray,
    electric: np.ndarray,
    psi: np.ndarray,
    beta: float,
    group_dimension: int,
) -> np.ndarray:
    """Return exact site source -dH/dpsi for the weighting convention."""
    p = np.asarray(psi, dtype=float)
    shape = p.shape
    source = np.zeros(shape, dtype=float)

    # Link energy h_l = 1/2 w_l E^2.
    # -d h_l / d psi_endpoint = h_l for either endpoint because
    # w_l = exp[-(psi_x + psi_y)].
    for axis in AXES:
        e2 = np.sum(
            np.asarray(electric[axis], dtype=float) ** 2,
            axis=-1,
        )
        h_link = 0.5 * link_weight(p, axis) * e2
        source += h_link
        source += np.roll(h_link, 1, axis=axis)

    # Plaquette energy h_p = beta w_p V_p.
    # w_p = exp[-(1/2) sum_four_corners psi], so each corner receives h_p/2.
    for i, j in PLANES:
        plaquette = su2_plaquette(links, i, j)
        trace = np.trace(
            plaquette,
            axis1=-2,
            axis2=-1,
        ).real
        density = 1.0 - trace / float(group_dimension)
        h_face = (
            beta
            * plaquette_weight(p, i, j)
            * density
        )
        quarter_source = 0.5 * h_face

        source += quarter_source
        source += np.roll(
            quarter_source,
            1,
            axis=i,
        )
        source += np.roll(
            quarter_source,
            1,
            axis=j,
        )
        source += np.roll(
            np.roll(
                quarter_source,
                1,
                axis=i,
            ),
            1,
            axis=j,
        )

    return source


def source_sum_identity_residual(
    links: np.ndarray,
    electric: np.ndarray,
    psi: np.ndarray,
    beta: float,
    group_dimension: int,
) -> float:
    source = local_geometry_source(
        links,
        electric,
        psi,
        beta,
        group_dimension,
    )
    energy = weighted_sun_energy(
        links,
        electric,
        psi,
        beta,
        group_dimension,
    )
    return float(np.sum(source) - 2.0 * energy)
