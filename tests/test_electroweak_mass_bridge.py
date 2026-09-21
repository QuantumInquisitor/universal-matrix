import math
import numpy as np

from src.electroweak_mass_bridge import (
    ElectroweakParameters,
    electric_coupling,
    mass_relation_residual,
    neutral_eigensystem,
    neutral_mass_squared_matrix,
    photon_direction,
    z_direction,
)


def test_neutral_mass_matrix_has_zero_determinant():
    p = ElectroweakParameters(0.65, 0.35, 246.0)
    matrix = neutral_mass_squared_matrix(p)
    assert abs(np.linalg.det(matrix)) < 1e-8


def test_photon_direction_is_exact_zero_mode():
    p = ElectroweakParameters(0.65, 0.35, 246.0)
    matrix = neutral_mass_squared_matrix(p)
    residual = matrix @ photon_direction(p)
    assert np.allclose(residual, 0.0, atol=1e-10, rtol=0)


def test_z_direction_has_z_mass_eigenvalue():
    p = ElectroweakParameters(0.65, 0.35, 246.0)
    matrix = neutral_mass_squared_matrix(p)
    z = z_direction(p)
    lhs = matrix @ z
    rhs = p.z_mass**2 * z
    assert np.allclose(lhs, rhs, atol=1e-9, rtol=0)


def test_neutral_eigenvalues_are_photon_and_z():
    p = ElectroweakParameters(0.7, 0.4, 10.0)
    values, _ = neutral_eigensystem(p)
    assert abs(values[0]) < 1e-12
    assert math.isclose(
        values[1],
        p.z_mass**2,
        rel_tol=0,
        abs_tol=1e-12,
    )


def test_w_z_mass_relation():
    p = ElectroweakParameters(0.65, 0.35, 246.0)
    assert abs(mass_relation_residual(p)) < 1e-12


def test_electric_coupling_equals_g_sin_theta():
    p = ElectroweakParameters(0.65, 0.35, 246.0)
    e = electric_coupling(p)
    assert math.isclose(
        e,
        p.g_su2 * p.sin_theta_w,
        rel_tol=0,
        abs_tol=1e-15,
    )
    assert math.isclose(
        e,
        p.g_u1 * p.cos_theta_w,
        rel_tol=0,
        abs_tol=1e-15,
    )
