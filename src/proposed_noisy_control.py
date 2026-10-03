"""Synthetic finite-band measurement noise on the preserved delayed controller.

Uses the existing mode-pair delayed-error convention and actuator force state.
Mechanical work per modal mass only; no electrical or calibrated hardware model.
"""

import math

import numpy as np

from .proposed_combined_control_limits import _actuator_rate, _rk4_step
from .proposed_measurement_noise import FourierMeasurementNoise
from .proposed_mode_pair_control import target
from .proposed_scalar_wave_control import _count, _finite


def noisy_control_trace(
    *,
    coefficients=None,
    position_sigma_m=0.0,
    velocity_sigma_m_s=0.0,
    actuator_time_constant_s=0.0,
    delay_s=0.0,
    force_limit=10.0,
    periods=20,
    steps_per_period=256,
):
    """Integrate the existing ideal plant with an optional lag on clipped force.

    Delayed error uses linear stored-history interpolation and the original
    target-relative negative-time history; delay must be zero or >= dt.
    Positive-tau force starts at zero. tau=0 applies the clipped command directly.
    The dt/tau<=0.5 guard resolves the extra fast state in explicit RK4; it is a
    numerical restriction, not a measured hardware limit.
    """
    noise = FourierMeasurementNoise(coefficients, position_sigma_m, velocity_sigma_m_s)
    for value in (actuator_time_constant_s, delay_s, force_limit):
        if isinstance(value, (bool, np.bool_)) or np.iscomplexobj(value):
            raise ValueError("time constant and force limit must be finite real scalars")
    tau = _finite(actuator_time_constant_s, "actuator_time_constant_s")
    delay = _finite(delay_s, "delay_s")
    limit = _finite(force_limit, "force_limit")
    if tau < 0 or delay < 0 or limit <= 0:
        raise ValueError("nonnegative time constant and positive force limit required")
    periods = _count(periods, "periods", 5)
    steps = _count(steps_per_period, "steps_per_period", 32)
    dt = 2 * math.pi / steps
    if tau > 0 and dt / tau > 0.5:
        raise ValueError("unresolved actuator: require dt/tau<=0.5; refine timestep")
    if 0 < delay < dt:
        raise ValueError("nonzero delay must be at least one timestep; refine the step")
    count = periods * steps
    # q(2),v(2),actual force(2), signed actuator work,pump work,damping loss.
    history = np.zeros((count + 1, 9))
    history[0, :4] = target(0) + np.array([0.25, 0, 0, 0])

    def command(t, mechanical, known):
        desired = target(t)
        k = 1 + 0.2 * math.cos(2 * t)
        sample_time = t - delay
        if delay == 0:
            sample = mechanical
        elif sample_time < 0:
            sample = target(sample_time) + np.array([0.25, 0, 0, 0])
        else:
            location = min(sample_time / dt, float(known))
            low = int(math.floor(location))
            high = min(low + 1, known)
            sample = history[low, :4] * (1 - (location - low)) + history[high, :4] * (
                location - low
            )
        error = sample - target(sample_time)
        if noise.enabled:
            error = error + noise(sample_time)
        raw = (k - 1) * desired[:2] + 0.04 * desired[2:] + (k - 1) * error[:2] - 0.6 * error[2:]
        magnitude = float(np.linalg.norm(raw))
        return raw * min(1.0, limit / max(magnitude, 1e-300)), magnitude

    def rhs(t, state, known):
        q, v = state[:2], state[2:4]
        limited, _ = command(t, state[:4], known)
        force = limited if tau == 0 else state[4:6]
        k = 1 + 0.2 * math.cos(2 * t)
        rate = np.zeros(2) if tau == 0 else _actuator_rate(force, limited, tau)
        return np.r_[
            v,
            -0.04 * v - k * q + force,
            rate,
            np.dot(force, v),
            -0.2 * math.sin(2 * t) * np.dot(q, q),
            0.04 * np.dot(v, v),
        ]

    for i in range(count):
        history[i + 1] = _rk4_step(
            lambda t, state, known=i: rhs(t, state, known), i * dt, history[i], dt
        )
        if not np.isfinite(history[i + 1]).all():
            raise ValueError("nonfinite trajectory; refine or change declared scales")
    times = np.arange(count + 1) * dt
    states = history[:, :4]
    commands = [
        command(t, state, i) for i, (t, state) in enumerate(zip(times, states, strict=True))
    ]
    limited = np.array([item[0] for item in commands])
    force = limited if tau == 0 else history[:, 4:6]
    raw_norm = np.array([item[1] for item in commands])
    force_norm = np.linalg.norm(force, axis=1)
    q, v = states[:, :2], states[:, 2:]
    energy = (np.sum(v * v, axis=1) + (1 + 0.2 * np.cos(2 * times)) * np.sum(q * q, axis=1)) / 2
    work, pump, loss = history[:, 6:].T
    residual = energy - energy[0] - work - pump + loss
    desired = np.array([target(t) for t in times])
    late_rms = float(np.sqrt(np.mean(np.sum((states - desired)[-5 * steps :, :2] ** 2, axis=1))))
    observations = np.array([noise(t - delay) for t in times])
    return dict(
        noise=noise.metadata(),
        sampled_noise_mean=observations.mean(axis=0).tolist(),
        sampled_noise_rms=np.sqrt(np.mean(observations**2, axis=0)).tolist(),
        noise_statistics_convention="Equal-weight output samples from t=0 through final time inclusive, evaluated at t-delay; channels qx,qy,vx,vy in m,m,m/s,m/s.",
        clipping_statistics_convention="Equal-weight output samples from t=0 through final time inclusive; raw command norm >= force limit.",
        parameters=dict(
            actuator_time_constant_s=tau,
            delay_s=delay,
            force_limit=limit,
            periods=periods,
            steps_per_period=steps,
        ),
        times_s=times.tolist(),
        states=states.tolist(),
        applied_force_per_mass=force.tolist(),
        limited_command_per_mass=limited.tolist(),
        mechanical_energy_per_mass=energy.tolist(),
        actuator_work_per_mass=work.tolist(),
        pump_work_per_mass=pump.tolist(),
        damping_loss_per_mass=loss.tolist(),
        energy_balance_residual_per_mass=residual.tolist(),
        max_energy_balance_residual_per_mass=float(np.max(np.abs(residual))),
        maximum_sampled_force_per_mass=float(np.max(force_norm)),
        sampled_command_clipping_fraction=float(np.mean(raw_norm >= limit)),
        sampled_applied_force_saturation_fraction=float(np.mean(force_norm >= limit * (1 - 1e-12))),
        late_position_rms_m=late_rms,
        diagnostic_limit_m=0.05,
        meets_declared_tracking_target=bool(late_rms <= 0.05),
        startup="Zero initial applied force for positive tau; instantaneous clipped command for tau=0.",
        scope="Synthetic finite-run delayed-error feedback and force lag; mechanical m^2/s^2 ledger only; finite-band prescribed measurement noise; no electrical draw, actuator storage, regeneration, stiffness mismatch or calibrated hardware model.",
    )
