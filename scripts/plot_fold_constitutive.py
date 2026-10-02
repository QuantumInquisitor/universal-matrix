"""Inspect source-backed reduced geometry and its saved per-element energies."""

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

try:
    from .report_fold_constitutive import geometry
except ImportError:
    from report_fold_constitutive import geometry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = json.loads(args.input.read_text(encoding="utf-8"))
    root = Path(__file__).resolve().parents[1]
    for name, expected in report["sources"].items():
        if hashlib.sha256((root / "scripts" / name).read_text().encode()).hexdigest() != expected:
            raise ValueError("Source/report mismatch: " + name)
    case = report["cases"]["mixed"]
    elements = {e["id"]: e for e in case["panels"] + case["bridges"]}
    vertices = geometry(case["q"], report["parameters"]["length_m_per_reference_unit"])
    fig = plt.figure(figsize=(13, 6), layout="constrained")
    ax = fig.add_subplot(121, projection="3d")
    bars = fig.add_subplot(122)
    maximum = max(p["energy_j"] for p in case["panels"])
    for row in vertices:
        points = np.array(row["vertices_m"])
        name = row["id"]
        if name.startswith("panel"):
            color = plt.cm.viridis(elements[name]["energy_j"] / maximum)
            ax.add_collection3d(
                Poly3DCollection([points], facecolor=color, edgecolor="#303f50", alpha=0.65)
            )
            center = points.mean(axis=0)
            ax.text(*center, name, fontsize=7)
        elif name.startswith("bridge"):
            ax.plot(*points.T, color="#dd751d", linewidth=2)
        else:
            ax.scatter(*points.T, color="#555555", s=35)
    all_points = np.vstack([v["vertices_m"] for v in vertices])
    middle = (all_points.max(axis=0) + all_points.min(axis=0)) / 2
    radius = np.ptp(all_points, axis=0).max() * 0.6
    ax.set_xlim(middle[0] - radius, middle[0] + radius)
    ax.set_ylim(middle[1] - radius, middle[1] + radius)
    ax.set_zlim(middle[2] - radius, middle[2] + radius)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=24, azim=38)
    ax.set(
        xlabel="x (m)",
        ylabel="y (m)",
        zlabel="z (m)",
        title="Actual midsurfaces and bridge centerlines",
    )
    names = [e["id"] for e in case["panels"]] + ["12 axial bridges"]
    energies = [1e6 * p["energy_j"] for p in case["panels"]]
    energies.append(1e6 * sum(b["energy_j"] for b in case["bridges"]))
    bars.barh(names, energies, color=["#287d8e"] * 6 + ["#dd751d"])
    bars.invert_yaxis()
    bars.set(
        xlabel="Elastic energy (microjoules)", title="Energy owned by declared reduced elements"
    )
    bars.grid(axis="x", alpha=0.2)
    fig.suptitle("Geometry-derived elasticity | scale 1.03, fold offset 0.08 rad", fontsize=17)
    fig.supxlabel(
        "Synthetic membrane + axial laws. Gray hubs have no elastic law; displayed lines have no thickness.\n"
        "This static reduced geometry is not a solid-union, collision, dynamics or XR validation.",
        fontsize=10,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=165)
    plt.close(fig)
    print(args.output)


if __name__ == "__main__":
    main()
