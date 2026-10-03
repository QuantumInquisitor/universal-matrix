"""Controls for the recursive upstream-parent drive audit."""

import numpy as np
import pytest

from scripts.report_fold_recursive_parent_drive import SAMPLE_TIMES_S, _power_factor, report


@pytest.fixture(scope="module")
def result():
    return report()


def test_full_tree_energy_accounts_remain_closed(result):
    full = result["full_tree_energy"]
    assert max(full["max_node_residual_j"]) < 1e-10
    assert max(full["max_edge_residual_j"]) < 1e-10
    assert max(full["max_group_residual_j"].values()) < 1e-10


def test_all_drive_metrics_and_ratios_are_finite(result):
    for case in result["cases"].values():
        assert set(case["rows"]) == {str(time) for time in SAMPLE_TIMES_S}
        for row in case["rows"].values():
            for side in ("embedded", "isolated"):
                metrics = row[side]
                for key in (
                    "parent_displacement_norm",
                    "parent_scaled_rate_norm",
                    "child_displacement_norm",
                    "child_scaled_rate_norm",
                    "relative_port_displacement_m",
                    "connector_potential_j",
                    "parent_force_norm",
                    "child_force_norm",
                    "parent_power_w",
                    "child_power_w",
                ):
                    assert np.isfinite(metrics[key])
                for key in ("parent_power_factor", "child_power_factor"):
                    assert metrics[key] is None or -1 <= metrics[key] <= 1
            for value in row["magnitude_ratios"].values():
                assert value is None or np.isfinite(value) and value >= 0


def test_first_interface_drive_remains_closest_to_isolated_at_final_time(result):
    final = str(max(SAMPLE_TIMES_S))
    ratios = {
        level: result["cases"][str(level)]["rows"][final]["magnitude_ratios"][
            "parent_displacement_norm"
        ]
        for level in (1, 2, 3)
    }
    assert abs(ratios[1] - 1) < abs(ratios[2] - 1)
    assert abs(ratios[1] - 1) < abs(ratios[3] - 1)


def test_power_factor_helper_handles_zero_and_bounds():
    assert _power_factor([0, 0], [1, 2]) is None
    assert _power_factor([1, 0], [1, 0]) == pytest.approx(1)
    assert _power_factor([1, 0], [-1, 0]) == pytest.approx(-1)


def test_claim_boundaries_remain_explicit(result):
    assert result["power_factor_is_generalized_coordinate_diagnostic"]
    assert not result["connector_coefficients_changed"]
    assert not result["material_scaling_law_changed"]
    assert not result["new_recursive_coupling_introduced"]
