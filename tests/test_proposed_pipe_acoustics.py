import math
from dataclasses import replace

import numpy as np
import pytest

from src.proposed_pipe_acoustics import PipeAcoustics


@pytest.mark.parametrize("left,right,expected", [
    ("open", "open", [171.5, 343, 514.5]),
    ("closed", "open", [85.75, 257.25, 428.75]),
    ("open", "closed", [85.75, 257.25, 428.75]),
    ("closed", "closed", [0, 171.5, 343]),
])
def test_analytic_boundary_conditions(left, right, expected):
    pipe = PipeAcoustics(1, 343, left, right)
    np.testing.assert_array_equal(pipe.analytic_frequencies_hz(), expected)


@pytest.mark.parametrize("left,right", [("open", "open"), ("closed", "open"), ("closed", "closed")])
def test_three_low_modes_converge_quadratically_to_continuum(left, right):
    pipe = PipeAcoustics(1, 343, left, right)
    exact = pipe.analytic_frequencies_hz(4)
    positive = exact > 0
    errors = []
    for intervals in (16, 32, 64):
        result = pipe.finite_element_modes(intervals=intervals, count=4)
        relative = result.frequencies_hz[positive]/exact[positive] - 1
        assert np.all(relative > 0)
        errors.append(np.max(relative))
    assert 3.9 < errors[0]/errors[1] < 4.1
    assert 3.9 < errors[1]/errors[2] < 4.1
    assert errors[-1] < 0.002


def test_capping_one_end_halves_fundamental_and_gives_odd_harmonics():
    opened = PipeAcoustics(1, 343)
    capped = replace(opened, left_end="closed")
    a, b = opened.analytic_frequencies_hz(), capped.analytic_frequencies_hz()
    assert b[0]/a[0] == 0.5
    np.testing.assert_array_equal(b/b[0], [1, 3, 5])
    n_open = opened.finite_element_modes(intervals=128).frequencies_hz
    n_closed = capped.finite_element_modes(intervals=128).frequencies_hz
    assert abs(n_closed[0]/n_open[0] - 0.5) < 1e-5
    assert n_closed[0] < n_open[0]  # Negative control for a doubled fundamental.


@pytest.mark.parametrize("left,right", [("open", "open"), ("closed", "open"), ("open", "closed"), ("closed", "closed")])
def test_nodal_shapes_match_independent_sine_cosine_modes(left, right):
    pipe = PipeAcoustics(2.5, 330, left, right)
    result = pipe.finite_element_modes(intervals=32, count=3)
    xi = result.positions_m/pipe.length_m
    for mode in range(3):
        if left == right:
            order = mode + (left == "open")
        else:
            order = mode + 0.5
        expected = np.sin(math.pi*order*xi) if left == "open" else np.cos(math.pi*order*xi)
        actual = result.pressure_modes[:, mode]
        actual = actual/np.max(np.abs(actual))
        if np.dot(actual, expected) < 0:
            actual = -actual
        expected /= np.max(np.abs(expected))
        np.testing.assert_allclose(actual, expected, rtol=0, atol=2e-12)
    if left == "open":
        np.testing.assert_array_equal(result.pressure_modes[0], 0)
    if right == "open":
        np.testing.assert_array_equal(result.pressure_modes[-1], 0)
    if left == right == "closed":
        assert result.frequencies_hz[0] == 0
        np.testing.assert_allclose(np.abs(result.pressure_modes[:, 0]), 1, atol=2e-15)


def test_endpoint_reversal_and_length_speed_scaling():
    pipe = PipeAcoustics(1.2, 300, "closed", "open")
    a = pipe.finite_element_modes(intervals=32)
    reflected = replace(pipe, left_end="open", right_end="closed").finite_element_modes(intervals=32)
    scaled_length = replace(pipe, length_m=2.4).finite_element_modes(intervals=32)
    scaled_speed = replace(pipe, sound_speed_m_s=600).finite_element_modes(intervals=32)
    np.testing.assert_allclose(a.frequencies_hz, reflected.frequencies_hz, rtol=5e-13)
    np.testing.assert_array_equal(a.frequencies_hz/2, scaled_length.frequencies_hz)
    np.testing.assert_array_equal(2*a.frequencies_hz, scaled_speed.frequencies_hz)


@pytest.mark.parametrize("changes", [
    {"length_m": 0}, {"length_m": -1}, {"length_m": True}, {"length_m": [1]},
    {"length_m": float("nan")}, {"sound_speed_m_s": float("inf")},
    {"sound_speed_m_s": 0}, {"sound_speed_m_s": 1j}, {"left_end": "sealed"},
    {"right_end": False}, {"length_m": 1e-308, "sound_speed_m_s": 1e308},
    {"length_m": 1e308, "sound_speed_m_s": 1e-308},
])
def test_invalid_pipe_inputs_reject(changes):
    with pytest.raises(ValueError):
        replace(PipeAcoustics(1, 343), **changes)


@pytest.mark.parametrize("count", (True, 0, -1, 2.5, 257, np.inf))
def test_invalid_mode_counts_reject_in_both_solvers(count):
    pipe = PipeAcoustics(1, 343)
    with pytest.raises(ValueError):
        pipe.analytic_frequencies_hz(count)
    with pytest.raises(ValueError):
        pipe.finite_element_modes(count=count)


@pytest.mark.parametrize("intervals", (True, 0, 1, 20.5, 257, 10**20))
def test_invalid_or_unbounded_mesh_requests_reject(intervals):
    with pytest.raises(ValueError):
        PipeAcoustics(1, 343).finite_element_modes(intervals=intervals)


def test_count_cannot_exceed_free_pressure_degrees_of_freedom():
    with pytest.raises(ValueError):
        PipeAcoustics(1, 343).finite_element_modes(intervals=2, count=2)
    assert len(PipeAcoustics(1, 343).finite_element_modes(intervals=2, count=1).frequencies_hz) == 1


def test_collapsed_physical_mesh_rejects_instead_of_reporting_duplicate_positions():
    pipe = PipeAcoustics(1e-323, 1e-323)
    with pytest.raises(ValueError, match="mesh spacing"):
        pipe.finite_element_modes(intervals=16)
