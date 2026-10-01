"""Plot saved supply-controlled folding samples without rerunning dynamics."""

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
    for name, expected in report["sources"].items():
        actual = hashlib.sha256(
            Path(__file__).with_name(name).read_text(encoding="utf-8").encode()
        ).hexdigest()
        if actual != expected:
            raise ValueError("Source/report mismatch: " + name)
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
    for name, label, color in (
        ("powered", "Supply on", "#225ea8"),
        ("source_off", "Supply off; finite reserves", "#d97916"),
    ):
        rows = report["cases"][name]["samples"]
        axes[0, 0].plot(
            [r["time_s"] for r in rows],
            [1e6 * r["total_mechanical_j"] for r in rows],
            label=label,
            color=color,
        )
    rows = report["cases"]["powered"]["samples"]
    time = [r["time_s"] for r in rows]
    reserve = np.array([r["reserve_j"] for r in rows])
    for node in range(4):
        axes[0, 1].plot(time, reserve[:, node] / reserve[0, node], label=f"Node {node}")
    injected = np.array([sum(r["input_j"]) for r in rows])
    stored = np.array([sum(r["reserve_j"]) + r["total_mechanical_j"] for r in rows])
    lost = np.array(
        [
            sum(r["damping_loss_j"]) + sum(r["conversion_loss_j"]) + sum(r["leakage_loss_j"])
            for r in rows
        ]
    )
    axes[1, 0].plot(time, 1e6 * injected, label="Received from external source", color="#225ea8")
    axes[1, 0].plot(
        time,
        1e6 * (stored - stored[0] + lost),
        "--",
        label="Stored change + all losses",
        color="#008a80",
    )
    errors = [
        max(report["cases"][name]["max_group_residual_j"].values())
        for name in ("powered", "source_off")
    ]
    errors += [
        max(report["cases"]["powered"]["missing_input_diagnostic"]["max_group_residual_j"].values())
    ]
    axes[1, 1].bar(
        ["Supply on", "Supply off", "Input omitted"],
        np.maximum(errors, 1e-24),
        color=["#225ea8", "#d97916", "#bd303c"],
    )
    axes[1, 1].set_yscale("log")
    axes[0, 0].set(
        title="Same mechanics, different supply",
        xlabel="Time (s)",
        ylabel="Mechanical + connector energy (microjoules)",
    )
    axes[0, 1].set(
        title="Powered case: reserve fractions", xlabel="Time (s)", ylabel="Fraction of capacity"
    )
    axes[1, 0].set(
        title="Where received energy goes", xlabel="Time (s)", ylabel="Energy (microjoules)"
    )
    axes[1, 1].set(title="Largest group accounting error", ylabel="Maximum absolute residual (J)")
    for ax in axes.flat:
        ax.grid(alpha=0.2)
    for ax in (axes[0, 0], axes[0, 1], axes[1, 0]):
        ax.legend(frameon=False, fontsize=9)
    fig.suptitle("Accounted external supply | computed folding experiment", fontsize=17)
    fig.supxlabel(
        "Saved accepted samples; joining lines are guides. Ideal source, uncalibrated materials.\nRed bar deliberately omits received energy from accounting; it is not another trajectory. Error display floor: 1e-24 J.",
        fontsize=9,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=160)
    plt.close(fig)
    print(args.output)


if __name__ == "__main__":
    main()
