from types import SimpleNamespace

from src.qball_threshold_persistence_scan import format_scan_report


def _point(**overrides):
    values = dict(
        central_amplitude=0.95,
        omega=0.85,
        radial_energy_per_charge=0.99,
        cartesian_energy_per_charge=0.991,
        mapping_relative_difference=0.001,
        below_free_mass_threshold=True,
        cartesian_below_free_mass_threshold=True,
        mapping_preserves_threshold_side=True,
        direct_survival=True,
        perturbed_survival=False,
        direct_energy_drift=1e-7,
        direct_charge_drift=1e-12,
        direct_peak_ratio=1.0,
        direct_radius_ratio=1.0,
        perturbed_energy_drift=2e-7,
        perturbed_charge_drift=2e-12,
        perturbed_peak_ratio=1.01,
        perturbed_radius_ratio=1.02,
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def test_report_keeps_energetic_and_persistence_results_separate():
    scan = SimpleNamespace(
        refinement=SimpleNamespace(
            crossing=SimpleNamespace(
                interpolated_amplitude=0.945,
                interpolated_omega=0.86,
            ),
            bracket_width=0.004,
        ),
        below_side=_point(),
        above_side=_point(
            central_amplitude=0.946,
            radial_energy_per_charge=1.001,
            cartesian_energy_per_charge=1.002,
            below_free_mass_threshold=False,
            cartesian_below_free_mass_threshold=True,
            mapping_preserves_threshold_side=False,
            direct_survival=True,
            perturbed_survival=True,
        ),
    )

    report = format_scan_report(scan)

    assert "below_radial_E_over_Q=0.9900000000" in report
    assert "below_perturbed_survival=False" in report
    assert "above_radial_E_over_Q=1.0010000000" in report
    assert "above_radial_below_threshold=False" in report
    assert "above_cartesian_below_threshold=True" in report
    assert "above_mapping_preserves_threshold_side=False" in report
    assert "above_direct_survival=True" in report
    assert "above_perturbed_survival=True" in report
