import numpy as np
import pytest

from src.proposed_actuator_bandwidth import actuator_bandwidth_trace
from src.proposed_combined_control_limits import combined_control_trace
from src.proposed_mode_pair_control import mode_pair_trace


@pytest.mark.parametrize("tau", [0.0, 0.5])
def test_zero_delay_recovers_actuator(tau):
    options = dict(actuator_time_constant_s=tau, periods=5)
    old, new = actuator_bandwidth_trace(**options), combined_control_trace(**options)
    for key in ("states", "actuator_work_per_mass", "pump_work_per_mass", "damping_loss_per_mass"):
        np.testing.assert_array_equal(old[key], new[key])


@pytest.mark.parametrize("delay", [0.0, 0.2, 1.0])
def test_zero_lag_recovers_delayed_controller(delay):
    options = dict(delay_s=delay, periods=5)
    old, new = mode_pair_trace(**options), combined_control_trace(**options)
    np.testing.assert_array_equal(old["states"], new["states"])
    assert old["late_position_rms_m"] == new["late_position_rms_m"]


def test_combined_refinement_and_wrong_work_control():
    runs = [
        combined_control_trace(
            actuator_time_constant_s=0.5, delay_s=0.2, periods=5, steps_per_period=n
        )
        for n in (256, 512, 1024)
    ]
    differences = [
        np.max(np.abs(np.array(a["states"]) - np.array(b["states"])[::2]))
        for a, b in zip(runs, runs[1:], strict=False)
    ]
    assert differences[1] < differences[0] / 2
    assert differences[1] < 2e-5
    errors = []
    for run in runs:
        t = np.array(run["times_s"])
        v = np.array(run["states"])[:, 2:]
        delivered = np.trapezoid(np.sum(np.array(run["applied_force_per_mass"]) * v, axis=1), t)
        command = np.trapezoid(np.sum(np.array(run["limited_command_per_mass"]) * v, axis=1), t)
        delta = run["mechanical_energy_per_mass"][-1] - run["mechanical_energy_per_mass"][0]
        remainder = delta - run["pump_work_per_mass"][-1] + run["damping_loss_per_mass"][-1]
        errors.append(abs(remainder - delivered))
        assert abs(remainder - command) > 0.01
        assert run["max_energy_balance_residual_per_mass"] < 1e-6
        assert np.min(np.diff(run["damping_loss_per_mass"])) >= 0
    assert errors[2] < errors[1] < errors[0]
    assert errors[2] < 1e-5


@pytest.mark.parametrize(
    "options",
    [
        {"delay_s": -1},
        {"delay_s": float("nan")},
        {"delay_s": True},
        {"delay_s": 1j},
        {"delay_s": 0.001},
        {"actuator_time_constant_s": 0.001},
        {"periods": 4},
        {"force_limit": 0},
    ],
)
def test_invalid_inputs(options):
    with pytest.raises(ValueError):
        combined_control_trace(**options)


def test_combined_low_force_clipping_and_delivered_work():
    result = combined_control_trace(
        actuator_time_constant_s=0.5, delay_s=0.2, force_limit=0.05, periods=5
    )
    force = np.array(result["applied_force_per_mass"])
    command = np.array(result["limited_command_per_mass"])
    assert np.max(np.linalg.norm(command, axis=1)) <= 0.05 * (1 + 1e-12)
    assert np.max(np.linalg.norm(force, axis=1)) <= 0.05 * (1 + 1e-12)
    assert np.max(np.abs(force - command)) > 0.01
    assert result["sampled_command_clipping_fraction"] > 0
    assert result["max_energy_balance_residual_per_mass"] < 1e-6
    assert not result["meets_declared_tracking_target"]
