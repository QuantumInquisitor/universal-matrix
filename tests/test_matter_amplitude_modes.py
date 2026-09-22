import math

import numpy as np
import pytest

from src.classical_matter_dynamics import matter_force
from src.localized_matter_variational import MatterPotential
from src.matter_amplitude_modes import (
    fixed_amplitude_rotor_parameters,
    lattice_laplacian_eigenvalue,
    matter_linear_branches,
    nonzero_stationary_densities,
    radial_mass_squared,
    stationary_density_summary,
)


DEFAULT = MatterPotential(
    mass2=1.0,
    lambda4=-2.0,
    lambda6=1.0,
)


def test_default_potential_has_two_nonzero_stationary_densities():
    roots = nonzero_stationary_densities(DEFAULT)
    assert roots == pytest.approx((1.0 / 3.0, 1.0), abs=1e-12)


def test_lower_nonzero_stationary_density_is_radially_unstable():
    mass2 = radial_mass_squared(1.0 / 3.0, DEFAULT)
    summary = stationary_density_summary(1.0 / 3.0, DEFAULT)

    assert mass2 == pytest.approx(-4.0 / 3.0)
    assert summary["stable"] is False
    assert summary["stability"] == "unstable"


def test_upper_nonzero_stationary_density_is_stable_with_gap_two():
    mass2 = radial_mass_squared(1.0, DEFAULT)
    summary = stationary_density_summary(1.0, DEFAULT)

    assert mass2 == pytest.approx(4.0)
    assert summary["stable"] is True
    assert summary["radial_gap"] == pytest.approx(2.0)


def test_stable_vacuum_has_gapless_phase_and_gapped_radial_mode():
    modes = matter_linear_branches((0.0, 0.0, 0.0), 1.0, DEFAULT)

    assert modes["phase_omega_squared"] == pytest.approx(0.0)
    assert modes["radial_omega_squared"] == pytest.approx(4.0)
    assert modes["radial_gap_squared"] == pytest.approx(4.0)


def test_zone_corner_separates_phase_and_radial_branches():
    modes = matter_linear_branches(
        (math.pi, math.pi, math.pi),
        1.0,
        DEFAULT,
    )

    assert lattice_laplacian_eigenvalue(
        (math.pi, math.pi, math.pi)
    ) == pytest.approx(12.0)
    assert modes["phase_omega_squared"] == pytest.approx(12.0)
    assert modes["radial_omega_squared"] == pytest.approx(16.0)


def test_fixed_amplitude_scalar_maps_to_equal_rotor_coupling_and_inertia():
    params = fixed_amplitude_rotor_parameters(1.7)

    assert params["coupling"] == pytest.approx(3.4)
    assert params["inertia"] == pytest.approx(3.4)
    assert params["lattice_wave_speed_squared"] == pytest.approx(1.0)
    assert params["lattice_wave_speed"] == pytest.approx(1.0)


def test_numeric_uniform_radial_force_matches_predicted_gap():
    shape = (4, 4, 4)
    links = np.zeros((3,) + shape)
    eps = 1e-6

    phi = np.full(shape, 1.0 + eps, dtype=complex)
    acceleration = matter_force(phi, links, DEFAULT)

    measured = -float(np.mean(acceleration.real)) / eps
    assert measured == pytest.approx(4.0, rel=2e-5)


def test_numeric_uniform_phase_direction_is_goldstone_to_linear_order():
    shape = (4, 4, 4)
    links = np.zeros((3,) + shape)
    eps = 1e-6

    phi = np.full(shape, 1.0 + 1j * eps, dtype=complex)
    acceleration = matter_force(phi, links, DEFAULT)

    measured = float(np.max(np.abs(acceleration.imag))) / eps
    assert measured < 1e-9


def test_numeric_finite_wavelength_phase_mode_matches_lattice_dispersion():
    shape = (8, 4, 4)
    links = np.zeros((3,) + shape)
    eps = 1e-6
    kx = 2.0 * math.pi / shape[0]

    x = np.arange(shape[0], dtype=float)[:, None, None]
    profile = np.cos(kx * x)
    phi = np.ones(shape, dtype=complex) + 1j * eps * profile

    acceleration = matter_force(phi, links, DEFAULT)
    expected_lap = 4.0 * math.sin(0.5 * kx) ** 2

    profile_full = np.broadcast_to(profile, shape)
    mask = np.abs(profile_full) > 0.5
    measured = -acceleration.imag[mask] / (eps * profile_full[mask])

    assert np.allclose(measured, expected_lap, rtol=2e-5, atol=1e-8)


def test_nonstationary_density_is_rejected_for_mode_analysis():
    with pytest.raises(ValueError):
        radial_mass_squared(0.7, DEFAULT)


def test_positive_quartic_free_mass_potential_has_no_nonzero_stationary_density():
    potential = MatterPotential(
        mass2=1.0,
        lambda4=0.5,
        lambda6=0.0,
    )
    assert nonzero_stationary_densities(potential) == ()
