"""Compare a published finite-spin timing candidate with ordinary timing inputs."""

# ruff: noqa: E402
import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.time_crystal_clock_subsystem import clock_receiver, floquet_trace


def render(report, output):
    group = report["summary"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), layout="constrained")
    for on, label in ((True, "Interacting spins"), (False, "Uncoupled spins")):
        entries = [g for g in group if g["group"] == "base" and g["interactions"] == on]
        for n, style in ((6, "o-"), (8, "s--")):
            rows = sorted([r for r in entries if r["qubits"] == n], key=lambda x: x["g"])
            axes[0].plot(
                [r["g"] for r in rows],
                [r["finite_shot_perfect_fraction"] for r in rows],
                style,
                label=f"{label}, N={n}",
            )
    axes[0].axhline(1, color="grey", linestyle=":", label="Ideal digital divider")
    axes[0].set(
        xlabel="Transverse pulse factor g (ideal = 1)",
        ylabel="Fraction with all 128 ticks correct",
        ylim=(-0.05, 1.08),
        title="Eight disorder/state seeds per point",
    )
    axes[0].legend(fontsize=7)
    for case in report["cases"]:
        p = case["trace"]["parameters"]
        if case["group"] == "base" and p["qubits"] == 8 and p["seed"] == 0 and p["g"] == 0.97:
            label = "Interacting" if p["interactions"] else "Uncoupled"
            signal = np.array(case["trace"]["initial_sign_corrected_signal"])
            axes[1].plot(
                np.arange(len(signal)), signal * (-1.0) ** np.arange(len(signal)), label=label
            )
    axes[1].axhline(0.2, color="grey", linestyle=":", label="Receiver confidence threshold")
    axes[1].set(
        xlabel="Drive cycle",
        ylabel="Sign-corrected alternating signal",
        title="Example only: N=8, seed=0, g=.97",
    )
    axes[1].legend(fontsize=8)
    fig.suptitle("Candidate timing subsystem: simulation and clock-interface playback")
    fig.savefig(output / "time-crystal-subsystem.png", dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--plot-only", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    destination = args.output / "time-crystal-subsystem.json"
    if args.plot_only:
        render(json.loads(destination.read_text()), args.output)
        return
    report = dict(
        status="running",
        role="optional timing input to canonical 36-step engine clock",
        source="https://www.nature.com/articles/s41586-021-04257-w",
        source_sha256={
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in ("src/time_crystal_clock_subsystem.py", "src/canonical_polarity_clock.py")
        },
        acceptance="all expected rising edges at cycles 2,4,...; no extra or missing edge; threshold .2 fixed for all sources",
        hardware_integration=False,
        cases=[],
        baselines=[],
    )
    configurations = []
    for n in (6, 8):
        for g in (1.0, 0.97, 0.9, 0.6):
            for seed in range(8):
                for on in (True, False):
                    configurations.append(("base", dict(qubits=n, g=g, seed=seed, interactions=on)))
    for n in (6, 8):
        for seed in range(8):
            for on in (True, False):
                configurations.append(
                    (
                        "readout_and_pulse_error",
                        dict(
                            qubits=n,
                            g=0.97,
                            seed=seed,
                            interactions=on,
                            pulse_jitter=0.01,
                            readout_flip_probability=0.05,
                        ),
                    )
                )
    for seed in range(4):
        for on in (True, False):
            configurations.append(
                ("longer", dict(qubits=8, g=0.97, seed=seed, interactions=on, cycles=1024))
            )
    for number, (group, parameters) in enumerate(configurations):
        trace = floquet_trace(**parameters)
        report["cases"].append(
            dict(
                group=group,
                trace=trace,
                expectation_receiver=clock_receiver(trace["initial_sign_corrected_signal"]),
                finite_shot_receiver=clock_receiver(trace["finite_shot_signal"]),
            )
        )
        if (number + 1) % 16 == 0:
            print("completed", number + 1, "of", len(configurations), flush=True)
    for g in (1.0, 0.97, 0.9, 0.6):
        signal = np.cos(np.pi * g * np.arange(257))
        report["baselines"].append(
            dict(
                kind="ordinary phase accumulator / coherent rotation",
                g=g,
                receiver=clock_receiver(signal),
            )
        )
    report["baselines"].append(
        dict(
            kind="ideal digital divide-by-two",
            g=None,
            receiver=clock_receiver((-1.0) ** np.arange(257)),
        )
    )
    buckets = defaultdict(list)
    for case in report["cases"]:
        p = case["trace"]["parameters"]
        buckets[(case["group"], p["qubits"], p["g"], p["interactions"])].append(case)
    report["summary"] = []
    for (group, n, g, on), cases in buckets.items():
        report["summary"].append(
            dict(
                group=group,
                qubits=n,
                g=g,
                interactions=on,
                seeds=len(cases),
                expectation_perfect_fraction=float(
                    np.mean([c["expectation_receiver"]["perfect_tick_delivery"] for c in cases])
                ),
                finite_shot_perfect_fraction=float(
                    np.mean([c["finite_shot_receiver"]["perfect_tick_delivery"] for c in cases])
                ),
                average_detected_ticks=float(
                    np.mean([c["finite_shot_receiver"]["detected_ticks"] for c in cases])
                ),
                mean_late_alternating_correlation=float(
                    np.mean([c["trace"]["late_alternating_correlation"] for c in cases])
                ),
            )
        )
    report["resource_scope"] = dict(
        quantum_rotations_per_drive_cycle="N single-spin X rotations plus N field rotations",
        interaction_gates_per_drive_cycle="N-1 ZZ rotations when enabled",
        hypothetical_endpoint_shots=256,
        state_preparations_for_257_endpoint_readouts=256 * 257,
        total_floquet_periods_across_those_shots=256 * 256 * 257 // 2,
        note="Endpoint ensembles cannot be interpreted as a continuously running single hardware clock. No joule or timing-jitter model.",
    )
    report["status"] = "complete_bounded_interface_experiment"
    destination.write_text(json.dumps(report, indent=2))
    render(report, args.output)
    print(json.dumps(report["summary"], indent=2), flush=True)


if __name__ == "__main__":
    main()
