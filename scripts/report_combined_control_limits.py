"""Bounded lag/delay composition; preserves the original tracking criterion."""

# ruff: noqa: E402
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.proposed_combined_control_limits import combined_control_trace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    cases = []
    for tau, delay, limit in [
        (0, 0, 10),
        (0.1, 0, 10),
        (0, 0.2, 10),
        (0.1, 0.2, 10),
        (0.5, 0.2, 10),
        (0.5, 1, 10),
        (0.5, 0.2, 0.05),
    ]:
        runs = [
            combined_control_trace(
                actuator_time_constant_s=tau, delay_s=delay, force_limit=limit, steps_per_period=n
            )
            for n in (256, 512, 1024)
        ]
        differences = [
            float(np.max(np.abs(np.array(a["states"]) - np.array(b["states"])[::2])))
            for a, b in zip(runs, runs[1:], strict=False)
        ]
        fields = (
            "parameters",
            "late_position_rms_m",
            "meets_declared_tracking_target",
            "diagnostic_limit_m",
            "max_energy_balance_residual_per_mass",
            "maximum_sampled_force_per_mass",
            "sampled_command_clipping_fraction",
        )
        cases.append(
            dict(
                runs=[{key: r[key] for key in fields} for r in runs],
                maximum_state_refinement_differences=differences,
            )
        )
        print(tau, delay, limit, [r["late_position_rms_m"] for r in runs], differences, flush=True)
    paths = [
        Path(__file__),
        ROOT / "src/proposed_combined_control_limits.py",
        ROOT / "src/proposed_mode_pair_control.py",
        ROOT / "src/proposed_scalar_wave_control.py",
    ]
    result = dict(
        cases=cases,
        source_sha256={
            p.relative_to(ROOT).as_posix(): hashlib.sha256(
                p.read_text(encoding="utf-8").encode("utf-8")
            ).hexdigest()
            for p in paths
        },
        source_hash_convention="UTF-8 normalized LF text",
        scope="Synthetic prescribed active tracking; 20 periods, final 5 periods RMS <=0.05 m; no stability-boundary or calibrated hardware claim. Mechanical energy per unit modal mass only.",
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
