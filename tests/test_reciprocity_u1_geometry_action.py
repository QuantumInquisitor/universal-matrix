import math
import numpy as np

from src.reciprocity_u1_geometry_action import (
    canonical_displacement,
    electric_from_displacement,
    gauge_characteristic_speed,
    geometry_scalar_characteristic_speed,
    geometry_source_density_canonical,
    geometry_source_density_velocity_form,
    hamiltonian_density,
    lagrangian_density,
    metric_null_speed,
    source_to_energy_ratio_for_free_gauge_field,
)


def test_legendre_transform_matches_hamiltonian():
    e = np.array([0.3, -0.2, 0.7])
    b = np.array([0.1, 0.4, -0.5])
    psi = 0.23

    d = canonical_displacement(e, psi)
    h = hamiltonian_density(d, b, psi)
    l = lagrangian_density(e, b, psi)

    legendre = float(np.dot(d, e)) - l
    assert math.isclose(h, legendre, rel_tol=0, abs_tol=1e-15)


def test_displacement_conversion_is_invertible():
    e = np.array([1.0, -2.0, 0.5])
    psi = -0.4
    d = canonical_displacement(e, psi)
    recovered = electric_from_displacement(d, psi)
    assert np.allclose(recovered, e, atol=1e-15, rtol=0)


def test_velocity_and_canonical_geometry_sources_agree():
    e = np.array([0.2, 0.5, -0.1])
    b = np.array([0.8, -0.3, 0.4])
    psi = 0.31
    d = canonical_displacement(e, psi)

    s1 = geometry_source_density_velocity_form(e, b, psi)
    s2 = geometry_source_density_canonical(d, b, psi)

    assert math.isclose(s1, s2, rel_tol=0, abs_tol=1e-15)


def test_free_gauge_active_source_is_twice_local_hamiltonian_density():
    d = np.array([0.4, 0.2, -0.6])
    b = np.array([0.1, 0.7, 0.3])
    psi = 0.2

    source = geometry_source_density_canonical(d, b, psi)
    energy = hamiltonian_density(d, b, psi)

    assert math.isclose(source, 2.0*energy, rel_tol=0, abs_tol=1e-15)
    assert math.isclose(
        source_to_energy_ratio_for_free_gauge_field(d, b, psi),
        2.0,
        rel_tol=0,
        abs_tol=1e-15,
    )


def test_all_local_characteristic_speeds_match():
    for psi in (-0.7, 0.0, 0.35, 1.2):
        gauge = gauge_characteristic_speed(psi)
        null = metric_null_speed(psi)
        scalar = geometry_scalar_characteristic_speed(psi)

        assert math.isclose(gauge, null, rel_tol=0, abs_tol=1e-15)
        assert math.isclose(gauge, scalar, rel_tol=0, abs_tol=1e-15)


def test_flat_limit_recovers_standard_maxwell_energy():
    d = np.array([0.3, 0.4, 0.0])
    b = np.array([0.0, 0.0, 0.5])
    h = hamiltonian_density(d, b, psi=0.0)
    expected = 0.5 * (float(np.dot(d,d)) + float(np.dot(b,b)))
    assert math.isclose(h, expected, rel_tol=0, abs_tol=1e-15)
