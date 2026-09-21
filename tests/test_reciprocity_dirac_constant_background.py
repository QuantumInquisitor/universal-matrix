import math
import numpy as np

from src.reciprocity_dirac_constant_background import (
    geometry_source_from_stationary_total,
    hamiltonian,
    massless_group_speed,
    metric_null_coordinate_speed,
    positive_energy,
    rest_coordinate_energy,
    rest_local_energy,
)


def test_hamiltonian_spectrum_matches_analytic_dispersion():
    p = np.array([0.3, -0.5, 0.7])
    mass = 1.2
    psi = 0.25
    h = hamiltonian(p, mass, psi)
    values = np.linalg.eigvalsh(h)
    e = positive_energy(p, mass, psi)

    assert np.allclose(
        values,
        [-e, -e, e, e],
        atol=1e-12,
        rtol=0,
    )


def test_massless_dirac_speed_matches_metric_null_speed():
    for psi in (-0.7, 0.0, 0.2, 0.9):
        assert math.isclose(
            massless_group_speed(psi),
            metric_null_coordinate_speed(psi),
            rel_tol=0,
            abs_tol=1e-15,
        )


def test_rest_coordinate_energy_redshifts_with_clock_lapse():
    mass = 2.3
    psi = 0.4
    assert math.isclose(
        rest_coordinate_energy(mass, psi),
        mass * math.exp(-psi),
        rel_tol=0,
        abs_tol=1e-15,
    )


def test_local_static_observer_measures_unshifted_rest_mass():
    for psi in (-0.5, 0.0, 0.6):
        assert math.isclose(
            rest_local_energy(1.7, psi),
            1.7,
            rel_tol=0,
            abs_tol=1e-15,
        )


def test_stationary_laue_spinor_composite_sources_total_energy():
    energy = 11.0
    stress = np.zeros((3,3))
    assert geometry_source_from_stationary_total(
        energy, stress
    ) == energy
