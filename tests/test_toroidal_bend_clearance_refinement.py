from __future__ import annotations

import pytest

from src.toroidal_bend_clearance_refinement import (
    RefinedClearanceRow,
    refine_vesica_clearance_boundary,
    refinement_axis,
)
from src.toroidal_bend_spacing_scan import BendSpacingResult


@pytest.fixture(scope="module")
def default_refinement():
    return refine_vesica_clearance_boundary(subdivisions=4)


def test_refinement_axis_includes_coarse_endpoints():
    axis = refinement_axis(3.0, 10.0, subdivisions=4)
    assert axis[0] == 3.0
    assert axis[-1] == 10.0
    assert len(axis) == 5
    assert all(left < right for left, right in zip(axis, axis[1:]))


def test_default_refinement_preserves_coarse_endpoint_classes(default_refinement):
    assert default_refinement.rows
    for row in default_refinement.rows:
        assert not row.results[0].collision_free
        assert row.results[-1].collision_free
        assert row.refined_width <= row.coarse_width / default_refinement.subdivisions + 1e-12


def test_refined_rows_preserve_margin_and_sorted_gap_order(default_refinement):
    for row in default_refinement.rows:
        assert tuple(sorted(row.shell_gaps)) == row.shell_gaps
        assert all(
            result.bend_margin == pytest.approx(row.bend_margin)
            for result in row.results
        )


def test_reentrant_collision_is_reported_without_monotonicity_assumption():
    row = RefinedClearanceRow(
        bend_margin=0.1,
        coarse_lower_colliding_gap=1.0,
        coarse_first_free_gap=5.0,
        results=(
            BendSpacingResult(1.0, 0.1, 1, 0.1),
            BendSpacingResult(2.0, 0.1, 0, 0.0),
            BendSpacingResult(3.0, 0.1, 1, 0.05),
            BendSpacingResult(4.0, 0.1, 0, 0.0),
            BendSpacingResult(5.0, 0.1, 0, 0.0),
        ),
    )
    assert row.transition_count == 3
    assert row.reentrant_collision
    assert row.refined_bracket == (1.0, 2.0)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"lower_gap": -0.1, "upper_gap": 1.0},
        {"lower_gap": 1.0, "upper_gap": 1.0},
        {"lower_gap": 2.0, "upper_gap": 1.0},
        {"lower_gap": 1.0, "upper_gap": 2.0, "subdivisions": 1},
    ],
)
def test_invalid_refinement_axes_are_rejected(kwargs):
    with pytest.raises(ValueError):
        refinement_axis(**kwargs)


def test_invalid_refinement_subdivisions_are_rejected():
    with pytest.raises(ValueError):
        refine_vesica_clearance_boundary(subdivisions=1)
