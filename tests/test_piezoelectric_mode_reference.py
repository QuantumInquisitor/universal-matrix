from __future__ import annotations

import math
from dataclasses import FrozenInstanceError, replace

import pytest

from src.piezoelectric_mode_reference import ModeState, PiezoelectricMode


def _mode(**changes):
    parameters = dict(mass_kg=2.0, stiffness_n_per_m=8.0, damping_n_s_per_m=0.3,
                      capacitance_f=0.5, coupling_c_per_m=2.0,
                      parameter_source="Synthetic test parameters; no material inference")
    return PiezoelectricMode(**(parameters | changes))


def _si_mode():
    return _mode(mass_kg=0.002, stiffness_n_per_m=800000.0, damping_n_s_per_m=0.1,
                 capacitance_f=2e-8, coupling_c_per_m=0.02,
                 parameter_source="Illustrative SI magnitudes, not fitted material data")


def _energy(mode, state):
    return (0.5 * mode.mass_kg * state.velocity_m_per_s**2
            + 0.5 * mode.stiffness_n_per_m * state.displacement_m**2
            + (state.charge_c - mode.coupling_c_per_m * state.displacement_m)**2
            / (2.0 * mode.capacitance_f))


def test_parameters_require_provenance_and_are_immutable():
    with pytest.raises(TypeError):
        PiezoelectricMode(2.0, 8.0, 0.3, 0.5, 2.0)
    with pytest.raises(ValueError):
        _mode(parameter_source=" ")
    mode = _mode()
    with pytest.raises(FrozenInstanceError):
        mode.mass_kg = 3.0
    state = ModeState(0.0, 0.0, 0.0)
    with pytest.raises(FrozenInstanceError):
        state.charge_c = 1.0


@pytest.mark.parametrize("field,value", (
    ("mass_kg", 0.0), ("mass_kg", -1.0), ("stiffness_n_per_m", 0.0),
    ("stiffness_n_per_m", float("inf")), ("capacitance_f", 0.0),
    ("capacitance_f", -0.1), ("damping_n_s_per_m", -0.1),
    ("coupling_c_per_m", float("nan")), ("damping_n_s_per_m", float("nan")),
))
def test_invalid_mode_parameters_are_rejected(field, value):
    with pytest.raises(ValueError):
        _mode(**{field: value})


@pytest.mark.parametrize("coordinates", ((float("nan"), 0.0, 0.0),
                                         (0.0, float("inf"), 0.0),
                                         (0.0, 0.0, float("-inf"))))
def test_nonfinite_state_is_rejected(coordinates):
    with pytest.raises(ValueError):
        ModeState(*coordinates)


def test_energy_and_voltage_have_the_expected_si_dimensions_and_values():
    synthetic = _mode()
    state = ModeState(0.3, -0.4, 0.9)
    assert synthetic.voltage_v(state) == pytest.approx(0.6)
    assert synthetic.energy_j(state) == pytest.approx(0.61)
    physical_scale = _si_mode()
    state = ModeState(1e-6, 0.04, 4e-8)
    assert physical_scale.voltage_v(state) == pytest.approx(1.0)
    assert physical_scale.energy_j(state) == pytest.approx(2.01e-6)


@pytest.mark.parametrize("coupling", (-2.0, 0.0, 2.0))
def test_boundary_frequencies_match_independent_analytic_values(coupling):
    mode = _mode(coupling_c_per_m=coupling, damping_n_s_per_m=0.0)
    assert mode.natural_frequency_hz("short") == pytest.approx(1.0 / math.pi)
    expected_open = (math.sqrt(2.0) if coupling else 1.0) / math.pi
    assert mode.natural_frequency_hz("open") == pytest.approx(expected_open)


def test_charge_coordinate_energy_accepts_coupling_larger_than_sqrt_stiffness_capacitance():
    mode = _mode(coupling_c_per_m=3.0)
    assert mode.natural_frequency_hz("open") == pytest.approx(math.sqrt(13.0) / (2.0 * math.pi))
    assert mode.energy_j(ModeState(0.2, 0.0, 0.6)) == pytest.approx(0.16)


def test_electrical_boundary_must_be_explicit():
    mode = _mode()
    with pytest.raises(TypeError):
        mode.natural_frequency_hz()
    with pytest.raises(ValueError):
        mode.natural_frequency_hz("unspecified")
    with pytest.raises(TypeError):
        mode.harmonic_response(0.2, force_n=1.0)


