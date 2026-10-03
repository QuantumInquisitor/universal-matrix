"""Plot saved mixed-size network samples; no new simulation or fitted curves."""

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
            raise ValueError("Report/source mismatch: " + name)
    case = report["cases"]["reference"]
    rows = case["samples"]
    times = [r["time_s"] for r in rows]
    energy = 1e6 * np.array([r["mechanical_j"] for r in rows])
    angles = np.degrees(np.array([r["q"] for r in rows])[:, :, 1])
    initial_angles = angles[0]
    colors = ["#225ea8", "#008a80", "#d97916", "#9b4a97"]
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
    for i, color in enumerate(colors):
        label = f"Node {i} | size {case['settings']['sizes'][i]:g}"
        axes[0, 0].plot(times, energy[:, i], "o-", color=color, label=label, ms=4)
        axes[0, 1].plot(times, angles[:, i] - initial_angles[i], "o-", color=color, ms=4)
    axes[0, 0].set(
        title="Mechanical energy reaches other nodes",
        ylabel="Energy (microjoules)",
        xlabel="Time (s)",
    )
    axes[0, 0].legend(frameon=False, fontsize=9)
    axes[0, 1].set(
        title="Computed folding response",
        ylabel="Angle change from initial state (degrees)",
        xlabel="Time (s)",
    )
    stored = [1e6 * (sum(r["mechanical_j"]) + sum(r["edge_potential_j"])) for r in rows]
    loss = [1e6 * sum(r["damping_loss_j"]) for r in rows]
    axes[1, 0].plot(
        times, stored, "o-", label="Mechanical + connector energy", color=colors[0], ms=4
    )
    axes[1, 0].plot(times, loss, "o-", label="Accumulated damping loss", color=colors[2], ms=4)
    axes[1, 0].plot(
        times, np.array(stored) + loss, "s--", label="Accounted total", color=colors[1], ms=4
    )
    axes[1, 0].set(
        title="Closed passive energy account", ylabel="Energy (microjoules)", xlabel="Time (s)"
    )
    axes[1, 0].legend(frameon=False, fontsize=9)
    names = ["reference", "three_quarters", "half", "wrong_reaction"]
    errors = [report["cases"][n]["max_group_residual_j"]["root"] for n in names]
    axes[1, 1].bar(range(4), np.maximum(errors, 1e-24), color=colors[:3] + ["#bd303c"])
    axes[1, 1].set_yscale("log")
    axes[1, 1].set_xticks(range(4), ["Scale 1", "Scale .75", "Scale .5", "Wrong\nreaction"])
    axes[1, 1].set(title="Whole-network balance error", ylabel="Maximum absolute residual (J)")
    for ax in axes.flat:
        ax.grid(alpha=0.18)
    fig.suptitle("Unequal-sized folding network | computed experiment", fontsize=17)
    fig.supxlabel(
        "Passive synthetic model; no material calibration or sustained-breathing claim.\nMarkers are saved samples; joining lines are guides. Red bar is a deliberately incorrect reaction. Error display floor: 1e-24 J.",
        fontsize=9,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=160)
    plt.close(fig)
    print(args.output)


if __name__ == "__main__":
    main()
