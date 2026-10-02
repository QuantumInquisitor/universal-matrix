"""Independent inertia, energy and numerical controls for synthetic fold forces."""

import numpy as np
import pytest

from scripts.report_fold_dynamics import (
    DAMPING,
    Q0,
    STIFFNESS,
    energy_identity_control,
    force,
    mechanical,
    rhs,
    simulate,
)
from scripts.report_fold_kinematics import kinematics


def test_positive_restoring_and_dissipative_laws():
    assert np.min(np.linalg.eigvalsh(STIFFNESS)) > 0
    assert np.min(np.linalg.eigvalsh(DAMPING)) >= 0
    np.testing.assert_array_equal(rhs(0, np.r_[Q0, 0.0, 0.0, 0.0, 0.0]), np.zeros(6))


@pytest.mark.parametrize("q,v", [(Q0, (0.12, -0.2)), ((0.94, 0.42), (-0.07, 0.13))])
def test_bias_against_finite_difference_christoffel(q, v):
    q, v = np.array(q), np.array(v)
    eps = 1e-5
    # Independent derivatives of M; no analytic H in expected expression.
    dm = np.array(
        [
            (kinematics(q + eps * e)["mass_matrix"] - kinematics(q - eps * e)["mass_matrix"])
            / (2 * eps)
            for e in np.eye(2)
        ]
    )
    expected = np.zeros(2)
    for a in range(2):
        for b in range(2):
            for c in range(2):
                expected[a] += 0.5 * (dm[b, a, c] + dm[c, a, b] - dm[a, b, c]) * v[b] * v[c]
    np.testing.assert_allclose(mechanical(q, v)[1], expected, rtol=1e-8, atol=1e-13)


def test_independent_energy_identity_and_negative_control():
    result = energy_identity_control()
    assert result["absolute_error_j_s"] < 1e-11
    assert result["omitted_bias_absolute_error_j_s"] > 1e-8


def test_conservative_energy_refinement():
    coarse = simulate(duration=0.4, dt=0.02, damping=0)
    fine = simulate(duration=0.4, dt=0.01, damping=0)
    assert fine["maximum_balance_residual_j"] < coarse["maximum_balance_residual_j"] / 10
    assert fine["maximum_balance_residual_j"] < 1e-10


def test_damping_and_external_work_ledger():
    passive = simulate(duration=0.5, dt=0.01)
    driven = simulate(duration=0.5, dt=0.01, drive=1)
    assert passive["final_energy_j"] < passive["initial_energy_j"]
    assert passive["maximum_energy_step_increase_j"] < 0
    assert passive["final_state"][4] == 0
    assert driven["final_state"][4] != 0
    for result in (passive, driven):
        assert result["final_state"][5] > 0
        assert result["maximum_balance_residual_j"] < 1e-10
        assert len(result["samples"][-1]["positions_m"]) == 22


def test_drive_shutoff_and_zero_drive_control():
    np.testing.assert_array_equal(force(1, 1, 1), np.zeros(2))
    np.testing.assert_array_equal(force(2, 1, 1), np.zeros(2))
    np.testing.assert_array_equal(force(0.3, 0), np.zeros(2))
    result = simulate(duration=2, dt=0.02, drive=1, drive_until=1)
    tail = [s for s in result["samples"] if s["time_s"] >= 1]
    assert len({s["work_j"] for s in tail}) == 1
    assert all(b["energy_j"] < a["energy_j"] for a, b in zip(tail, tail[1:], strict=False))


def test_excessive_velocity_is_rejected_before_overflow():
    with pytest.raises(ValueError, match="velocity outside numerical scope"):
        mechanical(Q0, (1e300, 0))


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(dt=0),
        dict(dt=-0.1),
        dict(dt=float("nan")),
        dict(duration=0.13, dt=0.1),
        dict(damping=-1),
        dict(drive=True),
        dict(drive_until=0),
    ],
)
def test_invalid_inputs(kwargs):
    with pytest.raises(ValueError):
        simulate(**kwargs)


def test_reject_scope_exit_without_clipping():
    with pytest.raises(ValueError, match="outside declared scope"):
        simulate(duration=0.1, dt=0.1, initial=[1.099, 0.2, 1.0, 0.0, 0.0, 0.0])
