"""Product-group overlap Dirac operator for SU(3) x SU(2) x U(1) multiplets.

For a Weyl multiplet with color representation R3, weak representation R2,
and Abelian charge Y, the internal link representation is

    U_rep,mu(x)
      = exp(i Y A_mu(x))
        [R3(U3_mu(x)) tensor R2(U2_mu(x))].

Supported representations match product_group_anomaly_ledger.py:
    SU(3): singlet, fundamental, antifundamental
    SU(2): singlet, doublet

Representation maps:
    fundamental      -> U
    antifundamental  -> U*
    singlet          -> 1.

The product link is then fed into the generic fundamental matrix-valued overlap
kernel. If the total internal dimension is one, the implementation reduces to
the existing compact-U(1) overlap operator.

This is a small-lattice Euclidean correctness layer. It does not yet define a
second-quantized Standard Model fermion theory and does not imply that the
Universal Matrix derives the supplied multiplet spectrum.
"""

from __future__ import annotations

import numpy as np

try:
    from .product_group_anomaly_ledger import (
        ProductWeylMultiplet,
    )
    from .u1_overlap_dirac_lattice import (
        gauge_transform_links as u1_gauge_transform_links,
        gauge_matrix as u1_lattice_gauge_matrix,
        gamma5_lattice as u1_gamma5_lattice,
        overlap_dirac_matrix as u1_overlap_dirac_matrix,
    )
    from .nonabelian_overlap_dirac_lattice import (
        gauge_transform_links as matrix_gauge_transform_links,
        lattice_gauge_matrix,
        gamma5_lattice as matrix_gamma5_lattice,
        overlap_dirac_matrix as matrix_overlap_dirac_matrix,
    )
except ImportError:
    from product_group_anomaly_ledger import (
        ProductWeylMultiplet,
    )
    from u1_overlap_dirac_lattice import (
        gauge_transform_links as u1_gauge_transform_links,
        gauge_matrix as u1_lattice_gauge_matrix,
        gamma5_lattice as u1_gamma5_lattice,
        overlap_dirac_matrix as u1_overlap_dirac_matrix,
    )
    from nonabelian_overlap_dirac_lattice import (
        gauge_transform_links as matrix_gauge_transform_links,
        lattice_gauge_matrix,
        gamma5_lattice as matrix_gamma5_lattice,
        overlap_dirac_matrix as matrix_overlap_dirac_matrix,
    )


def _validate_u1_links(
    u1_links: np.ndarray,
) -> tuple[int, int, int, int]:
    a = np.asarray(u1_links, dtype=float)
    if a.ndim != 5 or a.shape[0] != 4:
        raise ValueError(
            "u1_links must have shape (4,n0,n1,n2,n3)"
        )
    return tuple(int(v) for v in a.shape[1:])


def _color_dimension(
    multiplet: ProductWeylMultiplet,
) -> int:
    return multiplet.color_dimension


def _weak_dimension(
    multiplet: ProductWeylMultiplet,
) -> int:
    return multiplet.weak_dimension


def internal_dimension(
    multiplet: ProductWeylMultiplet,
) -> int:
    return (
        _color_dimension(multiplet)
        * _weak_dimension(multiplet)
    )


def _validate_su3_links(
    su3_links: np.ndarray | None,
    shape: tuple[int, int, int, int],
    multiplet: ProductWeylMultiplet,
) -> np.ndarray | None:
    if multiplet.color_rep == "singlet":
        return None

    if su3_links is None:
        raise ValueError(
            "non-singlet color representation requires su3_links"
        )

    u3 = np.asarray(
        su3_links,
        dtype=complex,
    )
    expected = (4,) + shape + (3, 3)
    if u3.shape != expected:
        raise ValueError(
            f"su3_links must have shape {expected}"
        )
    return u3


def _validate_su2_links(
    su2_links: np.ndarray | None,
    shape: tuple[int, int, int, int],
    multiplet: ProductWeylMultiplet,
) -> np.ndarray | None:
    if multiplet.weak_rep == "singlet":
        return None

    if su2_links is None:
        raise ValueError(
            "weak doublet representation requires su2_links"
        )

    u2 = np.asarray(
        su2_links,
        dtype=complex,
    )
    expected = (4,) + shape + (2, 2)
    if u2.shape != expected:
        raise ValueError(
            f"su2_links must have shape {expected}"
        )
    return u2


