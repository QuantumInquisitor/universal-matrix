"""Synthetic paired-mode tracking robustness, extending the recovered proposal.

Units: displacement m, time s, modal force per mass m/s^2. This is active
tracking, not spontaneous circulation or a calibrated material model.
"""

import math

import numpy as np

from .proposed_scalar_wave_control import _count, _finite


def target(t):
    """Declared unit-radius, unit-angular-frequency travelling mode."""
    return np.array([math.cos(t), math.sin(t), -math.sin(t), math.cos(t)])


def mode_pair_trace(
    *,
    force_limit=10.0,
    delay_s=0.0,
    measurement_amplitude=0.0,
    stiffness_ratio=1.0,
    periods=20,
    steps_per_period=256,
):
    """RK4 method of steps with interpolated measured history for nonzero delay.

    Gamma=.02, pump h=.2 at Omega=2, controller omega_c=1 and eta=.3.
    Measurement disturbance is deterministic two-frequency input, not Gaussian
    noise. Initial error is (.25,0,0,0); negative-time history holds that error
    relative to the travelling target. Delay must be zero or >= one step.
    """
    values = {
        name: _finite(value, name)
        for name, value in (
            ("force_limit", force_limit),
            ("delay_s", delay_s),
            ("measurement_amplitude", measurement_amplitude),
            ("stiffness_ratio", stiffness_ratio),
        )
    }
    force_limit, delay_s, measurement_amplitude, stiffness_ratio = values.values()
    if min(force_limit, stiffness_ratio) <= 0 or min(delay_s, measurement_amplitude) < 0:
        raise ValueError("positive force/stiffness and nonnegative delay/disturbance required")
    periods = _count(periods, "periods", 1)
    steps_per_period = _count(steps_per_period, "steps_per_period", 32)
    dt = 2 * math.pi / steps_per_period
    if 0 < delay_s < dt:
        raise ValueError("nonzero delay must be at least one timestep; refine the step")
    count = periods * steps_per_period
    history = np.zeros((count + 1, 4))
    error0 = np.array([0.25, 0, 0, 0])
    history[0] = target(0) + error0
    forces = np.zeros(count + 1)

    def measured(t, state, known):
        sample_time = t - delay_s
        if delay_s == 0:
            sample = state.copy()
        elif sample_time < 0:
            sample = target(sample_time) + error0
        else:
            location = min(sample_time / dt, float(known))
            low = int(math.floor(location))
            high = min(low + 1, known)
            sample = history[low] * (1 - (location - low)) + history[high] * (location - low)
        # q disturbance has units m, velocity disturbance has units m/s.
        sample += measurement_amplitude * np.array(
            [
                math.sin(7 * sample_time),
                math.cos(11 * sample_time),
                math.cos(7 * sample_time),
                math.sin(11 * sample_time),
            ]
        )
        return sample - target(sample_time)

    def rhs(t, state, known):
        desired = target(t)
        k = 1 + 0.2 * math.cos(2 * t)
        error = measured(t, state, known)
        command = (k - 1) * desired[:2] + 0.04 * desired[2:] + (k - 1) * error[:2] - 0.6 * error[2:]
        magnitude = float(np.linalg.norm(command))
        force = command * min(1.0, force_limit / max(magnitude, 1e-300))
        return np.r_[state[2:], -0.04 * state[2:] - stiffness_ratio * k * state[:2] + force], min(
            magnitude, force_limit
        )

    for index in range(count):
        t, state = index * dt, history[index]
        a, forces[index] = rhs(t, state, index)
        b, _ = rhs(t + dt / 2, state + dt * a / 2, index)
        c, _ = rhs(t + dt / 2, state + dt * b / 2, index)
        d, _ = rhs(t + dt, state + dt * c, index)
        history[index + 1] = state + dt * (a + 2 * b + 2 * c + d) / 6
        if not np.isfinite(history[index + 1]).all():
            raise ValueError("nonfinite trajectory; refine or change declared scales")
    _, forces[-1] = rhs(count * dt, history[-1], count)
    times = np.arange(count + 1) * dt
    desired = np.array([target(t) for t in times])
    error = history - desired
    late = error[-5 * steps_per_period :]
    return dict(
        parameters=values,
        times_s=times.tolist(),
        states=history.tolist(),
        late_position_rms_m=float(np.sqrt(np.mean(np.sum(late[:, :2] ** 2, axis=1)))),
        late_velocity_rms_m_s=float(np.sqrt(np.mean(np.sum(late[:, 2:] ** 2, axis=1)))),
        maximum_sampled_force_per_mass=float(max(forces)),
        sampled_saturation_fraction=float(np.mean(forces >= force_limit * (1 - 1e-12))),
        diagnostic_limit_m=0.05,
        meets_declared_tracking_target=bool(
            np.sqrt(np.mean(np.sum(late[:, :2] ** 2, axis=1))) <= 0.05
        ),
        scope="finite-run active controller; target <=.05 m late position RMS; not a proven stability boundary",
    )
