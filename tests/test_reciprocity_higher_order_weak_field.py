import math

from src.reciprocity_higher_order_weak_field import (
    exponential_gtt,
    exponential_series_coefficients,
    exponential_spatial_factor,
    isotropic_2pn_delta_exponential,
    isotropic_2pn_delta_schwarzschild,
    leading_spatial_difference_coefficient,
    leading_temporal_difference_coefficient,
    ppn_beta_gamma_exponential,
    schwarzschild_isotropic_gtt,
    schwarzschild_isotropic_spatial_factor,
    schwarzschild_series_coefficients,
)


def test_first_post_newtonian_beta_gamma_match_gr():
    beta, gamma = ppn_beta_gamma_exponential()
    assert beta == 1.0
    assert gamma == 1.0


def test_series_coefficients_match_through_expected_orders():
    exp = exponential_series_coefficients()
    schw = schwarzschild_series_coefficients()

    assert exp["gtt"][:3] == schw["gtt"][:3]
    assert exp["spatial"][:2] == schw["spatial"][:2]

    assert exp["spatial"][2] != schw["spatial"][2]
    assert exp["gtt"][3] != schw["gtt"][3]


def test_2pn_spatial_delta_differs_from_schwarzschild():
    assert math.isclose(
        isotropic_2pn_delta_exponential(),
        4.0/3.0,
        rel_tol=0,
        abs_tol=0,
    )
    assert isotropic_2pn_delta_schwarzschild() == 1.0


def test_leading_difference_coefficients():
    assert leading_spatial_difference_coefficient() == 0.5
    assert math.isclose(
        leading_temporal_difference_coefficient(),
        -1.0/6.0,
        rel_tol=0,
        abs_tol=0,
    )


def test_exact_metrics_are_close_in_very_weak_field():
    u = 1e-6
    assert abs(
        exponential_gtt(u)
        - schwarzschild_isotropic_gtt(u)
    ) < 1e-18

    spatial_difference = (
        exponential_spatial_factor(u)
        - schwarzschild_isotropic_spatial_factor(u)
    )
    assert abs(spatial_difference) < 1e-11
