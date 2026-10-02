"""Controls for recursive exact-clearance bracket refinement."""

import pytest

from scripts.report_fold_recursive_exact_clearance_refinement import (
    classify_mask,
    refinement_axis,
)


def test_refinement_axis_includes_ordered_endpoints():
    axis = refinement_axis(10.0, 20.0, subdivisions=4)
    assert axis == pytest.approx((10.0, 12.5, 15.0, 17.5, 20.0))


def test_single_transition_mask_classification():
    row = classify_mask((False, False, True, True, True))
    assert row["transition_count"] == 1
    assert row["first_free_index"] == 2
    assert not row["reentrant_collision"]


def test_reentrant_collision_is_reported():
    row = classify_mask((False, True, False, True))
    assert row["transition_count"] == 3
    assert row["first_free_index"] == 1
    assert row["reentrant_collision"]


@pytest.mark.parametrize(
    "lower,upper,subdivisions",
    [
        (0, 1, 4),
        (2, 1, 4),
        (1, 1, 4),
        (1, 2, 1),
        (1, 2, True),
    ],
)
def test_invalid_refinement_axis_rejected(lower, upper, subdivisions):
    with pytest.raises(ValueError):
        refinement_axis(lower, upper, subdivisions=subdivisions)


def test_mask_requires_at_least_two_samples():
    with pytest.raises(ValueError):
        classify_mask((False,))
