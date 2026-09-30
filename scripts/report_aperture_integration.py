"""Reproduce the fixed aperture, outer attachment and replacement-route audits."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.toroidal_aperture_attachment import (  # noqa: E402
    audit_aperture_attachment,
    build_aperture_attachment,
)
from src.toroidal_aperture_fanout import run as fanout_run  # noqa: E402
from src.toroidal_outer_attachment import run as outer_run  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/aperture")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summaries = []
    for current in (1.0, -1.0, 2e-8, -2e-8, 7.0, -7.0):
        attachment = audit_aperture_attachment(build_aperture_attachment(current))
        outer = outer_run(current)
        fanout = fanout_run(current)
        if not outer["candidate_accepted"] or not fanout["certified"]:
            raise RuntimeError(f"fixed geometry audit rejected current {current}")
        if fanout["full_network_certified"] or fanout["motion_certified"]:
            raise RuntimeError("scope flags incorrectly claim whole-network or motion completion")
        file = f"current-{current:g}.json"
        report = {"attachment": attachment, "outer": outer, "fanout": fanout}
        (args.output_dir / file).write_text(
            json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
        row = {
            "current": current,
            "inner_pairs": attachment["inner_pair_count"],
            "aperture_pairs": attachment["aperture_pair_count"],
            "outer_pairs": outer["pair_count"],
            "replacement_pairs": fanout["pair_count"],
            "outer_cut_flux_relative_error": outer["maximum_relative_cut_flux_residual"],
            "replacement_interfaces": len(fanout["interfaces"]),
            "outer_pass": outer["candidate_accepted"],
            "replacement_pass": fanout["certified"],
            "full_network_certified": False,
            "motion_certified": False,
            "report": file,
        }
        summaries.append(row)
        print(json.dumps(row), flush=True)
    source_names = [
        "toroidal_aperture_local.py",
        "toroidal_aperture_attachment.py",
        "toroidal_outer_attachment.py",
        "toroidal_aperture_fanout.py",
        "toroidal_retained_collision.py",
    ]
    manifest = {
        "scope": "Fixed changed-component inventories, not a combined whole-network certificate",
        "cases": summaries,
        "source_sha256": {
            f"src/{name}": hashlib.sha256((ROOT / "src" / name).read_bytes()).hexdigest()
            for name in source_names
        },
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
