"""Independent external-source and conservation checks."""

import numpy as np
import pytest

from scripts import report_fold_supply as m


def initial(rest=False):
    y = np.r_[m.initial_state(m.BASE_SIZES, m.EDGES), np.zeros(4)]
    if rest:
        y[:36].reshape(4, 9)[:, :4] = np.tile(np.r_[m.Q0, 0, 0], (4, 1))
    return y


def test_source_off_exact_old_derivative():
    y = initial()
    np.testing.assert_array_equal(
        m.rhs(y, power_density=0)[:44], m.active_rhs(y[:44], m.BASE_SIZES, m.EDGES)
    )
    np.testing.assert_array_equal(m.rhs(y, power_density=0)[44:], 0)


def test_group_energy_derivative_independent_finite_difference():
    y = initial()
    y[:36].reshape(4, 9)[:, 4] *= 0.6
    derivative = m.rhs(y)
    layout = m.compile_hierarchy(4, m.EDGES, m.TREE)

    def account(state):
        groups = m.measure(state[:44], m.BASE_SIZES, m.EDGES, layout)[3]
        return np.array(
            [
                g["accounted_energy_j"]
                - g["boundary_work_j"]
                - sum(state[44:][layout["groups"][p]])
                for p, g in groups.items()
            ]
        )

    h = 1e-5
    np.testing.assert_allclose(
        (account(y + h * derivative) - account(y - h * derivative)) / (2 * h), 0, atol=2e-15
    )


def test_scale_similarity_including_source_ledger():
    y = initial()
    y[:36].reshape(4, 9)[:, 4] *= 0.6
    d = m.rhs(y)
    g = 0.5
    z = y.copy()
    z[:36].reshape(4, 9)[:, 2:4] /= g
    z[:36].reshape(4, 9)[:, 4:] *= g**3
    z[36:] *= g**3
    dz = m.rhs(z, sizes=tuple(g * s for s in m.BASE_SIZES))
    expected = d.copy()
    expected[:36].reshape(4, 9)[:, :2] /= g
    expected[:36].reshape(4, 9)[:, 2:4] /= g**2
    expected[:36].reshape(4, 9)[:, 4:] *= g**2
    expected[36:] *= g**2
    np.testing.assert_allclose(dz, expected, rtol=2e-13, atol=1e-18)


def test_rest_analytic_reserve_input_without_self_start():
    run = m.simulate(0.2, rest=True)
    s = np.array(m.BASE_SIZES)
    cap = 2e-5 * s**3
    jmax = 6e-6 * s**2
    k = jmax / cap + 0.15 / s
    eq = jmax / k
    np.testing.assert_allclose(eq / cap, 2 / 3)
    np.testing.assert_allclose(4 * eq / (eq + 1e-5 * s**3), 16 / 7)
    for row in run["samples"]:
        t = row["time_s"]
        r = eq + (cap - eq) * np.exp(-k * t)
        inj = jmax * ((1 - eq / cap) * t - (cap - eq) / cap * (-np.expm1(-k * t)) / k)
        np.testing.assert_allclose(row["reserve_j"], r, rtol=1e-10, atol=1e-20)
        np.testing.assert_allclose(row["input_j"], inj, rtol=1e-9, atol=1e-18)
        assert row["total_mechanical_j"] == 0
        assert np.max(abs(np.array(row["rates"]))) == 0


def test_conservation_budget_and_missing_input_detection():
    run = m.simulate(0.2)
    assert run["termination"]["status"] == "completed"
    for key in (
        "max_node_mechanical_residual_j",
        "max_node_reservoir_residual_j",
        "max_edge_residual_j",
    ):
        assert max(run[key]) < 1e-12
    assert max(run["max_group_residual_j"].values()) < 1e-12
    assert run["missing_input_diagnostic"]["max_group_residual_j"]["root"] > 1e-8
    assert min(run["minimum_reserve_j"]) >= 0
    assert min(run["finite_supply_margin_j"]) >= 0
    assert max(run["maximum_reserve_upper_violation_j"]) == 0
    assert min(run["minimum_input_step_j"]) == 0
    assert max(run["maximum_input_budget_violation_j"]) == 0
    assert max(run["maximum_power_budget_violation_w"]) == 0
    assert run["total_received_j"] <= 6e-6 * sum(np.array(m.BASE_SIZES) ** 2) * 0.2


@pytest.mark.parametrize(
    "kwargs",
    [
        {"duration": 0},
        {"duration": 21},
        {"duration": True},
        {"power_density": -1},
        {"power_density": float("nan")},
        {"power_density": True},
        {"max_step": 0},
        {"rtol": 0},
        {"rest": 1},
    ],
)
def test_invalid_settings(kwargs):
    with pytest.raises(ValueError):
        m.simulate(**kwargs)


def test_no_clipping_initial_over_capacity():
    y = initial()
    y[4] *= 1.1
    with pytest.raises(ValueError, match="capacity"):
        m.simulate(0.1, initial=y)


def test_known_stage_error_retains_last_accepted_endpoint(monkeypatch):
    original = m.rhs
    calls = 0

    def injected(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls > 20:
            raise ValueError("negative reservoir: injected rejected stage")
        return original(*args, **kwargs)

    monkeypatch.setattr(m, "rhs", injected)
    run = m.simulate(0.1, max_step=0.01)
    assert run["termination"]["status"] == "scope_termination"
    assert 0 < run["termination"]["last_accepted_time_s"] < 0.1
    assert run["samples"][-1]["time_s"] == run["termination"]["last_accepted_time_s"]
    np.testing.assert_array_equal(run["samples"][-1]["input_j"], run["final_state"][44:])


def test_unknown_errors_propagate(monkeypatch):
    original = m.rhs
    calls = 0

    def injected(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls > 2:
            raise ValueError("unexpected defect")
        return original(*args, **kwargs)

    monkeypatch.setattr(m, "rhs", injected)
    with pytest.raises(ValueError, match="unexpected defect"):
        m.simulate(0.1)


def test_capacity_interval_has_inward_reservoir_derivatives():
    y = initial(rest=True)
    at_capacity = m.rhs(y)
    assert np.all(at_capacity[:36].reshape(4, 9)[:, 4] < 0)
    np.testing.assert_array_equal(at_capacity[44:], 0)
    y[:36].reshape(4, 9)[:, 4] = 0
    at_empty = m.rhs(y)
    assert np.all(at_empty[:36].reshape(4, 9)[:, 4] > 0)
    np.testing.assert_allclose(at_empty[44:], 6e-6 * np.array(m.BASE_SIZES) ** 2)
