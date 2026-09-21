import numpy as np

from src.u1_overlap_dirac_lattice import zero_links
from src.weyl_measure_curvature import (
    basis_projector,
    curvature_gauge_invariance_residual,
    curvature_imaginary_residual,
    gauge_transport_projector_residual,
    gauge_transport_singular_values,
    measure_curvature,
    projector_reconstruction_residual,
    weyl_basis,
    weyl_projector,
)


def test_weyl_basis_reconstructs_projector():
    links = zero_links((2, 2, 1, 1))
    projector = weyl_projector(
        links,
        chirality=-1,
        rho=1.0,
    )
    basis = weyl_basis(
        links,
        chirality=-1,
        rho=1.0,
    )

    assert projector_reconstruction_residual(
        projector,
        basis,
    ) < 1e-9
    assert np.allclose(
        basis.conj().T @ basis,
        np.eye(basis.shape[1]),
        atol=1e-10,
        rtol=0,
    )
    assert np.allclose(
        basis_projector(basis),
        projector,
        atol=1e-9,
        rtol=0,
    )


def test_gauge_related_weyl_projectors_transform_covariantly():
    shape = (2, 2, 1, 1)
    rng = np.random.default_rng(2001)
    links = rng.normal(
        scale=0.02,
        size=(4,) + shape,
    )
    alpha = rng.normal(
        scale=0.15,
        size=shape,
    )

    residual = gauge_transport_projector_residual(
        links,
        alpha,
        chirality=-1,
        rho=1.0,
    )
    assert residual < 1e-8


def test_gauge_transport_between_weyl_bases_is_unitary_up_to_basis_choice():
    shape = (2, 2, 1, 1)
    rng = np.random.default_rng(2002)
    links = rng.normal(
        scale=0.015,
        size=(4,) + shape,
    )
    alpha = rng.normal(
        scale=0.12,
        size=shape,
    )

    singular_values = gauge_transport_singular_values(
        links,
        alpha,
        chirality=-1,
        rho=1.0,
    )

    assert np.allclose(
        singular_values,
        np.ones_like(singular_values),
        atol=1e-8,
        rtol=0,
    )


def test_measure_curvature_is_antisymmetric():
    shape = (2, 2, 1, 1)
    rng = np.random.default_rng(2003)
    links = rng.normal(
        scale=0.01,
        size=(4,) + shape,
    )
    direction_a = rng.normal(
        scale=0.2,
        size=(4,) + shape,
    )
    direction_b = rng.normal(
        scale=0.2,
        size=(4,) + shape,
    )

    fab = measure_curvature(
        links,
        direction_a,
        direction_b,
        chirality=-1,
        rho=1.0,
        epsilon=2e-5,
    )
    fba = measure_curvature(
        links,
        direction_b,
        direction_a,
        chirality=-1,
        rho=1.0,
        epsilon=2e-5,
    )

    assert abs(fab + fba) < 1e-8


def test_measure_curvature_is_real_numerically():
    shape = (2, 2, 1, 1)
    rng = np.random.default_rng(2004)
    links = rng.normal(
        scale=0.01,
        size=(4,) + shape,
    )
    direction_a = rng.normal(
        scale=0.15,
        size=(4,) + shape,
    )
    direction_b = rng.normal(
        scale=0.15,
        size=(4,) + shape,
    )

    residual = curvature_imaginary_residual(
        links,
        direction_a,
        direction_b,
        chirality=-1,
        rho=1.0,
        epsilon=2e-5,
    )

    assert abs(residual) < 1e-8


def test_measure_curvature_is_gauge_invariant_for_fixed_u1_transform():
    shape = (2, 2, 1, 1)
    rng = np.random.default_rng(2005)
    links = rng.normal(
        scale=0.01,
        size=(4,) + shape,
    )
    alpha = rng.normal(
        scale=0.1,
        size=shape,
    )
    direction_a = rng.normal(
        scale=0.1,
        size=(4,) + shape,
    )
    direction_b = rng.normal(
        scale=0.1,
        size=(4,) + shape,
    )

    residual = curvature_gauge_invariance_residual(
        links,
        alpha,
        direction_a,
        direction_b,
        chirality=-1,
        rho=1.0,
        epsilon=2e-5,
    )

    assert abs(residual) < 2e-7
