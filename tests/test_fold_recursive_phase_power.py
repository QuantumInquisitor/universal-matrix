"""Unit controls for recursive modal phase/current diagnostics."""

import math

import pytest

from scripts.report_fold_recursive_phase_power import (
    phase_from_modal,
    wrap_phase,
)


@pytest.mark.parametrize(
    "displacement,rate,expected_phase,cosine,sine,quarter",
    [
        (1.0, 0.0, 0.0, 1.0, 0.0, 0),
        (0.0, -2.0, math.pi / 2, 0.0, 1.0, 1),
        (-1.0, 0.0, -math.pi, -1.0, 0.0, 2),
        (0.0, 2.0, -math.pi / 2, 0.0, -1.0, 3),
    ],
)
def test_phase_space_quarter_cycle_landmarks(
    displacement,
    rate,
    expected_phase,
    cosine,
    sine,
    quarter,
):
    row = phase_from_modal(displacement, rate, 2.0)
    assert row["phase_rad"] == pytest.approx(expected_phase)
    assert row["cos_projection"] == pytest.approx(cosine)
    assert row["sin_projection"] == pytest.approx(sine)
    assert row["quarter_cycle_index"] == quarter


def test_zero_amplitude_has_no_phase():
    row = phase_from_modal(0.0, 0.0, 1.0)
    assert row["phase_rad"] is None
    assert row["quarter_cycle_index"] is None


@pytest.mark.parametrize(
    "value,expected",
    [
        (0, 0),
        (math.pi, -math.pi),
        (-math.pi, -math.pi),
        (3 * math.pi / 2, -math.pi / 2),
        (-3 * math.pi / 2, math.pi / 2),
    ],
)
def test_phase_wrapping(value, expected):
    assert wrap_phase(value) == pytest.approx(expected)


@pytest.mark.parametrize(
    "args",
    [
        (1, 0, 0),
        (1, 0, -1),
        (float("nan"), 0, 1),
        (1, float("inf"), 1),
    ],
)
def test_invalid_phase_inputs_rejected(args):
    with pytest.raises(ValueError):
        phase_from_modal(*args)
