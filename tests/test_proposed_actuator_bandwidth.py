import math

import numpy as np
import pytest

from src.proposed_actuator_bandwidth import _actuator_rate, _rk4_step, actuator_bandwidth_trace
from src.proposed_mode_pair_control import mode_pair_trace


def test_zero_lag_matches_original_trajectory():
    options = dict(periods=5, steps_per_period=256)
    result = actuator_bandwidth_trace(**options)
    old = mode_pair_trace(**options)
    np.testing.assert_array_equal(result["states"], old["states"])
    assert result["late_position_rms_m"] == old["late_position_rms_m"]


def test_actuator_constant_command_matches_exponential():
    tau, dt = 0.3, 0.002
    initial, command = np.array([0.3, -0.4]), np.array([0.8, 0.1])
    state = initial.copy()
    for i in range(500):
        state = _rk4_step(lambda t, a: _actuator_rate(a, command, tau), i * dt, state, dt)
    np.testing.assert_allclose(
        state, command + (initial - command) * math.exp(-1 / tau), atol=1e-11
    )


def test_actuator_sinusoidal_gain_and_phase():
    tau, omega, dt = 0.4, 3.0, 0.002
    phase = math.atan(omega * tau)
    gain = 1 / math.sqrt(1 + (omega * tau) ** 2)
    state = np.array([-gain * math.sin(phase)])
    for i in range(1000):
        state = _rk4_step(
            lambda t, a: _actuator_rate(a, np.array([math.sin(omega * t)]), tau), i * dt, state, dt
        )
    np.testing.assert_allclose(state[0], gain * math.sin(omega * 2 - phase), atol=2e-11)


def test_resolved_small_lag_approaches_zero_lag():
    errors = []
    for tau in (0.1, 0.05):
        result = actuator_bandwidth_trace(actuator_time_constant_s=tau, periods=5)
        old = mode_pair_trace(periods=5)
        errors.append(
            np.max(np.abs(np.array(result["states"])[256:] - np.array(old["states"])[256:]))
        )
    assert errors[1] < 0.6 * errors[0]


def quadrature_residuals(result):
    t = np.array(result["times_s"])
    q, v = np.array(result["states"]).T[:2].T, np.array(result["states"])[:, 2:]
    f = np.array(result["applied_force_per_mass"])
    power = (
        np.sum(f * v, axis=1)
        - 0.2 * np.sin(2 * t) * np.sum(q * q, axis=1)
        - 0.04 * np.sum(v * v, axis=1)
    )
    work = np.trapezoid(power, t)
    energy = np.array(result["mechanical_energy_per_mass"])
    charge = q[:, 0] * v[:, 1] - q[:, 1] * v[:, 0]
    torque = q[:, 0] * f[:, 1] - q[:, 1] * f[:, 0] - 0.04 * charge
    return abs(energy[-1] - energy[0] - work), abs(charge[-1] - charge[0] - np.trapezoid(torque, t))


def test_ledger_and_independent_quadratures_refine():
    results = [
        actuator_bandwidth_trace(actuator_time_constant_s=0.5, periods=5, steps_per_period=n)
        for n in (256, 512)
    ]
    coarse, fine = results
    np.testing.assert_allclose(coarse["states"], np.array(fine["states"])[::2], atol=2e-7)
    assert (
        fine["max_energy_balance_residual_per_mass"]
        < coarse["max_energy_balance_residual_per_mass"] / 8
    )
    for result in results:
        assert np.min(np.diff(result["damping_loss_per_mass"])) >= 0
        assert result["applied_force_per_mass"][0] == [0.0, 0.0]
    times = np.array(fine["times_s"])
    velocity = np.array(fine["states"])[:, 2:]
    command = np.array(fine["limited_command_per_mass"])
    wrong_work = np.trapezoid(np.sum(command * velocity, axis=1), times)
    # Commands are not delivered forces: this intentionally wrong ledger must fail.
    wrong_residual = (
        fine["mechanical_energy_per_mass"][-1]
        - fine["mechanical_energy_per_mass"][0]
        - wrong_work
        - fine["pump_work_per_mass"][-1]
        + fine["damping_loss_per_mass"][-1]
    )
    assert abs(wrong_residual) > 0.01
    for coarse_error, fine_error in zip(
        quadrature_residuals(coarse), quadrature_residuals(fine), strict=True
    ):
        assert fine_error < coarse_error / 3
        assert fine_error < 1e-4


def test_low_force_negative_control_and_distinct_saturation_metrics():
    result = actuator_bandwidth_trace(actuator_time_constant_s=0.5, force_limit=0.05)
    assert not result["meets_declared_tracking_target"]
    assert result["maximum_sampled_force_per_mass"] <= 0.05 * (1 + 1e-12)
    assert (
        result["sampled_command_clipping_fraction"]
        > result["sampled_applied_force_saturation_fraction"]
    )


@pytest.mark.parametrize(
    "options",
    [
        {"actuator_time_constant_s": -1},
        {"actuator_time_constant_s": float("nan")},
        {"actuator_time_constant_s": float("inf")},
        {"actuator_time_constant_s": 0.01},
        {"force_limit": 0},
        {"periods": 4},
        {"periods": True},
        {"steps_per_period": 0},
    ],
)
def test_invalid_inputs(options):
    with pytest.raises(ValueError):
        actuator_bandwidth_trace(**options)


@pytest.mark.parametrize("name", ["actuator_time_constant_s", "force_limit"])
@pytest.mark.parametrize("value", [True, np.bool_(False), 1j, np.complex128(1 + 0j)])
def test_nonreal_or_boolean_inputs(name, value):
    with pytest.raises(ValueError):
        actuator_bandwidth_trace(**{name: value})
