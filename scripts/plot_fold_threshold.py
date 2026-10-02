"""Plot saved power-onset samples; no dynamics are rerun or fitted."""

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


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
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), layout="constrained")
    powers, ratios = [], []
    for i, power in enumerate(report["protocol"]["powers_w"]):
        case = report["cases"][f"power_{i}"]
        if case["termination"]["last_accepted_time_s"] != 20:
            raise ValueError("Endpoint comparison requires full 20-second coverage")
        rows = case["samples"]
        e0 = case["onset"]["initial_total_mechanical_j"]
        axes[0].plot(
            [r["time_s"] for r in rows],
            [r["total_mechanical_j"] / e0 for r in rows],
            label=f"{power * 1e6:g} microwatts",
        )
        powers.append(power * 1e6)
        ratios.append(case["onset"]["final_to_initial_energy_ratio"])
    axes[1].scatter(powers, ratios, color="#225ea8", s=60, zorder=3, label="20-second results")
    axes[1].axvline(
        1e6 * report["protocol"]["damping_threshold_w"],
        color="#bd303c",
        linestyle="--",
        label="Derived linear damping threshold",
    )
    for ax in axes:
        ax.axhline(1, color="gray", linestyle=":", linewidth=1)
        ax.grid(alpha=0.2)
        ax.legend(frameon=False, fontsize=9)
    axes[0].set(
        title="Same small deformation; equilibrium reserves",
        xlabel="Time (s)",
        ylabel="Mechanical + connector energy / initial energy",
    )
    axes[1].set(
        title="Finite-window change across source settings",
        xlabel="Unit-size source coefficient (microwatts)",
        ylabel="Final / initial mechanical + connector energy",
    )
    fig.suptitle("Supply onset | computed folding network", fontsize=17)
    fig.supxlabel(
        "Saved accepted samples; joining lines are guides. Initial reserve energies differ.\n"
        "Synthetic model; a 20-second sweep does not establish settled breathing or material performance.",
        fontsize=9,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=170)
    plt.close(fig)
    print(args.output)


if __name__ == "__main__":
    main()
