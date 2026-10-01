"""Controls for recursive spatial connector attachment adapters."""

import pytest

from scripts.report_fold_recursive_spatial_connector import (
    MODES,
    PARENT_SCALES,
    VESSEL_RATIOS,
    branch_rotation,
    report,
    spatial_connector,
)


@pytest.fixture(scope="module")
def result():
    return report()


def test_all_spatial_connector_forces_are_energy_gradients(result):
    for mode in MODES:
        for child_bit in ("0", "1"):
            for scale in PARENT_SCALES:
                row = result["cases"][mode][child_bit]["per_scale"][str(scale)]
                for gradient in row["gradient_errors"].values():
                    assert gradient["parent_force_gradient_error"] < 1e-9
                    assert gradient["child_force_gradient_error"] < 1e-9


def test_rest_translation_cancels_exactly_and_scales_with_vessel_ratio(result):
    for mode in MODES:
        for child_bit in ("0", "1"):
            for scale in PARENT_SCALES:
                row = result["cases"][mode][child_bit]["per_scale"][str(scale)]
                assert row["max_translation_cancellation_error_m"] < 1e-14
                assert row["rest_offset_parent_lengths"] == pytest.approx(
                    [ratio / 2 for ratio in VESSEL_RATIOS], abs=1e-12
                )


def test_parent_aligned_adapter_exactly_recovers_existing_connector(result):
    for child_bit in ("0", "1"):
        case = result["cases"]["parent_aligned"][child_bit]
        assert case["maximum_scale_similarity_error"] < 1e-12
        assert case["maximum_vessel_ratio_invariance_error"] < 1e-14
        for scale in PARENT_SCALES:
            row = case["per_scale"][str(scale)]
            assert row["max_abs_energy_difference_j"] < 1e-14
            assert row["max_abs_parent_force_difference"] < 1e-13
            assert row["max_abs_child_force_difference"] < 1e-13


def test_body_following_cooriented_branch_recovers_existing_connector(result):
    case = result["cases"]["body_following"]["0"]
    assert case["maximum_scale_similarity_error"] < 1e-12
    assert case["maximum_vessel_ratio_invariance_error"] < 1e-14
    for scale in PARENT_SCALES:
        row = case["per_scale"][str(scale)]
        assert row["max_abs_energy_difference_j"] < 1e-14
        assert row["max_abs_parent_force_difference"] < 1e-13
        assert row["max_abs_child_force_difference"] < 1e-13


def test_body_following_mirrored_branch_changes_current_dynamics(result):
    case = result["cases"]["body_following"]["1"]
    assert case["maximum_scale_similarity_error"] < 1e-12
    assert case["maximum_vessel_ratio_invariance_error"] < 1e-14
    assert (
        max(case["per_scale"][str(scale)]["max_abs_energy_difference_j"] for scale in PARENT_SCALES)
        > 1e-8
    )
    assert (
        max(
            case["per_scale"][str(scale)]["max_abs_parent_force_difference"]
            for scale in PARENT_SCALES
        )
        > 1e-6
    )


def test_claim_boundaries_remain_explicit(result):
    assert not result["connector_stiffness_changed"]
    assert not result["material_coefficients_changed"]
    assert result["geometric_rest_offset_added"]
    assert result["attachment_frame_choice_is_physical_input"]
    assert not result["abstract_port_mapped_to_specific_body_site"]
    assert not result["physical_attachment_convention_selected"]


@pytest.mark.parametrize(
    "child_bit,mode",
    [(-1, "parent_aligned"), (2, "body_following"), (True, "parent_aligned"), (0, "bad")],
)
def test_invalid_branch_frame_controls_rejected(child_bit, mode):
    with pytest.raises(ValueError):
        branch_rotation(child_bit, mode)


@pytest.mark.parametrize("ratio", [0, -1, float("nan")])
def test_invalid_vessel_ratio_rejected(ratio):
    with pytest.raises(ValueError):
        spatial_connector((1, 0.2), (1, 0.2), 1.0, 0, ratio)
