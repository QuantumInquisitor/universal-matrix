"""Two-mode ring Galerkin control; finite truncation, not material calibration.

u(x,t)=q1(t) cos(x)+q2(t) sin(x), with a local alpha*u**3 force.
Projection gives beta=3*alpha/4 and cross coupling c=1. c=0 is an
artificial independent-oscillator comparison, not the same local field PDE.
E, pump work and damping loss use unit modal mass (m**2/s**2).
"""

import math

import numpy as np
from scipy.integrate import solve_ivp

from .proposed_scalar_wave_control import RingMode, _count, _finite


def multimode_trace(
    mode: RingMode,
    *,
    alpha=4 / 3,
    coupling=1.0,
    initial=(0.01, 0.007, 0.0, 0.0),
    periods=400,
    steps_per_period=32,
    rtol=1e-9,
    atol=1e-11,
):
    """Integrate q1,q2,v1,v2 and independently accumulated work/loss."""
    alpha, coupling = _finite(alpha, "alpha"), _finite(coupling, "coupling")
    rtol, atol = _finite(rtol, "rtol"), _finite(atol, "atol")
    if alpha < 0 or coupling < 0 or not 0 < rtol < 1 or not 0 < atol < 1:
        raise ValueError("nonnegative coefficients and tolerances in (0,1) required")
    periods = _count(periods, "periods", 1)
    steps_per_period = _count(steps_per_period, "steps_per_period", 16)
    if len(initial) != 4:
        raise ValueError("initial must contain q1,q2,v1,v2")
    initial = [_finite(value, "initial") for value in initial]
    beta, omega2 = 0.75 * alpha, mode.omega_rad_s**2

    def rhs(t, y):
        q, v = y[:2], y[2:4]
        stiffness = omega2 * (1 + mode.modulation * math.cos(mode.drive_rad_s * t))
        force = -stiffness * q - beta * q * (q**2 + coupling * q[::-1] ** 2)
        pump = (
            -0.5
            * omega2
            * mode.modulation
            * mode.drive_rad_s
            * math.sin(mode.drive_rad_s * t)
            * (q @ q)
        )
        loss = 2 * mode.damping_per_s * (v @ v)
        return np.r_[v, force - 2 * mode.damping_per_s * v, pump, loss]

    times = np.arange(periods + 1) * mode.period_s
    solution = solve_ivp(
        rhs,
        (0, times[-1]),
        initial + [0, 0],
        t_eval=times,
        method="DOP853",
        max_step=mode.period_s / steps_per_period,
        rtol=rtol,
        atol=atol,
    )
    if not solution.success or not np.isfinite(solution.y).all():
        raise ValueError("integration failed")
    q, v = solution.y[:2].T, solution.y[2:4].T
    stiffness = omega2 * (1 + mode.modulation * np.cos(mode.drive_rad_s * times))
    energy = 0.5 * np.sum(v * v, axis=1) + 0.5 * stiffness * np.sum(q * q, axis=1)
    energy += beta / 4 * np.sum(q**4, axis=1) + beta * coupling / 2 * q[:, 0] ** 2 * q[:, 1] ** 2
    work, loss = solution.y[4:6]
    residual = energy - energy[0] - work + loss
    late = np.c_[q[-128:], v[-128:] / mode.omega_rad_s]
    amplitudes = np.sqrt(np.mean(late[:, :2] ** 2 + late[:, 2:] ** 2, axis=0))
    angular = q[:, 0] * v[:, 1] - q[:, 1] * v[:, 0]
    return dict(
        times_s=times.tolist(),
        states_q1_q2_v1_v2=solution.y[:4].T.tolist(),
        modal_state_rms_m=amplitudes.tolist(),
        total_state_rms_m=float(np.linalg.norm(amplitudes)),
        energy_per_modal_mass=energy.tolist(),
        pump_work_per_modal_mass=work.tolist(),
        damping_loss_per_modal_mass=loss.tolist(),
        max_energy_balance_residual=float(np.max(np.abs(residual))),
        angular_momentum=angular.tolist(),
        final_state=solution.y[:4, -1].tolist(),
        alpha=alpha,
        beta=beta,
        coupling=coupling,
        scope="two degenerate prescribed spatial basis modes; no complete spatial selection or time-crystal claim",
    )
