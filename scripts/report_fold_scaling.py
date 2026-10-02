"""Conditional homothetic scaling of the synthetic 22-point fold model."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .report_fold_dynamics import DAMPING, Q0, STIFFNESS, vector
    from .report_fold_dynamics import simulate as reference_simulate
    from .report_fold_kinematics import inventory, kinematics, scalar
except ImportError:
    from report_fold_dynamics import DAMPING, Q0, STIFFNESS, vector
    from report_fold_dynamics import simulate as reference_simulate
    from report_fold_kinematics import inventory, kinematics, scalar


def scale_value(value):
    value = scalar(value, "length scale")
    if not 0.25 <= value <= 1:
        raise ValueError("length scale outside [.25,1]")
    return value


def scaled_mechanical(q, velocity, scale=1.0):
    scale = scale_value(scale)
    masses = {name: mass * scale**3 for name, _, mass in inventory()}
    state = kinematics(q, length_m=0.1 * scale, masses=masses)
    v = vector(velocity, 2, "velocity")
    if np.max(np.abs(v)) > 1e6:
        raise ValueError("velocity outside numerical scope")
    hvv = np.einsum("nxab,a,b->nx", state["hessian"], v, v)
    bias = np.einsum("n,nxa,nx->a", state["mass"], state["jacobian"], hvv)
    delta = np.asarray(q) - Q0
    potential = float(scale**3 * delta @ STIFFNESS @ delta / 2)
    kinetic = float(v @ state["mass_matrix"] @ v / 2)
    return state, bias, kinetic + potential


def rhs(y, scale=1.0, *, wrong_inertia=False):
    scale = scale_value(scale)
    y = vector(y, 5, "scaled state")
    state, bias, _ = scaled_mechanical(y[:2], y[2:4], scale)
    v = y[2:4]
    resistance = scale**4 * DAMPING @ v
    mass = state["mass_matrix"] / (scale**2 if wrong_inertia else 1)
    acceleration = np.linalg.solve(mass, -(scale**3) * STIFFNESS @ (y[:2] - Q0) - resistance - bias)
    return np.r_[v, acceleration, v @ resistance]


def simulate(scale=1.0, *, wrong_inertia=False):
    scale = scale_value(scale)
    dt = 0.02 * scale
    y = np.r_[Q0 + (0.02, -0.03), np.array((0.01, 0.02)) / scale, 0.0]
    initial = y.tolist()
    initial_energy = scaled_mechanical(y[:2], y[2:4], scale)[2]
    trace = []
    for step in range(101):
        derivative = rhs(y, scale, wrong_inertia=wrong_inertia)
        energy = scaled_mechanical(y[:2], y[2:4], scale)[2]
        trace.append(
            dict(
                time_s=step * dt,
                reference_time_s=step * 0.02,
                q=y[:2].tolist(),
                rates=y[2:4].tolist(),
                mechanical_j=energy,
                loss_j=float(y[4]),
                residual_j=float(energy - initial_energy + y[4]),
            )
        )
        if step == 100:
            break
        a = derivative
        b = rhs(y + dt * a / 2, scale, wrong_inertia=wrong_inertia)
        c = rhs(y + dt * b / 2, scale, wrong_inertia=wrong_inertia)
        d = rhs(y + dt * c, scale, wrong_inertia=wrong_inertia)
        y = y + dt * (a + 2 * b + 2 * c + d) / 6
    return dict(
        length_scale=scale,
        duration_s=2 * scale,
        dt_s=dt,
        initial_state=initial,
        wrong_inertia=wrong_inertia,
        max_balance_residual_j=max(abs(t["residual_j"]) for t in trace),
        trace=trace,
    )


def point_inertia(state):
    # Point-mass angular inertia about the scaled coordinate origin, not solid-body inertia.
    x, m = state["position"], state["mass"]
    return sum(m[i] * (np.dot(p, p) * np.eye(3) - np.outer(p, p)) for i, p in enumerate(x))


def report():
    q, v = Q0 + (0.03, -0.04), np.array((0.12, -0.15))
    base, bias0, _ = scaled_mechanical(q, v)
    reference = reference_simulate(duration=2, dt=0.02)
    reference_q = np.array([t["q"] for t in reference["trace"]])
    reference_v = np.array([t["rates"] for t in reference["trace"]])
    reference_energy = np.array([t["energy_j"] for t in reference["trace"]])
    cases = []
    for scale in (1.0, 0.5, 0.25):
        state, bias, _ = scaled_mechanical(q, v, scale)
        run = simulate(scale)
        traces = run.pop("trace")
        run["samples"] = traces[::20]
        run["scaling_checks"] = dict(
            total_mass_kg=float(sum(state["mass"])),
            position_error_m=float(np.max(np.abs(state["position"] - scale * base["position"]))),
            mass_matrix_relative_error=float(
                np.max(np.abs(state["mass_matrix"] / scale**5 - base["mass_matrix"]))
                / np.max(abs(base["mass_matrix"]))
            ),
            bias_relative_error=float(np.max(np.abs(bias / scale**5 - bias0)) / np.max(abs(bias0))),
            point_inertia_relative_error=float(
                np.max(np.abs(point_inertia(state) / scale**5 - point_inertia(base)))
                / np.max(abs(point_inertia(base)))
            ),
        )
        run["similarity_checks"] = dict(
            coordinate_max_differences=np.max(
                np.abs(np.array([t["q"] for t in traces]) - reference_q), axis=0
            ).tolist(),
            reference_rate_max_differences=np.max(
                np.abs(scale * np.array([t["rates"] for t in traces]) - reference_v), axis=0
            ).tolist(),
            energy_max_difference_j=float(
                np.max(
                    np.abs(
                        np.array([t["mechanical_j"] for t in traces]) / scale**3 - reference_energy
                    )
                )
            ),
        )
        cases.append(run)
    bad = simulate(0.5, wrong_inertia=True)
    bad["samples"] = bad.pop("trace")[::20]
    return dict(
        schema=1,
        scope="Synthetic homothetic point-mass hypothesis; fixed density and strain-energy-density assumptions, chosen damping similarity",
        assumptions=dict(
            length_exponent=1,
            mass_exponent=3,
            generalized_inertia_exponent=5,
            potential_exponent=3,
            damping_exponent=4,
            time_exponent=1,
        ),
        sources={
            name: hashlib.sha256(
                Path(__file__).with_name(name).read_text(encoding="utf-8").encode()
            ).hexdigest()
            for name in (
                "report_fold_scaling.py",
                "report_fold_dynamics.py",
                "report_fold_kinematics.py",
            )
        },
        cases=cases,
        wrong_inertia_control=bad,
        calibrated_material=False,
        scaled_connector_integrated=False,
        recursive_assembly_validated=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            dict(
                cases=[c["max_balance_residual_j"] for c in result["cases"]],
                wrong=result["wrong_inertia_control"]["max_balance_residual_j"],
            )
        )
    )
