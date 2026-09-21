import numpy as np

from src.nonabelian_overlap_dirac_lattice import (
    covariance_residual,
    free_zero_mode_count,
    gamma5_hermiticity_residual,
    ginsparg_wilson_residual,
    hermitian_wilson_matrix,
    identity_links,
    lattice_gauge_matrix,
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
            raise ValueError("test helper only supports SU2/SU3")
    return out


def test_su2_lattice_gauge_matrix_is_unitary():
    shape = (2, 1, 1, 1)
    transforms = _site_transforms(
        shape,
        color_dim=2,
        seed=2801,
    )
    g = lattice_gauge_matrix(transforms)
    assert np.allclose(
        g.conj().T @ g,
        np.eye(g.shape[0]),
        atol=1e-11,
        rtol=0,
    )


def test_su3_lattice_gauge_matrix_is_unitary():
    shape = (2, 1, 1, 1)
    transforms = _site_transforms(
        shape,
        color_dim=3,
        seed=2802,
    )
    g = lattice_gauge_matrix(transforms)
    assert np.allclose(
        g.conj().T @ g,
        np.eye(g.shape[0]),
        atol=1e-10,
        rtol=0,
    )


def test_su2_hermitian_wilson_kernel_is_hermitian():
    links = identity_links(
        (2, 1, 1, 1),
        color_dim=2,
    )
    h = hermitian_wilson_matrix(
        links,
        rho=1.0,
    )
    assert np.allclose(
        h,
        h.conj().T,
        atol=1e-12,
        rtol=0,
    )


def test_su3_hermitian_wilson_kernel_is_hermitian():
    links = identity_links(
        (2, 1, 1, 1),
        color_dim=3,
    )
    h = hermitian_wilson_matrix(
        links,
        rho=1.0,
    )
    assert np.allclose(
        h,
        h.conj().T,
        atol=1e-12,
        rtol=0,
    )


def test_su2_overlap_is_locally_gauge_covariant():
    shape = (2, 1, 1, 1)
    links = identity_links(
        shape,
        color_dim=2,
    )
    transforms = _site_transforms(
        shape,
        color_dim=2,
        seed=2803,
    )

    residual = covariance_residual(
        links,
        transforms,
        rho=1.0,
    )
    assert np.linalg.norm(residual) < 1e-9


def test_su3_overlap_is_locally_gauge_covariant():
    shape = (2, 1, 1, 1)
    links = identity_links(
        shape,
        color_dim=3,
    )
    transforms = _site_transforms(
        shape,
        color_dim=3,
        seed=2804,
    )

    residual = covariance_residual(
        links,
        transforms,
        rho=1.0,
    )
    assert np.linalg.norm(residual) < 2e-9


def test_su2_overlap_satisfies_ginsparg_wilson_relation():
    links = identity_links(
        (2, 1, 1, 1),
        color_dim=2,
    )
    residual = ginsparg_wilson_residual(
        links,
        rho=1.0,
    )
    assert np.linalg.norm(residual) < 1e-10


def test_su3_overlap_satisfies_ginsparg_wilson_relation():
    links = identity_links(
        (2, 1, 1, 1),
        color_dim=3,
    )
    residual = ginsparg_wilson_residual(
        links,
        rho=1.0,
    )
    assert np.linalg.norm(residual) < 2e-10


def test_su2_overlap_has_gamma5_hermiticity():
    links = identity_links(
        (2, 1, 1, 1),
        color_dim=2,
    )
    residual = gamma5_hermiticity_residual(
        links,
        rho=1.0,
    )
    assert np.linalg.norm(residual) < 1e-10


def test_su3_overlap_has_gamma5_hermiticity():
    links = identity_links(
        (2, 1, 1, 1),
        color_dim=3,
    )
    residual = gamma5_hermiticity_residual(
        links,
        rho=1.0,
    )
    assert np.linalg.norm(residual) < 2e-10


def test_free_su2_overlap_has_four_spin_times_two_color_zero_modes():
    count = free_zero_mode_count(
        (2, 1, 1, 1),
        color_dim=2,
        rho=1.0,
        tolerance=1e-8,
    )
    assert count == 8


def test_free_su3_overlap_has_four_spin_times_three_color_zero_modes():
    count = free_zero_mode_count(
        (2, 1, 1, 1),
        color_dim=3,
        rho=1.0,
        tolerance=1e-8,
    )
    assert count == 12
