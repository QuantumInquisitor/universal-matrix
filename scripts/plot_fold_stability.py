"""Plot matched-time continuation samples; no simulation or fitted trajectories."""

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = json.loads(args.input.read_text(encoding="utf-8"))
    root = Path(__file__).resolve().parents[1]
    for name, expected in report["sources"].items():
        actual = hashlib.sha256(
            (root / "scripts" / name).read_text(encoding="utf-8").encode()
        ).hexdigest()
        if actual != expected:
            raise ValueError("Source/report mismatch: " + name)
    seed = report["seed"]
    if (
        hashlib.sha256((root / seed["path"]).read_text(encoding="utf-8").encode()).hexdigest()
        != seed["normalized_utf8_sha256"]
    ):
        raise ValueError("Seed/report mismatch")
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), layout="constrained")
    for name, label, color in (
        ("baseline", "Unchanged continuation", "#225ea8"),
        ("kicked", "1% velocity increase", "#d97916"),
    ):
        rows = report["cases"][name]["samples"]
        axes[0].plot(
            [r["physical_time_s"] for r in rows],
            [1e6 * r["total_mechanical_j"] for r in rows],
            label=label,
            color=color,
        )
    a = {r["time_s"]: r for r in report["cases"]["baseline"]["samples"]}
    b = {r["time_s"]: r for r in report["cases"]["kicked"]["samples"]}
    times = report["perturbation"]["common_times_s"]
    delta = np.array([np.abs(np.asarray(a[t]["q"]) - np.asarray(b[t]["q"])) for t in times])
    physical = [20 + t for t in times]
    axes[1].plot(physical, delta[:, :, 0].max(axis=1), color="#008a80")
    axes[2].plot(physical, np.degrees(delta[:, :, 1].max(axis=1)), color="#9b4a97")
    axes[0].set(
        title="Mechanical + connector energy",
        xlabel="Physical time (s)",
        ylabel="Energy (microjoules)",
    )
    axes[1].set(
        title="Largest scale-coordinate separation",
        xlabel="Physical time (s)",
        ylabel="Absolute scale difference",
    )
    axes[2].set(
        title="Largest fold-angle separation",
        xlabel="Physical time (s)",
        ylabel="Absolute angle difference (degrees)",
    )
    axes[0].legend(frameon=False, fontsize=9)
    for ax in axes:
        ax.grid(alpha=0.2)
    fig.suptitle("Replenished folding | continuation and accounted disturbance", fontsize=17)
    fig.supxlabel(
        "Common-time samples inside accepted solver steps; lines are guides. Intervention energy is recorded separately.\nSynthetic model. A single disturbance and finite window do not establish a stable breathing cycle.",
        fontsize=9,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=150)
    plt.close(fig)
    print(args.output)


if __name__ == "__main__":
    main()
