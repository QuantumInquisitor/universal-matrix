import pytest

from src.qball_highres_persistence_stage1 import HighResolutionPersistenceStage
from src.qball_highres_persistence_stage4 import (
    HighResolutionPersistenceStage4,
    format_high_resolution_persistence_stage4_report,
)


def _result():
    return HighResolutionPersistenceStage(
        shape=(91, 91, 91),
        spacing=0.175,
        steps=500,
        dt=0.001,
        radial_energy_per_charge=1.00058,
        cartesian_energy_per_charge=1.00011,
        threshold_side_preserved=True,
        direct_survival=True,
        perturbed_survival=True,
        direct_energy_drift=7e-11,
        direct_charge_drift=1e-14,
        direct_peak_ratio=0.9995,
        direct_radius_ratio=1.0001,
        perturbed_energy_drift=8e-11,
        perturbed_charge_drift=2e-14,
        perturbed_peak_ratio=0.9964,
        perturbed_radius_ratio=1.00024,
    )


def test_stage4_projection_ratios_compare_measurement_to_prior_diagnostic():
    stage = HighResolutionPersistenceStage4(
        result=_result(),
        projected_direct_peak_deviation=5e-4,
        projected_perturbed_peak_deviation=3.6e-3,
        projected_direct_radius_deviation=1e-4,
        projected_perturbed_radius_deviation=2.4e-4,
    )

    assert stage.direct_peak_projection_ratio == pytest.approx(1.0)
    assert stage.perturbed_peak_projection_ratio == pytest.approx(1.0)
    assert stage.direct_radius_projection_ratio == pytest.approx(1.0)
    assert stage.perturbed_radius_projection_ratio == pytest.approx(1.0)


def test_stage4_report_exposes_survival_and_projection_comparison():
    stage = HighResolutionPersistenceStage4(
        result=_result(),
        projected_direct_peak_deviation=5e-4,
        projected_perturbed_peak_deviation=3.6e-3,
        projected_direct_radius_deviation=1e-4,
        projected_perturbed_radius_deviation=2.4e-4,
    )
    report = format_high_resolution_persistence_stage4_report(stage)

    assert "steps=500" in report
    assert "direct_survival=True" in report
    assert "perturbed_survival=True" in report
    assert "measured_to_projected_direct_peak=1.0000000000" in report
