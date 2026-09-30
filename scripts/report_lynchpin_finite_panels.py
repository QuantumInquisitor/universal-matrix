"""Export panel surfaces, deformations and continuous core-clearance evidence."""
# ruff: noqa: E402

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.lynchpin_finite_panel_control import audit_core_cycle, deformation_metrics, panel_vertices
from src.lynchpin_geometry_audit import LYNCHPIN_PANELS


def main():
    cases = []
    for dimension in (3, 4):
        audit = audit_core_cycle(dimension)
        frames = []
        for k in range(65):
            phase = k / 64
            panels = []
            for index, pair in enumerate(LYNCHPIN_PANELS):
                full = panel_vertices(phase, dimension, index)
                core = panel_vertices(phase, dimension, index, 0.15)
                panels.append(
                    dict(
                        id="".join(map(str, pair)),
                        full_surface_vertices=full.tolist(),
                        core_surface_vertices=core.tolist(),
                        core_triangles=[[0, i, i + 1] for i in range(1, len(core) - 1)],
                        deformation=deformation_metrics(phase, dimension, index),
                    )
                )
            frames.append(dict(phase=phase, panels=panels))
        stretches = [
            s for f in frames for p in f["panels"] for s in p["deformation"]["principal_stretches"]
        ]
        areas = [p["deformation"]["area_ratio"] for f in frames for p in f["panels"]]
        cases.append(
            dict(
                audit=audit,
                frames=frames,
                sampled_stretch_range=[min(stretches), max(stretches)],
                sampled_area_ratio_range=[min(areas), max(areas)],
            )
        )
    source_files = (
        "src/lynchpin_finite_panel_control.py",
        "src/lynchpin_relative_motion_control.py",
        "src/lynchpin_geometry_audit.py",
    )
    result = dict(
        schema="lynchpin-finite-panel-control-v1",
        units="dimensionless",
        base_commit="a78576f83854a5b75c90815db121b1ca40a4f606",
        local_unpublished=True,
        surface_model="affine images of a unit-side regular pentagon",
        thickness_model="core surface plus ambient ball of radius .01",
        hinge_exclusion="coefficient collar a<.15 or b<.15; not a physical width or implemented hinge",
        input_hashes={
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in source_files
        },
        full_assembly_clearance=False,
        material_law=False,
        flow_model=False,
        cases=cases,
    )
    output = Path(sys.argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            [
                dict(
                    dimensions=c["audit"]["dimensions"],
                    accepted=c["audit"]["accepted"],
                    intervals=c["audit"]["interval_count"],
                    minimum_clearance=c["audit"]["minimum_clearance_bound"],
                    stretches=c["sampled_stretch_range"],
                    area_ratios=c["sampled_area_ratio_range"],
                )
                for c in cases
            ],
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
