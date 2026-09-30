"""Export exact-source mirror landmarks and a sampled projection diagnostic."""
# ruff: noqa: E402

import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.recursive_mirror_motion_control import LiftedMirrorControl
from src.stella_octangula_register_bridge import STELLA_VERTICES


def main():
    output = Path(sys.argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)
    frames = []
    for index in range(65):
        phase = index / 32
        control = LiftedMirrorControl(phase, 13)
        points = [control.map_point(v) for v in STELLA_VERTICES]
        frames.append(
            dict(
                phase=phase,
                vertices=points,
                projected_vertices=[p[:3] for p in points],
                projected_rank=control.projected_rank,
                projected_determinant=control.projected_determinant,
                intrinsic_volume_scale=control.intrinsic_volume_scale,
                minimum_vertex_distance=min(
                    math.dist(a, b) for i, a in enumerate(points) for b in points[i + 1 :]
                ),
            )
        )
    commit = subprocess.check_output(
        ["git", "-c", f"safe.directory={ROOT.as_posix()}", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    result = dict(
        base_commit=commit,
        experiment_status="optional_reference_control",
        operation="central mirror through XY and ZW rotations",
        spatial_dimensions_used=4,
        output_coordinates=13,
        intrinsic_dimension=3,
        preserves_preexisting_intersections=True,
        relative_hinge_motion=False,
        physical_dynamics=False,
        recursive_scale_transfer=False,
        source="src/recursive_mirror_motion_control.py",
        frames=frames,
    )
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            dict(
                frames=len(frames),
                minimum_vertex_distance=min(f["minimum_vertex_distance"] for f in frames),
                projection_rank_losses=[f["phase"] for f in frames if f["projected_rank"] < 3],
            )
        )
    )


if __name__ == "__main__":
    main()
