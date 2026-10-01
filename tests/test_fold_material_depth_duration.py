"""Controls for the bounded 0.1 s depth-three duration extension."""

import math

import numpy as np
import pytest

from scripts.report_fold_material_depth3 import initial_state, tree_configuration
from scripts.report_fold_material_depth_duration import (
    MAX_DURATION_S,
    RESOLUTION,
    SAMPLE_TIMES_S,
    advance,
    report,
)


@pytest.fixture(scope="module")
def result():
    return report()


def test_extended_healthy_cases_close_energy_accounts(result):
    for name in (
        "depth_2",
        "depth_3",
        "fine_depth_3",
        "depth_3_first_half",
        "depth_3_second_half",
    ):
        case = result["cases"][name]
        assert max(case["max_node_residual_j"]) < 1e-10
        assert max(case["max_edge_residual_j"], default=0) < 1e-10
        assert max(case["max_group_residual_j"].values()) < 1e-10


def test_all_extended_coordinates_remain_in_declared_domain(result):
    for name in ("depth_2", "depth_3", "fine_depth_3"):
        case = result["cases"][name]
        minimum = np.asarray(case["coordinate_min"])
        maximum = np.asarray(case["coordinate_max"])
        assert np.min(minimum[:, 0]) >= 0.9
        assert np.max(maximum[:, 0]) <= 1.1
        assert np.min(minimum[:, 1]) >= 0
        assert np.max(maximum[:, 1]) <= math.pi / 6


def test_segmented_restart_matches_continuous_depth_three(result):
    assert result["restart"]["maximum_absolute_state_difference"] < 1e-12


def test_longer_duration_classification_is_derived(result):
    assert tuple(result["sample_times_s"]) == SAMPLE_TIMES_S
    assert result["resolution_threshold"] == RESOLUTION
    samples = result["depth_2_to_3"]["samples"]
    for time_s in SAMPLE_TIMES_S:
        row = samples[str(time_s)]
        maximum = max(row["root_absolute_state_change"])
        assert row["maximum_root_absolute_state_change"] == pytest.approx(maximum)
        assert row["resolved"] is (maximum > RESOLUTION)
    expected = next(
        (time_s for time_s in SAMPLE_TIMES_S if samples[str(time_s)]["resolved"]),
        None,
    )
    assert result["depth_2_to_3"]["first_resolved_duration_s"] == expected


def test_depth_three_refinement_remains_bounded(result):
    assert result["refinement"]["maximum_absolute_state_difference"] < 1e-6


def test_no_physical_law_or_production_guard_was_changed(result):
    assert not result["connector_law_changed"]
    assert not result["material_scaling_law_changed"]
    assert not result["production_duration_guard_changed"]
    assert not result["arbitrary_depth_validated"]
    assert not result["infinite_depth_limit_validated"]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"duration": 0},
        {"duration": 0.1005},
        {"duration": float("nan")},
        {"duration": True},
        {"duration": 0.05025},
        {"duration": 0.05, "refinement": 3},
    ],
)
def test_invalid_duration_extension_controls(kwargs):
    cfg = tree_configuration(3)
    initial = initial_state(cfg["sizes"], cfg["edges"])
    with pytest.raises(ValueError):
        advance(initial, 3, **kwargs)


def test_declared_maximum_duration_constant():
    assert MAX_DURATION_S == 0.1
