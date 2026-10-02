"""Execute recovered original modules to export an independent geometry fixture.

Supply original PR119 control modules plus lynchpin_geometry_audit.py in
--source-dir. Their remaining unchanged imports resolve through --dependency-dir.
Only execute trusted repository source. This script does not fetch network data.
"""

import argparse
import hashlib
import importlib
import json
import math
import sys
import types
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--dependency-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit-clearance", action="store_true")
    args = parser.parse_args()
    source, dependencies = args.source_dir.resolve(), args.dependency_dir.resolve()
    package = types.ModuleType("fold_reference_original")
    package.__path__ = [str(source), str(dependencies)]
    sys.modules[package.__name__] = package
    connected = importlib.import_module(package.__name__ + ".lynchpin_connected_control")
    relative = importlib.import_module(package.__name__ + ".lynchpin_relative_motion_control")
    breathing = importlib.import_module(package.__name__ + ".lynchpin_breathing_control")
    cases = []
    for phase in (0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0):
        scale = breathing.BreathingCycle().state(phase)["scale"]
        rays = relative.compliant_rays(phase, 3)
        bodies = []
        for body in connected.bodies():
            vertices = scale * body["coefficients"] @ rays
            bodies.append(
                {
                    "name": body["name"],
                    "kind": body["kind"],
                    "vertices_reference_length": vertices.tolist(),
                    "coefficient_mean_position": vertices.mean(axis=0).tolist(),
                    "radius_reference_length": scale * body["radius"],
                }
            )
        cases.append(
            {
                "phase": phase,
                "scale": scale,
                "theta": math.pi / 6 * math.sin(math.pi * phase) ** 2,
                "bodies": bodies,
            }
        )
    hashes = {}
    for name, module in list(sys.modules.items()):
        if name.startswith(package.__name__ + ".") and getattr(module, "__file__", None):
            path = Path(module.__file__)
            hashes[path.name] = {
                "origin": "pinned-source" if path.parent == source else "local-dependency",
                "sha256_normalized_text": hashlib.sha256(
                    path.read_text(encoding="utf-8").encode()
                ).hexdigest(),
            }
    report = {
        "schema": 1,
        "reference_commit": "60a7fd60f57d73b89ea5397db58a3ff5d291556c",
        "scope": "Original source execution; dimensionless geometry. Mean vertices are coefficient markers, not volume centroids.",
        "executed_sources": hashes,
        "cases": cases,
    }
    if args.audit_clearance:
        audit = connected.audit_connected_cycle(dimensions=3, amplitude=0.1, maximum_depth=10)
        report["original_clearance_audit"] = {k: v for k, v in audit.items() if k != "pairs"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "cases": len(cases),
                "bodies_per_case": len(cases[0]["bodies"]),
                "source_count": len(hashes),
            }
        )
    )


if __name__ == "__main__":
    main()
