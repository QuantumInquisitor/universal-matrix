"""Independent leakage, finite fuel, passive and bounded-domain controls."""

import numpy as np
import pytest

from scripts import report_fold_duration as module
from scripts.report_fold_active_multiscale import BASE_SIZES, EDGES, initial_state


@pytest.fixture(scope="module")
def runs():
    return {
        name: module.simulate(duration=1, gain=gain, rest=rest)
        for name, gain, rest in (("active", 4, False), ("passive", 0, False), ("rest", 4, True))
    }


def test_exact_rest_is_analytic_leakage_without_self_start(runs):
    run = runs["rest"]
    for row in run["samples"]:
        np.testing.assert_allclose(
            row["reserve_j"],
            2e-5 * np.array(BASE_SIZES) ** 3 * np.exp(-0.15 * row["time_s"] / np.array(BASE_SIZES)),
            rtol=1e-11,
            atol=1e-20,
        )
        assert np.max(abs(np.asarray(row["rates"]))) == 0
        assert sum(row["work_j"]) == 0
        assert row["total_mechanical_j"] == 0


def test_energy_closure_and_finite_supply(runs):
    for run in runs.values():
        assert run["termination"]["status"] == "completed"
        for key in (
            "max_node_mechanical_residual_j",
            "max_node_reservoir_residual_j",
            "max_edge_residual_j",
        ):
            assert max(run[key]) < 1e-12
        assert max(run["max_group_residual_j"].values()) < 1e-12
        assert min(run["finite_supply_margin_j"]) >= 0
        assert min(run["final_reserve_fraction"]) > 0
        assert run["max_reserve_step_increase_j"] == 0
        assert np.all(
            np.array(run["final_reserve_fraction"])
            <= np.array(run["analytical_bounds"]["reserve_fraction_upper"]) + 1e-11
        )


def test_passive_network_mechanics_monotone(runs):
    run = runs["passive"]
    assert run["max_mechanical_step_increase_j"] < 1e-17
    assert run["analytical_bounds"]["damping_dominates_by_s"] == [0] * 4
    assert run["post_crossover_intervals"] > 0
    assert run["max_post_crossover_mechanical_step_increase_j"] < 1e-17


def test_crossover_inequality_is_uniform_after_bound():
    sizes = np.array(BASE_SIZES)
    times = np.array(module.bounds(0)["damping_dominates_by_s"])
    np.testing.assert_allclose(times, sizes * np.log(6) / 0.15)
    reserve = 2e-5 * sizes**3 * np.exp(-0.15 * times / sizes)
    np.testing.assert_allclose(4 * reserve / (reserve + 1e-5 * sizes**3), 1)
    assert module.bounds(0, gain=1)["damping_dominates_by_s"] == [0] * 4
    np.testing.assert_allclose(
        module.bounds(0, gain=4, reserve0=4e-5 * sizes**3)["damping_dominates_by_s"],
        sizes * np.log(12) / 0.15,
    )


def test_domain_exit_retains_last_accepted_state_without_clipping():
    initial = initial_state(BASE_SIZES, EDGES)
    initial[0], initial[2] = 1.099999, 0.1
    run = module.simulate(0.1, initial=initial)
    assert run["termination"]["status"] == "scope_termination"
    assert run["termination"]["last_accepted_time_s"] == 0
    np.testing.assert_array_equal(run["final_state"], initial)
    assert "outside declared scope" in run["termination"]["reason"]


def test_unrelated_value_error_not_reclassified(monkeypatch):
    real_rhs = module.rhs
    calls = 0

    def broken(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls > 2:
            raise ValueError("unexpected defect")
        return real_rhs(*args, **kwargs)

    monkeypatch.setattr(module, "rhs", broken)
    with pytest.raises(ValueError, match="unexpected defect"):
        module.simulate(0.1)


def test_later_invalid_stage_retains_preceding_accepted_endpoint(monkeypatch):
    real_rhs = module.rhs
    calls = 0

    def rejected_stage(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls > 20:
            raise ValueError("negative reservoir: injected rejected stage")
        return real_rhs(*args, **kwargs)

    monkeypatch.setattr(module, "rhs", rejected_stage)
    run = module.simulate(0.1, max_step=0.01)
    assert run["termination"]["status"] == "scope_termination"
    assert 0 < run["termination"]["last_accepted_time_s"] < 0.1
    assert run["samples"][-1]["time_s"] == run["termination"]["last_accepted_time_s"]
    np.testing.assert_array_equal(
        run["samples"][-1]["q"], np.array(run["final_state"][:36]).reshape(4, 9)[:, :2]
    )
    assert min(run["final_reserve_fraction"]) > 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"duration": 0},
        {"duration": 61},
        {"duration": True},
        {"max_step": 0},
        {"max_step": 0.2},
        {"rtol": 0},
        {"rtol": float("nan")},
        {"atol_factor": 0},
        {"rest": 1},
        {"gain": -1},
    ],
)
def test_invalid_settings(kwargs):
    with pytest.raises(ValueError):
        module.simulate(**kwargs)


def test_refinement_matches_at_fixed_short_horizon(runs):
    fine = module.simulate(1, max_step=0.025, rtol=1e-9, atol_factor=0.1)
    a = np.array(runs["active"]["final_state"][:36]).reshape(4, 9)
    b = np.array(fine["final_state"][:36]).reshape(4, 9)
    assert np.max(abs(a[:, :4] - b[:, :4])) < 1e-7
    assert np.max(abs(a[:, 4:] - b[:, 4:])) < 1e-12
