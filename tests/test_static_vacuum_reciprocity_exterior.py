import math

from src.static_vacuum_reciprocity_exterior import (
    active_energy_from_mu,
    full_static_metric_diagonal,
    mu_from_active_energy,
    outward_flux,
    point_profile_laplacian,
    spherical_vacuum_profile,
)


def test_mu_over_r_is_harmonic_for_every_positive_radius():
    mu = 2.3
    for radius in (0.1, 0.5, 1.0, 7.0, 100.0):
        assert math.isclose(
            point_profile_laplacian(radius, mu),
            0.0,
            rel_tol=0,
            abs_tol=1e-12,
        )


def test_flux_is_radius_independent_and_equals_minus_four_pi_mu():
    mu = 1.7
    expected = -4.0 * math.pi * mu
    for radius in (0.3, 1.0, 4.0, 20.0):
        assert math.isclose(
            outward_flux(radius, mu),
            expected,
            rel_tol=1e-15,
            abs_tol=1e-14,
        )


def test_mu_active_energy_mapping_is_invertible():
    energy = 5.0
    kappa = 0.2
    mu = mu_from_active_energy(energy, kappa)
    assert math.isclose(
        active_energy_from_mu(mu, kappa),
        energy,
        rel_tol=1e-15,
        abs_tol=0,
    )


def test_asymptotic_flatness_profile_tends_to_zero():
    mu = 1.0
    assert spherical_vacuum_profile(1e9, mu) < 1e-8


def test_full_static_metric_has_no_finite_positive_radius_lapse_zero():
    mu = 1.0
    for radius in (0.05, 0.1, 1.0, 10.0):
        metric = full_static_metric_diagonal(radius, mu)
        assert metric[0] < 0.0
        assert metric[0] != 0.0
        assert all(component > 0.0 for component in metric[1:])
