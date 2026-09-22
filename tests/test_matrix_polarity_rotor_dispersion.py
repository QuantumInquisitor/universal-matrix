import math

import numpy as np
import pytest

from src.matrix_polarity_rotor_dispersion import (
    analytic_cubic_omega_squared,
    analytic_periodic_spectrum,
    compensated_phase_for_polarity,
    normal_mode_omega_squared,
    periodic_wavevectors,
    stability_summary,
)
from src.matrix_polarity_rotor_transition import effective_phase_field


def test_compensated_phase_makes_effective_phase_uniform_for_any_polarity():
    rng = np.random.default_rng(123)
    bits = rng.integers(0, 2, size=(4, 3, 2))
    phase = compensated_phase_for_polarity(bits, reference_phase=0.37)

    eff = effective_phase_field(phase, bits, "independent")
    assert np.allclose(
        np.exp(1j * eff),
        np.exp(1j * 0.37),
        atol=1e-12,
    )


def test_periodic_wavevector_count_matches_site_count():
    shape = (3, 4, 5)
    assert periodic_wavevectors(shape).shape == (3 * 4 * 5, 3)


def test_analytic_dispersion_has_goldstone_zero_mode():
    assert analytic_cubic_omega_squared((0.0, 0.0, 0.0)) == pytest.approx(0.0)


def test_analytic_dispersion_long_wavelength_limit():
    k = np.array([1e-5, -2e-5, 3e-5])
    coupling = 2.7
    inertia = 1.3

    exact = analytic_cubic_omega_squared(
        k,
        coupling=coupling,
        inertia=inertia,
    )
    continuum = coupling / inertia * float(k @ k)

    assert exact == pytest.approx(continuum, rel=1e-10)


def test_compensated_random_polarity_is_isospectral_to_plain_rotor():
    rng = np.random.default_rng(44)
    shape = (4, 3, 2)
    bits = rng.integers(0, 2, size=shape)
    phase = compensated_phase_for_polarity(bits, reference_phase=-0.22)

    numeric = normal_mode_omega_squared(
        phase,
        bits,
        coupling=1.9,
        inertia=0.7,
    )
    analytic = analytic_periodic_spectrum(
        shape,
        coupling=1.9,
        inertia=0.7,
    )

    assert np.allclose(numeric, analytic, atol=1e-11)


def test_different_compensated_polarity_patterns_have_same_spectrum():
    shape = (4, 4, 2)
    rng = np.random.default_rng(91)
    a = rng.integers(0, 2, size=shape)
    b = rng.integers(0, 2, size=shape)

    spectrum_a = normal_mode_omega_squared(
        compensated_phase_for_polarity(a),
        a,
    )
    spectrum_b = normal_mode_omega_squared(
        compensated_phase_for_polarity(b),
        b,
    )

    assert np.allclose(spectrum_a, spectrum_b, atol=1e-11)


def test_checkerboard_uncompensated_background_is_stationary_but_unstable():
    shape = (4, 4, 4)
    coords = np.indices(shape)
    bits = np.mod(coords[0] + coords[1] + coords[2], 2).astype(np.int8)
    phase = np.zeros(shape)

    spectrum = normal_mode_omega_squared(
        phase,
        bits,
        coupling=1.0,
        inertia=1.0,
    )
    summary = stability_summary(spectrum)

    assert summary["stable"] is False
    assert summary["negative_modes"] == np.prod(shape) - 1
    assert summary["zero_modes"] == 1
    assert summary["minimum_omega_squared"] == pytest.approx(-12.0, abs=1e-12)


def test_compensating_checkerboard_restores_stable_standard_spectrum():
    shape = (4, 4, 4)
    coords = np.indices(shape)
    bits = np.mod(coords[0] + coords[1] + coords[2], 2).astype(np.int8)
    phase = compensated_phase_for_polarity(bits)

    spectrum = normal_mode_omega_squared(phase, bits)
    summary = stability_summary(spectrum)

    assert summary["stable"] is True
    assert summary["negative_modes"] == 0
    assert summary["zero_modes"] == 1
    assert summary["maximum_omega_squared"] == pytest.approx(12.0, abs=1e-12)


def test_clock_representation_ignores_branch_pattern_in_linear_spectrum():
    rng = np.random.default_rng(8)
    shape = (3, 3, 4)
    bits = rng.integers(0, 2, size=shape)
    phase = np.full(shape, 0.18)

    numeric = normal_mode_omega_squared(
        phase,
        bits,
        coupling=2.0,
        inertia=5.0,
        phase_representation="canonical_clock",
    )
    analytic = analytic_periodic_spectrum(
        shape,
        coupling=2.0,
        inertia=5.0,
    )

    assert np.allclose(numeric, analytic, atol=1e-11)


def test_high_symmetry_zone_corner_frequency():
    value = analytic_cubic_omega_squared(
        (math.pi, math.pi, math.pi),
        coupling=3.0,
        inertia=2.0,
    )
    assert value == pytest.approx(18.0)
