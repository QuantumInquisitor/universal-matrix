import numpy as np

from src.ginsparg_wilson_chirality import (
    chiral_projectors,
    covariance_residual,
    index_identity_residual,
    modified_gamma5,
    modified_gamma5_hermiticity_residual,
    modified_gamma5_involution_residual,
    overlap_index,
    overlap_index_from_modified_gamma5,
    projector_residuals,
)
from src.overlap_dirac_reference import (
    GAMMA5,
    overlap_dirac,
)
from src.u1_overlap_dirac_lattice import (
    gamma5_lattice,
    gauge_matrix,
    gauge_transform_links,
    overlap_dirac_matrix,
    zero_links,
)


def test_free_modified_gamma5_is_hermitian_involution():
    d = overlap_dirac(
        (0.21, -0.33, 0.17, 0.44),
        rho=1.0,
    )

    herm = modified_gamma5_hermiticity_residual(
        d,
        GAMMA5,
        rho=1.0,
    )
    inv = modified_gamma5_involution_residual(
        d,
        GAMMA5,
        rho=1.0,
    )

    assert np.linalg.norm(herm) < 1e-12
    assert np.linalg.norm(inv) < 1e-12


def test_free_chiral_projectors_are_exact_projectors():
    d = overlap_dirac(
        (0.15, 0.27, -0.19, 0.31),
        rho=1.1,
    )
    residuals = projector_residuals(
        d,
        GAMMA5,
        rho=1.1,
    )
    assert max(residuals.values()) < 1e-12


def test_projectors_split_modified_chirality_eigenspaces():
    d = overlap_dirac(
        (0.12, -0.24, 0.36, -0.18),
        rho=1.0,
    )
    gh = modified_gamma5(d, GAMMA5, 1.0)
    plus, minus = chiral_projectors(
        d,
        GAMMA5,
        1.0,
    )

    assert np.allclose(
        gh @ plus,
        plus,
        atol=1e-12,
        rtol=0,
    )
    assert np.allclose(
        gh @ minus,
        -minus,
        atol=1e-12,
        rtol=0,
    )


def test_free_finite_lattice_index_is_zero():
    shape = (2, 2, 1, 1)
    links = zero_links(shape)
    d = overlap_dirac_matrix(
        links,
        rho=1.0,
    )
    g5 = gamma5_lattice(shape)

    index = overlap_index(
        d,
        g5,
        rho=1.0,
    )
    index2 = overlap_index_from_modified_gamma5(
        d,
        g5,
        rho=1.0,
    )

    assert abs(index) < 1e-10
    assert abs(index2) < 1e-10
    assert abs(
        index_identity_residual(
            d,
            g5,
            rho=1.0,
        )
    ) < 1e-10


def test_u1_modified_chirality_is_gauge_covariant():
    shape = (2, 2, 1, 1)
    rng = np.random.default_rng(1901)

    links = rng.normal(
        scale=0.03,
        size=(4,) + shape,
    )
    alpha = rng.normal(
        scale=0.15,
        size=shape,
    )

    d = overlap_dirac_matrix(
        links,
        rho=1.0,
    )
    transformed_links = gauge_transform_links(
        links,
        alpha,
    )
    d2 = overlap_dirac_matrix(
        transformed_links,
        rho=1.0,
    )
    g = gauge_matrix(alpha)
    g5 = gamma5_lattice(shape)

    residual = covariance_residual(
        d,
        d2,
        g,
        g5,
        rho=1.0,
    )
    assert np.linalg.norm(residual) < 1e-9


def test_u1_projectors_remain_orthogonal_on_weak_field():
    shape = (2, 2, 1, 1)
    rng = np.random.default_rng(1902)
    links = rng.normal(
        scale=0.02,
        size=(4,) + shape,
    )
    d = overlap_dirac_matrix(
        links,
        rho=1.0,
    )
    g5 = gamma5_lattice(shape)

    residuals = projector_residuals(
        d,
        g5,
        rho=1.0,
    )
    assert max(residuals.values()) < 1e-9