@pytest.mark.parametrize("boundary", ("open", "short"))
@pytest.mark.parametrize("physical_scale", (False, True))
def test_force_phasors_satisfy_mechanical_and_electrical_equations(boundary, physical_scale):
    mode = _si_mode() if physical_scale else _mode()
    frequency = 2500.0 if physical_scale else 0.23
    force = 0.03 + 0.01j if physical_scale else 1.5 - 0.7j
    response = mode.harmonic_response(frequency, boundary=boundary, force_n=force)
    omega = 2.0 * math.pi * frequency
    x, voltage, charge, current = (response.displacement_m, response.voltage_v,
                                   response.charge_c, response.current_a)
    assert response.frequency_hz == frequency
    dynamic_force = ((mode.stiffness_n_per_m - mode.mass_kg * omega**2
                      + 1j * omega * mode.damping_n_s_per_m) * x
                     - mode.coupling_c_per_m * voltage)
    assert dynamic_force == pytest.approx(force, rel=2e-12, abs=1e-15)
    assert charge == pytest.approx(mode.capacitance_f * voltage + mode.coupling_c_per_m * x,
                                  rel=2e-12, abs=1e-18)
    assert current == pytest.approx(1j * omega * charge, rel=2e-12, abs=1e-18)
    if boundary == "open":
        assert charge == 0j
        assert current == 0j
    else:
        assert voltage == 0j


@pytest.mark.parametrize("boundary", ("open", "short"))
def test_reversing_coupling_reverses_electrical_polarity_only(boundary):
    positive, negative = _mode(), _mode(coupling_c_per_m=-2.0)
    a = positive.harmonic_response(0.23, boundary=boundary, force_n=1.5 - 0.7j)
    b = negative.harmonic_response(0.23, boundary=boundary, force_n=1.5 - 0.7j)
    assert b.displacement_m == pytest.approx(a.displacement_m)
    assert b.voltage_v == pytest.approx(-a.voltage_v)
    assert b.charge_c == pytest.approx(-a.charge_c)
    assert b.current_a == pytest.approx(-a.current_a)


@pytest.mark.parametrize("physical_scale", (False, True))
def test_voltage_clamp_phasor_obeys_force_and_charge_balance(physical_scale):
    mode = _si_mode() if physical_scale else _mode(coupling_c_per_m=-2.0)
    frequency = 2500.0 if physical_scale else 0.23
    voltage = 12.0 + 3.0j if physical_scale else 0.2 - 0.4j
    force = 0.01 - 0.02j if physical_scale else 0.3 + 0.5j
    response = mode.voltage_driven_response(frequency, voltage_v=voltage, force_n=force)
    omega = 2.0 * math.pi * frequency
    stiffness = (mode.stiffness_n_per_m - mode.mass_kg * omega**2
                 + 1j * omega * mode.damping_n_s_per_m)
    assert response.voltage_v == voltage
    assert stiffness * response.displacement_m == pytest.approx(
        force + mode.coupling_c_per_m * voltage, rel=2e-12
    )
    assert response.charge_c == pytest.approx(
        mode.capacitance_f * voltage + mode.coupling_c_per_m * response.displacement_m, rel=2e-12
    )
    assert response.current_a == pytest.approx(1j * omega * response.charge_c, rel=2e-12)


@pytest.mark.parametrize("boundary", ("open", "short"))
def test_undamped_exact_resonance_has_no_finite_force_response(boundary):
    mode = _mode(damping_n_s_per_m=0.0)
    resonance = (math.sqrt(2.0) if boundary == "open" else 1.0) / math.pi
    with pytest.raises(ValueError):
        mode.harmonic_response(resonance, boundary=boundary, force_n=1.0)


def test_undamped_voltage_clamp_resonance_is_rejected():
    mode = _mode(damping_n_s_per_m=0.0)
    with pytest.raises(ValueError):
        mode.voltage_driven_response(1.0 / math.pi, voltage_v=1.0)


def test_harmonic_sweep_keeps_input_order_and_duplicate_samples():
    frequencies = (0.1, 0.6, 0.1, 0.3)
    responses = _mode().harmonic_sweep(frequencies, boundary="open", force_n=1.0 + 0.5j)
    assert isinstance(responses, tuple)
    assert tuple(response.frequency_hz for response in responses) == frequencies
    assert responses[0] == responses[2]
    assert responses[0].displacement_m != responses[1].displacement_m


def test_zero_drives_leave_the_origin_at_rest():
    mode = _mode()
    origin = ModeState(0.0, 0.0, 0.0)
    for result in (mode.step_current_driven(origin, 0.05, load_conductance_s=0.2),
                   mode.step_short_circuit(origin, 0.05)):
        assert result.state == origin
        assert result.energy_after_j == result.external_work_j == result.dissipated_energy_j == 0.0
    for response in (mode.harmonic_response(0.2, boundary="open", force_n=0j),
                     mode.voltage_driven_response(0.2, voltage_v=0j)):
        assert response.displacement_m == response.voltage_v == response.charge_c == response.current_a == 0j


