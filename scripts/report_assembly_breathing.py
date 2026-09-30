"""Export the prescribed full-assembly breathing control and its limits."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.toroidal_assembly_breathing import audit_assembly_breathing  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/assembly-breathing")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    cases = []
    for current in (1.0, -1.0, 2e-8, -2e-8, 7.0, -7.0):
        report = audit_assembly_breathing(current)
        filename = f"current-{current:g}.json"
        (args.output_dir / filename).write_text(
            json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
        row = {k: v for k, v in report.items() if k not in ("moving_cut_diagnostics", "argument")}
        row["report"] = filename
        cases.append(row)
        print(json.dumps(row), flush=True)
    manifest = {
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
