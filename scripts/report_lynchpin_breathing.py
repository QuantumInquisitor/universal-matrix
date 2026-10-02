"""Export the breathing overlay and a scientific diagnostic figure."""

# ruff: noqa: E402
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

from src.lynchpin_breathing_control import BreathingCycle
from src.lynchpin_finite_panel_control import audit_core_cycle, panel_vertices


def main():
    output = Path(sys.argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)
    cycle = BreathingCycle(0.1)
    cases = []
    for dimension in (3, 4):
        base = audit_core_cycle(dimension)
        frames = [
            dict(
                phase=k / 100,
                breathing=cycle.state(k / 100),
                panels=[cycle.panel(k / 100, dimension, panel) for panel in range(6)],
            )
            for k in range(101)
        ]
        cases.append(
            dict(
                dimensions=dimension,
                base_core_audit=base,
                breathing_core_clearance_lower_bound=(1 - cycle.amplitude)
                * base["minimum_clearance_bound"]
                if base["accepted"]
                else None,
                frames=frames,
            )
        )
    result = dict(
        base_commit="a78576f83854a5b75c90815db121b1ca40a4f606",
        local_unpublished=True,
        amplitude=0.1,
        phase_is_not_physical_time=True,
        rate_law="prescribed s=1+0.1*sin(2*pi*phase); not inferred from Q-ball traces",
        all_lengths_scale=True,
        full_hinge_assembly_certified=False,
        fold_volume_flow_not_implemented=True,
        cases=cases,
    )
    output.with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n")
    fig = plt.figure(figsize=(14, 9), layout="constrained")
    grid = fig.add_gridspec(2, 4, height_ratios=(1.25, 1), hspace=0.2)
    colors = plt.cm.tab10(np.arange(6))
    for index, phase in enumerate((0, 0.25, 0.5, 0.75)):
        ax = fig.add_subplot(grid[0, index], projection="3d")
        scale = cycle.state(phase)["scale"]
        for panel in range(6):
            full = scale * panel_vertices(phase, 3, panel)
            core = np.array(cycle.panel(phase, 3, panel)["vertices"])
            ax.add_collection3d(
                Poly3DCollection([full], facecolors=[colors[panel]], alpha=0.08, edgecolors="none")
            )
            ax.add_collection3d(
                Poly3DCollection(
                    [core],
                    facecolors=[colors[panel]],
                    alpha=0.8,
                    edgecolors="#263238",
                    linewidths=0.5,
                )
            )
        ax.set(xlim=(-2, 2), ylim=(-2, 2), zlim=(-2, 2), xlabel="X", ylabel="Y", zlabel="Z")
        ax.set_box_aspect((1, 1, 1))
        ax.set_xticks((-2, 0, 2))
        ax.set_yticks((-2, 0, 2))
        ax.set_zticks((-2, 0, 2))
        ax.set_title(f"Phase {phase:.2f} | size {scale:.2f}")
        ax.view_init(elev=22, azim=35)
    phases = np.linspace(0, 1, 101)
    size_ax = fig.add_subplot(grid[1, :2])
    size_ax.plot(
        phases, [cycle.state(float(p))["scale"] for p in phases], label="Length / reference"
    )
    size_ax.plot(
        phases,
        [cycle.state(float(p))["similarity_volume_ratio"] for p in phases],
        label="Similarity volume / reference",
    )
    size_ax.set(
        xlabel="Cycle phase (not physical time)",
        ylabel="Ratio",
        title="Prescribed expansion and contraction",
    )
    size_ax.legend()
    size_ax.grid(alpha=0.2)
    density_ax = fig.add_subplot(grid[1, 2:])
    records = [cycle.panel(float(p), 3, 4) for p in phases]
    areas = np.array([r["area_ratio"] for r in records])
    densities = np.array([r["material_surface_density_ratio"] for r in records])
    density_ax.plot(phases, areas, label="Panel 13 area")
    density_ax.plot(phases, densities, label="Panel 13 surface density")
    density_ax.plot(phases, areas * densities, "--", label="Conserved panel content")
    density_ax.set(
        xlabel="Cycle phase (not physical time)",
        ylabel="Ratio to reference",
        title="Deformation and material conservation",
    )
    density_ax.legend()
    density_ax.grid(alpha=0.2)
    fig.suptitle(
        "Breathing + relative folding: 3D geometric control\nColored cores checked; faint hinge regions remain unmodeled. Thickness is not rendered.",
        fontsize=14,
    )
    fig.savefig(output.with_suffix(".png"), dpi=150)
    plt.close(fig)
    print(
        json.dumps(
            [
                dict(
                    dimensions=c["dimensions"],
                    core_clearance_lower_bound=c["breathing_core_clearance_lower_bound"],
                )
                for c in cases
            ]
        )
    )


if __name__ == "__main__":
    main()
