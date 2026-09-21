import numpy as np

from src.u1_overlap_dirac_lattice import (
    covariance_residual,
    free_zero_mode_count,
    gamma5_hermiticity_residual,
    ginsparg_wilson_residual,
    hermitian_wilson_matrix,
    overlap_dirac_matrix,
    wilson_dirac_matrix,
    zero_links,
)


def test_hermitian_wilson_kernel_is_hermitian():
    shape=(2,2,1,1)
    links=zero_links(shape)
    h=hermitian_wilson_matrix(links,rho=1.0)
    assert np.allclose(h,h.conj().T,atol=1e-12,rtol=0)


def test_overlap_ginsparg_wilson_on_small_free_lattice():
    links=zero_links((2,2,1,1))
    residual=ginsparg_wilson_residual(links,rho=1.0)
    assert np.linalg.norm(residual)<1e-10


def test_overlap_gamma5_hermiticity_on_small_free_lattice():
    links=zero_links((2,2,1,1))
    residual=gamma5_hermiticity_residual(links,rho=1.0)
    assert np.linalg.norm(residual)<1e-10


def test_overlap_is_locally_u1_gauge_covariant():
    shape=(2,2,1,1)
    rng=np.random.default_rng(1501)
    links=rng.normal(scale=0.05,size=(4,)+shape)
    alpha=rng.normal(scale=0.2,size=shape)

    residual=covariance_residual(
        links,alpha,rho=1.0
    )
    assert np.linalg.norm(residual)<1e-9


def test_free_2_to_the_4_lattice_has_only_four_spin_zero_modes():
    # One p=0 lattice momentum times four spin components.
    count=free_zero_mode_count(
        (2,2,2,2),
        rho=1.0,
        tolerance=1e-8,
    )
    assert count==4


def test_wilson_kernel_gamma5_hermiticity():
    shape=(2,2,1,1)
    rng=np.random.default_rng(1502)
    links=rng.normal(scale=0.03,size=(4,)+shape)
    d=wilson_dirac_matrix(links)
    from src.u1_overlap_dirac_lattice import gamma5_lattice
    g5=gamma5_lattice(shape)
    assert np.allclose(
        d.conj().T,
        g5@d@g5,
        atol=1e-11,
        rtol=0,
    )


def test_overlap_operator_is_finite_on_weak_random_field():
    shape=(2,2,1,1)
    rng=np.random.default_rng(1503)
    links=rng.normal(scale=0.02,size=(4,)+shape)
    d=overlap_dirac_matrix(links,rho=1.0)
    assert np.all(np.isfinite(d.real))
    assert np.all(np.isfinite(d.imag))
