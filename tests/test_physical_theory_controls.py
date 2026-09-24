from __future__ import annotations

import math

import numpy as np
import pytest

from src.physical_theory_controls import (
    ABCField,
    audit_hydrogen_vacuum_rows,
    audit_periodic_field,
    hydrogen_rydberg_wavelength_A,
    periodic_grid,
)


# Authoritative vacuum entries from NIST hydrogen strong-line table 2.
VACUUM_VALUES = ("926.2256", "930.7482", "937.8034", "949.7430",
                 "972.5367", "1025.7222", "1215.66824", "1215.67364")


def _row(wavelength="1215.66824", **changes):
    return dict(wavelength_A=wavelength, medium="vacuum", isotope="1H", spectrum="H I") | changes


def test_reduced_mass_improves_the_reference_discrepancy_without_being_an_exact_fit():
    result = audit_hydrogen_vacuum_rows([_row(wavelength) for wavelength in VACUUM_VALUES])
    assert len(result.lines) == 8
    assert result.excluded_air_rows == 0
    assert result.infinite_mass_rms_ppm == pytest.approx(533.24270157193, abs=2e-8)
    assert result.reduced_mass_rms_ppm == pytest.approx(11.14097816775, abs=2e-8)
    assert result.infinite_mass_rms_ppm > 40 * result.reduced_mass_rms_ppm
    assert all(8.0 < row.reduced_mass_residual_ppm < 14.0 for row in result.lines)
    assert tuple(row.upper_n for row in result.lines) == (8, 7, 6, 5, 4, 3, 2, 2)


def test_nonrelativistic_prediction_does_not_invent_fine_structure():
    result = audit_hydrogen_vacuum_rows([_row(value) for value in VACUUM_VALUES[-2:]])
    first, second = result.lines
    assert first.wavelength_A != second.wavelength_A
    assert first.reduced_mass_wavelength_A == second.reduced_mass_wavelength_A
    assert first.reduced_mass_wavelength_A == pytest.approx(1215.6844561726744, rel=2e-15)
    assert first.reduced_mass_residual_ppm != second.reduced_mass_residual_ppm


def test_infinite_and_reduced_mass_predictions_have_the_known_mass_ratio():
    for lower, upper in ((1, 2), (2, 3), (3, 5), (5, 10)):
        infinite = hydrogen_rydberg_wavelength_A(lower, upper, reduced_mass=False)
        reduced = hydrogen_rydberg_wavelength_A(lower, upper, reduced_mass=True)
        assert reduced / infinite == pytest.approx(1.0005446170214889, rel=2e-15)


def test_air_reference_is_counted_and_excluded_from_vacuum_comparison():
    result = audit_hydrogen_vacuum_rows([_row(), _row("6562.8518", medium="air")])
    assert len(result.lines) == 1
    assert result.excluded_air_rows == 1
    with pytest.raises(ValueError, match="at least one assigned vacuum"):
        audit_hydrogen_vacuum_rows([_row("6562.8518", medium="air")])


@pytest.mark.parametrize("changes", ({"medium": "unknown"}, {"isotope": "2H"},
                                     {"spectrum": "H II"}, {"wavelength_A": "1215.0"},
                                     {"wavelength_A": "NaN"}, {"wavelength_A": "0"}))
def test_reference_identity_units_and_series_assignment_cannot_be_guessed(changes):
    with pytest.raises(ValueError):
        audit_hydrogen_vacuum_rows([_row() | changes])


@pytest.mark.parametrize("lower,upper", ((0, 2), (2, 2), (3, 2), (True, 2), (1, 2.5)))
def test_invalid_quantum_numbers_are_rejected(lower, upper):
    with pytest.raises(ValueError):
        hydrogen_rydberg_wavelength_A(lower, upper, reduced_mass=True)


def test_mass_approximation_is_an_explicit_choice():
    with pytest.raises(TypeError):
        hydrogen_rydberg_wavelength_A(1, 2)
    with pytest.raises(ValueError):
        hydrogen_rydberg_wavelength_A(1, 2, reduced_mass="yes")


def test_abc_values_and_periodic_identifications():
    field = ABCField(amplitudes=(1.0, 2.0, 3.0), period_length=0.3, mode_number=2)
    assert field.value((0.0, 0.0, 0.0)) == pytest.approx((3.0, 1.0, 2.0))
    point = np.array((0.073, 0.122, 0.219))
    for axis in np.eye(3):
        assert field.value(point + 0.3 * axis) == pytest.approx(field.value(point), abs=2e-14)


def test_independent_centered_curl_refines_at_second_order():
    field = ABCField(amplitudes=(1.0, 2.0, 3.0))
    errors = []
    for size in (16, 32, 64):
        values = field.value(periodic_grid(size, field.period_length))
        audit = audit_periodic_field(values, period_length=field.period_length, curl_eigenvalue=1.0)
        # Every component has frequency one. The centered derivative symbol
        # gives sin(h)/h, independently fixing the exact expected discrepancy.
        h = 2.0 * math.pi / size
        expected_error = 1.0 - math.sin(h) / h
        assert audit.relative_curl_error == pytest.approx(expected_error, rel=2e-12)
        assert audit.relative_divergence_error < 1e-14
        assert audit.relative_force_free_error < 2e-14
        assert audit.mean_squared_field == pytest.approx(14.0, rel=2e-15)
        assert audit.magnetic_helicity == pytest.approx(14.0 * (2.0 * math.pi)**3, rel=2e-15)
        errors.append(audit.relative_curl_error)
    assert 3.9 < errors[0] / errors[1] < 4.0
    assert 3.9 < errors[1] / errors[2] < 4.0


