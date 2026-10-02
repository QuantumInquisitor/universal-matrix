"""Generate a bounded computed example using the existing material adapter."""

import hashlib
import json
import sys
from pathlib import Path

from scripts.export_fold_material_viewer_frames import export
from scripts.report_fold_material_supply import simulate

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    case = simulate(duration=0.4)
    sources = {}
    for module in list(sys.modules.values()):
        path = getattr(module, "__file__", None)
        if path and Path(path).parent == root / "scripts":
            p = Path(path)
            sources[p.name] = hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest()
    source = root / "docs/experiments/material-viewer-source.json"
    source.write_text(
        json.dumps(
            dict(
                schema=1,
                cases=dict(powered=case),
                sources=sources,
                scope="0.4 s synthetic material supply example; not calibrated",
                source_hash_encoding="UTF-8/LF",
            ),
            indent=2,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )
    data = export(source)
    data["source_report"]["path"] = "../experiments/material-viewer-source.json"
    (root / "docs/docs/material-viewer-example.json").write_text(
        json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
