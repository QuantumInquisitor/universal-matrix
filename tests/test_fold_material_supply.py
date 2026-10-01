"""Energy-source and accounting controls for the powered material graph."""

import numpy as np
import pytest

from scripts.report_fold_dynamics import Q0
from scripts.report_fold_material_supply import (
    BASE_SIZES,
    CAPACITY_DENSITY_J,
    EDGES,
    active_rhs,
    initial_state,
    rhs,
    simulate,
)


def test_source_off_reduces_exactly_to_unreplenished_material_rhs():
    y = initial_state()
    expected = active_rhs(y[:-4], BASE_SIZES, EDGES)
    actual = rhs(y, power_density=0)
    np.testing.assert_allclose(actual[:-4], expected, rtol=0, atol=0)
    np.testing.assert_array_equal(actual[-4:], 0)


def test_equilibrium_replenishment_has_identified_source_without_motion():
    y = initial_state()
    blocks = y[:36].reshape(4, 9)
    blocks[:, :4] = np.tile(np.r_[Q0, 0.0, 0.0], (4, 1))
    capacity = CAPACITY_DENSITY_J * np.asarray(BASE_SIZES) ** 3
    blocks[:, 4] = capacity / 2
    derivative = rhs(y, power_density=6e-6)
    db = derivative[:36].reshape(4, 9)
    np.testing.assert_allclose(db[:, :4], 0, atol=1e-20)
    np.testing.assert_allclose(db[:, 5:9], 0, atol=1e-20)
    assert np.all(db[:, 4] > 0)
    np.testing.assert_allclose(db[:, 4], derivative[-4:])


@pytest.fixture(scope="module")
def runs():
    return (
        simulate(),
        simulate(power_density=0),
        simulate(omitted_debit=0),
        simulate(max_step=0.001, rtol=1e-10),
    )


def test_powered_and_source_off_accounts_close(runs):
    powered, source_off, _, fine = runs
    for run in (powered, source_off, fine):
        for key in (
            "max_node_mechanical_residual_j",
            "max_node_reservoir_residual_j",
            "max_edge_residual_j",
        ):
            assert max(run[key]) < 1e-11
        assert max(run["max_group_residual_j"].values()) < 1e-11
        assert min(run["minimum_reserve_j"]) >= 0
        assert max(run["maximum_reserve_upper_violation_j"]) < 1e-13
        assert max(run["maximum_power_budget_violation_w"]) < 1e-15
        assert min(run["finite_supply_margin_j"]) >= -1e-13

    assert powered["total_received_j"] > 0
    assert source_off["total_received_j"] == 0
    assert powered["missing_input_control_max_group_residual_j"]["root"] > 1e-9
    assert source_off["missing_input_control_max_group_residual_j"]["root"] < 1e-11


def test_bad_reserve_debit_is_detected_and_localized(runs):
    _, _, broken, _ = runs
    assert broken["max_node_reservoir_residual_j"][0] > 1e-10
    assert max(
        broken["max_node_reservoir_residual_j"][i] for i in (1, 2, 3)
    ) < 1e-11
    assert broken["max_group_residual_j"]["root"] > 1e-10
    assert broken["max_group_residual_j"]["root/0"] > 1e-10
    assert broken["max_group_residual_j"]["root/1"] < 1e-11


def test_refined_powered_trajectory_agrees(runs):
    powered, _, _, fine = runs
    delta = np.asarray(powered["final_state"]) - np.asarray(fine["final_state"])
    blocks = abs(delta[:36]).reshape(4, 9)
    assert np.max(blocks[:, :2]) < 1e-7
    assert np.max(blocks[:, 2:4]) < 1e-6
    assert np.max(blocks[:, 4:]) < 1e-12
    assert np.max(abs(delta[36:])) < 1e-12


@pytest.mark.parametrize(
    "kwargs",
    [
        {"duration": 0},
        {"duration": 2},
        {"max_step": 0.02},
        {"rtol": 1e-5},
        {"power_density": -1},
        {"omitted_debit": True},
        {"omitted_debit": 4},
    ],
)
def test_invalid_inputs_rejected(kwargs):
    with pytest.raises(ValueError):
        simulate(**kwargs)
