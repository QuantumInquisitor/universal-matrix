from __future__ import annotations

import pytest

from src.toroidal_bend_clearance_boundary import (
    audit_vesica_clearance_boundary,
    format_clearance_boundary_report,
)
from src.toroidal_incident_bend_audit import BendSamplingGrid
from src.toroidal_sampling_reliability import (
    DEFAULT_GRIDS,
    audit_vesica_sampling_reliability,
    format_sampling_reliability_report,
)
from src.toroidal_uniform_scale_similarity import (
    evaluate_vesica_similarity_clearance,
    format_similarity_report,
)


@pytest.fixture(scope="module")
def missed_collision():
    # Original coarse grid, half-step shifted coarse grid, then denser grid.
    return audit_vesica_sampling_reliability(3.0, 0.05, grids=DEFAULT_GRIDS[:3])


def test_shift_and_density_both_recover_known_missed_collision(missed_collision):
    coarse, shifted, dense = missed_collision.results
    assert coarse.collision_count == 0
    assert shifted.collision_count == dense.collision_count == 2
    assert shifted.maximum_penetration > 0.19
    assert dense.maximum_penetration > 0.19
    assert missed_collision.collision_detected
    assert missed_collision.classification_changes


def test_coarse_similarity_does_not_certify_clearance(missed_collision):
    similarity = evaluate_vesica_similarity_clearance(3.0, 0.05, 1.0)
    assert similarity.collision_count == missed_collision.results[0].collision_count == 0
    assert similarity.sampling == missed_collision.results[0].sampling
    assert missed_collision.collision_detected
    report = format_similarity_report(((similarity,),))
    assert "zero_collisions_is_not_a_clearance_proof" in report
    assert "sampling:[phi:13,q:5,theta:24,offsets:[0,0,0]]" in report


def test_report_preserves_each_grid_and_adverse_evidence(missed_collision):
    report = format_sampling_reliability_report((missed_collision,))
    for result in missed_collision.results:
        assert result.sampling.description in report
    assert "outcome:collision_detected" in report
    assert "classification_changes:True" in report
    assert "no_collision_detected_is_not_certified_clearance" in report


def test_wider_candidate_remains_only_a_finite_sampling_result():
    audit = audit_vesica_sampling_reliability(8.25, 0.005, grids=DEFAULT_GRIDS[:3])
    assert not audit.collision_detected
    assert not audit.classification_changes
    report = format_sampling_reliability_report((audit,))
    assert "outcome:no_collision_detected" in report
    assert "no_collision_detected_is_not_certified_clearance" in report


def test_frontier_report_records_nondefault_resolution():
    audit = audit_vesica_clearance_boundary(
        shell_gaps=(3.0,), bend_margins=(0.05,), phi_samples=21, q_samples=9, theta_samples=48
    )
    assert audit.collision_count == 1
    report = format_clearance_boundary_report(audit)
    assert "sampling=phi:21,q:9,theta:48,offsets:[0,0,0]" in report
    assert "collision_free_means_no_collision_detected" in report


@pytest.mark.parametrize("name", ("phi_offset", "q_offset", "theta_offset"))
@pytest.mark.parametrize("value", (-0.01, 1.0, float("nan"), float("inf")))
def test_shift_must_stay_within_one_finite_grid_interval(name, value):
    with pytest.raises(ValueError, match=name):
        BendSamplingGrid(**{name: value})


@pytest.mark.parametrize("grids", ((), DEFAULT_GRIDS[:1], (DEFAULT_GRIDS[0],) * 2))
def test_reliability_audit_requires_distinct_grids(grids):
    with pytest.raises(ValueError, match="distinct"):
        audit_vesica_sampling_reliability(3.0, 0.05, grids=grids)
