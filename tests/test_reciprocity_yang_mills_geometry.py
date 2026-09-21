import math
import numpy as np

from src.reciprocity_yang_mills_geometry import (
    adjoint_dimension_su,
    canonical_displacement,
    characteristic_speed,
    electric_from_displacement,
    geometry_source_density,
    hamiltonian_density,
    lagrangian_density,
    source_energy_ratio,
)


def test_su2_and_su3_adjoint_dimensions():
    assert adjoint_dimension_su(2) == 3
    assert adjoint_dimension_su(3) == 8


def test_legendre_transform_matches_yang_mills_hamiltonian():
    rng = np.random.default_rng(1201)
    e = rng.normal(size=(8,3))
    b = rng.normal(size=(8,3))
    psi = 0.27

    d = canonical_displacement(e, psi)
    h = hamiltonian_density(d, b, psi)
    l = lagrangian_density(e, b, psi)

    legendre = float(np.sum(d*e)) - l
    assert math.isclose(h, legendre, rel_tol=0, abs_tol=1e-12)


def test_displacement_conversion_is_invertible_for_nonabelian_components():
    rng = np.random.default_rng(1202)
    e = rng.normal(size=(3,3))
    psi = -0.31
    d = canonical_displacement(e, psi)
    recovered = electric_from_displacement(d, psi)
    assert np.allclose(recovered, e, atol=1e-14, rtol=0)


def test_yang_mills_active_source_is_twice_local_energy():
    rng = np.random.default_rng(1203)
    d = rng.normal(size=(3,3))
    b = rng.normal(size=(3,3))
    psi = 0.11

    s = geometry_source_density(d, b, psi)
    h = hamiltonian_density(d, b, psi)

    assert math.isclose(s, 2.0*h, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(
        source_energy_ratio(d, b, psi),
        2.0,
        rel_tol=0,
        abs_tol=1e-14,
    )


def test_yang_mills_characteristic_speed_matches_reciprocity_null_speed():
    for psi in (-0.8, 0.0, 0.5, 1.1):
        assert math.isclose(
            characteristic_speed(psi),
            math.exp(-2.0*psi),
            rel_tol=0,
            abs_tol=1e-15,
        )


def test_flat_limit_recovers_sum_of_color_field_energies():
    d = np.array(
        [
            [1.0,0.0,0.0],
            [0.0,2.0,0.0],
            [0.0,0.0,3.0],
        ]
    )
    b = np.ones((3,3))*0.5
    expected = 0.5*(float(np.sum(d*d))+float(np.sum(b*b)))
    assert math.isclose(
        hamiltonian_density(d,b,0.0),
        expected,
        rel_tol=0,
        abs_tol=1e-15,
    )
