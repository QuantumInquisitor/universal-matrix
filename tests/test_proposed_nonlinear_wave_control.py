import math

import numpy as np
import pytest

from src.proposed_nonlinear_wave_control import nonlinear_trace
from src.proposed_scalar_wave_control import RingMode, floquet_audit


def mode(h=0.2, gamma=0.02):
    return RingMode(2 * math.pi, 1, 1, 0, gamma, h, 2)


def test_zero_cubic_matches_existing_linear_monodromy():
    result = nonlinear_trace(mode(), beta=0, periods=32)
    matrix = floquet_audit(mode(), steps=1024)["monodromy"]
    expected = np.linalg.matrix_power(matrix, 32) @ [0.01, 0]
    np.testing.assert_allclose(result["final_state"], expected, rtol=1e-8, atol=1e-10)


def test_unforced_damped_linear_analytic_solution():
    result = nonlinear_trace(mode(h=0), beta=0, periods=32)
    t = np.array(result["times_s"])
    frequency = math.sqrt(1 - 0.02**2)
    q = (
        0.01
        * np.exp(-0.02 * t)
        * (np.cos(frequency * t) + 0.02 / frequency * np.sin(frequency * t))
    )
    v = -0.01 / frequency * np.exp(-0.02 * t) * np.sin(frequency * t)
    np.testing.assert_allclose(result["states_q_m_v_m_s"], np.c_[q, v], atol=1e-10)


def test_unforced_undamped_cubic_energy_invariant():
    result = nonlinear_trace(mode(h=0, gamma=0), periods=32, displacement_m=0.5)
    q, v = np.array(result["states_q_m_v_m_s"]).T
    energy = 0.5 * v * v + 0.5 * q * q + 0.25 * q**4
    np.testing.assert_allclose(energy, energy[0], rtol=1e-8)


def test_zero_seed_stays_zero_despite_parametric_pump():
    result = nonlinear_trace(mode(), displacement_m=0, periods=32)
    assert not result["late_window"]["signal_resolved"]
    assert result["final_state"] == [0, 0]


@pytest.mark.parametrize(
    "parameters", ({"beta": -1}, {"periods": True}, {"rtol": 0}, {"steps_per_period": 4})
)
def test_invalid_parameters(parameters):
    with pytest.raises(ValueError):
        nonlinear_trace(mode(), **parameters)
