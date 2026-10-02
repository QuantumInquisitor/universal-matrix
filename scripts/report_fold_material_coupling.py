"""Material-law reservoir and two-module energy ownership controls."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .report_fold_coupling import simulate as pair
    from .report_fold_reservoir import simulate as single
except ImportError:
    from report_fold_coupling import simulate as pair
    from report_fold_reservoir import simulate as single


def compact(run):
    trace = run.pop("trace")
    run["samples"] = trace[:: max(1, (len(trace) - 1) // 8)]
    if run["samples"][-1] is not trace[-1]:
        run["samples"].append(trace[-1])
    return run


def report():
    duration = 0.4
    cases, refinements = {}, {}
    for name, options in {
        "fueled_pair": {},
        "conservative_pair": dict(fueled=False, gain=0, damping=0, leakage=0),
        "disconnected_pair": dict(coupling=0),
    }.items():
        runs = [
            pair(duration=duration, dt=dt, potential="constitutive", **options)
            for dt in (0.02, 0.01)
        ]
        refinements[name] = {
            "dt_s": [0.02, 0.01],
            "total_residuals_j": [r["max_total_residual_j"] for r in runs],
            "final_state_absolute_differences": np.abs(
                np.array(runs[0]["final_state"]) - runs[1]["final_state"]
            ).tolist(),
        }
        cases[name] = compact(runs[-1])
    cases["wrong_reaction"] = compact(
        pair(duration=duration, dt=0.01, potential="constitutive", wrong_reaction=True)
    )
    reservoir = {
        name: compact(single(duration=duration, dt=0.01, potential="constitutive", **options))
        for name, options in {
            "fueled": {},
            "empty": dict(reserve=0),
            "omitted_debit": dict(omit_debit=True),
        }.items()
    }
    difference = np.abs(
        np.array(cases["disconnected_pair"]["final_state"][:9]) - reservoir["fueled"]["final_state"]
    )
    root = Path(__file__).resolve().parent
    names = [
        "report_fold_material_coupling.py",
        "report_fold_coupling.py",
        "report_fold_reservoir.py",
        "report_fold_dynamics.py",
        "report_fold_constitutive.py",
        "report_fold_kinematics.py",
    ]
    return {
        "schema": "fold-material-coupling-v1",
        "sources": {
            n: hashlib.sha256((root / n).read_text(encoding="utf-8").encode()).hexdigest()
            for n in names
        },
        "potential": "constitutive",
        "cases": cases,
        "reservoir": reservoir,
        "refinements": refinements,
        "disconnected_single_maximum_state_difference": float(max(difference)),
        "ownership": "Each module owns kinetic/material/reservoir energy; the connector owns one spring energy. Delivered work is transfer, not additional storage. Damping, conversion and leakage are separate losses.",
        "physical_calibration": False,
        "sustained_breathing": False,
        "limitations": [
            "Two equal-size abstract modules, not full-structure recursion",
            "Synthetic generalized connector, not validated spatial joint/contact",
            "Finite internal reserve, no replenishing external power supply",
            "Other network/scaled models retain quadratic defaults",
            "No full-flow or XR integration",
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
