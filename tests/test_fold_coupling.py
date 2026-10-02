"""Independent spring gradient, transfer, symmetry and energy controls."""

import numpy as np
import pytest

from scripts.report_fold_coupling import initial_state, measure, rhs, simulate, spring
from scripts.report_fold_reservoir import simulate as single


def test_independent_spring_gradient_and_reaction():
    y = initial_state()
    qa, qb = y[:2], y[9:11]
    _, fa, fb = spring(qa, qb)
    np.testing.assert_array_equal(fa, -fb)
    for i in range(2):
        h = np.eye(2)[i] * 1e-6
        da = (spring(qa + h, qb)[0] - spring(qa - h, qb)[0]) / 2e-6
        db = (spring(qa, qb + h)[0] - spring(qa, qb - h)[0]) / 2e-6
        assert da == pytest.approx(-fa[i], abs=1e-13)
        assert db == pytest.approx(-fb[i], abs=1e-13)


def test_directional_global_energy_and_negative_control():
    y = initial_state()
    y[11:13] = (0.03, -0.04)
    eps = 1e-6
    derivative = rhs(y)
    slope = (measure(y + eps * derivative)[2] - measure(y - eps * derivative)[2]) / 2 / eps
    assert abs(slope) < 1e-12
    wrong = rhs(y, wrong_reaction=True)
    bad = (measure(y + eps * wrong)[2] - measure(y - eps * wrong)[2]) / 2 / eps
    expected = -2 * spring(y[:2], y[9:11])[2] @ y[11:13]
    assert abs(expected) > 1e-6
    assert bad == pytest.approx(expected, abs=1e-12)


def test_disconnected_matches_existing_single_module():
    pair = simulate(duration=0.4, coupling=0)
    reference = single(duration=0.4)
    np.testing.assert_allclose(
        pair["final_state"][:9], reference["final_state"], atol=1e-16, rtol=0
    )
    assert pair["trace"][-1]["mechanical_j"][1] == 0
    assert pair["final_state"][18:] == [0.0, 0.0]


def test_transfer_without_reservoir_and_three_ledgers():
    run = simulate(duration=1, fueled=False, gain=0, damping=0, leakage=0)
    end = run["trace"][-1]
    assert end["mechanical_j"][1] > 1e-9
    assert end["reservoir_work_j"] == [0.0, 0.0]
    assert run["max_total_residual_j"] < 1e-12
    assert run["max_module_residual_j"] < 1e-12
    assert run["max_connection_residual_j"] < 1e-12
    assert end["mechanical_j"][1] == pytest.approx(end["coupling_work_j"][1], abs=1e-12)


def test_label_swap_symmetry():
    y = initial_state()

    def swap(x):
        return np.r_[x[9:18], x[:9], x[19], x[18]]

    np.testing.assert_allclose(rhs(swap(y)), swap(rhs(y)), atol=0, rtol=0)


def test_synchronous_states_have_zero_connection_force():
    y = initial_state()
    y[9:18] = y[:9]
    np.testing.assert_allclose(rhs(y), rhs(y, coupling=0), atol=0, rtol=0)


def test_refinement_and_broken_reaction():
    coarse = simulate(duration=1, dt=0.04)
    fine = simulate(duration=1, dt=0.02)
    wrong = simulate(duration=1, wrong_reaction=True)
    assert fine["max_total_residual_j"] < coarse["max_total_residual_j"] / 8
    assert wrong["max_total_residual_j"] > 1e-9
    assert wrong["max_connection_residual_j"] > 1e-9


@pytest.mark.parametrize(
    "settings",
    [
        dict(coupling=-1),
        dict(coupling=True),
        dict(coupling=float("nan")),
        dict(duration=0),
        dict(dt=0),
        dict(dt=0.03, duration=0.1),
    ],
)
def test_invalid_parameters(settings):
    with pytest.raises(ValueError):
        simulate(**settings)


def test_nonzero_initial_work_rejected():
    y = initial_state()
    y[18] = 1e-6
    with pytest.raises(ValueError, match="ledgers"):
        simulate(initial=y)