def test_wavenumber_and_permeability_scale_the_current_without_a_force():
    field = ABCField(amplitudes=(0.002, -0.003, 0.001), period_length=0.4, mode_number=2)
    point = (0.03, 0.12, 0.21)
    permeability = 4.0 * math.pi * 1e-7  # Explicit illustrative H/m input.
    magnetic = field.value(point)
    current = field.current_density(point, permeability=permeability)
    assert field.wavenumber == pytest.approx(10.0 * math.pi)
    assert current == pytest.approx(magnetic * 2.5e7, rel=2e-15)
    assert np.linalg.norm(np.cross(current, magnetic)) < 1e-13
    with pytest.raises(TypeError):
        field.current_density(point)
    with pytest.raises(ValueError):
        field.current_density(point, permeability=0.0)


def test_axial_vector_reflection_reverses_curl_eigenvalue_and_helicity():
    field = ABCField(amplitudes=(1.0, 2.0, 0.5))
    grid = periodic_grid(32, field.period_length)
    # For S=diag(-1,1,1), B'(y)=det(S) S B(S^-1 y) transports axial B.
    # Curl then has eigenvalue -k; treating it as +k must fail the audit.
    reflected_points = grid * np.array((-1.0, 1.0, 1.0))
    reflected_field = field.value(reflected_points) * np.array((1.0, -1.0, -1.0))
    result = audit_periodic_field(reflected_field, period_length=field.period_length, curl_eigenvalue=-1.0)
    wrong_sign = audit_periodic_field(reflected_field, period_length=field.period_length, curl_eigenvalue=1.0)
    assert result.relative_curl_error < 0.007
    assert result.relative_divergence_error < 1e-14
    assert result.relative_force_free_error < 2e-14
    assert result.magnetic_helicity == pytest.approx(-5.25 * (2.0 * math.pi)**3, rel=2e-15)
    assert wrong_sign.relative_curl_error > 1.99


def test_divergence_free_offset_does_not_pass_force_free_control():
    field = ABCField()
    values = field.value(periodic_grid(32, field.period_length)) + np.array((0.3, 0.0, 0.0))
    audit = audit_periodic_field(values, period_length=field.period_length, curl_eigenvalue=1.0)
    assert audit.relative_divergence_error < 1e-14
    assert audit.relative_curl_error > 0.1
    assert audit.relative_force_free_error > 0.05


def test_gradient_contamination_is_detected_by_independent_divergence():
    field = ABCField()
    grid = periodic_grid(32, field.period_length)
    values = field.value(grid)
    values[..., 0] += 0.2 * np.cos(grid[..., 0])
    audit = audit_periodic_field(values, period_length=field.period_length, curl_eigenvalue=1.0)
    assert audit.relative_divergence_error > 0.05
    assert audit.relative_curl_error > 0.05


def test_small_field_amplitude_does_not_underflow_relative_force_diagnostic():
    field = ABCField(amplitudes=(1e-100, 2e-100, 3e-100))
    values = field.value(periodic_grid(16, field.period_length))
    audit = audit_periodic_field(values, period_length=field.period_length, curl_eigenvalue=1.0)
    assert audit.relative_force_free_error < 2e-14
    assert audit.relative_curl_error == pytest.approx(0.025504641595567312, rel=2e-12)
    assert audit.mean_squared_field == pytest.approx(14e-200, rel=2e-15, abs=0.0)


def test_nonzero_helicity_cannot_silently_underflow_to_zero():
    field = ABCField(period_length=1e-90)
    values = field.value(periodic_grid(16, field.period_length))
    with pytest.raises(ValueError, match="resolved magnetic helicity"):
        audit_periodic_field(values, period_length=field.period_length, curl_eigenvalue=field.wavenumber)


def test_unresolved_current_coefficient_cannot_silently_zero_a_finite_current():
    field = ABCField(amplitudes=(1e100, 1e100, 1e100), period_length=1e200)
    # The mathematical current is about 6.28e-300 in each component, but
    # computing k/mu first underflows. Reject that unresolved intermediate.
    with pytest.raises(ValueError, match="resolved current coefficient"):
        field.current_density((0.0, 0.0, 0.0), permeability=1e200)


@pytest.mark.parametrize("parameters", ({"period_length": 0.0}, {"period_length": float("inf")},
                                       {"mode_number": 0}, {"mode_number": True}, {"mode_number": 10**400},
                                       {"amplitudes": (1, 2)}, {"amplitudes": (1, 2, float("nan"))}))
def test_invalid_abc_parameters_are_rejected(parameters):
    with pytest.raises(ValueError):
        ABCField(**parameters)


def test_unresolved_or_nonfinite_periodic_audits_are_rejected():
    field = ABCField(mode_number=2)
    values = field.value(periodic_grid(4, field.period_length))
    with pytest.raises(ValueError, match="Nyquist"):
        audit_periodic_field(values, period_length=field.period_length, curl_eigenvalue=2.0)
    with pytest.raises(ValueError):
        field.value((0.0, 0.0, float("inf")))
    for invalid in (np.zeros((4, 4, 4, 3)), np.full((4, 4, 4, 3), float("nan")),
                    np.zeros((4, 5, 4, 3))):
        with pytest.raises(ValueError):
            audit_periodic_field(invalid, period_length=2.0 * math.pi, curl_eigenvalue=1.0)
