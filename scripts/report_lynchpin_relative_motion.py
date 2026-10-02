"""Export the bounded ray-fold control; no finite-panel clearance inference."""
# ruff: noqa: E402

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.lynchpin_relative_motion_control import (
    compliant_rays,
    panel_angles,
    reference_rays,
    rigidity_report,
)


def main():
    output = Path(sys.argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)
    cases = []
    for dimension in (3, 4):
        initial = panel_angles(reference_rays(dimension))
        frames = []
        for i in range(101):
            phase = i / 100
            rays = compliant_rays(phase, dimension)
            angles = panel_angles(rays)
            frames.append(
                dict(
                    phase=phase,
                    rays=rays.tolist(),
                    panel_angles_degrees=angles,
                    corner_angle_changes_degrees={k: angles[k] - initial[k] for k in initial},
                )
            )
        cases.append(
            dict(
                rigidity=rigidity_report(dimension),
                frames=frames,
                peak_corner_angle_changes_degrees={
                    k: max(abs(f["corner_angle_changes_degrees"][k]) for f in frames)
                    for k in initial
                },
            )
        )
    result = dict(
        base_commit="a78576f83854a5b75c90815db121b1ca40a4f606",
        experiment_status="optional_reference_control",
        amplitude_radians=math.pi / 6,
        amplitude_origin="declared test input, not a recovered hinge limit",
        changed_panel_angles=["13", "23"],
        finite_panel_clearance=False,
        material_model=False,
        recursive_dynamics=False,
        cases=cases,
    )
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            [
                dict(
                    dimensions=c["rigidity"]["dimensions"],
                    internal_modes=c["rigidity"]["internal_first_order_modes"],
                    peak_changes=c["peak_corner_angle_changes_degrees"],
                )
                for c in cases
            ],
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
