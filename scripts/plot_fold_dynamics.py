"""Plot actual reduced-model output; requires matplotlib, no resimulation."""

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
    for name, expected in report["source_sha256_normalized_text"].items():
        actual = hashlib.sha256(
            Path(__file__).with_name(name).read_text(encoding="utf-8").encode()
        ).hexdigest()
        if actual != expected:
            raise ValueError("Report source differs from current file: " + name)
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
    colors = {"driven": "#1769a8", "drive_off": "#dd7526"}
    for name, label in [
        ("driven", "Continuous forcing"),
        ("drive_off", "Force tapered off at 1 s"),
    ]:
        rows = report["cases"][name]["trace"]
        time = [r["time_s"] for r in rows]
        axes[0, 0].plot(time, [r["q"][0] for r in rows], color=colors[name], label=label)
        axes[0, 1].plot(time, np.degrees([r["q"][1] for r in rows]), color=colors[name])
    axes[0, 0].set(
        title="Computed size response", ylabel="Scale s (dimensionless)", xlabel="Time (s)"
    )
    axes[0, 0].legend(frameon=False, fontsize=9)
    axes[0, 1].set(
        title="Computed folding response", ylabel="Fold angle (degrees)", xlabel="Time (s)"
    )
    for ax in axes[0]:
        ax.axvline(1, color="#999999", ls=":", lw=1)
    rows = report["cases"]["drive_off"]["trace"]
    time = [r["time_s"] for r in rows]
    initial = report["cases"]["drive_off"]["initial_energy_j"]
    ax = axes[1, 0]
    ax.plot(
        time,
        [1e6 * (r["energy_j"] - initial) for r in rows],
        label="Stored energy change",
        color="#1769a8",
        lw=2.5,
    )
    ax.plot(
        time,
        [1e6 * (r["work_j"] - r["loss_j"]) for r in rows],
        label="External work minus loss",
        color="#dd7526",
        ls="--",
    )
    ax.axvline(1, color="#999999", ls=":", lw=1)
    ax.set(
        title="Energy ledger: force-off run",
        ylabel="Energy change (microjoules)",
        xlabel="Time (s)",
    )
    ax.legend(frameon=False, fontsize=9)
    names = ["conservative", "damped", "driven", "drive_off", "omitted_bias_control"]
    values = [report["cases"][n]["maximum_balance_residual_j"] for n in names]
    ax = axes[1, 1]
    ax.bar(range(5), np.maximum(values, 1e-22), color=["#1769a8"] * 4 + ["#b72d32"])
    ax.set_yscale("log")
    ax.set_xticks(range(5), ["Conserve", "Damped", "Driven", "Force off", "Inertia\nomitted"])
    ax.set(title="Maximum energy-balance error", ylabel="Absolute residual (J)")
    for ax in axes.flat:
        ax.grid(alpha=0.18)
    fig.suptitle("Force-driven folding | synthetic 22-point model", fontsize=17)
    fig.supxlabel(
        "Chosen masses and force laws; no material calibration or autonomous-breathing claim.\nCurves are computed states. Red bar is an intentionally incorrect model. Error display floor: 1e-22 J.",
        fontsize=9,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=170)
    plt.close(fig)
    print(args.output)


if __name__ == "__main__":
    main()
