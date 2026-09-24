from __future__ import annotations

import pytest

from src.toroidal_bend_spacing_scan import (
    evaluate_vesica_bend_spacing,
    first_collision_free_result,
    scan_vesica_bend_spacing,
)


def test_baseline_reproduces_incident_bend_collision():
    result = evaluate_vesica_bend_spacing(
        shell_gap=0.25,
        bend_margin=0.25,
        phi_samples=17,
        q_samples=7,
        theta_samples=32,
    )
    assert result.collision_count > 0
    assert result.maximum_penetration > 0.0
    assert result.collision_free is False


def test_gap_three_tight_bend_still_collides():
    result = evaluate_vesica_bend_spacing(
        shell_gap=3.0,
        bend_margin=0.05,
        phi_samples=21,
        q_samples=9,
        theta_samples=48,
    )
    assert result.collision_count == 2
    assert result.maximum_penetration > 0.19
    assert result.collision_free is False


@pytest.mark.parametrize("current", [1.0, -1.0])
def test_gap_three_collision_is_orientation_independent(current):
    result = evaluate_vesica_bend_spacing(
        shell_gap=3.0,
        bend_margin=0.05,
        current=current,
        phi_samples=17,
        q_samples=7,
        theta_samples=32,
    )
    assert result.collision_count == 2
    assert result.maximum_penetration > 0.19


def test_zero_current_has_no_active_incident_collision():
    result = evaluate_vesica_bend_spacing(
        shell_gap=0.25,
        bend_margin=0.25,
        current=0.0,
    )
    assert result.collision_free


def test_broad_grid_searches_for_a_collision_free_region():
    results = scan_vesica_bend_spacing(
        shell_gaps=(0.25, 1.0, 3.0, 10.0, 30.0),
        bend_margins=(0.005, 0.02, 0.05, 0.1, 0.25),
    )
    assert any(not result.collision_free for result in results)
    first = first_collision_free_result(results)
    assert first is not None, results
    assert first.collision_free


@pytest.mark.parametrize(
    "kwargs",
    [
        {"shell_gap": -0.1, "bend_margin": 0.1},
        {"shell_gap": 0.1, "bend_margin": 0.0},
        {"shell_gap": 0.1, "bend_margin": float("inf")},
    ],
)
def test_invalid_scan_parameters_are_rejected(kwargs):
    with pytest.raises(ValueError):
        evaluate_vesica_bend_spacing(**kwargs)


def test_empty_scan_axis_is_rejected():
    with pytest.raises(ValueError):
        scan_vesica_bend_spacing((), (0.1,))
    with pytest.raises(ValueError):
        scan_vesica_bend_spacing((0.1,), ())