@pytest.mark.parametrize("physical_scale", (False, True))
def test_current_driven_midpoint_obeys_coupled_equations_and_energy_balance(physical_scale):
    if physical_scale:
        mode, initial = _si_mode(), ModeState(1e-6, 0.04, 4e-8)
        dt, force, current, conductance = 1e-5, 0.02, 2e-5, 1e-5
    else:
        mode, initial = _mode(), ModeState(0.2, -0.3, 0.7)
        dt, force, current, conductance = 0.05, 0.8, -0.4, 0.25
    result = mode.step_current_driven(initial, dt, force_n=force, current_a=current,
                                      load_conductance_s=conductance)
    final = result.state
    x = (initial.displacement_m + final.displacement_m) / 2.0
    velocity = (initial.velocity_m_per_s + final.velocity_m_per_s) / 2.0
    charge = (initial.charge_c + final.charge_c) / 2.0
    voltage = (charge - mode.coupling_c_per_m * x) / mode.capacitance_f
    assert (final.displacement_m - initial.displacement_m) / dt == pytest.approx(velocity, rel=2e-11)
    assert mode.mass_kg * (final.velocity_m_per_s - initial.velocity_m_per_s) / dt == pytest.approx(
        force - mode.damping_n_s_per_m * velocity - mode.stiffness_n_per_m * x
        + mode.coupling_c_per_m * voltage, rel=2e-11, abs=2e-14
    )
    assert (final.charge_c - initial.charge_c) / dt == pytest.approx(
        current - conductance * voltage, rel=2e-11, abs=2e-14
    )
    work = dt * (force * velocity + current * voltage)
    dissipated = dt * (mode.damping_n_s_per_m * velocity**2 + conductance * voltage**2)
    assert result.energy_before_j == pytest.approx(_energy(mode, initial), rel=2e-13)
    assert result.energy_after_j == pytest.approx(_energy(mode, final), rel=2e-13)
    assert result.external_work_j == pytest.approx(work, rel=2e-12, abs=1e-20)
    assert result.dissipated_energy_j == pytest.approx(dissipated, rel=2e-12, abs=1e-20)
    scale = max(result.energy_before_j, result.energy_after_j, abs(work), dissipated)
    assert abs(_energy(mode, final) - _energy(mode, initial) - work + dissipated) < 2e-13 * scale
    assert abs(result.balance_error_j) < 2e-13 * scale


def test_passive_loaded_mode_loses_energy_without_external_power():
    mode = _mode()
    state = ModeState(0.2, 0.4, 0.7)
    initial_energy = mode.energy_j(state)
    previous_energy = initial_energy
    for _ in range(40):
        result = mode.step_current_driven(state, 0.05, load_conductance_s=0.2)
        assert result.external_work_j == 0.0
        assert result.dissipated_energy_j >= 0.0
        assert result.energy_after_j <= previous_energy + 1e-14 * initial_energy
        state, previous_energy = result.state, result.energy_after_j
    assert previous_energy < 0.8 * initial_energy


def test_short_circuit_step_preserves_charge_constraint_and_mechanical_energy_balance():
    mode = _mode()
    initial = ModeState(0.2, -0.4, 0.4)
    dt, force = 0.05, 0.7
    result = mode.step_short_circuit(initial, dt, force_n=force)
    state = result.state
    assert state.charge_c == pytest.approx(mode.coupling_c_per_m * state.displacement_m, abs=1e-14)
    assert mode.voltage_v(state) == pytest.approx(0.0, abs=1e-14)
    velocity = (state.velocity_m_per_s + initial.velocity_m_per_s) / 2.0
    x = (state.displacement_m + initial.displacement_m) / 2.0
    assert (state.displacement_m - initial.displacement_m) / dt == pytest.approx(velocity)
    assert mode.mass_kg * (state.velocity_m_per_s - initial.velocity_m_per_s) / dt == pytest.approx(
        force - mode.damping_n_s_per_m * velocity - mode.stiffness_n_per_m * x
    )
    assert result.external_work_j == pytest.approx(dt * force * velocity)
    assert result.dissipated_energy_j == pytest.approx(dt * mode.damping_n_s_per_m * velocity**2)
    assert abs(result.balance_error_j) < 1e-13


def test_short_circuit_cannot_discard_an_incompatible_initial_electrical_state():
    with pytest.raises(ValueError):
        _mode().step_short_circuit(ModeState(0.2, -0.4, 0.41), 0.05)


def test_tiny_charge_mismatch_cannot_discard_large_capacitor_energy():
    mode = _mode(mass_kg=1.0, stiffness_n_per_m=1.0, damping_n_s_per_m=0.0,
                 capacitance_f=1e-32, coupling_c_per_m=1.0)
    charged = ModeState(1.0, 0.0, 1.0 + 1e-15)
    assert mode.energy_j(charged) > 60.0
    with pytest.raises(ValueError, match="short-circuit initial charge"):
        mode.step_short_circuit(charged, 0.1)


