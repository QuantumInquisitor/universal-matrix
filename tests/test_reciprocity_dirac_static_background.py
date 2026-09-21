import math
import numpy as np

from src.reciprocity_dirac_static_background import (
    apply_static_reciprocity_dirac,
    inner_product,
    local_principal_speed,
    metric_null_coordinate_speed,
)
from src.wilson_dirac_reference import ALPHA, BETA


def test_spatially_varying_operator_is_hermitian():
    rng = np.random.default_rng(1101)
    shape = (4,4,4)
    a = (
        rng.normal(size=shape + (4,))
        + 1j*rng.normal(size=shape + (4,))
    )
    b = (
        rng.normal(size=shape + (4,))
        + 1j*rng.normal(size=shape + (4,))
    )
    psi = rng.normal(scale=0.2, size=shape)

    ha = apply_static_reciprocity_dirac(
        a, psi, mass=0.7
    )
    hb = apply_static_reciprocity_dirac(
        b, psi, mass=0.7
    )

    lhs = inner_product(a, hb)
    rhs = inner_product(ha, b)
    assert abs(lhs-rhs) < 1e-10


def test_constant_background_matches_discrete_plane_wave_dispersion_operator():
    shape = (6,6,6)
    psi0 = 0.3
    mass = 0.8
    mode = (1, 2, -1)
    k = np.array([
        2.0*math.pi*mode[i]/shape[i]
        for i in range(3)
    ])
    spinor = np.array([1.0, 0.2j, -0.3, 0.4], dtype=complex)

    coords = np.indices(shape, dtype=float)
    phase = (
        k[0]*coords[0]
        + k[1]*coords[1]
        + k[2]*coords[2]
    )
    field = np.exp(1j*phase)[...,None]*spinor
    psi = np.full(shape, psi0)

    result = apply_static_reciprocity_dirac(
        field, psi, mass=mass
    )

    h = (
        mass*math.exp(-psi0)*BETA
    ).astype(complex)
    for axis in range(3):
        h += (
            math.exp(-2.0*psi0)
            * math.sin(k[axis])
            * ALPHA[axis]
        )

    expected_spinor = h @ spinor
    expected = np.exp(1j*phase)[...,None]*expected_spinor

    assert np.allclose(
        result,
        expected,
        atol=1e-11,
        rtol=0,
    )


def test_massless_principal_speed_matches_metric_null_speed_pointwise():
    psi = np.array([
        [-0.3, 0.0],
        [0.4, 0.8],
    ])
    assert np.allclose(
        local_principal_speed(psi),
        metric_null_coordinate_speed(psi),
        atol=0,
        rtol=0,
    )


def test_zero_potential_reduces_to_flat_central_dirac_operator():
    rng = np.random.default_rng(1102)
    shape = (4,4,4)
    field = (
        rng.normal(size=shape + (4,))
        + 1j*rng.normal(size=shape + (4,))
    )
    psi = np.zeros(shape)
    mass = 0.5

    result = apply_static_reciprocity_dirac(
        field, psi, mass
    )

    expected = mass*np.einsum(
        "ab,...b->...a", BETA, field
    )
    for axis in range(3):
        forward = np.roll(field, -1, axis=axis)
        backward = np.roll(field, 1, axis=axis)
        p = -1j*(forward-backward)/2.0
        expected += np.einsum(
            "ab,...b->...a", ALPHA[axis], p
        )

    assert np.allclose(
        result,
        expected,
        atol=1e-12,
        rtol=0,
    )
