"""Controls for relative-marker recursive attachment-frame search."""

import pytest

from scripts.report_fold_recursive_relative_attachment import report


@pytest.fixture(scope="module")
def result():
    return report()


def test_pair_catalog_is_complete(result):
    assert result["marker_count"] == 58
    assert result["pair_candidate_count"] == 58 * 57 // 2


def test_exact_match_sets_are_nested(result):
    linear = set(result["exact_fixed_linear_candidates"])
    scaled = set(result["exact_scaled_orthogonal_candidates"])
    unit = set(result["exact_unit_orthogonal_projection_candidates"])
    assert scaled <= linear
    assert unit <= scaled


def test_report_candidates_are_sorted(result):
    scores = [row["score"] for row in result["best_candidates"]]
    assert scores == sorted(scores)


def test_nonphysical_anisotropic_fit_is_not_promoted(result):
    assert not result["anisotropic_linear_transform_counts_as_literal_frame"]
    assert result["relative_physical_segment_searched"]
    assert not result["state_dependent_transform_used"]
    assert not result["specific_physical_attachment_selected"]


def test_report_values_are_json_safe(result):
    for row in result["best_candidates"]:
        condition = row["condition_number"]
        assert condition is None or condition >= 1
        assert row["reference_segment_length_per_module_length"] >= 0
