import math

from src.causal_cone_bridge import (
    fractional_speed_mismatch,
    physical_causal_speed,
    satisfies_speed_bound,
    single_cone_dimensionless_speed,
)


def test_single_cone_speed_matches_sqrt_beta():
    beta = 2.25
    assert single_cone_dimensionless_speed(beta) == 1.5


def test_physical_speed_conversion():
    beta = 1.0
    spacing = 3.0
    time_unit = 2.0
    assert physical_causal_speed(beta, spacing, time_unit) == 1.5


def test_single_cone_has_zero_fractional_mismatch():
    speed = single_cone_dimensionless_speed(1.7)
    assert fractional_speed_mismatch(speed, speed) == 0.0


def test_observational_bound_checker():
    gauge = 1.0
    content = 1.0 + 5e-16
    assert satisfies_speed_bound(
        content,
        gauge,
        lower_fractional_bound=-3e-15,
        upper_fractional_bound=7e-16,
    )


def test_outside_bound_is_rejected():
    assert not satisfies_speed_bound(
        1.0 + 1e-12,
        1.0,
        lower_fractional_bound=-3e-15,
        upper_fractional_bound=7e-16,
    )
