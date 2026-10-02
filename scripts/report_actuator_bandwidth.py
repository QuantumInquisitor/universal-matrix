"""Run bounded synthetic actuator lag comparisons, preserving legacy wave sources."""

# ruff: noqa: E402
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.proposed_actuator_bandwidth import actuator_bandwidth_trace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()
    cases = {}
    for tau in (0.0, 0.1, 0.5, 2.0):
        runs = [
            actuator_bandwidth_trace(actuator_time_constant_s=tau, steps_per_period=n)
            for n in (256, 512)
        ]
        coarse, fine = runs
        difference = float(
            np.max(np.abs(np.array(coarse["states"]) - np.array(fine["states"])[::2]))
        )
        # Reproduction controls, not a calibrated hardware/stability threshold.
        assert difference < 1e-5
        assert abs(coarse["late_position_rms_m"] - fine["late_position_rms_m"]) < 1e-5
        assert coarse["meets_declared_tracking_target"] == fine["meets_declared_tracking_target"]
        assert max(r["max_energy_balance_residual_per_mass"] for r in runs) < 1e-5
        cases[str(tau)] = {
            "coarse": coarse,
            "refined": fine,
            "maximum_state_refinement_difference": difference,
        }
        print(
            tau, coarse["late_position_rms_m"], fine["late_position_rms_m"], difference, flush=True
        )
    assert cases["0.0"]["coarse"]["meets_declared_tracking_target"]
    paths = [
        ROOT / "src/proposed_actuator_bandwidth.py",
        ROOT / "src/proposed_mode_pair_control.py",
        ROOT / "src/proposed_scalar_wave_control.py",
        Path(__file__),
    ]
    payload = {
        "cases": cases,
        "source_sha256": {
            p.relative_to(ROOT).as_posix(): hashlib.sha256(
                p.read_text(encoding="utf-8").encode("utf-8")
            ).hexdigest()
            for p in paths
        },
        "source_hash_convention": "UTF-8 text with universal newlines normalized to LF",
        "scope": "Ideal instantaneous measurements, unit stiffness, synthetic first-order force actuator; unchanged 20 period/final 5 period/0.05 m criterion; no calibrated hardware or electrical energy claim.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if args.summary:
        fields = (
            "parameters",
            "late_position_rms_m",
            "diagnostic_limit_m",
            "meets_declared_tracking_target",
            "max_energy_balance_residual_per_mass",
            "maximum_sampled_force_per_mass",
            "sampled_command_clipping_fraction",
            "sampled_applied_force_saturation_fraction",
            "startup",
        )
        summary = {key: value for key, value in payload.items() if key != "cases"}
        summary["cases"] = {
            name: {
                "maximum_state_refinement_difference": case["maximum_state_refinement_difference"],
                **{
                    resolution: {key: case[resolution][key] for key in fields}
                    for resolution in ("coarse", "refined")
                },
            }
            for name, case in cases.items()
        }
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
