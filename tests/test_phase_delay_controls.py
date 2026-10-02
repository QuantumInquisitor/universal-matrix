"""Intervention causality and independent solution checks for phase tracking."""

import importlib.util
import math
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "phase_delay", Path(__file__).parents[1] / "scripts/report_phase_delay_controls.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
run = MODULE.run


@pytest.mark.parametrize("delay", [0.0, 0.5, 1.0])
def test_injected_information_cannot_arrive_before_transport(delay):
    result = run(delay=delay)
    assert result["maximum_prearrival_paired_difference"] == 0
    assert result["first_detected_paired_difference"] == pytest.approx(2 + delay + 0.01)


def test_no_coupling_means_no_detection_or_recovery():
    result = run(coupling=0)
    assert result["first_detected_paired_difference"] is None
    assert result["recovery_after_arrival"] is None
    assert result["integrated_squared_phase_drive"] == 0


def test_noise_free_response_matches_exact_nonlinear_solution():
    result = run(noise=0, coupling=0.5)
    amplitude = result["injected_amplitude"]
    elapsed = 12 - 2 - 0.5
    exact = amplitude - 2 * math.atan(math.tan(amplitude / 2) * math.exp(-0.5 * elapsed))
    assert result["final_phase"] == pytest.approx(exact, abs=2e-12)
    assert result["recovery_after_arrival"] is not None


def test_same_noise_path_across_step_refinement():
    coarse, fine, finest = [run(dt=dt) for dt in (0.02, 0.01, 0.005)]
    assert coarse["injected_amplitude"] == fine["injected_amplitude"]
    assert abs(fine["final_phase"] - finest["final_phase"]) < abs(
        coarse["final_phase"] - fine["final_phase"]
    )
    assert abs(fine["final_phase"] - finest["final_phase"]) < 1e-9


def test_seeded_reproducibility_and_distinct_interventions():
    assert run(seed=7) == run(seed=7)
    assert run(seed=7)["injected_amplitude"] != run(seed=19)["injected_amplitude"]


@pytest.mark.parametrize(
    "parameters",
    [
        {"delay": -1},
        {"noise": float("nan")},
        {"coupling": -1},
        {"dt": 0},
        {"delay": 0.505},
        {"duration": 2.1},
    ],
)
def test_invalid_parameters_rejected(parameters):
    with pytest.raises(ValueError):
        run(**parameters)
