import math

from src.phase_roles import (
    PhaseState,
    gauge_coupling_energy,
    gauge_covariant_difference,
    transform_link_phase,
)


def test_gauge_transform_does_not_change_polarity_observables():
    state = PhaseState(polarity_phase=0.7, gauge_phase=-0.2)
    transformed = state.gauge_transform(1.4)

    assert transformed.polarity_phase == state.polarity_phase
    assert transformed.polarity_carrier == state.polarity_carrier
    assert transformed.transfer_carrier == state.transfer_carrier


def test_covariant_difference_is_gauge_invariant():
    a = PhaseState(polarity_phase=0.1, gauge_phase=0.3)
    b = PhaseState(polarity_phase=1.2, gauge_phase=-0.8)
    theta = 0.6

    before = gauge_covariant_difference(a, b, theta)

    alpha_a = 0.9
    alpha_b = -0.4
    a2 = a.gauge_transform(alpha_a)
    b2 = b.gauge_transform(alpha_b)
    theta2 = transform_link_phase(theta, alpha_a, alpha_b)

    after = gauge_covariant_difference(a2, b2, theta2)
    assert math.isclose(before, after, abs_tol=1e-12)


def test_gauge_coupling_energy_is_invariant():
    a = PhaseState(0.4, 0.2)
    b = PhaseState(0.9, -0.5)
    theta = 0.3

    e0 = gauge_coupling_energy(a, b, theta, coupling=0.7)

    aa, ab = 1.0, -0.2
    e1 = gauge_coupling_energy(
        a.gauge_transform(aa),
        b.gauge_transform(ab),
        transform_link_phase(theta, aa, ab),
        coupling=0.7,
    )

    assert math.isclose(e0, e1, abs_tol=1e-12)
