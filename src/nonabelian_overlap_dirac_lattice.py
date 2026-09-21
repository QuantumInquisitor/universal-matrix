"""Fundamental-representation non-Abelian overlap Dirac operator.

This module generalizes the repository's compact-U(1) overlap correctness
reference to matrix-valued fundamental links.

Euclidean 4D links:
    U_mu(x) in SU(N_c)

Gauge transformation:
    U_mu(x)
      -> G(x) U_mu(x) G^dagger(x+mu)

Wilson kernel:
    D_W(x,y)
      = 4 r delta_xy
        - 1/2 sum_mu [
            (r-gamma_mu) tensor U_mu(x) delta_{x+mu,y}
            + (r+gamma_mu) tensor U_mu^dagger(x-mu) delta_{x-mu,y}
          ].

The spin-color site vector is ordered as
    (spin, color)
so a hopping block is
    (spin matrix) tensor (color matrix).

Define
    Gamma5 = I_sites tensor gamma5 tensor I_color
    H_W = Gamma5 (D_W - rho I)
    D_ov = rho [I + Gamma5 sign(H_W)].

The resulting operator satisfies, on admissible backgrounds:
- local non-Abelian gauge covariance;
- gamma5 Hermiticity;
- the Ginsparg-Wilson relation.

The dense implementation is a small-lattice correctness reference. It is not a
production solver and does not yet define a chiral gauge measure.
"""

from __future__ import annotations

import numpy as np

try:
    from .overlap_dirac_reference import GAMMA, GAMMA5
    from .u1_overlap_dirac_lattice import matrix_sign_hermitian
except ImportError:
    from overlap_dirac_reference import GAMMA, GAMMA5
    from u1_overlap_dirac_lattice import matrix_sign_hermitian


def site_count(shape: tuple[int, int, int, int]) -> int:
    if len(shape) != 4 or min(shape) < 1:
        raise ValueError("shape must contain four positive dimensions")
    return int(np.prod(shape))


def site_index(
    coord: tuple[int, int, int, int],
    shape: tuple[int, int, int, int],
) -> int:
    return int(np.ravel_multi_index(coord, shape))


def shift_coord(
    coord: tuple[int, int, int, int],
    axis: int,
    step: int,
    shape: tuple[int, int, int, int],
) -> tuple[int, int, int, int]:
    if axis not in (0, 1, 2, 3):
        raise ValueError("axis must be 0,1,2,3")
    out = list(coord)
    out[axis] = (out[axis] + step) % shape[axis]
    return tuple(out)


def infer_color_dimension(links: np.ndarray) -> int:
    a = np.asarray(links, dtype=complex)
    if a.ndim != 7 or a.shape[0] != 4:
        raise ValueError(
            "links must have shape (4,n0,n1,n2,n3,Nc,Nc)"
        )
    if a.shape[-1] != a.shape[-2]:
        raise ValueError("link color matrices must be square")
    if a.shape[-1] < 2:
        raise ValueError("color dimension must be at least two")
    return int(a.shape[-1])


def identity_links(
    shape: tuple[int, int, int, int],
    color_dim: int,
) -> np.ndarray:
    if color_dim < 2:
        raise ValueError("color_dim must be at least two")
    out = np.empty(
        (4,) + shape + (color_dim, color_dim),
        dtype=complex,
    )
    out[...] = np.eye(color_dim, dtype=complex)
    return out


def gauge_transform_links(
    links: np.ndarray,
    site_transform: np.ndarray,
) -> np.ndarray:
    a = np.asarray(links, dtype=complex)
    color_dim = infer_color_dimension(a)
    shape = a.shape[1:5]
    g = np.asarray(site_transform, dtype=complex)

    if g.shape != shape + (color_dim, color_dim):
        raise ValueError("site_transform shape mismatch")

    out = np.empty_like(a)
    for coord in np.ndindex(shape):
        for mu in range(4):
            xp = shift_coord(
                coord,
                mu,
                1,
                shape,
            )
            out[(mu,) + coord] = (
                g[coord]
                @ a[(mu,) + coord]
                @ g[xp].conj().T
            )
    return out


def lattice_gauge_matrix(
    site_transform: np.ndarray,
) -> np.ndarray:
    """Block-diagonal I_spin tensor G(x) in site-major ordering."""
    g = np.asarray(site_transform, dtype=complex)
    if g.ndim != 6 or g.shape[-1] != g.shape[-2]:
        raise ValueError(
            "site_transform must have shape (n0,n1,n2,n3,Nc,Nc)"
        )
    shape = g.shape[:4]
    color_dim = g.shape[-1]
    site_block_dim = 4 * color_dim
    total_dim = site_count(shape) * site_block_dim

    out = np.zeros(
        (total_dim, total_dim),
        dtype=complex,
    )
    i4 = np.eye(4, dtype=complex)

    for coord in np.ndindex(shape):
        site = site_index(coord, shape)
        sl = slice(
            site_block_dim * site,
            site_block_dim * (site + 1),
        )
        out[sl, sl] = np.kron(
            i4,
            g[coord],
        )
    return out


def gamma5_lattice(
    shape: tuple[int, int, int, int],
    color_dim: int,
) -> np.ndarray:
    return np.kron(
        np.eye(site_count(shape), dtype=complex),
        np.kron(
            GAMMA5,
            np.eye(color_dim, dtype=complex),
        ),
    )


