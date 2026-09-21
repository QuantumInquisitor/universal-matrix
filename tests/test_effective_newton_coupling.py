import math

from src.effective_newton_coupling import (
    effective_newton_coupling,
    inverse_square_acceleration_magnitude,
    point_source_mu,
    required_combined_coupling,
    source_equivalence_ratio,
)


def test_effective_g_matches_mu_acceleration_relation():
    c = 3.0
    g_clock = 0.2
    k_field = 0.7
    q_mass = 1.4
    mass = 5.0
    radius = 2.5

    g_eff = effective_newton_coupling(c, g_clock, k_field, q_mass)
    mu = point_source_mu(mass, g_clock, k_field, q_mass)

    from_mu = c**2 * mu / radius**2
    from_g = g_eff * mass / radius**2

    assert math.isclose(from_mu, from_g, rel_tol=0, abs_tol=1e-15)


def test_acceleration_is_inverse_square():
    kwargs = dict(
        source_mass=2.0,
        causal_speed=4.0,
        clock_coupling=0.3,
        field_coupling=0.5,
        content_charge_per_mass=1.1,
    )
    a1 = inverse_square_acceleration_magnitude(radius=2.0, **kwargs)
    a2 = inverse_square_acceleration_magnitude(radius=4.0, **kwargs)
    assert math.isclose(a1 / a2, 4.0, rel_tol=0, abs_tol=1e-14)


def test_required_combined_coupling_inverts_effective_g():
    target_g = 6.7
    c = 2.3
    q = 0.8
    product = required_combined_coupling(target_g, c, q)

    reconstructed = c**2 * product * q / (4.0 * math.pi)
    assert math.isclose(reconstructed, target_g, rel_tol=0, abs_tol=1e-14)


def test_identical_content_charge_per_mass_has_zero_source_mismatch():
    assert source_equivalence_ratio(1.0, 1.0) == 0.0


def test_source_mismatch_changes_sign_when_arguments_swap():
    ab = source_equivalence_ratio(1.01, 0.99)
    ba = source_equivalence_ratio(0.99, 1.01)
    assert math.isclose(ab, -ba, rel_tol=0, abs_tol=0)
