import math

from src.gauge_dispersion import (
    dimensional_speed,
    long_wavelength_speed,
    phase_velocity,
    routing_wave_number,
    weak_field_angular_frequency,
    weak_field_frequency_squared,
    weak_field_group_velocity,
)
from src.gauge_dynamics import ROUTING_PERIOD
from src.gauge_hamiltonian import U1HamiltonianState


def test_exact_dispersion_formula():
    beta = 2.25
    for m in range(ROUTING_PERIOD):
        q = routing_wave_number(m)
        expected = 4.0 * beta * math.sin(q / 2.0) ** 2
        assert math.isclose(
            weak_field_frequency_squared(m, beta),
            expected,
            rel_tol=0,
            abs_tol=1e-14,
        )


def test_mode_symmetry():
    for m in range(1, ROUTING_PERIOD):
        assert math.isclose(
            weak_field_angular_frequency(m),
            weak_field_angular_frequency(ROUTING_PERIOD - m),
            rel_tol=0,
            abs_tol=1e-14,
        )


def test_zero_mode_and_long_wave_speed():
    assert weak_field_angular_frequency(0, beta=4.0) == 0.0
    assert long_wavelength_speed(beta=4.0) == 2.0


def test_low_mode_phase_velocity_approaches_long_wave_speed():
    beta = 1.0
    v = phase_velocity(1, beta=beta, period=3600)
    assert abs(v - 1.0) < 1e-6


def test_group_velocity_goes_to_zero_at_nyquist():
    assert abs(weak_field_group_velocity(ROUTING_PERIOD // 2)) < 1e-12


def test_dimensional_speed_exposes_calibration():
    assert dimensional_speed(beta=4.0, lattice_spacing=3.0, time_unit=2.0) == 3.0


def test_hamiltonian_initial_acceleration_matches_mode_eigenvalue():
    beta = 1.7
    mode = 3
    amplitude = 1e-7

    state = U1HamiltonianState.zeros(2, beta=beta)
    for k in range(ROUTING_PERIOD):
        q = routing_wave_number(mode)
        state.field.scale_links[0][k] = amplitude * math.cos(q * k)

    # E_dot = -dV/dtheta. In the weak-field limit this should be
    # -omega^2 * s(k) for a Fourier eigenmode.
    _, scale_grad = state.field.linearized_euler_lagrange_residuals()
    omega2 = weak_field_frequency_squared(mode, beta)

    for k in range(ROUTING_PERIOD):
        acceleration = -scale_grad[0][k]
        expected = -omega2 * state.field.scale_links[0][k]
        assert math.isclose(
            acceleration,
            expected,
            rel_tol=0,
            abs_tol=1e-18,
        )
