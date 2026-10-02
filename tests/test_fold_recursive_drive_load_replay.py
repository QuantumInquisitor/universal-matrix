"""Controls for recursive drive-history and downstream-loading replay."""

import numpy as np
import pytest

from scripts.report_fold_recursive_drive_load_replay import (
    SAMPLE_TIMES_S,
    hermite_parent,
    replay_configuration,
    report,
)


@pytest.fixture(scope="module")
def result():
    return report()


def test_full_tree_and_replays_close_energy_accounts(result):
    full = result["full_tree_energy"]
    assert max(full["max_node_residual_j"]) < 1e-10
    assert max(full["max_edge_residual_j"]) < 1e-10
    assert max(full["max_group_residual_j"].values()) < 1e-10
    for case in result["cases"].values():
        assert case["free"]["max_energy_balance_residual_j"] < 1e-10
        assert case["loaded"]["max_energy_balance_residual_j"] < 1e-10


def test_replay_comparisons_are_finite_and_nonnegative(result):
    for case in result["cases"].values():
        assert set(case["comparisons"]) == {str(time) for time in SAMPLE_TIMES_S}
        for row in case["comparisons"].values():
            for key in (
                "isolated_fraction",
                "free_replay_fraction",
                "loaded_replay_fraction",
                "embedded_fraction",
                "upstream_history_factor",
                "downstream_loading_factor",
                "replay_to_embedded_fraction_ratio",
                "loaded_root_coordinate_error",
                "loaded_root_rate_error",
            ):
                assert row[key] is not None
                assert np.isfinite(row[key])
                assert row[key] >= 0


def test_level_three_free_and_loaded_replays_are_identical(result):
    for row in result["cases"]["3"]["comparisons"].values():
        assert row["free_replay_fraction"] == pytest.approx(
            row["loaded_replay_fraction"], rel=0, abs=1e-14
        )


def test_loaded_replay_tracks_embedded_child_reasonably(result):
    for case in result["cases"].values():
        for row in case["comparisons"].values():
            assert row["loaded_root_coordinate_error"] < 1e-5
            assert row["loaded_root_rate_error"] < 1e-4


def test_replay_claim_boundaries_remain_explicit(result):
    assert result["parent_trajectory_prescribed_from_full_tree"]
    assert not result["connector_coefficients_changed"]
    assert not result["material_scaling_law_changed"]
    assert not result["new_recursive_coupling_introduced"]
    assert not result["global_spatial_embedding_validated"]


@pytest.mark.parametrize(
    "level,loaded",
    [(0, False), (4, False), (1, 0), (2, "yes"), (3, None)],
)
def test_invalid_replay_configuration_rejected(level, loaded):
    with pytest.raises(ValueError):
        replay_configuration(level, loaded)


def test_parent_hermite_rejects_out_of_range_time():
    fake = {
        "settings": {"dt_s": 0.1},
        "trace": [
            {"q": [[1, 2]], "rates": [[0, 0]]},
            {"q": [[1, 2]], "rates": [[0, 0]]},
        ],
    }
    with pytest.raises(ValueError):
        hermite_parent(fake, 0, 0.3)
