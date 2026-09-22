import pytest

from src.qball_threshold_preserving_grid import (
    TARGET_SHAPE,
    TARGET_SPACING,
    ThresholdPreservingGridResult,
    format_threshold_preserving_grid_report,
    target_half_width,
)


def test_target_grid_is_centered_and_has_expected_half_width():
    assert TARGET_SHAPE == (91, 91, 91)
    assert TARGET_SPACING == pytest.approx(0.175)
    assert target_half_width() == pytest.approx(7.875)


def test_report_exposes_finite_grid_threshold_classification():
    result = ThresholdPreservingGridResult(
        shape=TARGET_SHAPE,
        spacing=TARGET_SPACING,
        half_width=7.875,
        radial_energy_per_charge=1.00058,
        cartesian_energy_per_charge=1.00008,
        mapping_relative_difference=5e-4,
        radial_above_threshold=True,
        cartesian_above_threshold=True,
        threshold_side_preserved=True,
        joint_fit_prediction=1.00009,
        prediction_absolute_error=1e-5,
    )
    report = format_threshold_preserving_grid_report(result)

    assert "threshold_side_preserved=True" in report
    assert "cartesian_above_threshold=True" in report
    assert "joint_fit_prediction=1.0000900000" in report
