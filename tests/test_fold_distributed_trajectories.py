"""Trajectory ledger and numerical controls for distributed inertia."""

import numpy as np
import pytest

from scripts.report_fold_distributed_trajectories import report, simulate


@pytest.fixture(scope="module")
def result():
    return report()


def test_independent_power_quadrature_converges(result):
    for name in ("passive", "driven", "drive_off"):
        case = result["cases"][name]
        for ledger in ("work", "loss"):
            coarse = case["refinement"][f"coarse_{ledger}_quadrature_error_j"]
            fine = case[f"independent_{ledger}_error_j"]
            if coarse > 1e-15:
                assert fine < 0.3 * coarse


def test_loss_is_nonnegative_and_owned_once(result):
    for case in result["cases"].values():
        rows = case["trace"]
        loss = np.array([r["loss_j"] for r in rows])
        assert np.min(loss) >= -1e-14
        assert np.min(np.diff(loss)) >= -1e-14
        initial = rows[0]["energy_j"]
        residuals = [r["energy_j"] - initial - r["work_j"] + r["loss_j"] for r in rows]
        assert max(abs(v) for v in residuals) < 1e-10
    assert result["cases"]["passive"]["trace"][-1]["loss_j"] > 1e-10
    assert result["cases"]["driven"]["trace"][-1]["work_j"] > 1e-10


def test_omitting_loss_from_audit_is_detected(result):
    rows = result["cases"]["passive"]["trace"]
    wrong = rows[-1]["energy_j"] - rows[0]["energy_j"]
    assert abs(wrong) > 1e-10


@pytest.mark.parametrize(
    "kwargs",
    [
        {"duration": 0},
        {"duration": 0.5},
        {"max_step": 0},
        {"max_step": True},
        {"samples": True},
        {"samples": 2},
        {"samples": 3.5},
        {"damping": -1},
        {"drive": float("nan")},
        {"initial": [1, 0.2, 0, 0, 1, 0]},
    ],
)
def test_rejects_invalid_scope(kwargs):
    with pytest.raises(ValueError):
        simulate(**kwargs)
