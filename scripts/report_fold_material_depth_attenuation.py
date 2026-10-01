"""Measure root backreaction versus recursive depth and observation duration."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .report_fold_material_depth3 import root_state, simulate
except ImportError:
    from report_fold_material_depth3 import root_state, simulate


DURATIONS_S = (0.005, 0.01, 0.02, 0.04, 0.05)
DEPTHS = (0, 1, 2, 3)
RESOLUTION = 1e-12


def root_difference(deeper, shallower):
    return np.abs(root_state(deeper) - root_state(shallower))


def report():
    runs = {}
    rows = []
    for duration in DURATIONS_S:
        depth_runs = {depth: simulate(depth, duration=duration) for depth in DEPTHS}
        runs[str(duration)] = {
            f"depth_{depth}": {
                key: value
                for key, value in run.items()
                if key not in ("initial_state", "final_state")
            }
            for depth, run in depth_runs.items()
        }
        transitions = {}
        for depth in (1, 2, 3):
            delta = root_difference(depth_runs[depth], depth_runs[depth - 1])
            transitions[f"{depth - 1}_to_{depth}"] = {
                "root_absolute_state_change": delta.tolist(),
                "maximum_root_absolute_state_change": float(np.max(delta)),
                "resolved": bool(np.max(delta) > RESOLUTION),
            }
        rows.append(
            {
                "duration_s": duration,
                "transitions": transitions,
            }
        )

    summary = {}
    baseline = max(
        row["transitions"]["0_to_1"]["maximum_root_absolute_state_change"] for row in rows
    )
    for name in ("0_to_1", "1_to_2", "2_to_3"):
        values = [row["transitions"][name]["maximum_root_absolute_state_change"] for row in rows]
        first = next(
            (
                row["duration_s"]
                for row in rows
                if row["transitions"][name]["resolved"]
            ),
            None,
        )
        summary[name] = {
            "maximum_over_duration_grid": max(values),
            "first_resolved_duration_s": first,
            "relative_to_depth_0_to_1_maximum": None
            if baseline == 0
            else max(values) / baseline,
        }

    disconnected = simulate(3, connected=False, duration=max(DURATIONS_S))
    single = simulate(0, duration=max(DURATIONS_S))
    disconnected_delta = root_difference(disconnected, single)

    return {
        "schema": 1,
        "scope": (
            "bounded passive root-backreaction sweep through depth 3 under the unchanged "
            "half-scale material and mapped-connector laws"
        ),
        "resolution_threshold": RESOLUTION,
        "durations_s": DURATIONS_S,
        "depths": DEPTHS,
        "rows": rows,
        "summary": summary,
        "disconnected_control": {
            "duration_s": max(DURATIONS_S),
            "root_absolute_state_change": disconnected_delta.tolist(),
            "maximum_root_absolute_state_change": float(np.max(disconnected_delta)),
        },
        "energy_accounts": runs,
        "sources": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in (
                "report_fold_material_depth_attenuation.py",
                "report_fold_material_depth3.py",
                "report_fold_scale_extension.py",
                "report_fold_constitutive.py",
                "report_fold_mapped.py",
            )
        },
        "connector_law_changed": False,
        "material_scaling_law_changed": False,
        "threshold_tuned_to_result": False,
        "arbitrary_depth_validated": False,
        "infinite_depth_limit_validated": False,
        "macroscopic_deep_backreaction_claimed": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
