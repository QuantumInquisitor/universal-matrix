import math
import numpy as np

from src.scale_transfer import (
    crossing_carrier,
    directional_label,
    quadratic_content,
    transfer_chain,
    transfer_pair,
)


def test_transfer_vanishes_at_polarity_extrema():
    pair = (1.2, -0.4)
    assert transfer_pair(*pair, phase=0.0, coupling=2.0, dt=0.3) == pair
    a, b = transfer_pair(*pair, phase=math.pi, coupling=2.0, dt=0.3)
    assert math.isclose(a, pair[0], abs_tol=1e-15)
    assert math.isclose(b, pair[1], abs_tol=1e-15)


def test_neutral_crossing_is_maximal_activation():
    assert abs(crossing_carrier(math.pi / 2.0)) == 1.0
    assert abs(crossing_carrier(3.0 * math.pi / 2.0)) == 1.0


def test_pair_transfer_conserves_quadratic_content():
    before = quadratic_content([0.7, -1.3])
    after_pair = transfer_pair(
        0.7,
        -1.3,
        phase=math.pi / 2.0,
        coupling=0.8,
        dt=0.17,
    )
    after = quadratic_content(after_pair)
    assert math.isclose(before, after, rel_tol=0, abs_tol=1e-14)


def test_reversing_transition_phase_reverses_pair_rotation():
    original = (0.9, 0.2)
    forward = transfer_pair(
        *original,
        phase=math.pi / 2.0,
        coupling=0.6,
        dt=0.4,
    )
    recovered = transfer_pair(
        *forward,
        phase=3.0 * math.pi / 2.0,
        coupling=0.6,
        dt=0.4,
    )
    assert np.allclose(recovered, original, atol=1e-14, rtol=0)


def test_chain_transfer_conserves_global_quadratic_content():
    amplitudes = [1.0, -0.3, 0.8, 0.2, -0.5]
    phases = [
        math.pi / 2.0,
        math.pi / 4.0,
        3.0 * math.pi / 2.0,
        0.0,
    ]
    before = quadratic_content(amplitudes)
    after_values = transfer_chain(
        amplitudes,
        phases,
        coupling=0.7,
        dt=0.11,
    )
    after = quadratic_content(after_values)
    assert math.isclose(before, after, rel_tol=0, abs_tol=1e-13)


def test_direction_labels_follow_transition_carrier():
    assert directional_label(0.0) == "no-scale-transfer"
    assert directional_label(math.pi / 2.0) == "micro-to-macro"
    assert directional_label(3.0 * math.pi / 2.0) == "macro-to-micro"
