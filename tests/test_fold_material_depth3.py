"""Controls for the 15-module experimental depth-three material tree."""

import numpy as np
import pytest

from scripts.report_fold_material_depth3 import (
    report,
    simulate,
    subtree_members,
    tree_configuration,
)


def test_depth_three_configuration_has_fifteen_dynamical_modules():
    cfg = tree_configuration(3)
    assert len(cfg["sizes"]) == 15
    assert len(cfg["edges"]) == 14
    assert cfg["levels"].count(3) == 8
    assert min(cfg["sizes"]) == 0.125
    assert cfg["sizes"][0] == 1


def test_subtree_membership_is_complete_and_nonovercounting():
    groups = subtree_members(15)
    assert groups[0] == tuple(range(15))
    assert groups[7] == (7,)
    assert groups[1] == (1, 3, 4, 7, 8, 9, 10)
    assert groups[2] == (2, 5, 6, 11, 12, 13, 14)


@pytest.fixture(scope="module")
def result():
    return report()


def test_healthy_depth_three_cases_close_all_energy_accounts(result):
    for name in ("depth_2", "depth_3", "disconnected_depth_3", "fine_depth_3", "single"):
        case = result["cases"][name]
        assert max(case["max_node_residual_j"]) < 1e-11
        assert max(case["max_edge_residual_j"], default=0) < 1e-11
        assert max(case["max_group_residual_j"].values()) < 1e-11


def test_disconnected_descendants_do_not_change_root(result):
    delta = result["depth_response"][
        "disconnected_depth_3_to_single_root_absolute_state_change"
    ]
    assert max(delta) < 1e-14


def test_depth_three_root_backreaction_is_below_declared_resolution(result):
    response = result["depth_response"]
    delta = response["depth_2_to_3_root_absolute_state_change"]
    assert max(delta) < response["resolved_root_backreaction_threshold"]
    assert not response["depth_3_root_backreaction_resolved"]


def test_broken_reaction_is_detected(result):
    healthy = result["cases"]["depth_3"]
    broken = result["cases"]["broken_depth_3"]
    assert broken["max_edge_residual_j"][0] > 1e-13
    assert broken["max_edge_residual_j"][0] > 100 * max(healthy["max_edge_residual_j"])


def test_depth_three_refinement_agrees(result):
    assert result["refinement"]["maximum_absolute_state_difference"] < 2e-7


def test_claim_boundaries_remain_explicit(result):
    assert result["physical_depth_three_executed"]
    assert result["maximum_modules_tested"] == 15
    assert result["smallest_scale_tested"] == 0.125
    assert not result["production_scale_guard_changed"]
    assert not result["production_topology_guard_changed"]
    assert not result["spatial_parent_child_geometry_validated"]
    assert not result["powered_depth_three_validated"]
    assert not result["arbitrary_depth_validated"]
    assert not result["infinite_depth_convergence_validated"]


@pytest.mark.parametrize("depth", [-1, 4, True, 1.5])
def test_invalid_depth_rejected(depth):
    with pytest.raises(ValueError):
        tree_configuration(depth)


@pytest.mark.parametrize("nodes", [0, 2, 8, 31])
def test_invalid_subtree_size_rejected(nodes):
    with pytest.raises(ValueError):
        subtree_members(nodes)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"refinement": 3},
        {"duration": 0},
        {"duration": 0.051},
        {"broken_edge": True},
        {"broken_edge": 14},
    ],
)
def test_invalid_simulation_controls_rejected(kwargs):
    with pytest.raises(ValueError):
        simulate(3, **kwargs)
