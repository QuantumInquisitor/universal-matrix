"""Controls for replicated passive material modules in a binary tree."""

import pytest

from scripts.report_fold_material_recursive_tree import (
    recursive_configuration,
    report,
    simulate,
)


def test_recursive_configuration_has_real_additional_degrees_of_freedom():
    expected = {
        0: (1, 0),
        1: (3, 2),
        2: (7, 6),
    }
    for depth, (nodes, edges) in expected.items():
        cfg = recursive_configuration(depth)
        assert len(cfg["sizes"]) == nodes
        assert len(cfg["edges"]) == edges
        assert cfg["levels"].count(depth) == 2**depth
        assert min(cfg["sizes"]) == 0.5**depth


@pytest.fixture(scope="module")
def result():
    return report()


def test_healthy_recursive_cases_close_energy_accounts(result):
    for name in ("depth_0", "depth_1", "depth_2", "disconnected_depth_2", "fine_depth_2"):
        case = result["cases"][name]
        assert max(case["max_node_residual_j"]) < 1e-12
        assert max(case["max_edge_residual_j"], default=0) < 1e-12
        assert max(case["max_group_residual_j"].values()) < 1e-12


def test_disconnected_extra_modules_do_not_change_root_dynamics(result):
    delta = result["depth_response"]["disconnected_depth_2_to_depth_0_root_absolute_state_change"]
    assert max(delta) < 1e-14


def test_connected_child_modules_change_root_response(result):
    first = result["depth_response"]["depth_0_to_1_root_absolute_state_change"]
    second = result["depth_response"]["depth_1_to_2_root_absolute_state_change"]
    assert max(first) > 1e-12
    assert max(second) > 1e-12


def test_broken_parent_child_reaction_is_detected(result):
    healthy = result["cases"]["depth_2"]
    broken = result["cases"]["broken_depth_2"]
    assert broken["max_edge_residual_j"][0] > 1e-13
    assert broken["max_edge_residual_j"][0] > 100 * max(healthy["max_edge_residual_j"])


def test_depth_two_refinement_agrees(result):
    assert result["refinement"]["maximum_absolute_state_difference"] < 1e-7


def test_claim_boundaries_are_explicit(result):
    assert result["replicated_dynamical_modules"]
    assert result["maximum_physical_modules_tested"] == 7
    assert result["physical_depths_tested"] == [0, 1, 2]
    assert not result["arbitrary_depth_validated"]
    assert not result["spatial_parent_child_geometry_validated"]
    assert not result["powered_recursive_tree_validated"]
    assert not result["stable_recursive_limit_cycle_validated"]


@pytest.mark.parametrize("depth", [-1, 3, True, 1.5])
def test_invalid_depth_rejected(depth):
    with pytest.raises(ValueError):
        recursive_configuration(depth)


def test_invalid_connected_flag_rejected():
    with pytest.raises(ValueError):
        recursive_configuration(1, connected=1)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"refinement": 3},
        {"duration": 0},
        {"duration": 0.2},
        {"broken_edge": True},
        {"broken_edge": 6},
    ],
)
def test_invalid_simulation_controls_rejected(kwargs):
    with pytest.raises(ValueError):
        simulate(2, **kwargs)
