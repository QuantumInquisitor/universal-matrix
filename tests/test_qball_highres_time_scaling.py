import pytest

from src.qball_highres_time_scaling import (
    analyze_stage_scaling,
    format_scaling_report,
    local_power_exponent,
    recommended_stage4_time,
)


def test_local_power_exponent_recovers_quadratic_growth():
    assert local_power_exponent(0.1, 0.01, 0.2, 0.04) == pytest.approx(2.0)


def test_radius_channels_remain_close_to_quadratic_scaling():
    channels = {channel.name: channel for channel in analyze_stage_scaling()}

    assert channels["direct_radius_deviation"].global_exponent == pytest.approx(
        2.0451760914,
        rel=1e-6,
    )
    assert channels["perturbed_radius_deviation"].global_exponent == pytest.approx(
        2.0064466428,
        rel=1e-6,
    )


def test_energy_drift_late_exponent_is_near_saturation():
    channels = {channel.name: channel for channel in analyze_stage_scaling()}

    assert channels["direct_energy_drift"].late_exponent < 0.1
    assert channels["perturbed_energy_drift"].late_exponent < 0.1


def test_stage4_candidate_is_half_time_unit_under_one_percent_limit():
    assert recommended_stage4_time(structural_limit=0.01) == pytest.approx(0.5)


def test_report_marks_extrapolation_as_diagnostic_only():
    report = format_scaling_report()

    assert "recommended_stage4_time=0.5000000000" in report
    assert "not asymptotic laws" in report
