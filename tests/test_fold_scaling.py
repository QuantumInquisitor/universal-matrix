"""Independent reconstruction, similarity and energy checks for scaled modules."""

import numpy as np
import pytest

from scripts.report_fold_dynamics import Q0, mechanical
from scripts.report_fold_dynamics import rhs as original_rhs
from scripts.report_fold_kinematics import inventory
from scripts.report_fold_scaling import point_inertia, rhs, scale_value, scaled_mechanical, simulate


@pytest.mark.parametrize("scale", [1.0, 0.5, 0.25])
def test_reconstructed_inertia_and_cartesian_kinetic_energy(scale):
    q, v = Q0 + (0.03, -0.04), np.array((0.11, -0.12))
    state, bias, _ = scaled_mechanical(q, v, scale)
    base, bias0, _ = mechanical(q, v)
    np.testing.assert_allclose(
        state["mass_matrix"], scale**5 * base["mass_matrix"], rtol=1e-13, atol=0
    )
    np.testing.assert_allclose(bias, scale**5 * bias0, rtol=1e-13, atol=0)
    velocities = state["jacobian"] @ v
    cartesian = 0.5 * sum(m * np.dot(u, u) for m, u in zip(state["mass"], velocities, strict=True))
    generalized = 0.5 * v @ state["mass_matrix"] @ v
    assert cartesian == pytest.approx(generalized, rel=1e-13)
    assert sum(state["mass"]) == pytest.approx(scale**3 * sum(m for _, _, m in inventory()))
    np.testing.assert_allclose(
        point_inertia(state), scale**5 * point_inertia(base), rtol=1e-13, atol=0
    )


def test_unit_scale_recovers_original_dynamics():
    y = np.r_[Q0 + (0.02, -0.03), 0.01, 0.02, 0.0]
    original = original_rhs(0, np.r_[y[:4], 0.0, 0.0])
    np.testing.assert_allclose(rhs(y), original[[0, 1, 2, 3, 5]], rtol=0, atol=0)


def test_acceleration_time_scaling_and_dissipation():
    y = np.r_[Q0 + (0.03, -0.04), 0.12, -0.15, 0.0]
    base = rhs(y)
    scale = 0.5
    rescaled = y.copy()
    rescaled[2:4] /= scale
    actual = rhs(rescaled, scale)
    np.testing.assert_allclose(actual[:2], base[:2] / scale, rtol=1e-13, atol=0)
    np.testing.assert_allclose(actual[2:4], base[2:4] / scale**2, rtol=1e-13, atol=0)
    assert actual[4] == pytest.approx(scale**2 * base[4], rel=1e-13)


def test_independent_total_energy_derivative_and_wrong_inertia():
    scale = 0.5
    y = np.r_[Q0 + (0.03, -0.04), 0.15, -0.2, 0.0]

    def total(z):
        return scaled_mechanical(z[:2], z[2:4], scale)[2] + z[4]

    eps = 1e-6
    d = rhs(y, scale)
    assert abs((total(y + eps * d) - total(y - eps * d)) / 2 / eps) < 1e-12
    wrong = rhs(y, scale, wrong_inertia=True)
    assert abs((total(y + eps * wrong) - total(y - eps * wrong)) / 2 / eps) > 1e-8


def test_trajectory_similarity_and_negative_control():
    base = simulate(1.0)
    half = simulate(0.5)
    for a, b in zip(base["trace"], half["trace"], strict=True):
        np.testing.assert_allclose(a["q"], b["q"], atol=1e-13, rtol=0)
        np.testing.assert_allclose(a["rates"], 0.5 * np.array(b["rates"]), atol=1e-13, rtol=0)
        assert a["mechanical_j"] == pytest.approx(b["mechanical_j"] / 0.5**3, abs=1e-16)
    wrong = simulate(0.5, wrong_inertia=True)
    assert wrong["max_balance_residual_j"] > 1e-9


@pytest.mark.parametrize("scale", [True, 0.1, 1.1, 0, float("nan"), 1j, "0.5", 10**400])
def test_invalid_scale(scale):
    with pytest.raises(ValueError):
        scale_value(scale)