def color_representation_matrix(
    matrix: np.ndarray | None,
    representation: str,
) -> np.ndarray:
    if representation == "singlet":
        return np.ones(
            (1, 1),
            dtype=complex,
        )
    if matrix is None:
        raise ValueError(
            "non-singlet color representation requires matrix"
        )
    u = np.asarray(matrix, dtype=complex)
    if u.shape != (3, 3):
        raise ValueError(
            "color matrix must be 3x3"
        )
    if representation == "fundamental":
        return u
    if representation == "antifundamental":
        return np.conj(u)
    raise ValueError(
        f"unsupported color representation: {representation}"
    )


def weak_representation_matrix(
    matrix: np.ndarray | None,
    representation: str,
) -> np.ndarray:
    if representation == "singlet":
        return np.ones(
            (1, 1),
            dtype=complex,
        )
    if matrix is None:
        raise ValueError(
            "weak doublet representation requires matrix"
        )
    u = np.asarray(matrix, dtype=complex)
    if u.shape != (2, 2):
        raise ValueError(
            "weak matrix must be 2x2"
        )
    if representation == "doublet":
        return u
    raise ValueError(
        f"unsupported weak representation: {representation}"
    )


def product_representation_links(
    u1_links: np.ndarray,
    su2_links: np.ndarray | None,
    su3_links: np.ndarray | None,
    multiplet: ProductWeylMultiplet,
) -> np.ndarray:
    """Return matrix-valued links for the complete product representation."""
    a = np.asarray(
        u1_links,
        dtype=float,
    )
    shape = _validate_u1_links(a)
    u2 = _validate_su2_links(
        su2_links,
        shape,
        multiplet,
    )
    u3 = _validate_su3_links(
        su3_links,
        shape,
        multiplet,
    )

    dim = internal_dimension(multiplet)
    out = np.empty(
        (4,) + shape + (dim, dim),
        dtype=complex,
    )

    for mu in range(4):
        for coord in np.ndindex(shape):
            color = color_representation_matrix(
                None
                if u3 is None
                else u3[(mu,) + coord],
                multiplet.color_rep,
            )
            weak = weak_representation_matrix(
                None
                if u2 is None
                else u2[(mu,) + coord],
                multiplet.weak_rep,
            )
            phase = np.exp(
                1j
                * multiplet.u1_charge
                * a[(mu,) + coord]
            )
            out[(mu,) + coord] = (
                phase
                * np.kron(
                    color,
                    weak,
                )
            )

    return out


def product_site_transform(
    alpha: np.ndarray,
    su2_site_transform: np.ndarray | None,
    su3_site_transform: np.ndarray | None,
    multiplet: ProductWeylMultiplet,
) -> np.ndarray:
    phase_field = np.asarray(
        alpha,
        dtype=float,
    )
    if phase_field.ndim != 4:
        raise ValueError(
            "alpha must be a 4D lattice field"
        )
    shape = phase_field.shape

    if multiplet.weak_rep == "doublet":
        if su2_site_transform is None:
            raise ValueError(
                "weak doublet requires su2_site_transform"
            )
        g2 = np.asarray(
            su2_site_transform,
            dtype=complex,
        )
        if g2.shape != shape + (2, 2):
            raise ValueError(
                "su2_site_transform shape mismatch"
            )
    else:
        g2 = None

    if multiplet.color_rep != "singlet":
        if su3_site_transform is None:
            raise ValueError(
                "color non-singlet requires su3_site_transform"
            )
        g3 = np.asarray(
            su3_site_transform,
            dtype=complex,
        )
        if g3.shape != shape + (3, 3):
            raise ValueError(
                "su3_site_transform shape mismatch"
            )
    else:
        g3 = None

    dim = internal_dimension(multiplet)
    out = np.empty(
        shape + (dim, dim),
        dtype=complex,
    )

    for coord in np.ndindex(shape):
        color = color_representation_matrix(
            None
            if g3 is None
            else g3[coord],
            multiplet.color_rep,
        )
        weak = weak_representation_matrix(
            None
            if g2 is None
            else g2[coord],
            multiplet.weak_rep,
        )
        phase = np.exp(
            1j
            * multiplet.u1_charge
            * phase_field[coord]
        )
        out[coord] = (
            phase
            * np.kron(
                color,
                weak,
            )
        )

    return out


