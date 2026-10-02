"""Declared single-mode cubic extension of the existing linear ring control.

q'' + 2 gamma q' + omega^2 (1+h cos(Omega t)) q + beta q^3 = 0.
beta has units m^-2 s^-2. No geometry-derived material or many-body claim.
"""

import math

import numpy as np
from scipy.integrate import solve_ivp

from .proposed_scalar_wave_control import RingMode, _count, _finite
from .time_order_diagnostics import stroboscopic_diagnostics


def nonlinear_trace(
    mode: RingMode,
    *,
    beta=1.0,
    periods=400,
    steps_per_period=32,
    displacement_m=0.01,
    velocity_m_s=0.0,
    rtol=1e-9,
    atol=1e-11,
):
    beta = _finite(beta, "beta")
    rtol, atol = _finite(rtol, "rtol"), _finite(atol, "atol")
    if beta < 0 or not 0 < rtol < 1 or not 0 < atol < 1:
        raise ValueError("nonnegative beta and tolerances in (0,1) required")
    periods = _count(periods, "periods", 32)
    steps_per_period = _count(steps_per_period, "steps_per_period", 16)
    initial = [_finite(displacement_m, "displacement"), _finite(velocity_m_s, "velocity")]
    omega2 = mode.omega_rad_s**2

    def rhs(t, y):
        q, v = y
        return (
            v,
            -2 * mode.damping_per_s * v
            - omega2 * (1 + mode.modulation * math.cos(mode.drive_rad_s * t)) * q
            - beta * q**3,
        )

    times = np.arange(periods + 1) * mode.period_s
    solution = solve_ivp(
        rhs,
        (0.0, float(times[-1])),
        initial,
        t_eval=times,
        method="DOP853",
        max_step=mode.period_s / steps_per_period,
        rtol=rtol,
        atol=atol,
    )
    if not solution.success or not np.isfinite(solution.y).all():
        raise ValueError("integration failed or produced nonfinite states")
    states = solution.y.T
    normalized = states / np.array([1.0, mode.omega_rad_s])
    return dict(
        times_s=times.tolist(),
        states_q_m_v_m_s=states.tolist(),
        final_state=states[-1].tolist(),
        beta_m_minus2_s_minus2=beta,
        diagnostic_coordinates="q and v/omega, both metres; sampled at drive phase zero",
        late_window=stroboscopic_diagnostics(normalized[-128:]),
        scope="single prescribed spatial mode with simulated amplitude; no collective crystal claim",
    )
