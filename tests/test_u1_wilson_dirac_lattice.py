import math
import numpy as np

from src.u1_wilson_dirac_lattice import (
    apply_wilson_dirac,
    gauge_transform_links,
    gauge_transform_spinor,
    inner_product,
    spinor_density,
)
from src.wilson_dirac_reference import hamiltonian


def test_local_u1_covariance():
    rng = np.random.default_rng(901)
    shape = (3,3,3)
    psi = (
        rng.normal(size=shape + (4,))
        + 1j*rng.normal(size=shape + (4,))
    )
    links = rng.normal(scale=0.3, size=(3,) + shape)
    alpha = rng.normal(size=shape)

    hpsi = apply_wilson_dirac(
        psi,
        links,
        mass=0.2,
        wilson_r=0.9,
    )

    psi2 = gauge_transform_spinor(psi, alpha)
    links2 = gauge_transform_links(links, alpha)
    hpsi2 = apply_wilson_dirac(
        psi2,
        links2,
        mass=0.2,
        wilson_r=0.9,
    )

    expected = gauge_transform_spinor(hpsi, alpha)
    assert np.allclose(hpsi2, expected, atol=1e-10, rtol=0)


def test_spinor_density_is_gauge_invariant():
    rng = np.random.default_rng(902)
    shape = (3,3,3)
    psi = (
        rng.normal(size=shape + (4,))
        + 1j*rng.normal(size=shape + (4,))
    )
    alpha = rng.normal(size=shape)

    assert np.allclose(
        spinor_density(psi),
        spinor_density(gauge_transform_spinor(psi, alpha)),
        atol=1e-12,
        rtol=0,
    )


def test_position_space_operator_is_hermitian():
    rng = np.random.default_rng(903)
    shape = (3,3,3)
    a = (
        rng.normal(size=shape + (4,))
        + 1j*rng.normal(size=shape + (4,))
    )
    b = (
        rng.normal(size=shape + (4,))
        + 1j*rng.normal(size=shape + (4,))
    )
    links = rng.normal(scale=0.2, size=(3,) + shape)

    ha = apply_wilson_dirac(a, links, mass=0.3, wilson_r=1.0)
    hb = apply_wilson_dirac(b, links, mass=0.3, wilson_r=1.0)

    lhs = inner_product(a, hb)
    rhs = inner_product(ha, b)

    assert abs(lhs - rhs) < 1e-10


def test_zero_gauge_plane_wave_matches_momentum_space_hamiltonian():
    shape = (4,4,4)
    momentum = (
        2.0*math.pi/shape[0],
        0.0,
        -2.0*math.pi/shape[2],
    )
    spinor = np.array([1.0, 0.3j, -0.2, 0.5], dtype=complex)

    coords = np.indices(shape, dtype=float)
    phase = (
        momentum[0]*coords[0]
        + momentum[1]*coords[1]
        + momentum[2]*coords[2]
    )
    psi = np.exp(1j*phase)[..., None] * spinor
    links = np.zeros((3,) + shape)

    lattice_result = apply_wilson_dirac(
        psi,
        links,
        mass=0.4,
        wilson_r=0.8,
    )

    hp = hamiltonian(
        momentum,
        mass=0.4,
        wilson_r=0.8,
    )
    expected_spinor = hp @ spinor
    expected = np.exp(1j*phase)[..., None] * expected_spinor

    assert np.allclose(lattice_result, expected, atol=1e-11, rtol=0)
