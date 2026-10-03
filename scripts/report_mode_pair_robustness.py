"""Run ten robustness cases and delayed-failure refinement; no stability theorem."""

# ruff: noqa: E402
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.proposed_mode_pair_control import mode_pair_trace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    cases = {}
    for label, parameters in (
        ("ideal", {}),
        ("force_0.05", {"force_limit": 0.05}),
        ("delay_0.1", {"delay_s": 0.1}),
        ("delay_1", {"delay_s": 1}),
        ("delay_2", {"delay_s": 2}),
        ("delay_2_refined", {"delay_s": 2, "steps_per_period": 512}),
        ("measurement_0.02", {"measurement_amplitude": 0.02}),
        ("stiffness_1.2", {"stiffness_ratio": 1.2}),
        ("stiffness_1.02", {"stiffness_ratio": 1.02}),
        ("stiffness_1.05", {"stiffness_ratio": 1.05}),
        (
            "combined",
            {
                "force_limit": 0.15,
                "delay_s": 0.1,
                "measurement_amplitude": 0.02,
                "stiffness_ratio": 1.2,
            },
        ),
    ):
        cases[label] = mode_pair_trace(**parameters)
        args.output.write_text(json.dumps(cases, indent=2))
        print(label, cases[label]["late_position_rms_m"], flush=True)


if __name__ == "__main__":
    main()
