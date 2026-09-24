from __future__ import annotations

import pytest

from src.toroidal_bend_clearance_boundary import (
    audit_vesica_clearance_boundary,
    sampled_clearance_frontier,
)
from src.toroidal_bend_spacing_scan import BendSpacingResult


def _mask(audit):
    return tuple(
        (result.shell_gap, result.bend_margin, result.collision_free)
        for result in audit.results
    )


def test_default_boundary_audit_contains_both_outcomes():
    audit = audit_vesica_clearance_boundary()
    assert audit.sample_count == 25
    assert audit.mixed_outcome
    assert audit.collision_count > 0
    assert audit.collision_free_count > 0
    assert audit.frontier


def test_frontier_is_the_first_sampled_free_gap_per_margin():
    audit = audit_vesica_clearance_boundary()
    lookup = {
        (result.shell_gap, result.bend_margin): result
        for result in audit.results
    }
    for point in audit.frontier:
        first = lookup[
            (point.minimum_collision_free_gap, point.bend_margin)
        ]
        assert first.collision_free
        smaller = [
            result
            for result in audit.results
            if result.bend_margin == point.bend_margin
            and result.shell_gap < point.minimum_collision_free_gap
        ]
        assert all(not result.collision_free for result in smaller)
        if point.lower_colliding_gap is not None:
            lower = lookup[(point.lower_colliding_gap, point.bend_margin)]
            assert not lower.collision_free


def test_clearance_mask_is_current_orientation_independent():
    positive = audit_vesica_clearance_boundary(current=1.0)
    negative = audit_vesica_clearance_boundary(current=-1.0)
    assert _mask(positive) == _mask(negative)


def test_zero_current_frontier_starts_at_smallest_gap():
    audit = audit_vesica_clearance_boundary(current=0.0)
    assert audit.collision_count == 0
    assert not audit.unresolved_margins
    assert all(
        point.minimum_collision_free_gap == min(audit.shell_gaps)
        for point in audit.frontier
    )


def test_unresolved_margin_is_reported():
    frontier, unresolved = sampled_clearance_frontier(
        (
            BendSpacingResult(0.25, 0.1, 2, 0.2),
            BendSpacingResult(1.0, 0.1, 1, 0.1),
        )
    )
    assert frontier == ()
    assert unresolved == (0.1,)


def test_sampled_frontier_rejects_duplicate_points():
    result = BendSpacingResult(1.0, 0.1, 0, 0.0)
    with pytest.raises(ValueError):
        sampled_clearance_frontier((result, result))


@pytest.mark.parametrize(
    "kwargs",
    [
        {"shell_gaps": ()},
        {"shell_gaps": (1.0, 1.0)},
        {"shell_gaps": (-1.0, 1.0)},
        {"bend_margins": ()},
        {"bend_margins": (0.1, 0.1)},
        {"bend_margins": (0.0, 0.1)},
    ],
)
def test_boundary_axes_are_validated(kwargs):
    with pytest.raises(ValueError):
        audit_vesica_clearance_boundary(**kwargs)
