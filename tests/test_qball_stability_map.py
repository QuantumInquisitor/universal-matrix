from types import SimpleNamespace

import pytest

from src.qball_stability_map import (
    attach_persistence_evidence,
    build_static_evidence_map,
    evidence_summary,
    select_refinement_amplitudes,
)


def _record(amplitude, omega, energy, charge, eq, accepted=True):
    potential = SimpleNamespace(free_mass=1.0)
    solution = SimpleNamespace(
        omega=omega,
        energy=energy,
        charge=charge,
        energy_per_charge=eq,
        potential=potential,
    )
    return SimpleNamespace(
        central_amplitude=amplitude,
        solution=solution,
        accepted_as_seed=accepted,
        below_free_mass_threshold=eq < potential.free_mass,
    )


def _report(*, energy_drift=1e-7, charge_drift=1e-12, peak=1.0, radius=1.0):
    return SimpleNamespace(
        relative_energy_drift=energy_drift,
        relative_charge_drift=charge_drift,
        peak_ratio=peak,
        radius_ratio=radius,
    )


def test_static_map_keeps_energetic_and_branch_slope_evidence_separate():
    records = [
        _record(0.8, 0.95, 9.5, 10.0, 1.05),
        _record(0.9, 0.90, 10.8, 12.0, 1.02),
        _record(1.0, 0.85, 12.75, 15.0, 0.97),
    ]

    points = build_static_evidence_map(records)

    assert len(points) == 3
    assert points[0].below_free_mass_threshold is False
    assert points[-1].below_free_mass_threshold is True
    assert all(
        point.negative_slope_on_available_secants is True
        for point in points
    )


def test_refinement_amplitudes_fill_only_the_threshold_bracket():
    records = [
        _record(0.8, 0.95, 9.5, 10.0, 1.05),
        _record(0.9, 0.90, 10.8, 12.0, 1.02),
        _record(1.0, 0.85, 12.75, 15.0, 0.97),
    ]

    values = select_refinement_amplitudes(records, interior_points=4)

    assert values == pytest.approx((0.92, 0.94, 0.96, 0.98))


def test_persistence_attachment_does_not_overwrite_other_evidence():
    records = [
        _record(0.9, 0.90, 10.8, 12.0, 1.02),
        _record(1.0, 0.85, 12.75, 15.0, 0.97),
    ]
    points = build_static_evidence_map(records)

    updated = attach_persistence_evidence(
        points,
        amplitude=1.0,
        direct_report=_report(),
        perturbed_report=_report(peak=1.2),
    )

    assert updated[-1].below_free_mass_threshold is True
    assert updated[-1].direct_survival is True
    assert updated[-1].perturbed_survival is False
    assert updated[-1].finite_time_persistence_supported is False


def test_summary_counts_each_evidence_channel_independently():
    records = [
        _record(0.9, 0.90, 10.8, 12.0, 1.02),
        _record(1.0, 0.85, 12.75, 15.0, 0.97),
    ]
    points = build_static_evidence_map(records)
    points = attach_persistence_evidence(
        points,
        amplitude=1.0,
        direct_report=_report(),
        perturbed_report=_report(),
    )

    summary = evidence_summary(points)

    assert summary["points"] == 2
    assert summary["energetically_bound"] == 1
    assert summary["negative_slope_candidates"] == 2
    assert summary["direct_survival_supported"] == 1
    assert summary["perturbed_survival_supported"] == 1
    assert summary["both_persistence_tests_supported"] == 1


def test_missing_threshold_bracket_is_explicit():
    records = [
        _record(0.7, 0.96, 8.8, 8.0, 1.10),
        _record(0.8, 0.94, 9.9, 9.0, 1.10),
    ]

    with pytest.raises(ValueError, match="threshold bracket"):
        select_refinement_amplitudes(records)
