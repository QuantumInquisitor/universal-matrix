import math

import numpy as np
import pytest

from src.proposed_mode_pair_control import mode_pair_trace, target


def test_ideal_feedback_matches_closed_error_equation():
    result = mode_pair_trace(periods=3)
    t = np.array(result["times_s"])
    actual = np.array(result["states"]) - np.array([target(x) for x in t])
    wd = math.sqrt(1 - 0.32**2)
    expected = np.zeros_like(actual)
    expected[:, 0] = 0.25 * np.exp(-0.32 * t) * (np.cos(wd * t) + 0.32 / wd * np.sin(wd * t))
    expected[:, 2] = -0.25 / wd * np.exp(-0.32 * t) * np.sin(wd * t)
    np.testing.assert_allclose(actual, expected, atol=3e-8)


def test_negligible_force_preserves_known_charge_decay():
    result = mode_pair_trace(force_limit=1e-20, periods=3)
    q1, q2, v1, v2 = np.array(result["states"]).T
    charge = q1 * v2 - q2 * v1
    expected = 1.25 * np.exp(-0.04 * np.array(result["times_s"]))
    np.testing.assert_allclose(charge, expected, rtol=2e-7)
    assert result["maximum_sampled_force_per_mass"] <= 1e-20


def test_delayed_disturbed_trace_converges_under_refinement():
    options = dict(delay_s=0.1, measurement_amplitude=0.02, stiffness_ratio=1.2, periods=3)
    coarse = mode_pair_trace(**options)
    fine = mode_pair_trace(**options, steps_per_period=512)
    np.testing.assert_allclose(coarse["states"], np.array(fine["states"])[::2], atol=8e-5)


@pytest.mark.parametrize(
    "options",
    (
        {"force_limit": 0},
        {"delay_s": -0.1},
        {"delay_s": 0.001},
        {"measurement_amplitude": -0.1},
        {"stiffness_ratio": 0},
        {"periods": True},
    ),
)
def test_invalid_inputs(options):
    with pytest.raises(ValueError):
        mode_pair_trace(**options)
