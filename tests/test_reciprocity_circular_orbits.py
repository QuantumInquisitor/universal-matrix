import math

from src.reciprocity_circular_orbits import (
    circular_orbit_angular_momentum_squared,
    circular_orbit_energy_squared,
    circular_orbit_omega,
    isco_areal_fractional_difference_from_schwarzschild,
    isco_areal_radius,
    isco_dimensionless_frequency,
    isco_frequency_fractional_difference_from_schwarzschild,
    isco_isotropic_radius,
    photon_orbit_isotropic_radius,
    schwarzschild_isco_dimensionless_frequency,
)


def test_photon_orbit_is_at_two_mu():
    assert photon_orbit_isotropic_radius(3.0) == 6.0


def test_isco_is_three_plus_sqrt_five_mu():
    mu = 2.0
    expected = (3.0+math.sqrt(5.0))*mu
    assert math.isclose(
        isco_isotropic_radius(mu),
        expected,
        rel_tol=0,
        abs_tol=1e-15,
    )


def test_isco_satisfies_marginal_stability_polynomial():
    mu = 1.7
    r = isco_isotropic_radius(mu)
    residual = r*r - 6.0*mu*r + 4.0*mu*mu
    assert abs(residual) < 1e-13


def test_isco_areal_radius_is_about_6_point_338_mu():
    ratio = isco_areal_radius(1.0)
    assert math.isclose(
        ratio,
        6.337940264856347,
        rel_tol=0,
        abs_tol=1e-14,
    )


def test_isco_frequency_differs_from_schwarzschild():
    exp_freq = isco_dimensionless_frequency()
    gr_freq = schwarzschild_isco_dimensionless_frequency()

    assert exp_freq < gr_freq
    assert math.isclose(
        exp_freq,
        0.06333263134872662,
        rel_tol=0,
        abs_tol=1e-15,
    )


def test_isco_fractional_differences_are_nonzero():
    assert isco_areal_fractional_difference_from_schwarzschild() > 0.05
    assert isco_frequency_fractional_difference_from_schwarzschild() < -0.06


def test_circular_energy_and_angular_momentum_are_positive_outside_photon_orbit():
    mu = 1.0
    r = 8.0
    assert circular_orbit_energy_squared(r,mu) > 0
    assert circular_orbit_angular_momentum_squared(r,mu) > 0
    assert circular_orbit_omega(r,mu) > 0
