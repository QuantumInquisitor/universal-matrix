import math

from src.weak_field_ppn_bridge import (
    clock_rate_ratio_from_psi,
    optical_index_from_psi,
    point_source_deflection,
    satisfies_gamma_bound,
    spatial_scale_factor,
)


def test_clock_only_sector_gives_half_gr_light_bending_target():
    mu = 2e-6
    b = 3.0
    clock_only = point_source_deflection(mu, b, gamma_matrix=0.0)
    symmetric = point_source_deflection(mu, b, gamma_matrix=1.0)
    assert math.isclose(symmetric, 2.0 * clock_only, rel_tol=0, abs_tol=0)


def test_gamma_one_gives_four_mu_over_b():
    mu = 1.3e-5
    b = 4.2
    value = point_source_deflection(mu, b, gamma_matrix=1.0)
    assert math.isclose(value, 4.0 * mu / b, rel_tol=0, abs_tol=1e-18)


def test_optical_index_is_clock_and_spatial_product():
    psi = 0.03
    gamma = 0.8
    n = optical_index_from_psi(psi, gamma)
    expected = spatial_scale_factor(psi, gamma) / clock_rate_ratio_from_psi(psi)
    assert math.isclose(n, expected, rel_tol=0, abs_tol=1e-15)


def test_clock_only_corresponds_to_gamma_zero():
    psi = 0.04
    assert math.isclose(
        optical_index_from_psi(psi, 0.0),
        math.exp(psi),
        rel_tol=0,
        abs_tol=1e-15,
    )


def test_cassini_like_gamma_one_is_inside_supplied_interval():
    assert satisfies_gamma_bound(
        gamma_matrix=1.0,
        central_deviation=2.1e-5,
        one_sigma_uncertainty=2.3e-5,
        sigma=1.0,
    )


def test_gamma_zero_is_excluded_by_cassini_like_interval():
    assert not satisfies_gamma_bound(
        gamma_matrix=0.0,
        central_deviation=2.1e-5,
        one_sigma_uncertainty=2.3e-5,
        sigma=5.0,
    )
