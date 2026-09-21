import math
import numpy as np

from src.clock_space_reciprocity import (
    clock_rate_ratio,
    local_causal_speed_ratio,
    optical_index,
    point_source_light_deflection,
    reciprocity_gamma,
    reciprocity_metric_diagonal,
    weak_field_ppn_parameters,
    weak_massive_acceleration,
)


def test_reciprocity_forces_gamma_one():
    gamma = reciprocity_gamma()
    assert gamma == 1.0
    for psi in (-0.2, 0.0, 0.3, 1.1):
        assert math.isclose(
            local_causal_speed_ratio(psi, gamma),
            1.0,
            rel_tol=0,
            abs_tol=1e-15,
        )


def test_nonunit_gamma_changes_local_speed_for_nonzero_potential():
    assert not math.isclose(
        local_causal_speed_ratio(0.3, 0.8),
        1.0,
        rel_tol=0,
        abs_tol=1e-12,
    )


def test_metric_has_expected_exponential_clock_and_space_factors():
    psi = 0.2
    metric = reciprocity_metric_diagonal(psi, causal_speed=2.0)
    assert math.isclose(metric[0], -4.0 * math.exp(-0.4), abs_tol=1e-15)
    assert np.allclose(metric[1:], math.exp(0.4), atol=1e-15, rtol=0)


def test_optical_index_is_space_over_clock_rate():
    psi = 0.17
    expected = math.exp(psi) / clock_rate_ratio(psi)
    assert math.isclose(optical_index(psi), expected, abs_tol=1e-15)


def test_weak_field_ppn_coefficients_are_beta_gamma_one():
    beta, gamma = weak_field_ppn_parameters()
    assert beta == 1.0
    assert gamma == 1.0


def test_point_source_massive_acceleration_points_inward():
    grad_psi = np.array([-0.2, 0.0, 0.0])
    acceleration = weak_massive_acceleration(grad_psi, causal_speed=3.0)
    assert acceleration[0] < 0
    assert np.allclose(acceleration, 9.0 * grad_psi)


def test_reciprocity_light_deflection_is_four_mu_over_b():
    mu = 2.3e-6
    b = 5.0
    assert math.isclose(
        point_source_light_deflection(mu, b),
        4.0 * mu / b,
        rel_tol=0,
        abs_tol=1e-18,
    )
