import math

import numpy as np
import pytest

from src.proposed_combined_control_limits import combined_control_trace
from src.proposed_measurement_noise import (
    FREQUENCIES_RAD_S,
    FourierMeasurementNoise,
    seeded_coefficients,
)
from src.proposed_noisy_control import noisy_control_trace


@pytest.mark.parametrize("tau,delay", [(0.0, 0.0), (0.1, 0.2)])
def test_zero_noise_preserves_existing_trajectory_and_ledgers(tau, delay):
    options = dict(actuator_time_constant_s=tau, delay_s=delay, periods=5)
    old, new = (
        combined_control_trace(**options),
        noisy_control_trace(coefficients=seeded_coefficients(7), **options),
    )
    for key in (
        "states",
        "applied_force_per_mass",
        "actuator_work_per_mass",
        "pump_work_per_mass",
        "damping_loss_per_mass",
        "late_position_rms_m",
    ):
        np.testing.assert_array_equal(new[key], old[key])


@pytest.mark.parametrize("tau,delay", [(0.0, 0.0), (0.1, 0.2)])
def test_zero_coefficients_exercise_noisy_arithmetic(tau, delay):
    options = dict(actuator_time_constant_s=tau, delay_s=delay, periods=5)
    old = combined_control_trace(**options)
    new = noisy_control_trace(
        coefficients=np.zeros((4, 8, 2)), position_sigma_m=0.1, velocity_sigma_m_s=0.1, **options
    )
    for key in (
        "states",
        "applied_force_per_mass",
        "actuator_work_per_mass",
        "pump_work_per_mass",
        "damping_loss_per_mass",
    ):
        np.testing.assert_array_equal(new[key], old[key])


def test_independent_fourier_evaluation_negative_and_delayed_time():
    coeff = seeded_coefficients(7)
    noise = FourierMeasurementNoise(coeff, 0.01, 0.02)
    for time in (-0.2, 0, 0.037, 2.31):
        expected = [
            sigma
            / math.sqrt(8)
            * sum(
                coeff[c, j, 0] * math.cos(w * time) + coeff[c, j, 1] * math.sin(w * time)
                for j, w in enumerate(FREQUENCIES_RAD_S)
            )
            for c, sigma in enumerate((0.01, 0.01, 0.02, 0.02))
        ]
        np.testing.assert_allclose(noise(time), expected, atol=2e-17)


def test_common_path_refinement_and_per_step_redraw_negative_control():
    noise = FourierMeasurementNoise(seeded_coefficients(19), 0.1, 0.1)
    coarse = np.arange(257) * (2 * math.pi / 256)
    fine = np.arange(513) * (2 * math.pi / 512)
    np.testing.assert_array_equal([noise(t) for t in coarse], [noise(t) for t in fine[::2]])
    wrong_coarse = np.random.Generator(np.random.PCG64(19)).normal(size=(257, 4))
    wrong_fine = np.random.Generator(np.random.PCG64(19)).normal(size=(513, 4))
    assert np.max(np.abs(wrong_coarse[1:] - wrong_fine[::2][1:])) > 1
    assert not np.array_equal(seeded_coefficients(7), seeded_coefficients(19))


