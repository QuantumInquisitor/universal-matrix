"""Independent energy identity, passive replay and finite supply controls."""

import numpy as np
import pytest

from scripts.report_fold_dynamics import Q0, mechanical
from scripts.report_fold_dynamics import simulate as passive
from scripts.report_fold_reservoir import rhs, simulate


def test_directional_total_energy_identity():
    y = np.r_[Q0 + (0.025, -0.04), 0.1, -0.15, 2e-5, 0.0, 0.0, 0.0, 0.0]
    delta = rhs(y)
    eps = 1e-6

    def total(z):
        return mechanical(z[:2], z[2:4])[2] + z[4] + sum(z[6:])

    observed = (total(y + eps * delta) - total(y - eps * delta)) / (2 * eps)
    assert abs(observed) < 1e-11
    wrong = rhs(y, omit_debit=True)
    bad = (total(y + eps * wrong) - total(y - eps * wrong)) / (2 * eps)
    assert bad > 1e-6


def test_disconnected_matches_original_passive_model():
    run = simulate(duration=0.4, gain=0)
    reference = passive(duration=0.4, dt=0.02)
    np.testing.assert_allclose(
        run["final_state"][:4], reference["final_state"][:4], atol=1e-15, rtol=0
    )
    assert run["final_state"][5] == 0


def test_empty_reservoir_stays_empty():
    run = simulate(duration=0.4, reserve=0)
    assert run["final_state"][4] == run["final_state"][5] == 0
    assert run["trace"][-1]["mechanical_j"] < run["initial_mechanical_j"]


def test_equilibrium_does_not_self_start_and_leak_is_analytic():
    run = simulate(duration=0.4, equilibrium=True)
    np.testing.assert_array_equal(run["final_state"][:4], np.r_[Q0, 0.0, 0.0])
    assert run["final_state"][5] == 0
    assert run["final_state"][4] == pytest.approx(2e-5 * np.exp(-0.15 * 0.4), rel=1e-12)


def test_finite_supply_and_separate_ledgers():
    run = simulate(duration=1)
    end = run["final_state"]
    assert 0 < end[5] <= 0.8 * 2e-5
    assert 0 < end[4] < 2e-5
    assert all(x > 0 for x in end[6:])
    assert end[7] == pytest.approx(0.25 * end[5], abs=1e-18)
    assert run["max_total_residual_j"] < 1e-12
    assert run["max_mechanical_residual_j"] < 1e-12
    assert run["max_reservoir_residual_j"] < 1e-18
    assert np.all(np.diff([r["reserve_j"] for r in run["trace"]]) <= 0)
    for field in ("damping_loss_j", "conversion_loss_j", "leakage_loss_j"):
        assert np.all(np.diff([r[field] for r in run["trace"]]) >= 0)


def test_feedback_crosses_damping_threshold():
    for reserve, sign in ((1e-6, -1), (1e-5, 1)):
        y = np.r_[Q0, 0.1, -0.1, reserve, 0.0, 0.0, 0.0, 0.0]
        derivative = rhs(y)
        assert sign * (derivative[5] - derivative[6]) > 0


def test_refinement_and_omitted_debit_control():
    coarse = simulate(duration=1, dt=0.04)
    fine = simulate(duration=1, dt=0.02)
    bad = simulate(duration=1, omit_debit=True)
    assert fine["max_total_residual_j"] < coarse["max_total_residual_j"] / 8
    assert bad["max_total_residual_j"] > 1e-8


def test_ideal_transfer_conserves_mechanics_plus_reserve():
    run = simulate(duration=0.4, efficiency=1, leakage=0, damping=0)
    assert run["final_state"][6:] == [0.0, 0.0, 0.0]
    assert run["max_total_residual_j"] < 1e-12


@pytest.mark.parametrize(
    "settings",
    [
        dict(reserve=-1),
        dict(efficiency=0),
        dict(efficiency=1.1),
        dict(gain=-1),
        dict(leakage=-1),
        dict(dt=True),
        dict(reserve=float("nan")),
        dict(duration=0.031, dt=0.02),
    ],
)
def test_invalid_settings(settings):
    with pytest.raises(ValueError):
        simulate(**settings)


def test_negative_stage_reserve_is_rejected():
    with pytest.raises(ValueError, match="negative reservoir"):
        rhs(np.r_[Q0, 0.0, 0.0, -1e-12, 0.0, 0.0, 0.0, 0.0])
