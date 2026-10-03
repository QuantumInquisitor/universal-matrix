"""Export actual connected geometry; --audit also reproduces interval checks."""

# ruff: noqa: E402
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from src.lynchpin_connected_control import audit_connected_cycle, scene


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    sources = [
        "lynchpin_connected_control.py",
        "lynchpin_breathing_control.py",
        "lynchpin_finite_panel_control.py",
        "lynchpin_relative_motion_control.py",
        "lynchpin_geometry_audit.py",
    ]
    packet = dict(
        schema="connected-compliant-specimen-v1",
        units="dimensionless",
        source_sha256={
            name: hashlib.sha256((ROOT / "src" / name).read_bytes()).hexdigest() for name in sources
        },
        motion="prescribed fold and common breathing; not emergent dynamics",
        material="convex hull of each vertex array offset by its stated ball radius",
        frames=[
            dict(dimensions=d, phase=float(p), bodies=scene(float(p), d))
            for d in (3, 4)
            for p in np.linspace(0, 1, 101)
        ],
    )
    (args.output / "connected-fold-scene.json").write_text(json.dumps(packet, indent=2))
    if args.audit:
        for dimension in (3, 4):
            result = audit_connected_cycle(dimension)
            (args.output / f"connected-fold-{dimension}d.json").write_text(
                json.dumps(result, indent=2)
            )
            print(dimension, result["accepted"], result["interval_count"], flush=True)
    fig = plt.figure(figsize=(14, 5), layout="constrained")
    for index, phase in enumerate((0, 0.25, 0.5, 0.75)):
        ax = fig.add_subplot(1, 4, index + 1, projection="3d")
        for body in scene(phase):
            points = np.array(body["vertices"])
            if body["kind"] == "panel":
                ax.add_collection3d(
                    Poly3DCollection(
                        [points],
                        facecolor="#4994b4",
                        edgecolor="#153c53",
                        alpha=0.38,
                        linewidth=0.6,
                    )
                )
            elif body["kind"] == "bridge":
                ax.plot(*points.T, color="#b84627", linewidth=2)
            else:
                u, v = np.meshgrid(np.linspace(0, 2 * np.pi, 16), np.linspace(0, np.pi, 10))
                radius = body["offset_radius"]
                ax.plot_surface(
                    points[0, 0] + radius * np.cos(u) * np.sin(v),
                    points[0, 1] + radius * np.sin(u) * np.sin(v),
                    points[0, 2] + radius * np.cos(v),
                    color="#df9234",
                    linewidth=0,
                )
        ax.set(
            xlim=(-1.8, 1.8),
            ylim=(-1.8, 1.8),
            zlim=(-1.8, 1.8),
            title=f"Phase {phase:g} | scale {1 + 0.1 * np.sin(2 * np.pi * phase):.2f}",
            xlabel="x",
            ylabel="y",
            zlabel="z",
        )
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=20, azim=35)
    fig.suptitle("Connected breathing specimen: 6 compliant panels, 4 hubs, 12 bridges")
    fig.text(
        0.5,
        0.01,
        "3D computed geometry. Panel midsurfaces and bridge centerlines shown; full offset radii are in the data. Prescribed motion.",
        ha="center",
        fontsize=9,
    )
    fig.savefig(args.output / "connected-fold.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
