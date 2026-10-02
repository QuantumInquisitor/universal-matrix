"""Independent small-amplitude normal-mode reference for the reduced fold model."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

try:
    from .report_fold_dynamics import Q0, STIFFNESS, simulate
    from .report_fold_kinematics import kinematics, scalar
except ImportError:
    from report_fold_dynamics import Q0, STIFFNESS, simulate
    from report_fold_kinematics import kinematics, scalar


def linear_modes():
    mass = kinematics(Q0)["mass_matrix"]
    eigenmass, basis = np.linalg.eigh(mass)
    inverse_root = (basis / np.sqrt(eigenmass)) @ basis.T
    omega_squared, vectors = np.linalg.eigh(inverse_root @ STIFFNESS @ inverse_root)
    shapes = inverse_root @ vectors
    # Coordinate normalization, not a physical norm across unlike coordinates.
    shapes /= np.max(np.abs(shapes), axis=0)
    return mass, np.sqrt(omega_squared), shapes


def compare(mode, amplitude, duration=10.0, dt=0.01):
    if type(mode) is not int or mode not in (0, 1):
        raise ValueError("mode must be 0 or 1")
    amplitude = scalar(amplitude, "amplitude")
    if not 0 < amplitude <= 0.02:
        raise ValueError("amplitude must be finite and in (0,.02]")
    mass, omega, shapes = linear_modes()
    shape = shapes[:, mode]
    run = simulate(
        duration=duration,
        dt=dt,
        damping=0,
        initial=np.r_[Q0 + amplitude * shape, 0.0, 0.0, 0.0, 0.0],
    )
    times = np.array([r["time_s"] for r in run["trace"]])
    positions = np.array([r["q"] for r in run["trace"]])
    rates = np.array([r["rates"] for r in run["trace"]])
    reference = Q0 + amplitude * np.cos(omega[mode] * times)[:, None] * shape
    reference_rates = -amplitude * omega[mode] * np.sin(omega[mode] * times)[:, None] * shape
    return {
        "mode": mode,
        "amplitude_parameter": amplitude,
        "duration_s": duration,
        "dt_s": dt,
        "angular_frequency_rad_per_s": float(omega[mode]),
        "frequency_hz": float(omega[mode] / math.tau),
        "mode_shape_scale_and_angle_rad": shape.tolist(),
        "max_scale_error": float(np.max(np.abs(positions[:, 0] - reference[:, 0]))),
        "max_angle_error_rad": float(np.max(np.abs(positions[:, 1] - reference[:, 1]))),
        "max_scale_rate_error_per_s": float(np.max(np.abs(rates[:, 0] - reference_rates[:, 0]))),
        "max_angle_rate_error_rad_per_s": float(
            np.max(np.abs(rates[:, 1] - reference_rates[:, 1]))
        ),
        "maximum_balance_residual_j": run["maximum_balance_residual_j"],
        "final_state": run["final_state"],
        "eigen_residual_components": (STIFFNESS @ shape - omega[mode] ** 2 * mass @ shape).tolist(),
    }


def report():
    mass, omega, shapes = linear_modes()
    cases = [compare(mode, amplitude) for mode in (0, 1) for amplitude in (0.02, 0.01, 0.005)]
    fine = compare(0, 0.01, dt=0.005)
    normal = next(c for c in cases if c["mode"] == 0 and c["amplitude_parameter"] == 0.01)
    return {
        "schema": 1,
        "scope": "Linearized normal modes of synthetic reduced mechanics; not measured material resonances",
        "sources": {
            name: hashlib.sha256(
                Path(__file__).with_name(name).read_text(encoding="utf-8").encode()
            ).hexdigest()
            for name in (
                "report_fold_modes.py",
                "report_fold_dynamics.py",
                "report_fold_kinematics.py",
            )
        },
        "mass_at_equilibrium": mass.tolist(),
        "frequencies_hz": (omega / math.tau).tolist(),
        "mode_shapes_columns": shapes.tolist(),
        "normalization": "Largest numerical coordinate component = 1; components retain scale and radian meanings, no combined physical norm",
        "cases": cases,
        "step_refinement": {
            "mode": 0,
            "amplitude": 0.01,
            "dt_s": [0.01, 0.005],
            "final_coordinate_absolute_differences": np.abs(
                np.array(fine["final_state"][:4]) - normal["final_state"][:4]
            ).tolist(),
            "columns": ["scale", "angle_rad", "scale_rate_per_s", "angle_rate_rad_per_s"],
        },
        "limits": [
            "two-coordinate linearization only",
            "finite 10 second window",
            "no full solid or measured resonance validation",
            "no sustained autonomous breathing claim",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = report()
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "frequencies_hz": result["frequencies_hz"],
                "step_refinement": result["step_refinement"],
            }
        )
    )
