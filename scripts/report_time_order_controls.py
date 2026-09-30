"""Reproduce finite-record time-order and nonlinear standing-wave controls."""

# ruff: noqa: E402
import argparse
import hashlib
import json
import math
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.proposed_nonlinear_wave_control import nonlinear_trace
from src.proposed_scalar_wave_control import RingMode
from src.time_order_diagnostics import stroboscopic_diagnostics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--plot-only", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.plot_only:
        render(json.loads((args.output / "time-order-controls.json").read_text()), args.output)
        return
    source_names = (
        "proposed_nonlinear_wave_control.py",
        "proposed_scalar_wave_control.py",
        "time_order_diagnostics.py",
    )
    report = dict(
        scope="single-mode synthetic controls; no collective time-crystal claim",
        source_sha256={
            name: hashlib.sha256((ROOT / "src" / name).read_bytes()).hexdigest()
            for name in source_names
        },
        criteria="small two-cycle error plus resolved, stationary amplitude; these are necessary diagnostics only",
        cases={},
    )
    scenarios = [
        ("nonlinear", {}),
        ("linear", {"beta": 0}),
        ("drive_off", {"modulation": 0}),
        ("strong_damping", {"gamma": 0.08}),
        ("zero_seed", {"displacement_m": 0}),
        ("opposite_seed", {"displacement_m": -0.01}),
        ("velocity_seed", {"displacement_m": 0, "velocity_m_s": 0.01}),
        ("drive_1.8", {"drive": 1.8}),
        ("drive_1.92", {"drive": 1.92}),
        ("drive_2.08", {"drive": 2.08}),
        ("drive_2.2", {"drive": 2.2}),
        ("refined", {"steps_per_period": 64, "rtol": 1e-11, "atol": 1e-13}),
        ("longer", {"periods": 800}),
    ]
    for label, parameters in scenarios:
        parameters = parameters.copy()
        mode = RingMode(
            2 * math.pi,
            1.0,
            1,
            0.0,
            parameters.pop("gamma", 0.02),
            parameters.pop("modulation", 0.2),
            parameters.pop("drive", 2.0),
        )
        result = nonlinear_trace(mode, **parameters)
        result["mode"] = asdict(mode)
        result["solver_overrides"] = parameters
        report["cases"][label] = result
        (args.output / "time-order-controls.json").write_text(json.dumps(report, indent=2))
        print(label, result["late_window"], flush=True)
    # Start at the same drive phase after an even number of drive periods.
    baseline = report["cases"]["nonlinear"]
    q, v = baseline["final_state"]
    disturbed = nonlinear_trace(
        RingMode(**baseline["mode"]), displacement_m=1.2 * q, velocity_m_s=v + 0.02, periods=200
    )
    disturbed["mode"] = baseline["mode"]
    report["cases"]["disturbed_restart"] = disturbed

    def phase_equivalent_distance(a, b):
        return float(min(np.linalg.norm(np.array(a) - b), np.linalg.norm(np.array(a) + b)))

    report["comparisons"] = dict(
        refinement_final_state_difference=float(
            np.linalg.norm(
                np.array(baseline["final_state"]) - report["cases"]["refined"]["final_state"]
            )
        ),
        duration_final_state_difference=float(
            np.linalg.norm(
                np.array(baseline["final_state"]) - report["cases"]["longer"]["final_state"]
            )
        ),
        disturbed_phase_equivalent_final_distance=phase_equivalent_distance(
            disturbed["final_state"], baseline["final_state"]
        ),
        opposite_seed_symmetry_error=float(
            np.linalg.norm(
                np.array(baseline["final_state"]) + report["cases"]["opposite_seed"]["final_state"]
            )
        ),
    )
    cycles = np.arange(128)
    report["imposed_signal_controls"] = {
        "constant_at_drive_phase": stroboscopic_diagnostics(np.ones(128)),
        "imposed_two_cycle": stroboscopic_diagnostics((-1.0) ** cycles),
        "decaying_two_cycle": stroboscopic_diagnostics((-1.0) ** cycles * np.exp(-0.03 * cycles)),
        "four_cycle": stroboscopic_diagnostics(np.cos(math.pi / 2 * cycles)),
    }
    (args.output / "time-order-controls.json").write_text(json.dumps(report, indent=2))
    render(report, args.output)
    print("comparisons", report["comparisons"], flush=True)


def render(report, output):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8), layout="constrained")
    for name in ("nonlinear", "linear", "drive_off", "strong_damping"):
        case = report["cases"][name]
        state = np.array(case["states_q_m_v_m_s"])
        amplitude = np.linalg.norm(state / np.array([1.0, 1.0]), axis=1)
        axes[0].semilogy(np.arange(len(state)), np.maximum(amplitude, 1e-18), label=name)
    axes[0].set(
        xlabel="Drive cycles",
        ylabel="Sampled norm of (q, v/omega), m",
        title="Nonlinearity limits growth in this run",
    )
    axes[0].legend(fontsize=8)
    for name in ("nonlinear", "opposite_seed"):
        q = np.array(report["cases"][name]["states_q_m_v_m_s"])[-20:, 0]
        axes[1].plot(np.arange(381, 401), q, "o-", label=name)
    axes[1].set(
        xlabel="Drive cycle",
        ylabel="Displacement at fixed drive phase, m",
        title="Alternating response and opposite phase",
    )
    axes[1].legend(fontsize=8)
    for name, frequency in (
        ("drive_1.8", 1.8),
        ("drive_1.92", 1.92),
        ("nonlinear", 2.0),
        ("drive_2.08", 2.08),
        ("drive_2.2", 2.2),
    ):
        diag = report["cases"][name]["late_window"]
        axes[2].scatter(frequency, diag["centered_state_rms"], color="#18688b")
    axes[2].set(
        xlabel="Drive angular frequency, rad/s",
        ylabel="Late-window sampled RMS, m",
        title="Five-point detuning check",
    )
    fig.suptitle("Time-order controls: simulated single-mode response, not a time crystal")
    fig.savefig(output / "time-order-controls.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