def overlap_dirac_matrix(
    u1_links: np.ndarray,
    su2_links: np.ndarray | None,
    su3_links: np.ndarray | None,
    multiplet: ProductWeylMultiplet,
    rho: float = 1.0,
    wilson_r: float = 1.0,
    spectral_tolerance: float = 1e-10,
) -> np.ndarray:
    dim = internal_dimension(
        multiplet
    )

    if dim == 1:
        return u1_overlap_dirac_matrix(
            multiplet.u1_charge
            * np.asarray(
                u1_links,
                dtype=float,
            ),
            rho=rho,
            wilson_r=wilson_r,
            spectral_tolerance=spectral_tolerance,
        )

    links = product_representation_links(
        u1_links,
        su2_links,
        su3_links,
        multiplet,
    )
    return matrix_overlap_dirac_matrix(
        links,
        rho=rho,
        wilson_r=wilson_r,
        spectral_tolerance=spectral_tolerance,
    )


def gamma5_lattice(
    u1_links: np.ndarray,
    multiplet: ProductWeylMultiplet,
) -> np.ndarray:
    shape = _validate_u1_links(
        u1_links
    )
    dim = internal_dimension(
        multiplet
    )
    if dim == 1:
        return u1_gamma5_lattice(
            shape
        )
    return matrix_gamma5_lattice(
        shape,
        dim,
    )


def ginsparg_wilson_residual(
    u1_links: np.ndarray,
    su2_links: np.ndarray | None,
    su3_links: np.ndarray | None,
    multiplet: ProductWeylMultiplet,
    rho: float = 1.0,
    wilson_r: float = 1.0,
) -> np.ndarray:
    d = overlap_dirac_matrix(
        u1_links,
        su2_links,
        su3_links,
        multiplet,
        rho,
        wilson_r,
    )
    g5 = gamma5_lattice(
        u1_links,
        multiplet,
    )
    return (
        g5 @ d
        + d @ g5
        - (1.0 / rho)
        * d @ g5 @ d
    )


def gamma5_hermiticity_residual(
    u1_links: np.ndarray,
    su2_links: np.ndarray | None,
    su3_links: np.ndarray | None,
    multiplet: ProductWeylMultiplet,
    rho: float = 1.0,
    wilson_r: float = 1.0,
) -> np.ndarray:
    d = overlap_dirac_matrix(
        u1_links,
        su2_links,
        su3_links,
        multiplet,
        rho,
        wilson_r,
    )
    g5 = gamma5_lattice(
        u1_links,
        multiplet,
    )
    return (
        d.conj().T
        - g5 @ d @ g5
    )


def covariance_residual(
    u1_links: np.ndarray,
    su2_links: np.ndarray | None,
    su3_links: np.ndarray | None,
    alpha: np.ndarray,
    su2_site_transform: np.ndarray | None,
    su3_site_transform: np.ndarray | None,
    multiplet: ProductWeylMultiplet,
    rho: float = 1.0,
    wilson_r: float = 1.0,
) -> np.ndarray:
    d = overlap_dirac_matrix(
        u1_links,
        su2_links,
        su3_links,
        multiplet,
        rho,
        wilson_r,
    )

    transformed_u1 = u1_gauge_transform_links(
        np.asarray(
            u1_links,
            dtype=float,
        ),
        np.asarray(
            alpha,
            dtype=float,
        ),
    )

    if multiplet.weak_rep == "doublet":
        if su2_links is None or su2_site_transform is None:
            raise ValueError(
                "weak doublet gauge transform is incomplete"
            )
        transformed_u2 = matrix_gauge_transform_links(
            su2_links,
            su2_site_transform,
        )
    else:
        transformed_u2 = None

    if multiplet.color_rep != "singlet":
        if su3_links is None or su3_site_transform is None:
            raise ValueError(
                "color gauge transform is incomplete"
            )
        transformed_u3 = matrix_gauge_transform_links(
            su3_links,
            su3_site_transform,
        )
    else:
        transformed_u3 = None

    d2 = overlap_dirac_matrix(
        transformed_u1,
        transformed_u2,
        transformed_u3,
        multiplet,
        rho,
        wilson_r,
    )

    internal_g = product_site_transform(
        alpha,
        su2_site_transform,
        su3_site_transform,
        multiplet,
    )

    if internal_dimension(multiplet) == 1:
        full_g = u1_lattice_gauge_matrix(
            multiplet.u1_charge
            * np.asarray(
                alpha,
                dtype=float,
            )
        )
    else:
        full_g = lattice_gauge_matrix(
            internal_g
        )

    return (
        d2
        - full_g
        @ d
        @ full_g.conj().T
    )
