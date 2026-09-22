from types import SimpleNamespace

import pytest

from src.qball_mapping_convergence import (
    MappingConvergencePoint,
    MappingGrid,
    best_mapping_point,
    format_mapping_convergence_report,
    threshold_side_stabilized,
)


def _point(error, preserved, spacing):
    return MappingConvergencePoint(
        shape=(25, 25, 25),
        spacing=spacing,
        minimum_half_width=6.0,
        radial_energy_per_charge=1.0005,
        cartesian_energy_per_charge=1.0005 * (1.0 - error),
        relative_difference=error,
        radial_below_threshold=False,
        cartesian_below_threshold=preserved is False,
        threshold_side_preserved=preserved,
    )


def test_mapping_grid_requires_centered_odd_shape():
    with pytest.raises(ValueError):
        MappingGrid((24, 25, 25), 0.5)


def test_best_mapping_point_selects_smallest_energy_per_charge_error():
    points = (_point(0.004, False, 0.5), _point(0.001, True, 0.3))
    assert best_mapping_point(points).spacing == pytest.approx(0.3)


def test_threshold_side_stabilization_uses_refined_tail():
    points = (
        _point(0.004, False, 0.5),
        _point(0.002, True, 0.4),
        _point(0.001, True, 0.3),
    )
    assert threshold_side_stabilized(points, tail=2) is True
    assert threshold_side_stabilized(points, tail=3) is False


def test_report_exposes_mapping_classification():
    points = (
        _point(0.004, False, 0.5),
        _point(0.001, True, 0.3),
    )
    report = format_mapping_convergence_report(points)
    assert "grid_0_threshold_side_preserved=False" in report
    assert "grid_1_threshold_side_preserved=True" in report
    assert "best_spacing=0.3000000000" in report
