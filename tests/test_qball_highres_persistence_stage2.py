import pytest

from src.qball_highres_persistence_stage1 import HighResolutionPersistenceStage
from src.qball_highres_persistence_stage2 import (
    HighResolutionPersistenceStage2,
    format_high_resolution_persistence_stage2_report,
)


def _result():
    return HighResolutionPersistenceStage(
        shape=(91, 91, 91),
        spacing=0.175,
        steps=100,
        dt=0.001,
        radial_energy_per_charge=1.00058,
        cartesian_energy_per_charge=1.00011,
        threshold_side_preserved=True,
        direct_survival=True,
        perturbed_survival=True,
        direct_energy_drift=1e-10,
        direct_charge_drift=1e-14,
        direct_peak_ratio=0.9998,
        direct_radius_ratio=1.0002,
        perturbed_energy_drift=2e-10,
        perturbed_charge_drift=2e-14,
        perturbed_peak_ratio=0.994,
        perturbed_radius_ratio=1.0004,
    )


def test_stage2_duration_is_four_times_stage1_reference():
    stage = HighResolutionPersistenceStage2(result=_result())
    assert stage.duration_multiplier == pytest.approx(4.0)


def test_stage2_report_preserves_both_survival_channels():
    stage = HighResolutionPersistenceStage2(result=_result())
    report = format_high_resolution_persistence_stage2_report(stage)

    assert "steps=100" in report
    assert "duration_multiplier_vs_stage1=4.0000000000" in report
    assert "direct_survival=True" in report
    assert "perturbed_survival=True" in report
