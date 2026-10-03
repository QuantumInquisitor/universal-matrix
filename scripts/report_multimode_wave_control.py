"""Reproduce bounded two-mode wave competition controls."""
# ruff: noqa: E402

import argparse
import hashlib
import json
import math
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.proposed_multimode_wave_control import multimode_trace
from src.proposed_scalar_wave_control import RingMode


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts" / "waves")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    mode = RingMode(2 * math.pi, 1, 1, 0, 0.02, 0.2, 2)
    cases = {}
    specifications = {
        "projected_coupling": {},
        "independent_comparison": {"coupling": 0},
        "rotated_seed": {"initial": (-0.007, 0.01, 0, 0)},
        "one_mode_seed": {"initial": (0.01, 0, 0, 0)},
        "refinement": {"steps_per_period": 64, "rtol": 1e-11, "atol": 1e-13},
        "longer": {"periods": 800},
        "weaker_nonlinearity": {"alpha": 2 / 3},
        "no_pump": {},
    }
    for name, options in specifications.items():
        case_mode = RingMode(2 * math.pi, 1, 1, 0, 0.02, 0, 2) if name == "no_pump" else mode
        result = multimode_trace(case_mode, **options)
        cases[name] = dict(
            parameters=dict(mode=asdict(case_mode), overrides=options), result=result
        )
        print(
            name,
            result["modal_state_rms_m"],
            "energy residual",
            result["max_energy_balance_residual"],
            flush=True,
        )
    base = np.array(cases["projected_coupling"]["result"]["final_state"])
    comparisons = {
        name: float(np.linalg.norm(np.array(cases[name]["result"]["final_state"]) - base))
        for name in ("refinement", "longer")
    }
    payload = dict(
        cases=cases,
        final_state_difference=comparisons,
        source_sha256={
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (ROOT / "src/proposed_multimode_wave_control.py", Path(__file__))
        },
        limitations="Finite two-mode truncation; omitted third harmonics, no calibrated material coupling or time-crystal evidence.",
    )
    (args.output / "multimode-wave-control.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    print("final-state differences", comparisons, flush=True)


if __name__ == "__main__":
    main()
