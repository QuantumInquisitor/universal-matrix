"""Synthetic first-order force actuator; mechanical work per unit modal mass.

Ideal instantaneous measurements only: no delayed/noisy observations or stiffness
mismatch. A force lag is not an electrical supply or actuator storage model.
"""

import math

import numpy as np

from .proposed_mode_pair_control import target
from .proposed_scalar_wave_control import _count, _finite


def _rk4_step(rhs, t, state, dt):
    a = rhs(t, state)
    b = rhs(t + dt / 2, state + dt * a / 2)
    c = rhs(t + dt / 2, state + dt * b / 2)
    d = rhs(t + dt, state + dt * c)
    return state + dt * (a + 2 * b + 2 * c + d) / 6


def _actuator_rate(force, limited_command, tau):
    return (limited_command - force) / tau


def actuator_bandwidth_trace(
    *, actuator_time_constant_s=0.0, force_limit=10.0, periods=20, steps_per_period=256
):
    """Integrate the existing ideal plant with an optional lag on clipped force.

    Positive-tau force starts at zero. tau=0 applies the clipped command directly.
    The dt/tau<=0.5 guard resolves the extra fast state in explicit RK4; it is a
    numerical restriction, not a measured hardware limit.
    """
    for value in (actuator_time_constant_s, force_limit):
        if isinstance(value, (bool, np.bool_)) or np.iscomplexobj(value):
            raise ValueError("time constant and force limit must be finite real scalars")
    tau = _finite(actuator_time_constant_s, "actuator_time_constant_s")
    limit = _finite(force_limit, "force_limit")
    if tau < 0 or limit <= 0:
        raise ValueError("nonnegative time constant and positive force limit required")
    periods = _count(periods, "periods", 5)
    steps = _count(steps_per_period, "steps_per_period", 32)
    dt = 2 * math.pi / steps
    if tau > 0 and dt / tau > 0.5:
        raise ValueError("unresolved actuator: require dt/tau<=0.5; refine timestep")
    count = periods * steps
    # q(2),v(2),actual force(2), signed actuator work,pump work,damping loss.
    history = np.zeros((count + 1, 9))
    history[0, :4] = target(0) + np.array([0.25, 0, 0, 0])

    def command(t, mechanical):
        desired = target(t)
        k = 1 + 0.2 * math.cos(2 * t)
        error = mechanical - desired
        raw = (k - 1) * desired[:2] + 0.04 * desired[2:] + (k - 1) * error[:2] - 0.6 * error[2:]
        magnitude = float(np.linalg.norm(raw))
        return raw * min(1.0, limit / max(magnitude, 1e-300)), magnitude

    def rhs(t, state):
        q, v = state[:2], state[2:4]
        limited, _ = command(t, state[:4])
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
        history[i + 1] = _rk4_step(rhs, i * dt, history[i], dt)
        if not np.isfinite(history[i + 1]).all():
            raise ValueError("nonfinite trajectory; refine or change declared scales")
    times = np.arange(count + 1) * dt
    states = history[:, :4]
    commands = [command(t, state) for t, state in zip(times, states, strict=True)]
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
    return dict(
        parameters=dict(
            actuator_time_constant_s=tau, force_limit=limit, periods=periods, steps_per_period=steps
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
        scope="Synthetic finite-run ideal-measurement force lag; mechanical m^2/s^2 ledger only; no electrical draw, actuator storage, regeneration, delay, noise or stiffness mismatch model.",
    )
