import pytest

from src.qball_highres_persistence_stage1 import HighResolutionPersistenceStage
from src.qball_highres_persistence_stage3 import (
    HighResolutionPersistenceStage3,
    format_high_resolution_persistence_stage3_report,
)


def _result():
    return HighResolutionPersistenceStage(
        shape=(91, 91, 91),
        spacing=0.175,
        steps=250,
        dt=0.001,
        radial_energy_per_charge=1.00058,
        cartesian_energy_per_charge=1.00011,
        threshold_side_preserved=True,
        direct_survival=True,
        perturbed_survival=True,
        direct_energy_drift=1e-9,
        direct_charge_drift=1e-14,
        direct_peak_ratio=0.999,
        direct_radius_ratio=1.001,
        perturbed_energy_drift=2e-9,
        perturbed_charge_drift=2e-14,
        perturbed_peak_ratio=0.998,
        perturbed_radius_ratio=1.002,
    )


def test_stage3_duration_multipliers_are_explicit():
    stage = HighResolutionPersistenceStage3(result=_result())
    assert stage.duration_multiplier_vs_stage1 == pytest.approx(10.0)
    assert stage.duration_multiplier_vs_stage2 == pytest.approx(2.5)


def test_stage3_report_preserves_both_survival_channels():
    stage = HighResolutionPersistenceStage3(result=_result())
    report = format_high_resolution_persistence_stage3_report(stage)

    assert "steps=250" in report
    assert "duration_multiplier_vs_stage1=10.0000000000" in report
    assert "duration_multiplier_vs_stage2=2.5000000000" in report
    assert "direct_survival=True" in report
    assert "perturbed_survival=True" in report
