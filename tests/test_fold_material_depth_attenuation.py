"""Controls for recursive root-backreaction attenuation versus time and depth."""

import numpy as np
import pytest

from scripts.report_fold_material_depth3 import simulate
from scripts.report_fold_material_depth_attenuation import (
    DEPTHS,
    DURATIONS_S,
    RESOLUTION,
    report,
)


@pytest.fixture(scope="module")
def result():
    return report()


def test_sweep_is_declared_before_classification(result):
    assert tuple(result["durations_s"]) == DURATIONS_S
    assert tuple(result["depths"]) == DEPTHS
    assert result["resolution_threshold"] == RESOLUTION
    assert len(result["rows"]) == len(DURATIONS_S)


def test_all_sweep_runs_close_energy_accounts(result):
    for case in result["energy_accounts"].values():
        assert max(case["max_node_residual_j"]) < 1e-11
        assert max(case["max_edge_residual_j"], default=0) < 1e-11
        assert max(case["max_group_residual_j"].values()) < 1e-11


def test_resolution_flags_are_derived_not_forced(result):
    for row in result["rows"]:
        assert set(row["transitions"]) == {"0_to_1", "1_to_2", "2_to_3"}
        for transition in row["transitions"].values():
            maximum = max(transition["root_absolute_state_change"])
            assert transition["maximum_root_absolute_state_change"] == pytest.approx(
                maximum
            )
            assert transition["resolved"] is (maximum > RESOLUTION)

    for name, summary in result["summary"].items():
        values = [
            row["transitions"][name]["maximum_root_absolute_state_change"]
            for row in result["rows"]
        ]
        assert summary["maximum_over_duration_grid"] == max(values)
        expected = next(
            (
                row["duration_s"]
                for row in result["rows"]
                if row["transitions"][name]["resolved"]
            ),
            None,
        )
        assert summary["first_resolved_duration_s"] == expected


def test_disconnected_depth_three_matches_single_root(result):
    control = result["disconnected_control"]
    assert control["duration_s"] == max(DURATIONS_S)
    assert control["maximum_root_absolute_state_change"] < 1e-14


def test_depth_three_direct_reference_remains_consistent():
    run = simulate(3, duration=0.05)
    assert max(run["max_node_residual_j"]) < 1e-11
    assert max(run["max_edge_residual_j"]) < 1e-11
    assert max(run["max_group_residual_j"].values()) < 1e-11


def test_claim_boundaries_and_unchanged_laws(result):
    assert not result["connector_law_changed"]
    assert not result["material_scaling_law_changed"]
    assert not result["threshold_tuned_to_result"]
    assert not result["arbitrary_depth_validated"]
    assert not result["infinite_depth_limit_validated"]
    assert not result["macroscopic_deep_backreaction_claimed"]


def test_summary_ratios_are_nonnegative_or_none(result):
    for item in result["summary"].values():
        ratio = item["relative_to_depth_0_to_1_maximum"]
        assert ratio is None or np.isfinite(ratio) and ratio >= 0