def test_noise_and_clipping_statistics_use_inclusive_output_samples():
    coefficients = seeded_coefficients(7)
    r = noisy_control_trace(
        coefficients=coefficients,
        position_sigma_m=0.1,
        velocity_sigma_m_s=0.1,
        actuator_time_constant_s=0.1,
        delay_s=0.2,
        force_limit=0.05,
        periods=5,
    )
    noise = FourierMeasurementNoise(coefficients, 0.1, 0.1)
    samples = np.array([noise(t - 0.2) for t in r["times_s"]])
    np.testing.assert_array_equal(r["sampled_noise_mean"], samples.mean(axis=0))
    np.testing.assert_array_equal(r["sampled_noise_rms"], np.sqrt(np.mean(samples**2, axis=0)))
    force = np.array(r["applied_force_per_mass"])
    assert np.max(np.linalg.norm(force, axis=1)) <= 0.05 * (1 + 1e-12)
    assert r["sampled_command_clipping_fraction"] > 0
    assert r["max_energy_balance_residual_per_mass"] < 1e-5
    times = np.array(r["times_s"])
    v = np.array(r["states"])[:, 2:]
    wrong = np.trapezoid(np.sum(np.array(r["limited_command_per_mass"]) * v, axis=1), times)
    assert abs(wrong - r["actuator_work_per_mass"][-1]) > 0.001
    assert np.min(np.diff(r["damping_loss_per_mass"])) >= 0


@pytest.mark.parametrize("sigma", [-1, float("nan"), float("inf"), True, 1j])
def test_invalid_scales(sigma):
    with pytest.raises(ValueError):
        FourierMeasurementNoise(seeded_coefficients(7), sigma, 0)


@pytest.mark.parametrize(
    "coeff", [[], np.zeros((4, 8)), np.full((4, 8, 2), np.nan), np.ones((4, 8, 2)) * 1j]
)
def test_invalid_coefficients(coeff):
    with pytest.raises(ValueError):
        FourierMeasurementNoise(coeff, 0.1, 0.1)


def test_missing_coefficients_rejected_for_nonzero_noise():
    with pytest.raises(ValueError):
        FourierMeasurementNoise(None, 0.1, 0.1)


@pytest.mark.parametrize(
    "late,expected",
    [
        (0.02, "meets_finite_run_target"),
        (0.08, "fails_finite_run_target"),
        (0.05, "borderline_unresolved"),
    ],
)
def test_classification_preserves_tracking_outcome_and_borderline(monkeypatch, late, expected):
    import scripts.report_control_noise as reporter

    runs = [
        {"states": np.zeros((3, 4)).tolist(), "n": 0, "late_position_rms_m": late},
        {"states": np.zeros((5, 4)).tolist(), "n": 1, "late_position_rms_m": late},
    ]

    def summary(run):
        return {
            "late_position_rms_m": late,
            "meets_declared_tracking_target": late <= 0.05,
            "max_energy_balance_residual_per_mass": 1e-8,
            "minimum_sampled_damping_increment": 0,
            "sampled_power_quadrature_residual_per_mass": 1e-5 / (run["n"] + 1),
        }

    monkeypatch.setattr(reporter, "sampled_summary", summary)
    assert reporter.compare(runs)["classification"] == expected
    runs[0]["states"][0][0] = 0.001
    assert reporter.compare(runs)["classification"] == "numerically_unresolved"


def test_flip_and_preselected_nonconvergence_are_unresolved(monkeypatch):
    import scripts.report_control_noise as reporter

    runs = [
        {"states": np.full((n, 4), value).tolist(), "n": i, "late_position_rms_m": 0.02}
        for i, (n, value) in enumerate(((3, 0), (5, 1e-5), (9, 3e-5)))
    ]

    def summary(run):
        return {
            "late_position_rms_m": run["late_position_rms_m"],
            "meets_declared_tracking_target": run["late_position_rms_m"] <= 0.05,
            "max_energy_balance_residual_per_mass": 1e-8,
            "minimum_sampled_damping_increment": 0,
            "sampled_power_quadrature_residual_per_mass": 1e-5 / (run["n"] + 1),
        }

    monkeypatch.setattr(reporter, "sampled_summary", summary)
    result = reporter.compare(runs)
    assert result["classification"] == "numerically_unresolved"
    assert any(
        "preselected_finer_difference" in reason for reason in result["numerical_gate_failures"]
    )
    runs[0]["late_position_rms_m"], runs[1]["late_position_rms_m"] = 0.04998, 0.05002
    assert reporter.compare(runs[:2])["classification"] == "borderline_unresolved"
