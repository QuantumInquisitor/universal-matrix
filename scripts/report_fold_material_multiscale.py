"""Reproduce unequal-size passive material graph controls."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .fold_material_multiscale import comparison, scaled_material, simulate
    from .report_fold_constitutive import constitutive
    from .report_fold_dynamics import Q0
except ImportError:
    from fold_material_multiscale import comparison, scaled_material, simulate
    from report_fold_constitutive import constitutive
    from report_fold_dynamics import Q0


def compact(run):
    result = {k: v for k, v in run.items() if k != "trace"}
    trace = run["trace"]
    result["samples"] = trace[:: max(1, (len(trace) - 1) // 8)]
    if result["samples"][-1] is not trace[-1]:
        result["samples"].append(trace[-1])
    return result


def report():
    base = simulate()
    half = simulate(0.5)
    fine = simulate(0.5, refinement=2)
    broken = simulate(broken_edge=1)
    q = Q0 + (0.02, -0.03)
    original = scaled_material(q)
    scaled = scaled_material(q, 0.5)
    fixed = constitutive(q, length_m=0.05, thickness_m=1e-4, bridge_ea_n=0.1)
    cases = {
        name: compact(run)
        for name, run in {
            "reference": base,
            "half": half,
            "fine_half": fine,
            "broken_edge": broken,
        }.items()
    }
    root = Path(__file__).resolve().parent
    names = [
        "report_fold_material_multiscale.py",
        "fold_material_multiscale.py",
        "report_fold_constitutive.py",
        "report_fold_multiscale.py",
        "report_fold_scaling.py",
        "report_fold_mapped.py",
        "report_fold_hierarchy.py",
        "report_fold_network.py",
        "report_fold_coupling.py",
        "report_fold_reservoir.py",
        "report_fold_dynamics.py",
        "report_fold_kinematics.py",
    ]
    return {
        "schema": "fold-material-multiscale-v1",
        "sources": {
            n: hashlib.sha256((root / n).read_text(encoding="utf-8").encode()).hexdigest()
            for n in names
        },
        "size_laws": {
            "length": "a",
            "thickness": "a",
            "bridge_EA": "a^2",
            "mass": "a^3",
            "generalized_inertia": "a^5",
            "potential": "a^3",
            "damping": "a^4",
            "similarity_time": "a",
        },
        "cases": cases,
        "similarity": comparison(half, base),
        "refinement": {
            "final_state_absolute_differences": np.abs(
                np.array(half["final_state"]) - fine["final_state"]
            ).tolist(),
            "coarse_group_residuals_j": half["max_group_residual_j"],
            "fine_group_residuals_j": fine["max_group_residual_j"],
        },
        "scaling_control": {
            "q": q.tolist(),
            "scale": 0.5,
            "energy_a3_absolute_error_j": abs(
                scaled["total_energy_j"] - 0.5**3 * original["total_energy_j"]
            ),
            "gradient_a3_absolute_error": np.abs(
                np.array(scaled["gradient"]) - 0.5**3 * np.array(original["gradient"])
            ).tolist(),
            "fixed_thickness_and_EA_energy_discrepancy_j": abs(
                fixed["total_energy_j"] - 0.5**3 * original["total_energy_j"]
            ),
        },
        "physical_calibration": False,
        "active_supply": False,
        "stable_breathing": False,
        "limitations": [
            "Conditional full geometric scaling, not fixed-thickness fabrication",
            "Point-mass inertia; no distributed rotational inertia",
            "Four passive reduced modules; no whole-flow or XR mapping",
            "Mapped connectors lack spatial collision and joint validation",
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
