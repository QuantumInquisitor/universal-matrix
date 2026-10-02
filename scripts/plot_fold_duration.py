"""Plot accepted samples from the finite-source duration experiment."""

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
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), layout="constrained")
    colors = {"active": "#225ea8", "passive": "#d97916", "rest": "#008a80"}
    for name, case in report["cases"].items():
        rows = case["samples"]
        time = [r["time_s"] for r in rows]
        energy = np.array([sum(r["mechanical_j"]) + sum(r["edge_potential_j"]) for r in rows])
        axes[0].plot(time, 1e6 * energy, label=name, color=colors[name])
    rows = report["cases"]["active"]["samples"]
    time = [r["time_s"] for r in rows]
    reserve = np.array([r["reserve_j"] for r in rows])
    for node in range(4):
        axes[1].semilogy(time, reserve[:, node] / reserve[0, node], label=f"Node {node}")
    axes[1].axhline(0.01, color="#555555", linestyle="--", label="1% threshold")
    names = list(report["cases"])
    errors = [max(report["cases"][n]["max_group_residual_j"].values()) for n in names]
    axes[2].bar(names, np.maximum(errors, 1e-24), color=[colors[n] for n in names])
    axes[2].set_yscale("log")
    axes[0].set(
        title="Mechanical + connector energy", xlabel="Time (s)", ylabel="Energy (microjoules)"
    )
    axes[1].set(
        title="Active run: remaining reserves",
        xlabel="Time (s)",
        ylabel="Fraction of initial reserve",
    )
    axes[2].set(title="Largest group accounting error", ylabel="Maximum absolute residual (J)")
    for ax in axes:
        ax.grid(alpha=0.2)
    axes[0].legend(frameon=False)
    axes[1].legend(frameon=False, fontsize=9)
    fig.suptitle("Finite-source folding | longer-duration experiment", fontsize=17)
    fig.supxlabel(
        "Saved accepted samples; joining lines are guides. Synthetic model, no replenishment.\nError display floor: 1e-24 J. Full termination and refinement details are in the source-hashed report.",
        fontsize=9,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=150)
    plt.close(fig)
    print(args.output)


if __name__ == "__main__":
    main()