def wilson_dirac_matrix(
    links: np.ndarray,
    wilson_r: float = 1.0,
) -> np.ndarray:
    if wilson_r <= 0:
        raise ValueError("wilson_r must be positive")

    a = np.asarray(links, dtype=complex)
    color_dim = infer_color_dimension(a)
    shape = a.shape[1:5]
    sites = site_count(shape)
    block_dim = 4 * color_dim
    dim = sites * block_dim

    d = np.zeros(
        (dim, dim),
        dtype=complex,
    )
    i4 = np.eye(4, dtype=complex)
    ic = np.eye(color_dim, dtype=complex)
    onsite = 4.0 * wilson_r * np.kron(i4, ic)

    for coord in np.ndindex(shape):
        x = site_index(coord, shape)
        xs = slice(
            block_dim * x,
            block_dim * (x + 1),
        )
        d[xs, xs] += onsite

        for mu in range(4):
            xp = shift_coord(
                coord,
                mu,
                1,
                shape,
            )
            xm = shift_coord(
                coord,
                mu,
                -1,
                shape,
            )
            yp = site_index(xp, shape)
            ym = site_index(xm, shape)
            yps = slice(
                block_dim * yp,
                block_dim * (yp + 1),
            )
            yms = slice(
                block_dim * ym,
                block_dim * (ym + 1),
            )

            u_forward = a[(mu,) + coord]
            u_backward = a[(mu,) + xm].conj().T

            spin_forward = (
                wilson_r * i4 - GAMMA[mu]
            )
            spin_backward = (
                wilson_r * i4 + GAMMA[mu]
            )

            d[xs, yps] += (
                -0.5
                * np.kron(
                    spin_forward,
                    u_forward,
                )
            )
            d[xs, yms] += (
                -0.5
                * np.kron(
                    spin_backward,
                    u_backward,
                )
            )

    return d


def hermitian_wilson_matrix(
    links: np.ndarray,
    rho: float = 1.0,
    wilson_r: float = 1.0,
) -> np.ndarray:
    if not 0 < rho < 2.0 * wilson_r:
        raise ValueError(
            "require 0 < rho < 2*wilson_r"
        )

    a = np.asarray(links, dtype=complex)
    color_dim = infer_color_dimension(a)
    shape = a.shape[1:5]
    d = wilson_dirac_matrix(
        a,
        wilson_r,
    )
    g5 = gamma5_lattice(
        shape,
        color_dim,
    )
    return g5 @ (
        d
        - rho * np.eye(
            d.shape[0],
            dtype=complex,
        )
    )


def overlap_dirac_matrix(
    links: np.ndarray,
    rho: float = 1.0,
    wilson_r: float = 1.0,
    spectral_tolerance: float = 1e-10,
) -> np.ndarray:
    a = np.asarray(links, dtype=complex)
    color_dim = infer_color_dimension(a)
    shape = a.shape[1:5]

    h = hermitian_wilson_matrix(
        a,
        rho,
        wilson_r,
    )
    sign_h = matrix_sign_hermitian(
        h,
        spectral_tolerance,
    )
    g5 = gamma5_lattice(
        shape,
        color_dim,
    )
    identity = np.eye(
        h.shape[0],
        dtype=complex,
    )
    return rho * (
        identity + g5 @ sign_h
    )


def ginsparg_wilson_residual(
    links: np.ndarray,
    rho: float = 1.0,
    wilson_r: float = 1.0,
) -> np.ndarray:
    a = np.asarray(links, dtype=complex)
    color_dim = infer_color_dimension(a)
    shape = a.shape[1:5]
    d = overlap_dirac_matrix(
        a,
        rho,
        wilson_r,
    )
    g5 = gamma5_lattice(
        shape,
        color_dim,
    )
    return (
        g5 @ d
        + d @ g5
        - (1.0 / rho)
        * d @ g5 @ d
    )


def gamma5_hermiticity_residual(
    links: np.ndarray,
    rho: float = 1.0,
    wilson_r: float = 1.0,
) -> np.ndarray:
    a = np.asarray(links, dtype=complex)
    color_dim = infer_color_dimension(a)
    shape = a.shape[1:5]
    d = overlap_dirac_matrix(
        a,
        rho,
        wilson_r,
    )
    g5 = gamma5_lattice(
        shape,
        color_dim,
    )
    return (
        d.conj().T
        - g5 @ d @ g5
    )


def covariance_residual(
    links: np.ndarray,
    site_transform: np.ndarray,
    rho: float = 1.0,
    wilson_r: float = 1.0,
) -> np.ndarray:
    d = overlap_dirac_matrix(
        links,
        rho,
        wilson_r,
    )
    transformed_links = gauge_transform_links(
        links,
        site_transform,
    )
    d2 = overlap_dirac_matrix(
        transformed_links,
        rho,
        wilson_r,
    )
    g = lattice_gauge_matrix(
        site_transform,
    )
    return (
        d2
        - g @ d @ g.conj().T
    )


def free_zero_mode_count(
    shape: tuple[int, int, int, int],
    color_dim: int,
    rho: float = 1.0,
    wilson_r: float = 1.0,
    tolerance: float = 1e-9,
) -> int:
    d = overlap_dirac_matrix(
        identity_links(
            shape,
            color_dim,
        ),
        rho,
        wilson_r,
    )
    singular = np.linalg.svd(
        d,
        compute_uv=False,
    )
    return int(
        np.count_nonzero(
            singular < tolerance
        )
    )
