import math

import numpy as np

from src.canonical_polarity_clock import (
    POLARITY_PHASE_PER_ROUTING_TICK,
    polarity_phase_from_tick,
)
from src.canonical_scale_transfer import (
    alternating_polarity_carrier,
    alternating_transfer_carrier,
    canonical_transfer_angle,
    canonical_transfer_chain,
    canonical_transfer_pair,
    conservation_residual,
    scale_orientation,
)
from src.scale_transfer import quadratic_content


def test_scale_orientation_alternates_by_layer():
    assert [scale_orientation(i) for i in range(6)] == [1, -1, 1, -1, 1, -1]


def test_adjacent_layers_have_opposite_polarity_and_transfer_carriers():
    phase = 0.37
    assert math.isclose(
        alternating_polarity_carrier(phase, 0),
        -alternating_polarity_carrier(phase, 1),
        abs_tol=1e-15,
    )
    assert math.isclose(
        alternating_transfer_carrier(phase, 0),
        -alternating_transfer_carrier(phase, 1),
        abs_tol=1e-15,
    )


def test_canonical_transfer_vanishes_at_polarity_extrema():
    assert abs(canonical_transfer_angle(0.0, 0)) < 1e-15
    assert abs(canonical_transfer_angle(math.pi, 0)) < 1e-15


def test_neutral_crossing_uses_exact_canonical_tick_angle():
    assert math.isclose(
        canonical_transfer_angle(math.pi / 2.0, 0),
        POLARITY_PHASE_PER_ROUTING_TICK,
        rel_tol=0,
        abs_tol=1e-15,
    )
    assert math.isclose(
        canonical_transfer_angle(math.pi / 2.0, 1),
        -POLARITY_PHASE_PER_ROUTING_TICK,
        rel_tol=0,
        abs_tol=1e-15,
    )


def test_one_tick_neutral_transfer_matches_rotation():
    lower, upper = canonical_transfer_pair(
        1.0,
        0.0,
        phase=math.pi / 2.0,
        lower_layer_index=0,
    )
    angle = POLARITY_PHASE_PER_ROUTING_TICK
    assert math.isclose(lower, math.cos(angle), abs_tol=1e-15)
    assert math.isclose(upper, math.sin(angle), abs_tol=1e-15)


def test_transition_reversal_exactly_undoes_pair_rotation():
    original = (0.8, -0.35)
    forward = canonical_transfer_pair(
        *original,
        phase=math.pi / 2.0,
        lower_layer_index=0,
    )
    recovered = canonical_transfer_pair(
        *forward,
        phase=3.0 * math.pi / 2.0,
        lower_layer_index=0,
    )
    assert np.allclose(recovered, original, rtol=0, atol=1e-14)


def test_full_canonical_clock_cycle_closes_single_edge_transfer():
    state = (0.91, -0.27)
    original = state
    for tick in range(36):
        state = canonical_transfer_pair(
            *state,
            phase=polarity_phase_from_tick(tick),
            lower_layer_index=0,
        )
    assert np.allclose(state, original, rtol=0, atol=1e-13)


def test_chain_preserves_global_quadratic_content():
    amplitudes = [1.0, -0.3, 0.8, 0.2, -0.5]
    phases = [
        math.pi / 2.0,
        math.pi / 4.0,
        3.0 * math.pi / 2.0,
        0.0,
    ]
    before = quadratic_content(amplitudes)
    after_values = canonical_transfer_chain(amplitudes, phases)
    after = quadratic_content(after_values)
    assert math.isclose(before, after, rel_tol=0, abs_tol=1e-13)
    assert abs(conservation_residual(amplitudes, after_values)) < 1e-13


def test_invalid_layer_and_tick_fraction_are_rejected():
    try:
        scale_orientation(-1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative layer index should fail")

    try:
        canonical_transfer_angle(0.5, 0, tick_fraction=-0.1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative tick_fraction should fail")
