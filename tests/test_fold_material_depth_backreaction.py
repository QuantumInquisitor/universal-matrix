"""Controls for selective-level recursive backreaction diagnostics."""

import numpy as np
import pytest

from scripts.report_fold_material_depth_backreaction import (
    RESPONSE_FLOOR,
    SAMPLE_TIMES_S,
    configuration_through_level,
    report,
    simulate,
)


@pytest.fixture(scope="module")
def result():
    return report()


def test_all_runs_keep_fifteen_modules_and_expected_edges(result):
    expected_edges = {"0": 0, "1": 2, "2": 6, "3": 14}
    for level, run in result["runs"].items():
        assert len(run["settings"]["sizes"]) == 15
        assert len(run["settings"]["edges"]) == expected_edges[level]


def test_all_runs_close_energy_accounts(result):
    for run in result["runs"].values():
        assert max(run["max_node_residual_j"]) < 1e-10
        assert max(run["max_edge_residual_j"], default=0) < 1e-10
        assert max(run["max_group_residual_j"].values()) < 1e-10


def test_incremental_backreaction_is_derived_from_fixed_module_count(result):
    assert tuple(result["sample_times_s"]) == SAMPLE_TIMES_S
    assert result["response_floor"] == RESPONSE_FLOOR
    for time_s in SAMPLE_TIMES_S:
        row = result["incremental_root_backreaction"][str(time_s)]
        for level in ("1", "2", "3"):
            maximum = max(row[level]["absolute_root_state_change"])
            assert row[level]["maximum_absolute_root_state_change"] == pytest.approx(maximum)
            assert row[level]["resolved"] is (maximum > RESPONSE_FLOOR)


def test_full_tree_edge_energy_identities_close(result):
    rows = result["full_tree_final_edge_energy_transfer"]
    for level in ("1", "2", "3"):
        assert rows[level]["edge_count"] == 2 ** int(level)
        assert abs(rows[level]["energy_identity_residual_j"]) < 1e-10
        fraction = rows[level]["child_uptake_fraction_of_parent_magnitude"]
        assert fraction is not None
        assert np.isfinite(fraction)
        assert fraction >= 0


def test_cut_runs_have_no_deeper_edge_work(result):
    for admitted in (0, 1, 2):
        final = result["runs"][str(admitted)]["snapshots"][-1]
        for child_level in range(admitted + 1, 4):
            row = final["edge_levels"][str(child_level)]
            assert row["edge_count"] == 0
            assert row["potential_change_j"] == 0
            assert row["parent_endpoint_work_j"] == 0
            assert row["child_endpoint_work_j"] == 0


def test_claim_boundaries_remain_explicit(result):
    assert result["module_count_held_fixed"]
    assert not result["connector_coefficients_changed"]
    assert not result["material_scaling_law_changed"]
    assert not result["spatial_parent_child_geometry_validated"]
    assert not result["new_recursive_coupling_introduced"]
    assert not result["arbitrary_depth_validated"]


@pytest.mark.parametrize("level", [-1, 4, True, 1.5, None])
def test_invalid_edge_level_rejected(level):
    with pytest.raises(ValueError):
        configuration_through_level(level)


def test_direct_simulation_uses_requested_edge_level():
    run = simulate(2)
    assert run["settings"]["connected_through_level"] == 2
    assert len(run["settings"]["edges"]) == 6
