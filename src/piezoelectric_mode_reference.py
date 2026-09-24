"""Single-mode linear piezoelectric reference with explicit SI parameters.

This optional model is not a material reduction of the toroidal geometry.
Its demonstration uses synthetic parameters, not measured ring properties.
Phasors use exp(i omega t); electrical current enters the positive electrode.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


def _finite(value, name: str) -> float:
    if isinstance(value, (bool, np.bool_)):
        raise ValueError(f"{name} must be a finite real number")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{name} must be a finite real number") from error
    if not math.isfinite(result):
        raise ValueError(f"{name} must be a finite real number")
    return result


def _phasor(value, name: str) -> complex:
    if isinstance(value, (bool, np.bool_)):
        raise ValueError(f"{name} must be a finite complex amplitude")
    try:
        result = complex(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{name} must be a finite complex amplitude") from error
    if not (math.isfinite(result.real) and math.isfinite(result.imag)):
        raise ValueError(f"{name} must be a finite complex amplitude")
    return result


def _positive(value, name: str) -> float:
    result = _finite(value, name)
    if result <= 0:
        raise ValueError(f"{name} must be positive")
    return result


@dataclass(frozen=True)
class ModeState:
    displacement_m: float
    velocity_m_per_s: float
    charge_c: float

    def __post_init__(self) -> None:
        for name in ("displacement_m", "velocity_m_per_s", "charge_c"):
            object.__setattr__(self, name, _finite(getattr(self, name), name))


@dataclass(frozen=True)
class HarmonicResponse:
    frequency_hz: float
    displacement_m: complex
    voltage_v: complex
    charge_c: complex
    current_a: complex


@dataclass(frozen=True)
class StepResult:
    state: ModeState
    energy_before_j: float
    energy_after_j: float
    external_work_j: float
    dissipated_energy_j: float
    balance_error_j: float


@dataclass(frozen=True)
class PiezoelectricMode:
    """Effective modal parameters; coupling is signed C/m, equivalently N/V.

    No parameter is inferred from a frequency label or a canonical Matrix tick.
    parameter_source must identify the supplied or synthetic parameter set.
    """

    mass_kg: float
    stiffness_n_per_m: float
    damping_n_s_per_m: float
    capacitance_f: float
    coupling_c_per_m: float
    parameter_source: str

    def __post_init__(self) -> None:
        for name in ("mass_kg", "stiffness_n_per_m", "capacitance_f"):
            object.__setattr__(self, name, _positive(getattr(self, name), name))
        for name in ("damping_n_s_per_m", "coupling_c_per_m"):
            object.__setattr__(self, name, _finite(getattr(self, name), name))
        if self.damping_n_s_per_m < 0:
            raise ValueError("damping must be nonnegative")
        if not isinstance(self.parameter_source, str) or not self.parameter_source.strip():
            raise ValueError("parameter_source must identify the parameter set")
        _positive(self._stiffness("open"), "open-circuit stiffness")

    def _stiffness(self, boundary: str) -> float:
        if boundary == "short":
            return self.stiffness_n_per_m
        if boundary == "open":
            return self.stiffness_n_per_m + self.coupling_c_per_m * (
                self.coupling_c_per_m / self.capacitance_f
            )
        raise ValueError("boundary must be explicitly 'short' or 'open'")

    def voltage_v(self, state: ModeState) -> float:
        return _finite((state.charge_c - self.coupling_c_per_m * state.displacement_m)
                       / self.capacitance_f, "voltage")

    def energy_j(self, state: ModeState) -> float:
        voltage = self.voltage_v(state)
        return _finite(0.5 * (self.mass_kg * state.velocity_m_per_s**2
                             + self.stiffness_n_per_m * state.displacement_m**2
                             + self.capacitance_f * voltage**2), "energy")

    def natural_frequency_hz(self, boundary: str) -> float:
        """Undamped natural frequency, not a damping-dependent response peak."""
        return _positive(math.sqrt(self._stiffness(boundary) / self.mass_kg)
                         / (2 * math.pi), "natural frequency")

    def _response(self, frequency_hz, stiffness, force, voltage=None) -> HarmonicResponse:
        frequency = _positive(frequency_hz, "frequency_hz")
        omega = _positive(2 * math.pi * frequency, "angular frequency")
        inertia = _finite(self.mass_kg * omega * omega, "inertia")
        dynamic = complex(stiffness - inertia, _finite(self.damping_n_s_per_m * omega, "damping impedance"))
        # At a real undamped pole, a finite unique steady response does not exist.
        if abs(dynamic) <= 8 * np.finfo(float).eps * max(stiffness, inertia):
            raise ValueError("singular undamped resonance or numerically unresolved pole")
        x = _phasor(force / dynamic, "displacement response")
        if voltage is None:  # Open electrode, zero incremental free charge.
            v = _phasor(-self.coupling_c_per_m * x / self.capacitance_f, "voltage response")
            q = 0j
        else:
            v = voltage
            q = _phasor(self.capacitance_f * v + self.coupling_c_per_m * x, "charge response")
        return HarmonicResponse(frequency, x, v, q, _phasor(1j * omega * q, "current response"))

    def harmonic_response(self, frequency_hz, *, boundary: str, force_n) -> HarmonicResponse:
        """Mechanical force response with shorted or open electrodes."""
        stiffness = self._stiffness(boundary)
        force = _phasor(force_n, "force_n")
        return self._response(frequency_hz, stiffness, force,
                              voltage=0j if boundary == "short" else None)

    def voltage_driven_response(self, frequency_hz, *, voltage_v, force_n=0j) -> HarmonicResponse:
        """Ideal imposed voltage; returns the electrode current it requires."""
        voltage = _phasor(voltage_v, "voltage_v")
        force = _phasor(force_n, "force_n")
        effective_force = _phasor(force + self.coupling_c_per_m * voltage, "effective force")
        return self._response(frequency_hz, self.stiffness_n_per_m, effective_force, voltage)

    def harmonic_sweep(self, frequencies_hz, *, boundary: str, force_n) -> tuple[HarmonicResponse, ...]:
        self._stiffness(boundary)
        force = _phasor(force_n, "force_n")
        return tuple(self.harmonic_response(f, boundary=boundary, force_n=force) for f in frequencies_hz)

    def _step_result(self, before: ModeState, after: ModeState, dt, force, current, conductance) -> StepResult:
        midpoint = ModeState(0.5 * (before.displacement_m + after.displacement_m),
                             0.5 * (before.velocity_m_per_s + after.velocity_m_per_s),
                             0.5 * (before.charge_c + after.charge_c))
        voltage, velocity = self.voltage_v(midpoint), midpoint.velocity_m_per_s
        work = _finite(dt * (force * velocity + voltage * current), "external work")
        loss = _finite(dt * (self.damping_n_s_per_m * velocity**2 + conductance * voltage**2), "loss")
        initial, final = self.energy_j(before), self.energy_j(after)
        return StepResult(after, initial, final, work, loss, final - initial - work + loss)

    def step_current_driven(self, state: ModeState, dt_s, *, force_n=0.0, current_a=0.0,
                            load_conductance_s=0.0) -> StepResult:
        """Implicit midpoint with constant step inputs and a passive shunt.

        qdot = current_a - G V. G=0 and current_a=0 is open circuit.
        Midpoint work/loss exactly balance the quadratic energy in exact arithmetic.
        """
        dt = _positive(dt_s, "dt_s")
        force, current = _finite(force_n, "force_n"), _finite(current_a, "current_a")
        conductance = _finite(load_conductance_s, "load_conductance_s")
        if conductance < 0:
            raise ValueError("load conductance must be nonnegative")
        m, c, cap, theta = (self.mass_kg, self.damping_n_s_per_m,
                             self.capacitance_f, self.coupling_c_per_m)
        # Energy coordinates avoid conditioning caused merely by unlike SI units.
        root_k, root_m, root_cap = map(math.sqrt, (self.stiffness_n_per_m, m, cap))
        omega, coupling_rate = root_k / root_m, (theta / root_cap) / root_m
        matrix = np.array([[0, omega, 0], [-omega, -c / m, coupling_rate],
                           [0, -coupling_rate, -conductance / cap]], dtype=float)
        previous = np.array([root_k * state.displacement_m, root_m * state.velocity_m_per_s,
                             root_cap * self.voltage_v(state)])
        rhs = (np.eye(3) + 0.5 * dt * matrix) @ previous + dt * np.array([0, force / root_m, current / root_cap])
        system = np.eye(3) - 0.5 * dt * matrix
        if not (np.all(np.isfinite(system)) and np.all(np.isfinite(rhs))):
            raise ValueError("step exceeds finite numerical range")
        try:
            next_state = np.linalg.solve(system, rhs)
        except np.linalg.LinAlgError as error:
            raise ValueError("step is numerically singular") from error
        x, velocity = next_state[0] / root_k, next_state[1] / root_m
        after = ModeState(x, velocity, root_cap * next_state[2] + theta * x)
        return self._step_result(state, after, dt, force, current, conductance)

    def step_short_circuit(self, state: ModeState, dt_s, *, force_n=0.0) -> StepResult:
        """Ideal zero-voltage clamp; initial charge must satisfy q=theta*x.

        Switching a charged capacitor onto an ideal short needs its own impulse
        and energy accounting, so inconsistent initial states are rejected.
        """
        dt, force = _positive(dt_s, "dt_s"), _finite(force_n, "force_n")
        expected_charge = self.coupling_c_per_m * state.displacement_m
        if state.charge_c != expected_charge:
            raise ValueError("short-circuit initial charge must satisfy q=theta*x")
        root_k, root_m = math.sqrt(self.stiffness_n_per_m), math.sqrt(self.mass_kg)
        omega = root_k / root_m
        matrix = np.array([[0, omega], [-omega, -self.damping_n_s_per_m / self.mass_kg]])
        previous = np.array([root_k * state.displacement_m, root_m * state.velocity_m_per_s])
        rhs = (np.eye(2) + 0.5 * dt * matrix) @ previous + dt * np.array([0, force / root_m])
        system = np.eye(2) - 0.5 * dt * matrix
        if not (np.all(np.isfinite(system)) and np.all(np.isfinite(rhs))):
            raise ValueError("step exceeds finite numerical range")
        try:
            scaled_x, scaled_v = np.linalg.solve(system, rhs)
        except np.linalg.LinAlgError as error:
            raise ValueError("step is numerically singular") from error
        x, velocity = scaled_x / root_k, scaled_v / root_m
        after = ModeState(x, velocity, self.coupling_c_per_m * x)
        return self._step_result(state, after, dt, force, 0, 0)


def main() -> None:
    mode = PiezoelectricMode(2.0, 8.0, 0.4, 0.5, 2.0, "synthetic_control_not_a_material_fit")
    print("SINGLE-MODE PIEZOELECTRIC REFERENCE")
    print(f"parameter_source={mode.parameter_source}")
    for boundary in ("short", "open"):
        sweep = mode.harmonic_sweep(np.geomspace(0.05, 2.0, 501), boundary=boundary, force_n=1.0)
        peak = max(sweep, key=lambda response: abs(response.displacement_m))
        print(f"boundary={boundary}; undamped_natural_hz={mode.natural_frequency_hz(boundary):.9g}; "
              f"sampled_force_response_peak_hz={peak.frequency_hz:.9g}")
    state = ModeState(0.1, 0.0, 0.0)
    largest_residual = 0.0
    for _ in range(200):
        step = mode.step_current_driven(state, 0.01, load_conductance_s=0.2)
        largest_residual = max(largest_residual, abs(step.balance_error_j))
        state = step.state
    print(f"midpoint_energy_balance_max_error_j={largest_residual:.3g}")
    print("scope=single_linear_mode; material_tensor_reduction_and_ring_validation_remain_open")


if __name__ == "__main__":
    main()
