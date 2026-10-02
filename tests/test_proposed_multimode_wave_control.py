import math

import numpy as np
import pytest

from src.proposed_multimode_wave_control import multimode_trace
from src.proposed_nonlinear_wave_control import nonlinear_trace
from src.proposed_scalar_wave_control import RingMode


def mode(h=0.2, gamma=0.02):
    return RingMode(2 * math.pi, 1, 1, 0, gamma, h, 2)


def test_cubic_projection_matches_local_field_quadrature():
    x = np.arange(2048) * 2 * math.pi / 2048
    q = np.array([0.31, -0.27])
    basis = np.array([np.cos(x), np.sin(x)])
    projected = 2 * np.mean((q @ basis) ** 3 * basis, axis=1)
    np.testing.assert_allclose(projected, 0.75 * q * (q @ q), atol=1e-15)


def test_no_coupling_matches_two_independent_existing_controls():
    result = multimode_trace(mode(), coupling=0, periods=32)
    states = np.array(result["states_q1_q2_v1_v2"])
    for index, seed in enumerate((0.01, 0.007)):
        reference = nonlinear_trace(mode(), periods=32, displacement_m=seed)
        np.testing.assert_allclose(
            states[:, [index, index + 2]], reference["states_q_m_v_m_s"], atol=2e-10
        )


def test_conservative_energy_and_rotational_invariant():
    result = multimode_trace(mode(h=0, gamma=0), initial=(0.3, 0.2, 0.1, -0.2), periods=24)
    np.testing.assert_allclose(
        result["energy_per_modal_mass"], result["energy_per_modal_mass"][0], atol=1e-10
    )
    np.testing.assert_allclose(result["angular_momentum"], -0.08, atol=1e-10)


def test_driven_energy_balance_and_damped_angular_momentum():
    result = multimode_trace(mode(), initial=(0.3, 0.2, 0.1, -0.2), periods=32)
    assert result["max_energy_balance_residual"] < 1e-9
    expected = -0.08 * np.exp(-0.04 * np.array(result["times_s"]))
    np.testing.assert_allclose(result["angular_momentum"], expected, atol=1e-10)


def test_isotropic_radial_reduction_and_zero_mode_invariance():
    result = multimode_trace(mode(), periods=32)
    states = np.array(result["states_q1_q2_v1_v2"])
    np.testing.assert_allclose(states[:, 1], 0.7 * states[:, 0], atol=1e-12)
    reference = nonlinear_trace(mode(), periods=32, displacement_m=math.hypot(0.01, 0.007))
    np.testing.assert_allclose(
        states[:, [0, 2]] * math.sqrt(1.49), reference["states_q_m_v_m_s"], atol=1e-10
    )
    zero = multimode_trace(mode(), initial=(0.01, 0, 0, 0), periods=16)
    assert np.all(np.array(zero["states_q1_q2_v1_v2"])[:, [1, 3]] == 0)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"coupling": -1},
        {"alpha": -1},
        {"initial": (0, 0)},
        {"initial": (0, 0, 0, float("nan"))},
        {"periods": True},
        {"steps_per_period": 3},
        {"rtol": 0},
    ],
)
def test_invalid_parameters(kwargs):
    with pytest.raises(ValueError):
        multimode_trace(mode(), **kwargs)
