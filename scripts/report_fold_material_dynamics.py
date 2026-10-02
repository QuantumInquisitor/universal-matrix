"""Reproducible bounded dynamics with the geometry-derived material potential."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .report_fold_dynamics import Q0, energy_identity_control, simulate
except ImportError:
    from report_fold_dynamics import Q0, energy_identity_control, simulate


def report():
    settings = {
        "equilibrium": dict(initial=np.r_[Q0, 0.0, 0.0, 0.0, 0.0]),
        "conservative": dict(damping=0),
        "passive": dict(),
        "driven": dict(drive=1),
        "drive_off": dict(drive=1, drive_until=0.2),
    }
    cases, refinements = {}, {}
    for name, kwargs in settings.items():
        runs = [
            simulate(duration=0.4, dt=dt, potential="constitutive", **kwargs)
            for dt in (0.01, 0.005, 0.0025)
        ]
        cases[name] = runs[-1]
        refinements[name] = {
            "step_sizes_s": [r["dt_s"] for r in runs],
            "balance_residuals_j": [r["maximum_balance_residual_j"] for r in runs],
            "successive_final_state_differences": [
                np.abs(np.array(a["final_state"]) - b["final_state"]).tolist()
                for a, b in zip(runs, runs[1:], strict=False)
            ],
            "columns": [
                "scale",
                "angle_rad",
                "scale_rate_per_s",
                "angle_rate_rad_per_s",
                "work_j",
                "loss_j",
            ],
        }
    root = Path(__file__).resolve().parent
    names = [
        "report_fold_material_dynamics.py",
        "report_fold_dynamics.py",
        "report_fold_constitutive.py",
        "report_fold_kinematics.py",
    ]
    return {
        "schema": "fold-material-dynamics-v1",
        "sources": {
            n: hashlib.sha256((root / n).read_text(encoding="utf-8").encode()).hexdigest()
            for n in names
        },
        "potential": "constitutive",
        "parameters": {
            "young_pa": 1000,
            "poisson": 0.3,
            "thickness_m": 1e-4,
            "bridge_ea_n": 0.1,
            "length_m": 0.1,
        },
        "energy_account": "kinetic + constitutive - initial - applied_work + damping_loss = 0",
        "energy_identity": energy_identity_control(potential="constitutive"),
        "cases": cases,
        "refinements": refinements,
        "physical_calibration": False,
        "stable_breathing_established": False,
        "limitations": [
            "22 point-mass owners; no distributed rotational inertia",
            "six membrane and twelve axial energies; four hubs have no material law",
            "prescribed external force; no finite power supply coupled here",
            "short bounded controls; no continuous collision certificate",
            "separate 69-domain flow assembly and XR integration remain open",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report(), indent=2, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
