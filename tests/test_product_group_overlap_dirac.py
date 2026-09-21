import numpy as np

from src.nonabelian_overlap_dirac_lattice import (
    identity_links as matrix_identity_links,
)
from src.product_group_anomaly_ledger import (
    ProductWeylMultiplet,
)
from src.product_group_overlap_dirac import (
    covariance_residual,
    gamma5_hermiticity_residual,
    ginsparg_wilson_residual,
    internal_dimension,
    overlap_dirac_matrix,
    product_representation_links,
)
from src.su2_lattice_gauge import random_su2
from src.su3_lattice_gauge import random_su3


def _site_transforms(shape, color_dim, seed):
    rng = np.random.default_rng(seed)
    out = np.empty(
        shape + (color_dim, color_dim),
        dtype=complex,
    )
    for coord in np.ndindex(shape):
        if color_dim == 2:
            out[coord] = random_su2(rng)
        elif color_dim == 3:
            out[coord] = random_su3(rng)
        else:
            raise ValueError("unsupported test color dimension")
    return out


def _zero_u1(shape):
    return np.zeros(
        (4,) + shape,
        dtype=float,
    )


def test_internal_dimensions_match_product_representations():
    q = ProductWeylMultiplet(
        "Q",
        "fundamental",
        "doublet",
        1.0 / 6.0,
        1,
    )
    u = ProductWeylMultiplet(
        "u",
        "fundamental",
        "singlet",
        2.0 / 3.0,
        -1,
    )
    l = ProductWeylMultiplet(
        "L",
        "singlet",
        "doublet",
        -0.5,
        1,
    )
    e = ProductWeylMultiplet(
        "e",
        "singlet",
        "singlet",
        -1.0,
        -1,
    )

    assert internal_dimension(q) == 6
    assert internal_dimension(u) == 3
    assert internal_dimension(l) == 2
    assert internal_dimension(e) == 1


def test_q_like_product_links_are_unitary():
    shape = (2, 1, 1, 1)
    multiplet = ProductWeylMultiplet(
        "Q",
        "fundamental",
        "doublet",
        1.0 / 6.0,
        1,
    )
    u1 = _zero_u1(shape)
    u2 = matrix_identity_links(
        shape,
        color_dim=2,
    )
    u3 = matrix_identity_links(
        shape,
        color_dim=3,
    )

    links = product_representation_links(
        u1,
        u2,
        u3,
        multiplet,
    )

    identity = np.eye(6)
    for mu in range(4):
        for coord in np.ndindex(shape):
            u = links[(mu,) + coord]
            assert np.allclose(
                u.conj().T @ u,
                identity,
                atol=1e-12,
                rtol=0,
            )


def test_q_like_overlap_is_gauge_covariant_under_all_three_factors():
    shape = (2, 1, 1, 1)
    multiplet = ProductWeylMultiplet(
        "Q",
        "fundamental",
        "doublet",
        1.0 / 6.0,
        1,
    )

    u1 = _zero_u1(shape)
    u2 = matrix_identity_links(
        shape,
        color_dim=2,
    )
    u3 = matrix_identity_links(
        shape,
        color_dim=3,
    )

    rng = np.random.default_rng(3001)
    alpha = rng.normal(
        scale=0.1,
        size=shape,
    )
    g2 = _site_transforms(
        shape,
        2,
        3002,
    )
    g3 = _site_transforms(
        shape,
        3,
        3003,
    )

    residual = covariance_residual(
        u1,
        u2,
        u3,
        alpha,
        g2,
        g3,
        multiplet,
        rho=1.0,
    )

    assert np.linalg.norm(residual) < 5e-9


def test_q_like_overlap_satisfies_ginsparg_wilson_and_gamma5_hermiticity():
    shape = (2, 1, 1, 1)
    multiplet = ProductWeylMultiplet(
        "Q",
        "fundamental",
        "doublet",
        1.0 / 6.0,
        1,
    )
    u1 = _zero_u1(shape)
    u2 = matrix_identity_links(
        shape,
        color_dim=2,
    )
    u3 = matrix_identity_links(
        shape,
        color_dim=3,
    )

    gw = ginsparg_wilson_residual(
        u1,
        u2,
        u3,
        multiplet,
    )
    herm = gamma5_hermiticity_residual(
        u1,
        u2,
        u3,
        multiplet,
    )

    assert np.linalg.norm(gw) < 5e-10
    assert np.linalg.norm(herm) < 5e-10


def test_antifundamental_color_representation_is_gauge_covariant():
    shape = (2, 1, 1, 1)
    multiplet = ProductWeylMultiplet(
        "anti",
        "antifundamental",
        "singlet",
        -1.0 / 3.0,
        1,
    )

    u1 = _zero_u1(shape)
    u3 = matrix_identity_links(
        shape,
        color_dim=3,
    )

    rng = np.random.default_rng(3004)
    alpha = rng.normal(
        scale=0.08,
        size=shape,
    )
    g3 = _site_transforms(
        shape,
        3,
        3005,
    )

    residual = covariance_residual(
        u1,
        None,
        u3,
        alpha,
        None,
        g3,
        multiplet,
    )
    assert np.linalg.norm(residual) < 5e-9


def test_singlet_singlet_case_reduces_to_u1_overlap_size():
    shape = (2, 1, 1, 1)
    multiplet = ProductWeylMultiplet(
        "e",
        "singlet",
        "singlet",
        -1.0,
        -1,
    )
    u1 = _zero_u1(shape)

    d = overlap_dirac_matrix(
        u1,
        None,
        None,
        multiplet,
    )

    assert d.shape == (
        4 * int(np.prod(shape)),
        4 * int(np.prod(shape)),
    )


def test_singlet_singlet_u1_case_is_gauge_covariant():
    shape = (2, 1, 1, 1)
    multiplet = ProductWeylMultiplet(
        "e",
        "singlet",
        "singlet",
        -1.0,
        -1,
    )

    u1 = _zero_u1(shape)
    rng = np.random.default_rng(3006)
    alpha = rng.normal(
        scale=0.1,
        size=shape,
    )

    residual = covariance_residual(
        u1,
        None,
        None,
        alpha,
        None,
        None,
        multiplet,
    )

    assert np.linalg.norm(residual) < 1e-9
