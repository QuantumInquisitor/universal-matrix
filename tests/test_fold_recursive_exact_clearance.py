"""Primitive geometry controls for recursive exact-clearance audit."""

import numpy as np
import pytest

from scripts.report_fold_recursive_exact_clearance import (
    body_distance,
    path_category,
    point_segment_distance,
    point_triangle_distance,
    segment_segment_distance,
    segment_triangle_distance,
    triangle_triangle_distance,
)


def test_point_segment_distance():
    assert point_segment_distance([0, 1, 0], [0, 0, 0], [2, 0, 0]) == pytest.approx(1)


def test_crossing_segments_have_zero_distance():
    assert segment_segment_distance(
        [-1, 0, 0],
        [1, 0, 0],
        [0, -1, 0],
        [0, 1, 0],
    ) == pytest.approx(0, abs=1e-14)


def test_parallel_segments_have_unit_distance():
    assert segment_segment_distance(
        [0, 0, 0],
        [1, 0, 0],
        [0, 1, 0],
        [1, 1, 0],
    ) == pytest.approx(1)


def test_point_in_triangle_plane_has_zero_distance():
    assert point_triangle_distance(
        [0.2, 0.2, 0],
        [0, 0, 0],
        [1, 0, 0],
        [0, 1, 0],
    ) == pytest.approx(0, abs=1e-14)


def test_segment_piercing_triangle_has_zero_distance():
    assert segment_triangle_distance(
        [0.2, 0.2, -1],
        [0.2, 0.2, 1],
        [0, 0, 0],
        [1, 0, 0],
        [0, 1, 0],
    ) == pytest.approx(0, abs=1e-14)


def test_separated_triangles_have_expected_distance():
    a = ([0, 0, 0], [1, 0, 0], [0, 1, 0])
    b = ([0, 0, 1], [1, 0, 1], [0, 1, 1])
    assert triangle_triangle_distance(*a, *b) == pytest.approx(1)


def test_body_distance_panel_bridge_intersection():
    panel = {
        "kind": "panel",
        "vertices": np.array(([0, 0, 0], [1, 0, 0], [0, 1, 0])),
    }
    bridge = {
        "kind": "bridge",
        "vertices": np.array(([0.2, 0.2, -1], [0.2, 0.2, 1])),
    }
    assert body_distance(panel, bridge) == pytest.approx(0, abs=1e-14)


@pytest.mark.parametrize(
    "a,b,expected",
    [
        ((), (0,), "parent_child"),
        ((), (0, 1), "ancestor_descendant"),
        ((0, 0), (0, 1), "siblings"),
        ((0, 0), (1, 0), "cross_branch"),
    ],
)
def test_path_categories(a, b, expected):
    assert path_category(a, b) == expected
