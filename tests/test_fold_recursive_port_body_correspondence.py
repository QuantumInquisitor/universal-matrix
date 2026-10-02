"""Controls for fixed port-to-body correspondence search."""

import numpy as np
import pytest

from scripts.report_fold_constitutive import geometry
from scripts.report_fold_dynamics import Q0
from scripts.report_fold_recursive_port_body_correspondence import report


@pytest.fixture(scope="module")
def result():
    return report()


def test_candidate_catalog_covers_every_source_geometry_vertex(result):
    expected = sum(len(np.asarray(row["vertices_m"])) for row in geometry(Q0, length_m=1.0))
    assert result["candidate_count"] == expected
    assert sum(result["candidate_counts_by_body_kind"].values()) == expected


def test_candidate_metrics_are_finite_except_declared_degenerate_condition(result):
    for row in result["candidates"]:
        for key in (
            "maximum_normalized_displacement_error",
            "maximum_normalized_jacobian_error",
            "maximum_other_scale_displacement_error",
            "maximum_other_scale_jacobian_error",
            "scaled_orthogonal_relative_error",
            "uniform_projection_scale",
            "theta_sensitivity",
            "score",
        ):
            assert np.isfinite(row[key])


def test_exact_candidate_flags_follow_predeclared_thresholds(result):
    threshold = result["thresholds"]
    for row in result["candidates"]:
        exact = (
            row["maximum_normalized_displacement_error"] < threshold["exact_displacement"]
            and row["maximum_normalized_jacobian_error"] < threshold["exact_jacobian"]
        )
        assert row["exact_fixed_linear_match"] is exact
        scaled = exact and row["scaled_orthogonal_relative_error"] < threshold["scaled_orthogonal"]
        assert row["exact_scaled_orthogonal_match"] is scaled


def test_exact_scaled_orthogonal_matches_are_subset_of_linear_matches(result):
    linear = set(result["exact_fixed_linear_candidates"])
    scaled = set(result["exact_scaled_orthogonal_candidates"])
    unit = set(result["exact_unit_orthogonal_projection_candidates"])
    assert scaled <= linear
    assert unit <= scaled


def test_best_candidate_list_is_sorted_by_fixed_transform_error(result):
    scores = [row["score"] for row in result["best_candidates"]]
    assert scores == sorted(scores)


def test_no_state_dependent_fit_or_attachment_selection_is_claimed(result):
    assert not result["state_dependent_transform_used"]
    assert result["candidate_specific_fixed_transform_allowed"]
    assert not result["anisotropic_linear_transform_counts_as_literal_projection"]
    assert not result["specific_physical_attachment_selected"]
