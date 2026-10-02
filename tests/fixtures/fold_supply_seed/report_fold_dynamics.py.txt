"""Synthetic force-driven dynamics of the existing 22-body point-mass reduction."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

try:
    from .report_fold_kinematics import kinematics, scalar
except ImportError:  # direct script invocation
    from report_fold_kinematics import kinematics, scalar

Q0 = np.array((1.0, math.pi / 12))
STIFFNESS = np.array(((0.02, 0.002), (0.002, 0.006)))
DAMPING = np.diag((0.0004, 0.0001))


def vector(value, size, name):
    if not isinstance(value, (tuple, list, np.ndarray)) or np.shape(value) != (size,):
        raise ValueError(f"{name} must have {size} finite real entries")
    return np.array([scalar(v, name) for v in value])


def parameters(damping=1.0, drive=0.0, drive_until=None):
    damping, drive = scalar(damping, "damping"), scalar(drive, "drive")
    if not 0 <= damping <= 10 or abs(drive) > 10:
        raise ValueError("damping and drive outside numerical scope")
    if drive_until is not None:
        drive_until = scalar(drive_until, "drive_until")
        if drive_until <= 0:
            raise ValueError("drive_until must be positive")
    return damping, drive, drive_until


def force(t, drive=0.0, drive_until=None):
    # sin^2 envelope reaches zero with zero slope at shutoff.
    envelope = (
        1.0
        if drive_until is None
        else (math.sin(math.pi * t / drive_until) ** 2 if 0 <= t < drive_until else 0.0)
    )
    return drive * envelope * np.array((0.0001 * math.sin(2 * t), 0.00004 * math.cos(2 * t)))


def mechanical(q, velocity):
    state = kinematics(q)
    v = vector(velocity, 2, "velocity")
    if np.max(np.abs(v)) > 1e6:
        raise ValueError("velocity outside numerical scope +/-1e6 per second")
    h_vv = np.einsum("nxab,a,b->nx", state["hessian"], v, v)
    bias = np.einsum("n,nxa,nx->a", state["mass"], state["jacobian"], h_vv)
    delta = np.asarray(q) - Q0
    energy = float(v @ state["mass_matrix"] @ v / 2 + delta @ STIFFNESS @ delta / 2)
    return state, bias, energy


def rhs(t, y, damping=1.0, drive=0.0, drive_until=None, *, omit_bias=False):
    t = scalar(t, "time")
    y = vector(y, 6, "state")
    damping, drive, drive_until = parameters(damping, drive, drive_until)
    state, bias, _ = mechanical(y[:2], y[2:4])
    v = y[2:4]
    applied = force(t, drive, drive_until)
    resistance = damping * DAMPING @ v
    acceleration = np.linalg.solve(
        state["mass_matrix"],
        applied - resistance - STIFFNESS @ (y[:2] - Q0) - (0 if omit_bias else bias),
    )
    return np.r_[v, acceleration, applied @ v, v @ resistance]


def simulate(
    *,
    duration=2.0,
    dt=0.01,
    damping=1.0,
    drive=0.0,
    drive_until=None,
    initial=None,
    omit_bias=False,
):
    duration, dt = scalar(duration, "duration"), scalar(dt, "dt")
    parameters(damping, drive, drive_until)
    if not 0 < duration <= 10 or not 0 < dt <= 0.1:
        raise ValueError("duration in (0,10], dt in (0,.1] required")
    steps = round(duration / dt)
    if steps < 1 or steps > 10000 or not math.isclose(steps * dt, duration, abs_tol=1e-12):
        raise ValueError("duration must contain 1..10000 complete steps")
    y = (
        np.r_[Q0 + (0.02, -0.03), 0.01, 0.02, 0.0, 0.0]
        if initial is None
        else vector(initial, 6, "initial")
    )
    if np.any(y[4:] != 0):
        raise ValueError("initial work and loss must be zero")
    _, _, initial_energy = mechanical(y[:2], y[2:4])
    residuals, energies, samples, trace = [], [], [], []
    minimum, maximum = y[:2].copy(), y[:2].copy()

    def evaluate(t, value):
        return rhs(t, value, damping, drive, drive_until, omit_bias=omit_bias)

    for step in range(steps + 1):
        t = step * dt
        state, _, energy = mechanical(y[:2], y[2:4])
        energies.append(energy)
        residuals.append(energy - initial_energy - y[4] + y[5])
        kinetic = float(y[2:4] @ state["mass_matrix"] @ y[2:4] / 2)
        trace.append(
            dict(
                time_s=t,
                q=y[:2].tolist(),
                rates=y[2:4].tolist(),
                kinetic_j=kinetic,
                potential_j=energy - kinetic,
                energy_j=energy,
                work_j=float(y[4]),
                loss_j=float(y[5]),
                residual_j=float(residuals[-1]),
            )
        )
        minimum, maximum = np.minimum(minimum, y[:2]), np.maximum(maximum, y[:2])
        if step % max(1, steps // 8) == 0 or step == steps:
            samples.append(
                dict(
                    time_s=t,
                    q=y[:2].tolist(),
                    rates=y[2:4].tolist(),
                    energy_j=energy,
                    work_j=float(y[4]),
                    loss_j=float(y[5]),
                    positions_m=state["position"].tolist(),
                )
            )
        if step == steps:
            break
        a = evaluate(t, y)
        b = evaluate(t + dt / 2, y + dt * a / 2)
        c = evaluate(t + dt / 2, y + dt * b / 2)
        d = evaluate(t + dt, y + dt * c)
        y = y + dt * (a + 2 * b + 2 * c + d) / 6
    return dict(
        duration_s=duration,
        dt_s=dt,
        steps=steps,
        damping_factor=damping,
        drive_factor=drive,
        drive_until_s=drive_until,
        omitted_inertial_bias=omit_bias,
        final_state=y.tolist(),
        initial_energy_j=initial_energy,
        final_energy_j=energies[-1],
        maximum_balance_residual_j=float(np.max(np.abs(residuals))),
        maximum_energy_step_increase_j=float(max(np.diff(energies))),
        q_min=minimum.tolist(),
        q_max=maximum.tolist(),
        extrema_scope="accepted endpoint extrema; RK derivative stages also domain-checked",
        samples=samples,
        trace=trace,
    )


def energy_identity_control():
    q, v = Q0 + (0.04, -0.06), np.array((0.12, -0.2))
    y = np.r_[q, v, 0.0, 0.0]
    derivative = rhs(0.37, y, 0.8, 1.0)
    eps = 1e-6
    plus = mechanical(q + eps * v, v + eps * derivative[2:4])[2]
    minus = mechanical(q - eps * v, v - eps * derivative[2:4])[2]
    measured = (plus - minus) / (2 * eps)
    predicted = derivative[4] - derivative[5]
    wrong = rhs(0.37, y, 0.8, 1.0, omit_bias=True)
    wrong_derivative = (
        mechanical(q + eps * v, v + eps * wrong[2:4])[2]
        - mechanical(q - eps * v, v - eps * wrong[2:4])[2]
    ) / (2 * eps)
    return dict(
        finite_difference_step_s=eps,
        directional_energy_rate_j_s=measured,
        expected_power_j_s=float(predicted),
        absolute_error_j_s=abs(measured - predicted),
        omitted_bias_absolute_error_j_s=abs(wrong_derivative - predicted),
    )


def report():
    cases = {}
    settings = dict(
        equilibrium=dict(initial=np.r_[Q0, 0.0, 0.0, 0.0, 0.0]),
        conservative=dict(damping=0),
        damped=dict(),
        driven=dict(drive=1),
        drive_off=dict(drive=1, drive_until=1),
        omitted_bias_control=dict(damping=0, omit_bias=True),
    )
    refinements = []
    for name, kwargs in settings.items():
        runs = [simulate(dt=dt, **kwargs) for dt in (0.02, 0.01, 0.005)]
        cases[name] = runs[-1]
        if name not in ("driven", "drive_off"):
            cases[name].pop("trace")
        differences = [
            np.abs(np.array(runs[i]["final_state"][:4]) - runs[i + 1]["final_state"][:4]).tolist()
            for i in (0, 1)
        ]
        refinements.append(
            dict(
                case=name,
                step_sizes_s=[0.02, 0.01, 0.005],
                successive_final_state_absolute_differences=differences,
                difference_columns=[
                    "scale",
                    "angle_rad",
                    "scale_rate_per_s",
                    "angle_rate_rad_per_s",
                ],
                balance_residuals_j=[r["maximum_balance_residual_j"] for r in runs],
            )
        )
    root = Path(__file__).resolve().parent
    hashes = {
        name: hashlib.sha256((root / name).read_text(encoding="utf-8").encode()).hexdigest()
        for name in ("report_fold_dynamics.py", "report_fold_kinematics.py")
    }
    return dict(
        schema_version=1,
        source_sha256_normalized_text=hashes,
        body_ids=kinematics(Q0)["ids"],
        equilibrium=Q0.tolist(),
        stiffness=STIFFNESS.tolist(),
        damping=DAMPING.tolist(),
        force_formula="drive * envelope * [1e-4 sin(2t), 4e-5 cos(2t)]",
        shutoff_envelope="sin(pi*t/drive_until)^2 before shutoff; zero thereafter",
        units=dict(
            time="s",
            scale="dimensionless",
            angle="rad",
            energy="J",
            scale_force="J per unit scale",
            angle_force="J/rad",
            stiffness="J/(coordinate_a coordinate_b)",
            damping="J s/(coordinate_a coordinate_b)",
        ),
        physical_calibration=False,
        autonomous_breathing=False,
        collision_scope="stage coordinates checked inside admitted rectangle; no between-stage collision certificate",
        limitations=[
            "synthetic point masses and quadratic restoring law",
            "no recursive whole-assembly coupling",
            "no material strain law or rotational body inertia",
            "no invented time-energy source",
        ],
        energy_identity=energy_identity_control(),
        cases=cases,
        refinements=refinements,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report(), indent=2, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
