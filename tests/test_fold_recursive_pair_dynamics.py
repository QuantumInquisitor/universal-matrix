"""Controls for isolated versus embedded recursive pair dynamics."""

import numpy as np
import pytest

from scripts.report_fold_recursive_pair_dynamics import (
    EMBEDDED_PHYSICAL_TIMES_S,
    PARENT_SCALES,
    REFERENCE_SAMPLE_TIMES_S,
    initial_state,
    pair_sizes,
    report,
)


@pytest.fixture(scope="module")
def result():
    return report()


def test_isolated_pair_energy_accounts_close(result):
    for row in result["pairs"].values():
        assert row["max_module_residual_j"] < 1e-10
        assert row["max_connector_residual_j"] < 1e-10
        assert row["max_total_residual_j"] < 1e-10


def test_isolated_pair_dynamics_are_self_similar(result):
    for scale in PARENT_SCALES:
        row = result["pair_similarity"][str(scale)]
        assert row["coordinate_max_difference"] < 1e-10
        assert row["rescaled_rate_max_difference"] < 1e-9
        assert row["rescaled_energy_max_difference_j"] < 1e-10
        assert row["rescaled_work_max_difference_j"] < 1e-10


def test_isolated_child_work_fraction_repeats_at_matching_reference_time(result):
    for time in REFERENCE_SAMPLE_TIMES_S:
        values = [
            result["isolated_samples"][str(scale)][str(time)][
                "child_work_fraction_of_parent_magnitude"
            ]
            for scale in PARENT_SCALES
        ]
        assert all(value is not None for value in values)
        assert max(values) - min(values) < 1e-10


def test_embedded_comparison_uses_corresponding_scaled_time(result):
    for child_level, parent_scale in ((1, 1.0), (2, 0.5), (3, 0.25)):
        rows = result["embedded_comparison"][str(child_level)]
        assert set(rows) == {str(time) for time in EMBEDDED_PHYSICAL_TIMES_S}
        for physical_time in EMBEDDED_PHYSICAL_TIMES_S:
            row = rows[str(physical_time)]
            assert row["parent_scale"] == parent_scale
            assert row["reference_time_s"] == pytest.approx(
                physical_time / parent_scale
            )
            assert row["isolated_child_work_fraction"] is not None
            assert row["embedded_child_work_fraction"] is not None
            assert np.isfinite(row["embedded_to_isolated_fraction_ratio"])
            assert row["embedded_to_isolated_fraction_ratio"] >= 0


def test_quarter_to_eighth_refinement_is_bounded(result):
    assert result["quarter_to_eighth_refinement_max_state_difference"] < 1e-6


def test_claim_boundaries_remain_explicit(result):
    assert not result["connector_coefficients_changed"]
    assert not result["material_scaling_law_changed"]
    assert not result["production_scale_guard_changed"]
    assert result["isolated_pair_similarity_expected"]
    assert not result["embedded_loading_equated_with_isolated_pair"]
    assert not result["new_recursive_coupling_introduced"]


@pytest.mark.parametrize("scale", [0, 0.125, 0.75, 2, True, None])
def test_invalid_parent_scale_rejected(scale):
    with pytest.raises(ValueError):
        pair_sizes(scale)


def test_initial_rates_follow_dynamic_similarity():
    for scale in PARENT_SCALES:
        state = initial_state(scale)
        np.testing.assert_allclose(
            scale * state[2:4],
            np.array((0.002, 0.004)),
            rtol=0,
            atol=1e-15,
        )
