import math

from src.canonical_polarity_clock import POLARITY_PHASE_PER_ROUTING_TICK
from src.content_clock import (
    ContentClockState,
    clock_rate_ratio,
    effective_refractive_index,
    effective_tick_duration,
    lapse_factor,
    physical_polarity_angular_frequency,
)


def test_reference_content_has_unit_lapse():
    assert lapse_factor(2.0, coupling=0.7, reference_content=2.0) == 1.0
    assert clock_rate_ratio(2.0, coupling=0.7, reference_content=2.0) == 1.0


def test_positive_excess_content_slows_clock_for_positive_coupling():
    low = clock_rate_ratio(1.0, coupling=0.2, reference_content=0.0)
    high = clock_rate_ratio(3.0, coupling=0.2, reference_content=0.0)
    assert high < low < 1.0


def test_lapse_composition_is_multiplicative():
    g = 0.31
    x = 0.7
    y = 1.2
    lhs = lapse_factor(x + y, coupling=g)
    rhs = lapse_factor(x, coupling=g) * lapse_factor(y, coupling=g)
    assert math.isclose(lhs, rhs, rel_tol=0, abs_tol=1e-14)


def test_canonical_phase_advance_is_not_changed():
    tau0 = 2.5
    content = 1.3
    g = 0.4
    tau = effective_tick_duration(tau0, content, g)
    omega = physical_polarity_angular_frequency(tau0, content, g)
    assert math.isclose(
        omega * tau,
        POLARITY_PHASE_PER_ROUTING_TICK,
        rel_tol=0,
        abs_tol=1e-15,
    )


def test_refractive_index_matches_inverse_speed_ratio():
    content = 1.8
    g = 0.15
    n = effective_refractive_index(content, g)
    rate = clock_rate_ratio(content, g)
    assert math.isclose(n * rate, 1.0, rel_tol=0, abs_tol=1e-15)


def test_weak_content_limit_matches_linear_term():
    g = 0.2
    x = 1e-6
    exact = lapse_factor(x, coupling=g)
    linear = 1.0 + g * x
    assert abs(exact - linear) < 1e-12


def test_state_snapshot_is_explicitly_experimental():
    state = ContentClockState(
        local_content=2.0,
        reference_content=1.0,
        coupling=0.1,
        reference_tick_duration=0.5,
    )
    snap = state.snapshot()
    assert snap["lapse_factor"] > 1.0
    assert snap["model_status"] == "experimental_content_clock_not_gravity_law"
