"""Verify archived original numerical evidence without rerunning experiments."""

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile


def verify(directory):
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != "numerical-evidence-backup-v1":
        raise ValueError("unsupported evidence manifest")
    count = 0
    for item in manifest["artifacts"]:
        name = item["archive"]
        if Path(name).name != name or "/" in name or "\\" in name:
            raise ValueError("archive must be a local basename")
        archive = directory / name
        data = archive.read_bytes()
        if len(data) != item["bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise ValueError(f"archive bytes differ: {name}")
        with ZipFile(archive) as zipped:
            names = [member["name"] for member in item["members"]]
            if sorted(zipped.namelist()) != sorted(names) or len(set(names)) != len(names):
                raise ValueError(f"member inventory differs: {name}")
            for member in item["members"]:
                raw = zipped.read(member["name"])
                if (
                    len(raw) != member["bytes"]
                    or hashlib.sha256(raw).hexdigest() != member["sha256"]
                ):
                    raise ValueError(f"member bytes differ: {member['name']}")
                json.loads(raw)
        count += 1
    if count != 3:
        raise ValueError("this frozen backup must contain all three reviewed artifacts")
    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--directory",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "docs/recovery/evidence",
    )
    args = parser.parse_args()
    print(f"Verified {verify(args.directory)} original archives and their JSON members.")
