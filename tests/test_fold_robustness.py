"""Controls for sensitivity classifications and interpretable metrics."""

import json

import numpy as np
import pytest

from scripts import report_fold_robustness as study


def test_deterministic_distinct_perturbations_and_bounded_ensemble():
    cases = study.configurations()
    assert cases == study.configurations()
    assert len(cases) == 24
    assert len({name for name, _ in cases}) == 24
    perturbed = [settings["initial"] for name, settings in cases if name.startswith("perturb")]
    assert perturbed[0] != perturbed[1]
    assert all(settings["duration"] <= 10 for _, settings in cases)


def test_success_reports_independent_coordinate_units_and_energy():
    case = study.run_case("short", duration=0.2, dt=0.01, damping=1.0)
    assert case["classification"] == "success"
    m = case["metrics"]
    assert len(m["state_min"]) == len(m["state_max"]) == 4
    assert np.all(np.array(m["state_min"]) <= m["state_max"])
    assert m["final_energy_j"] < m["initial_energy_j"]
    assert m["relative_balance_residual"] == m["max_balance_residual_j"] / m["balance_reference_j"]
    assert "trace" not in case
    json.dumps(case, allow_nan=False)


@pytest.mark.parametrize("dt", [0.02, 0.01, 0.005])
def test_high_rate_model_region_rejection_survives_refinement(dt):
    initial = np.r_[study.Q0, 2.0, 0.0, 0.0, 0.0].tolist()
    case = study.run_case("escape", duration=0.2, dt=dt, initial=initial, damping=0)
    assert case["classification"] == "domain-rejected"
    assert case["collision_status"] == "not assessed"
    assert case["metrics"] is None


def test_invalid_configuration_is_not_physical_domain_rejection():
    with pytest.raises(ValueError, match="duration"):
        study.run_case("bad-duration", duration=11)


def test_unexpected_value_error_is_not_silenced(monkeypatch):
    def broken(**_):
        raise ValueError("implementation problem")

    monkeypatch.setattr(study, "simulate", broken)
    with pytest.raises(ValueError, match="implementation problem"):
        study.run_case("broken")


def test_numerical_error_is_separate(monkeypatch):
    def singular(**_):
        raise np.linalg.LinAlgError("singular")

    monkeypatch.setattr(study, "simulate", singular)
    case = study.run_case("singular")
    assert case["classification"] == "numerical-error"
    assert case["metrics"] is None


def test_nonfinite_ledger_is_not_reported_as_success(monkeypatch):
    run = study.simulate(duration=0.02, dt=0.02)
    run["trace"][0]["loss_j"] = float("nan")
    monkeypatch.setattr(study, "simulate", lambda **_: run)
    case = study.run_case("corrupted")
    assert case["classification"] == "numerical-error"
    assert case["collision_status"] == "not assessed"
    json.dumps(case, allow_nan=False)


def test_zero_energy_reference_is_finite():
    initial = np.r_[study.Q0, 0.0, 0.0, 0.0, 0.0].tolist()
    case = study.run_case("equilibrium", duration=0.02, dt=0.02, initial=initial)
    assert case["metrics"]["balance_reference_j"] == 0
    assert case["metrics"]["relative_balance_residual"] == 0


def test_accepted_refinement_reduces_ledger_error():
    coarse = study.run_case("coarse", duration=0.4, dt=0.02, damping=0.25, drive=1)["metrics"]
    fine = study.run_case("fine", duration=0.4, dt=0.01, damping=0.25, drive=1)["metrics"]
    assert fine["max_balance_residual_j"] < coarse["max_balance_residual_j"] / 10
    differences = np.abs(np.array(coarse["final_state"][:4]) - fine["final_state"][:4])
    assert np.all(differences < [1e-7, 1e-6, 1e-6, 1e-5])
