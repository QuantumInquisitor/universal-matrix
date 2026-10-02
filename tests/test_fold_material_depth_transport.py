"""Controls for per-level recursive material transport diagnostics."""

import numpy as np
import pytest

from scripts.report_fold_material_depth_transport import (
    RESPONSE_FLOOR,
    SAMPLE_TIMES_S,
    report,
    simulate_transport,
)


@pytest.fixture(scope="module")
def result():
    return report()


def test_transport_runs_close_all_energy_accounts(result):
    for run in (result["connected"], result["disconnected"]):
        assert max(run["max_node_residual_j"]) < 1e-10
        assert max(run["max_edge_residual_j"], default=0) < 1e-10
        assert max(run["max_group_residual_j"].values()) < 1e-10


def test_declared_sample_grid_and_level_membership(result):
    run = result["connected"]
    assert tuple(run["settings"]["sample_times_s"]) == SAMPLE_TIMES_S
    assert run["settings"]["response_floor"] == RESPONSE_FLOOR
    assert [row["time_s"] for row in run["snapshots"]] == list(SAMPLE_TIMES_S)
    first = run["snapshots"][0]["levels"]
    assert [first[str(level)]["module_count"] for level in range(4)] == [1, 2, 4, 8]


def test_only_root_is_perturbed_initially(result):
    first = result["connected"]["snapshots"][0]
    assert first["levels"]["0"]["maximum_coordinate_response"] > 0
    for level in (1, 2, 3):
        assert first["levels"][str(level)]["maximum_coordinate_response"] == 0
        assert first["levels"][str(level)]["maximum_scale_normalized_rate"] == 0


def test_deeper_connector_potentials_start_unloaded(result):
    first = result["connected"]["snapshots"][0]["edges_by_child_level"]
    assert first["1"]["connector_potential_j"] > 0
    assert first["2"]["connector_potential_j"] == 0
    assert first["3"]["connector_potential_j"] == 0


def test_disconnected_descendants_remain_exactly_unresponsive(result):
    assert result["disconnected_descendant_maximum_coordinate_response"] == 0
    run = result["disconnected"]
    for snapshot in run["snapshots"]:
        for level in (1, 2, 3):
            metrics = snapshot["levels"][str(level)]
            assert metrics["maximum_coordinate_response"] == 0
            assert metrics["maximum_scale_normalized_rate"] == 0
            assert metrics["mechanical_energy_j"] == 0
        for metrics in snapshot["edges_by_child_level"].values():
            assert metrics["edge_count"] == 0
            assert metrics["connector_potential_j"] == 0
            assert metrics["sum_abs_child_endpoint_work_j"] == 0


def test_resolution_times_follow_recorded_coordinate_floor(result):
    run = result["connected"]
    assert run["first_coordinate_resolution_s"]["0"] == 0
    for level in (1, 2, 3):
        value = run["first_coordinate_resolution_s"][str(level)]
        assert value is None or 0 < value <= run["settings"]["duration_s"]


def test_snapshot_metrics_are_finite_nonnegative_where_unsigned(result):
    for snapshot in result["connected"]["snapshots"]:
        for metrics in snapshot["levels"].values():
            for key in (
                "maximum_coordinate_response",
                "maximum_scale_normalized_rate",
                "mechanical_energy_j",
                "damping_loss_j",
            ):
                assert np.isfinite(metrics[key])
                assert metrics[key] >= 0
        for metrics in snapshot["edges_by_child_level"].values():
            for key in (
                "connector_potential_j",
                "sum_abs_child_endpoint_work_j",
                "maximum_abs_child_endpoint_work_j",
            ):
                assert np.isfinite(metrics[key])
                assert metrics[key] >= 0


def test_claim_boundaries_remain_explicit(result):
    assert not result["connector_law_changed"]
    assert not result["material_scaling_law_changed"]
    assert not result["response_floor_tuned_to_result"]
    assert not result["spatial_parent_child_geometry_validated"]
    assert not result["arbitrary_depth_validated"]
    assert not result["infinite_depth_limit_validated"]


@pytest.mark.parametrize("connected", [0, 1, "yes", None])
def test_invalid_connected_control_rejected(connected):
    with pytest.raises(ValueError):
        simulate_transport(connected=connected)
