import math

from src import canonical_kernel as ck
from src.polarity_oscillator import (
    PolarityOscillator,
    canonical_polarity_state,
    coupled_phase_drives,
    discrete_polarity,
    polarity_carrier,
)


def test_half_cycle_applies_canonical_polarity_involution():
    n0 = 17
    state0 = canonical_polarity_state(n0, 0.0, 1)
    state1 = canonical_polarity_state(n0, math.pi, 1)

    assert state0 == (17, 1)
    assert state1 == (ck.polarity(17), -1)


def test_full_cycle_returns_discrete_state():
    n0 = 41
    start = canonical_polarity_state(n0, 0.0, -1)
    full = canonical_polarity_state(n0, 2.0 * math.pi, -1)
    assert start == full


def test_continuous_carrier_changes_sign_through_neutral_crossing():
    assert polarity_carrier(0.0) == 1.0
    assert abs(polarity_carrier(math.pi / 2.0)) < 1e-12
    assert polarity_carrier(math.pi) == -1.0


def test_oscillator_half_period_flips_node_and_polarity():
    osc = PolarityOscillator(
        base_node=5,
        angular_rate=2.0,
        initial_polarity=1,
    )
    half_period = math.pi / osc.angular_rate
    osc.advance(half_period)

    assert osc.node == ck.polarity(5)
    assert osc.polarity == -1
    assert math.isclose(osc.carrier, -1.0, abs_tol=1e-12)


def test_two_half_periods_return_state():
    osc = PolarityOscillator(base_node=23, angular_rate=3.0)
    period = 2.0 * math.pi / osc.angular_rate
    osc.advance(period)

    assert osc.node == 23
    assert osc.polarity == 1
    assert math.isclose(osc.carrier, 1.0, abs_tol=1e-12)


def test_discrete_polarity_tracks_half_cycles():
    assert discrete_polarity(0.1) == 1
    assert discrete_polarity(math.pi + 0.1) == -1
    assert discrete_polarity(2.0 * math.pi + 0.1) == 1


def test_coupled_phase_drive_conserves_net_internal_drive():
    phases = [0.2, 0.8, -0.3, 1.4]
    links = [0.1, -0.2, 0.4]
    drives = coupled_phase_drives(phases, links, coupling=0.7)
    assert abs(sum(drives)) < 1e-12
