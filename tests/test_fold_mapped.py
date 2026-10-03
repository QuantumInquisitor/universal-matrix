"""Independent mapped-port gradients, power and local stiffness checks."""

import numpy as np
import pytest

from scripts.report_fold_coupling import initial_state
from scripts.report_fold_dynamics import Q0
from scripts.report_fold_mapped import PORT_STIFFNESS, connector, measure, port, rhs, simulate


def test_port_jacobian_independent_difference():
    q = Q0 + (0.03, -0.04)
    _, j = port(q, 0.05)
    for k in range(2):
        d = np.eye(2)[k] * 1e-6
        measured = (port(q + d, 0.05)[0] - port(q - d, 0.05)[0]) / 2e-6
        np.testing.assert_allclose(measured, j[:, k], atol=1e-11, rtol=0)


@pytest.mark.parametrize("ratio", [0.25, 0.5, 1.0])
def test_potential_gradient_and_connector_power(ratio):
    qa, qb = Q0 + (0.03, -0.04), Q0 + (-0.01, 0.02)
    va, vb = np.array((0.1, -0.2)), np.array((-0.07, 0.11))
    _, fa, fb = connector(qa, qb, ratio)
    for k in range(2):
        h = np.eye(2)[k] * 1e-6
        da = (connector(qa + h, qb, ratio)[0] - connector(qa - h, qb, ratio)[0]) / 2e-6
        db = (connector(qa, qb + h, ratio)[0] - connector(qa, qb - h, ratio)[0]) / 2e-6
        assert da == pytest.approx(-fa[k], abs=1e-13)
        assert db == pytest.approx(-fb[k], abs=1e-13)
    eps = 1e-6
    udot = (
        (
            connector(qa + eps * va, qb + eps * vb, ratio)[0]
            - connector(qa - eps * va, qb - eps * vb, ratio)[0]
        )
        / 2
        / eps
    )
    assert abs(udot + fa @ va + fb @ vb) < 1e-12


def test_equilibrium_stiffness_blocks_and_null_modes():
    ratio = 0.5
    base = np.r_[Q0, Q0]

    def force(z):
        _, fa, fb = connector(z[:2], z[2:], ratio)
        return np.r_[fa, fb]

    hessian = np.zeros((4, 4))
    for i in range(4):
        h = np.eye(4)[i] * 1e-6
        hessian[:, i] = -(force(base + h) - force(base - h)) / 2e-6
    k = 0.01 * PORT_STIFFNESS
    expected = np.block([[k, -ratio * k], [-ratio * k, ratio**2 * k]])
    np.testing.assert_allclose(hessian, expected, atol=1e-12, rtol=0)
    np.testing.assert_allclose(expected @ np.r_[ratio * np.eye(2), np.eye(2)], 0, atol=1e-18)
    assert np.linalg.eigvalsh(expected).min() > -1e-18


def test_global_directional_energy_and_wrong_mapping():
    y = initial_state()
    y[11:13] = (0.05, -0.08)
    eps = 1e-6
    d = rhs(y)
    slope = (measure(y + eps * d)[2] - measure(y - eps * d)[2]) / 2 / eps
    assert abs(slope) < 1e-12
    wrong = rhs(y, wrong_child_jacobian=True)
    error = (measure(y + eps * wrong)[2] - measure(y - eps * wrong)[2]) / 2 / eps
    assert abs(error) > 1e-7


def test_run_balance_refinement_and_negative_control():
    coarse = simulate(duration=1, dt=0.04)
    fine = simulate(duration=1, dt=0.02)
    bad = simulate(duration=1, wrong_child_jacobian=True)
    assert fine["max_total_residual_j"] < 1e-12
    assert fine["max_total_residual_j"] < coarse["max_total_residual_j"] / 8
    assert bad["max_node_residual_j"] < 1e-12
    assert bad["max_connector_residual_j"] > 1e-9
    assert bad["max_total_residual_j"] > 1e-9


def test_no_fuel_transfer():
    run = simulate(duration=0.4, fueled=False, gain=0, damping=0, leakage=0)
    end = run["trace"][-1]
    assert end["mechanical_j"][1] > 0
    assert end["reservoir_work_j"] == [0.0, 0.0]
    assert run["max_total_residual_j"] < 1e-12


@pytest.mark.parametrize("ratio", [True, 0, 0.09, 1.1, float("nan"), "0.5"])
def test_invalid_ratio(ratio):
    with pytest.raises(ValueError):
        connector(Q0, Q0, ratio)


@pytest.mark.parametrize("length", [True, 0, -0.1, float("inf")])
def test_invalid_length(length):
    with pytest.raises(ValueError):
        port(Q0, length)