def test_finite_damping_input_cannot_hide_overflow_in_harmonic_impedance():
    mode = _mode(mass_kg=1.0, stiffness_n_per_m=1.0, damping_n_s_per_m=1e308,
                 capacitance_f=1.0, coupling_c_per_m=0.0)
    with pytest.raises(ValueError):
        mode.harmonic_response(1.0, boundary="short", force_n=1.0)


def test_midpoint_converges_at_second_order_to_the_analytic_open_oscillator():
    mode = _mode(damping_n_s_per_m=0.0)
    initial = ModeState(0.3, 0.2, 0.0)
    omega, duration = math.sqrt(8.0), 1.3
    exact_x = 0.3 * math.cos(omega * duration) + 0.2 / omega * math.sin(omega * duration)
    exact_v = -0.3 * omega * math.sin(omega * duration) + 0.2 * math.cos(omega * duration)
    errors = []
    for steps in (20, 40):
        state = initial
        for _ in range(steps):
            state = mode.step_current_driven(state, duration / steps).state
        assert state.charge_c == pytest.approx(0.0, abs=1e-15)
        assert mode.energy_j(state) == pytest.approx(mode.energy_j(initial), rel=3e-13)
        errors.append(math.hypot(state.displacement_m - exact_x, (state.velocity_m_per_s - exact_v) / omega))
    assert 3.8 < errors[0] / errors[1] < 4.2


@pytest.mark.parametrize("physical_scale", (False, True))
def test_full_electrode_polarity_reversal_preserves_motion_and_power(physical_scale):
    if physical_scale:
        positive, state_a = _si_mode(), ModeState(1e-6, 0.04, 4e-8)
        dt, force, current, conductance = 1e-5, 0.02, 2e-5, 1e-5
    else:
        positive, state_a = _mode(), ModeState(0.2, -0.3, 0.7)
        dt, force, current, conductance = 0.05, 0.8, -0.4, 0.25
    negative = replace(positive, coupling_c_per_m=-positive.coupling_c_per_m)
    state_b = replace(state_a, charge_c=-state_a.charge_c)
    for _ in range(12):
        a = positive.step_current_driven(state_a, dt, force_n=force, current_a=current,
                                         load_conductance_s=conductance)
        b = negative.step_current_driven(state_b, dt, force_n=force, current_a=-current,
                                         load_conductance_s=conductance)
        assert b.state.displacement_m == pytest.approx(a.state.displacement_m, rel=2e-12, abs=0.0)
        assert b.state.velocity_m_per_s == pytest.approx(a.state.velocity_m_per_s, rel=2e-12, abs=0.0)
        assert b.state.charge_c == pytest.approx(-a.state.charge_c, rel=2e-12, abs=0.0)
        assert negative.voltage_v(b.state) == pytest.approx(-positive.voltage_v(a.state), rel=2e-12, abs=0.0)
        assert b.energy_after_j == pytest.approx(a.energy_after_j, rel=2e-12, abs=0.0)
        assert b.external_work_j == pytest.approx(a.external_work_j, rel=2e-12, abs=0.0)
        assert b.dissipated_energy_j == pytest.approx(a.dissipated_energy_j, rel=2e-12, abs=0.0)
        state_a, state_b = a.state, b.state


def test_zero_coupling_recovers_an_independent_capacitor_rc_decay():
    mode = _mode(coupling_c_per_m=0.0)
    state = ModeState(0.0, 0.0, 0.8)
    # C=0.5 F and G=0.25 S give tau=C/G=2 s.
    for _ in range(40):
        result = mode.step_current_driven(state, 0.05, load_conductance_s=0.25)
        assert result.state.displacement_m == 0.0
        assert result.state.velocity_m_per_s == 0.0
        assert result.energy_after_j < result.energy_before_j
        state = result.state
    assert state.charge_c == pytest.approx(0.8 * math.exp(-1.0), rel=6e-5)
    assert mode.voltage_v(state) == pytest.approx(1.6 * math.exp(-1.0), rel=6e-5)


def test_zero_coupling_current_charges_the_capacitor_without_mechanical_motion():
    mode = _mode(coupling_c_per_m=0.0)
    initial = ModeState(0.0, 0.0, 0.8)
    result = mode.step_current_driven(initial, 0.2, current_a=-0.3)
    assert result.state.displacement_m == 0.0
    assert result.state.velocity_m_per_s == 0.0
    assert result.state.charge_c == pytest.approx(0.74, rel=2e-15, abs=0.0)
    assert result.external_work_j == pytest.approx((0.74**2 - 0.8**2) / (2.0 * 0.5))
    assert result.dissipated_energy_j == 0.0
