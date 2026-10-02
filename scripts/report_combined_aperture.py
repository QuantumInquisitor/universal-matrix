"""Reproduce all six fixed combined assembly cases and their full pair inventory."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.toroidal_combined_aperture import audit_combined_aperture  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/combined-aperture")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    cases = []
    for current in (1.0, -1.0, 2e-8, -2e-8, 7.0, -7.0):
        report = audit_combined_aperture(current)
        if not report["static_pair_clearance_complete"]:
            raise RuntimeError(f"unresolved combined geometry at current {current}")
        filename = f"current-{current:g}.json"
        (args.output_dir / filename).write_text(
            json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
        row = {
            k: report[k]
            for k in (
                "current",
                "component_count",
                "pair_count",
                "methods",
                "static_pair_clearance_complete",
                "junction_flux_balances",
                "motion_certified",
                "material_dynamics_validated",
            )
        }
        row.update(
            port_count=len(report["ports"]),
            interface_count=len(report["interfaces"]),
            report=filename,
            maximum_port_relative_residual=max(
                p["relative_vector_residual"] for p in report["ports"]
            ),
        )
        cases.append(row)
        print(json.dumps(row), flush=True)
    manifest = {
        "scope": report["scope"],
        "cases": cases,
        "source_sha256": {
            str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / "src").glob("toroidal_*.py"))
        },
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
