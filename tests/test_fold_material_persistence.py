"""Restart persistence and hierarchy-depth controls for powered material state."""

import numpy as np
import pytest

from scripts.report_fold_material_persistence import advance, hierarchy_audit, report, wrapped_tree
from scripts.report_fold_material_supply import initial_state
from scripts.report_fold_hierarchy import compile_hierarchy
from scripts.report_fold_multiscale import EDGES


@pytest.fixture(scope="module")
def result():
    return report()


def test_segmented_restart_matches_continuous_powered_run(result):
    restart = result["restart"]
    assert restart["powered_maximum_absolute_state_difference"] < 1e-8
    delta = np.asarray(restart["powered_absolute_state_differences"])
    assert np.max(delta[:36]) < 1e-8
    assert np.max(delta[36:]) < 1e-12


def test_segmented_restart_matches_continuous_source_off_run(result):
    restart = result["restart"]
    assert restart["source_off_maximum_absolute_state_difference"] < 1e-8
    delta = np.asarray(restart["source_off_absolute_state_differences"])
    assert np.max(delta[:36]) < 1e-8
    assert np.max(delta[36:]) < 1e-12


def test_every_segment_keeps_energy_ledgers_closed(result):
    for segment in result["segments"].values():
        for key in (
            "max_node_mechanical_residual_j",
            "max_node_reservoir_residual_j",
            "max_edge_residual_j",
        ):
            assert max(segment[key]) < 1e-10
        assert max(segment["max_group_residual_j"].values()) < 1e-10
        assert min(segment["minimum_reserve_j"]) >= 0


def test_deeper_hierarchy_is_only_regrouping(result):
    audit = result["hierarchy"]
    assert not audit["physical_recursive_replication_tested"]
    assert set(audit["cases"]) == {"0", "1", "3", "6"}
    for case in audit["cases"].values():
        assert abs(case["root_energy_difference_j"]) < 1e-18
        assert abs(case["root_input_difference_j"]) < 1e-18
        assert case["owned_edge_count"] == len(EDGES)
    assert audit["cases"]["6"]["group_count"] > audit["cases"]["0"]["group_count"]


def test_depth_limit_is_explicit_not_silent():
    with pytest.raises(ValueError):
        wrapped_tree(7)
    tree = wrapped_tree(6)
    compile_hierarchy(4, EDGES, tree)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"duration": 0},
        {"duration": 2},
        {"max_step": 0.02},
        {"rtol": 1e-5},
    ],
)
def test_invalid_advance_inputs(kwargs):
    with pytest.raises(ValueError):
        advance(initial_state(), **kwargs)


def test_saved_state_shape_is_enforced():
    with pytest.raises(ValueError):
        advance([0] * 47, 0.1)


def test_claim_boundaries_remain_explicit(result):
    assert result["persistent_state_demonstrated_over_s"] == 0.8
    assert not result["arbitrary_physical_depth_demonstrated"]
    assert not result["stable_limit_cycle_demonstrated"]
    assert not result["measured_material_calibration"]
