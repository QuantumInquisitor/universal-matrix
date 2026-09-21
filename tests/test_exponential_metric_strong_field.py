import math

from src.exponential_metric_strong_field import (
    areal_radius,
    critical_impact_parameter,
    has_finite_radius_horizon,
    photon_sphere_areal_radius,
    photon_sphere_isotropic_radius,
    shadow_scale_fractional_difference_from_schwarzschild,
    throat_areal_radius,
    throat_isotropic_radius,
)


def test_areal_radius_has_minimum_at_mu():
    mu = 2.0
    r0 = throat_isotropic_radius(mu)
    center = areal_radius(r0, mu)
    left = areal_radius(0.9 * r0, mu)
    right = areal_radius(1.1 * r0, mu)

    assert center < left
    assert center < right
    assert math.isclose(center, throat_areal_radius(mu), rel_tol=0, abs_tol=1e-14)


def test_no_finite_radius_horizon():
    assert not has_finite_radius_horizon(1.0)


def test_photon_sphere_is_at_two_mu_in_isotropic_radius():
    assert photon_sphere_isotropic_radius(3.0) == 6.0


def test_photon_sphere_areal_radius():
    mu = 1.0
    expected = 2.0 * math.exp(0.5)
    assert math.isclose(
        photon_sphere_areal_radius(mu),
        expected,
        rel_tol=0,
        abs_tol=1e-15,
    )


def test_critical_impact_parameter_is_two_e_mu():
    mu = 1.7
    assert math.isclose(
        critical_impact_parameter(mu),
        2.0 * math.e * mu,
        rel_tol=0,
        abs_tol=1e-15,
    )


def test_shadow_scale_differs_from_schwarzschild_by_about_five_percent():
    difference = shadow_scale_fractional_difference_from_schwarzschild(1.0)
    assert 0.04 < difference < 0.05
