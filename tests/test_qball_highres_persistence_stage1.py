import pytest

from src.qball_highres_persistence_stage1 import (
    HighResolutionPersistenceStage,
    format_high_resolution_persistence_report,
)


def test_report_exposes_stage_duration_and_both_survival_channels():
    result = HighResolutionPersistenceStage(
        shape=(91, 91, 91),
        spacing=0.175,
        steps=25,
        dt=0.001,
        radial_energy_per_charge=1.00058,
        cartesian_energy_per_charge=1.00011,
        threshold_side_preserved=True,
        direct_survival=True,
        perturbed_survival=True,
        direct_energy_drift=1e-10,
        direct_charge_drift=1e-14,
        direct_peak_ratio=0.9999,
        direct_radius_ratio=1.0001,
        perturbed_energy_drift=2e-10,
        perturbed_charge_drift=2e-14,
        perturbed_peak_ratio=0.995,
        perturbed_radius_ratio=1.0002,
    )
    report = format_high_resolution_persistence_report(result)

    assert "steps=25" in report
    assert "threshold_side_preserved=True" in report
    assert "direct_survival=True" in report
    assert "perturbed_survival=True" in report


def test_stage_result_retains_threshold_classification():
    result = HighResolutionPersistenceStage(
        shape=(91, 91, 91),
        spacing=0.175,
        steps=25,
        dt=0.001,
        radial_energy_per_charge=1.00058,
        cartesian_energy_per_charge=1.00011,
        threshold_side_preserved=True,
        direct_survival=True,
        perturbed_survival=False,
        direct_energy_drift=0.0,
        direct_charge_drift=0.0,
        direct_peak_ratio=1.0,
        direct_radius_ratio=1.0,
        perturbed_energy_drift=0.0,
        perturbed_charge_drift=0.0,
        perturbed_peak_ratio=1.2,
        perturbed_radius_ratio=1.0,
    )
    assert result.radial_energy_per_charge > 1.0
    assert result.cartesian_energy_per_charge > 1.0
    assert result.threshold_side_preserved is True
    assert result.perturbed_survival is False
