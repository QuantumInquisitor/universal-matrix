from __future__ import annotations

import math

from src.sri_yantra_huet_planar import (
    HUET_PLANAR_SOLUTION,
    apex_base_residuals,
    common_circumcircle_residual,
    concurrency_residuals,
    maximal_triangle_segments,
    maximum_concurrency_residual,
)


def test_huet_solution_contains_nine_complete_maximal_triangles():
    assert len(HUET_PLANAR_SOLUTION.triangles) == 9
    assert len(maximal_triangle_segments(HUET_PLANAR_SOLUTION)) == 27
    assert all(item.half_height > 0.0 for item in HUET_PLANAR_SOLUTION.triangles)


def test_huet_solution_preserves_t1_through_t9_base_order():
    bases = HUET_PLANAR_SOLUTION.base_points
    assert bases == tuple(sorted(bases))
    expected = (
        0.1130433243,
        0.2308072497,
        0.332,
        0.3961210639,
        0.4487673715,
        0.537,
        0.602,
        0.7351531571,
        0.835,
    )
    assert all(math.isclose(value, target, abs_tol=2e-9) for value, target in zip(bases, expected))


def test_all_seven_apex_base_conditions_close():
    assert max(abs(value) for value in apex_base_residuals(HUET_PLANAR_SOLUTION)) < 1e-12


def test_all_twelve_three_line_concurrencies_close():
    assert max(abs(value) for value in concurrency_residuals(HUET_PLANAR_SOLUTION)) < 1e-12
    assert maximum_concurrency_residual(HUET_PLANAR_SOLUTION) < 1e-12


def test_t3_and_t7_share_the_normalized_outer_circumcircle():
    assert common_circumcircle_residual(HUET_PLANAR_SOLUTION) < 1e-12
