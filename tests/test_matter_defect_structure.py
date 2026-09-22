import numpy as np
import pytest

from src.matter_defect_structure import (
    DEFAULT_DEFECT_POTENTIAL,
    default_potential_energy_from_amplitude,
    derrick_scaled_energy,
    derrick_stationarity_residual,
    domain_wall_derivative,
    domain_wall_energy_density,
    domain_wall_profile,
    domain_wall_tension_exact,
    static_field_equation_residual,
    static_scalar_lump_allowed_by_derrick,
)


def test_default_potential_factorization_matches_repository_coefficients():
    f = np.linspace(0.0, 1.5, 21)
    rho = f * f
    direct = (
        DEFAULT_DEFECT_POTENTIAL.mass2 * rho
        + DEFAULT_DEFECT_POTENTIAL.lambda4 * rho**2
        + DEFAULT_DEFECT_POTENTIAL.lambda6 * rho**3
    )
    factored = default_potential_energy_from_amplitude(f)

    assert np.allclose(direct, factored, atol=1e-14)


def test_domain_wall_connects_zero_and_unit_vacua():
    x = np.array([-20.0, 0.0, 20.0])
    f = domain_wall_profile(x)

    assert f[0] < 1e-8
    assert f[1] == pytest.approx(1.0 / np.sqrt(2.0))
    assert 1.0 - f[2] < 1e-8


def test_domain_wall_satisfies_first_order_identity():
    x = np.linspace(-5.0, 5.0, 101)
    f = domain_wall_profile(x)
    fp = domain_wall_derivative(x)

    assert np.allclose(fp, f * (1.0 - f * f), atol=1e-14)


def test_domain_wall_solves_static_second_order_field_equation():
    x = np.linspace(-8.0, 8.0, 401)
    residual = static_field_equation_residual(x)

    assert np.max(np.abs(residual)) < 1e-14


def test_domain_wall_tension_matches_numerical_integral():
    x = np.linspace(-20.0, 20.0, 200001)
    density = domain_wall_energy_density(x)
    numerical = float(np.trapezoid(density, x))

    assert domain_wall_tension_exact() == pytest.approx(0.5)
    assert numerical == pytest.approx(0.5, rel=2e-8, abs=2e-10)


def test_three_dimensional_nonnegative_scalar_lump_fails_derrick_stationarity():
    assert derrick_stationarity_residual(2.0, 3.0, dimension=3) == pytest.approx(-11.0)
    assert not static_scalar_lump_allowed_by_derrick(2.0, 3.0, dimension=3)


def test_nontrivial_three_dimensional_configuration_lowers_energy_under_shrinking_scaling_direction():
    t = 2.0
    v = 3.0
    e0 = derrick_scaled_energy(1.0, t, v, dimension=3)
    e_up = derrick_scaled_energy(1.01, t, v, dimension=3)

    assert e_up < e0


def test_trivial_zero_energy_configuration_is_derick_stationary():
    assert static_scalar_lump_allowed_by_derrick(0.0, 0.0, dimension=3)
