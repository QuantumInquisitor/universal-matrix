import math

from src.reciprocity_second_order_light_deflection import (
    orbit_x0,
    orbit_x1,
    orbit_x2,
    reciprocity_deflection_second_order,
    schwarzschild_deflection_second_order,
    second_order_coefficient_reciprocity,
    second_order_coefficient_schwarzschild,
    second_order_difference_coefficient,
    turning_point_series,
)


def _second_derivative(function, x, h=1e-5):
    return (function(x+h)-2*function(x)+function(x-h))/h**2


def test_order_zero_orbit_equation():
    for phi in (-0.7, 0.0, 0.6):
        residual = _second_derivative(orbit_x0, phi) + orbit_x0(phi)
        assert abs(residual) < 1e-5


def test_order_one_orbit_equation():
    for phi in (-0.7, 0.0, 0.6):
        residual = _second_derivative(orbit_x1, phi) + orbit_x1(phi)
        assert abs(residual - 2.0) < 1e-5


def test_order_two_orbit_equation():
    for phi in (-0.7, 0.0, 0.6):
        residual = _second_derivative(orbit_x2, phi) + orbit_x2(phi)
        expected = 8.0*math.cos(phi)
        assert abs(residual-expected) < 2e-4


def test_turning_point_series_satisfies_equation_through_second_order():
    eps = 1e-4
    xt = turning_point_series(eps)
    residual = xt*xt - math.exp(4.0*eps*xt)
    assert abs(residual) < 1e-11


def test_second_order_deflection_coefficients():
    assert math.isclose(
        second_order_coefficient_reciprocity(),
        4.0*math.pi,
        rel_tol=0,
        abs_tol=0,
    )
    assert math.isclose(
        second_order_coefficient_schwarzschild(),
        15.0*math.pi/4.0,
        rel_tol=0,
        abs_tol=0,
    )
    assert math.isclose(
        second_order_difference_coefficient(),
        math.pi/4.0,
        rel_tol=0,
        abs_tol=0,
    )


def test_both_theories_share_leading_four_mu_over_b():
    mu = 1e-8
    b = 1.0
    exp_angle = reciprocity_deflection_second_order(mu,b)
    gr_angle = schwarzschild_deflection_second_order(mu,b)

    assert abs(exp_angle - 4.0*mu/b) < 1e-14
    assert abs(gr_angle - 4.0*mu/b) < 1e-14
    assert exp_angle > gr_angle
