"""Our M4-inspired, linear parametrically driven ring-mode hypothesis.

This declared equation is not attributed to an M4 author or fitted to matter.
Energy and work are per unit modal mass, in m^2/s^2; q is in metres.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math

import numpy as np


def _finite(value, name):
    if isinstance(value, (bool, np.bool_)):
        raise ValueError(f"{name} must be finite and real")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{name} must be finite and real") from error
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite and real")
    return result


def _count(value, name, minimum):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)


@dataclass(frozen=True)
class RingMode:
    circumference_m: float
    wave_speed_m_s: float
    mode_number: int
    gap_rad_s: float
    damping_per_s: float
    modulation: float
    drive_rad_s: float

    def __post_init__(self):
        for name in ("circumference_m", "wave_speed_m_s", "gap_rad_s",
                     "damping_per_s", "modulation", "drive_rad_s"):
            object.__setattr__(self, name, _finite(getattr(self, name), name))
        object.__setattr__(self, "mode_number", _count(self.mode_number, "mode_number", 0))
        if min(self.circumference_m, self.wave_speed_m_s, self.drive_rad_s) <= 0:
            raise ValueError("circumference, wave speed, and drive must be positive")
        if min(self.gap_rad_s, self.damping_per_s) < 0 or not 0 <= self.modulation < 1:
            raise ValueError("gap and damping must be nonnegative; modulation must be in [0, 1)")
        try:
            omega = self.omega_rad_s
            scales = (omega * omega, omega / self.drive_rad_s,
                      self.damping_per_s / self.drive_rad_s, 2 * math.pi / self.drive_rad_s)
        except (OverflowError, ZeroDivisionError) as error:
            raise ValueError("derived scales must be finite and resolved") from error
        if omega <= 0 or not all(math.isfinite(v) for v in scales) or min(scales[0], scales[1], scales[3]) <= 0:
            raise ValueError("derived scales must be finite and resolved")

    @property
    def omega_rad_s(self):
        return math.hypot(self.gap_rad_s,
                          (2 * math.pi * self.mode_number / self.circumference_m) * self.wave_speed_m_s)

    @property
    def period_s(self):
        return 2 * math.pi / self.drive_rad_s


def _rk4(rhs, initial, steps, periods=1):
    steps = _count(steps, "steps", 16)
    periods = _count(periods, "periods", 1)
    state = np.array(initial, dtype=float, copy=True)
    delta = 2 * math.pi / steps
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        try:
            for index in range(steps * periods):
                phase = (index % steps) * delta
                a = rhs(phase, state)
                b = rhs(phase + delta / 2, state + delta * a / 2)
                c = rhs(phase + delta / 2, state + delta * b / 2)
                d = rhs(phase + delta, state + delta * c)
                state += delta * (a + 2 * b + 2 * c + d) / 6
        except FloatingPointError as error:
            raise ValueError("integration overflow; reduce scales or refine steps") from error
    if not np.isfinite(state).all():
        raise ValueError("integration must remain finite")
    return state


def _resolved_steps(mode, steps):
    steps = _count(steps, "steps", 16)
    damping_increment = (4 * math.pi * (mode.damping_per_s / mode.drive_rad_s)) / steps
    if mode.damping_per_s > 0 and damping_increment <= np.finfo(float).eps:
        raise ValueError("nonzero damping is unresolved at this step size")
    return steps


def floquet_audit(mode: RingMode, *, steps=512):
    """One drive period, phase zero; multipliers describe linear onset only.

    Matrix coordinates returned are (q, qdot). Numerical stability decisions
    require refinement; determinant agreement alone does not bound phase error.
    """
    steps = _resolved_steps(mode, steps)
    ratio = mode.omega_rad_s / mode.drive_rad_s
    drag = 2 * (mode.damping_per_s / mode.drive_rad_s)

    def rhs(phase, matrix):
        generator = np.array(((0, ratio),
                              (-ratio * (1 + mode.modulation * math.cos(phase)), -drag)))
        return generator @ matrix

    normalized = _rk4(rhs, np.eye(2), steps)
    multipliers = np.linalg.eigvals(normalized)
    radius = float(np.max(np.abs(multipliers)))
    if radius <= 0 or not math.isfinite(radius):
        raise ValueError("Floquet multipliers must be finite and resolved")
    matrix = normalized * np.array(((1, 1 / mode.omega_rad_s), (mode.omega_rad_s, 1)))
    if not np.isfinite(matrix).all():
        raise ValueError("physical monodromy must remain finite")
    expected = math.exp(-4 * math.pi * (mode.damping_per_s / mode.drive_rad_s))
    return {"monodromy": matrix, "multipliers": multipliers,
            "spectral_radius": radius, "growth_rate_per_s": math.log(radius) / mode.period_s,
            "expected_determinant": expected,
            "determinant_error": abs(float(np.linalg.det(normalized)) - expected)}


def energy_audit(mode: RingMode, *, steps=512, periods=1,
                 displacement_m=1.0, velocity_m_s=0.0):
    """Integrate q and independent drive-work/loss quadratures with RK4.

    residual = E_final - E_initial - drive_work + damping_loss.
    Every energy quantity is per unit modal mass, in m^2/s^2.
    """
    steps = _resolved_steps(mode, steps)
    q = _finite(displacement_m, "displacement_m")
    u = _finite(velocity_m_s, "velocity_m_s") / mode.omega_rad_s
    ratio = mode.omega_rad_s / mode.drive_rad_s
    drag = 2 * (mode.damping_per_s / mode.drive_rad_s)

    def rhs(phase, state):
        q, u = state[:2]
        return np.array((ratio * u, -ratio * (1 + mode.modulation * math.cos(phase)) * q - drag * u,
                         -0.5 * mode.modulation * math.sin(phase) * q * q, drag * u * u))

    final = _rk4(rhs, (q, u, 0, 0), steps, periods)
    omega_squared = mode.omega_rad_s * mode.omega_rad_s
    before = 0.5 * (u * u + (1 + mode.modulation) * q * q) * omega_squared
    after = 0.5 * (final[1]**2 + (1 + mode.modulation) * final[0]**2) * omega_squared
    work, loss = final[2:] * omega_squared
    result = {"displacement_m": final[0], "velocity_m_s": final[1] * mode.omega_rad_s,
              "energy_before": before, "energy_after": after,
              "drive_work": work, "damping_loss": loss,
              "balance_residual": after - before - work + loss}
    if not all(math.isfinite(value) for value in result.values()):
        raise ValueError("energy audit must remain finite")
    return result


def main():
    """Report the synthetic experiments with all supplied scales explicit."""
    base = RingMode(2 * math.pi, 1.0, 1, 0.0, 0.02, 0.2, 2.0)
    onset = []
    for ratio in (1.5, 2.0, 2.5):
        mode = RingMode(2 * math.pi, 1.0, 1, 0.0, 0.02, 0.2, ratio)
        for steps in (256, 512, 1024):
            result = floquet_audit(mode, steps=steps)
            onset.append({"drive_over_natural_frequency": ratio, "steps": steps,
                          "spectral_radius": result["spectral_radius"],
                          "growth_rate_per_s": result["growth_rate_per_s"],
                          "determinant_error": result["determinant_error"]})
    # An independent example with a nonzero gap makes the scale assumption visible.
    gapped = RingMode(2 * math.pi, 1.0, 1, 0.5, 0.02, 0.2, 2 * math.sqrt(1.25))
    scaled = RingMode(4 * math.pi, 1.0, 1, 0.25, 0.01, 0.2, math.sqrt(1.25))
    fixed_gap = RingMode(4 * math.pi, 1.0, 1, 0.5, 0.01, 0.2, math.sqrt(1.25))
    scaling = {}
    for label, mode in (("base", gapped), ("joint_scale_by_two", scaled),
                        ("fixed_gap_negative_control", fixed_gap)):
        result = floquet_audit(mode, steps=1024)
        scaling[label] = {"omega_rad_s": mode.omega_rad_s,
                          "spectral_radius": result["spectral_radius"],
                          "growth_rate_per_s": result["growth_rate_per_s"]}
    print(json.dumps({"scope": "our_proposed_linear_ring_mode",
                      "parameters": {"L_m": 2 * math.pi, "v_m_s": 1.0, "n": 1,
                                     "gap_rad_s": 0.0, "gamma_per_s": 0.02, "h": 0.2},
                      "onset": onset,
                      "energy_per_unit_modal_mass_m2_per_s2": energy_audit(base, steps=1024, periods=8),
                      "scaling": scaling}, indent=2))


if __name__ == "__main__":
    main()
