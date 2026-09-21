import math

from src.reciprocity_newton_normalization import (
    effective_newton_constant,
    einstein_kappa,
    point_source_acceleration,
    point_source_psi,
    reciprocity_kappa_from_newton,
)


def test_reciprocity_kappa_is_half_einstein_kappa_for_same_g_and_c():
    g = 6.6743e-11
    c = 299792458.0
    k = reciprocity_kappa_from_newton(g, c)
    ke = einstein_kappa(g, c)
    assert math.isclose(k, 0.5 * ke, rel_tol=1e-15, abs_tol=0)


def test_effective_newton_constant_inverts_kappa_mapping():
    g = 6.6743e-11
    c = 299792458.0
    k = reciprocity_kappa_from_newton(g, c)
    assert math.isclose(
        effective_newton_constant(k, c),
        g,
        rel_tol=1e-15,
        abs_tol=0,
    )


def test_point_source_acceleration_reproduces_newton_when_matched():
    g = 6.6743e-11
    c = 299792458.0
    mass = 5.972e24
    radius = 6.371e6
    k = reciprocity_kappa_from_newton(g, c)

    a = point_source_acceleration(mass, radius, k, c)
    expected = g * mass / radius**2

    assert math.isclose(a, expected, rel_tol=1e-15, abs_tol=0)


def test_point_source_psi_is_gm_over_c_squared_r_when_matched():
    g = 6.6743e-11
    c = 299792458.0
    mass = 1.989e30
    radius = 1.496e11
    k = reciprocity_kappa_from_newton(g, c)

    psi = point_source_psi(mass, radius, k, c)
    expected = g * mass / (c**2 * radius)

    assert math.isclose(psi, expected, rel_tol=1e-15, abs_tol=0)
