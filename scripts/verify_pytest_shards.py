"""Reject omitted, duplicated, incomplete, failed or inconsistent pytest shards."""

import argparse
import json
from pathlib import Path

from scripts.pytest_shard import owner


def verify(manifests, count):
    if len(manifests) != count or {m["index"] for m in manifests} != set(range(count)):
        raise ValueError("missing or duplicate shards")
    expected = manifests[0]["collected"]
    if not expected or len(set(expected)) != len(expected):
        raise ValueError("empty or duplicate test collection")
    selected = []
    for m in manifests:
        if m["count"] != count or m["collected"] != expected or m["exitstatus"] != 0:
            raise ValueError("inconsistent collection or failed shard")
        assigned = [node for node in expected if owner(node, count) == m["index"]]
        if m["selected"] != assigned or sorted(m["completed"]) != sorted(assigned):
            raise ValueError("incorrect assignment or incomplete execution")
        selected.extend(m["selected"])
    if sorted(selected) != sorted(expected):
        raise ValueError("test partition is not complete and disjoint")
    return len(expected)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--count", type=int, required=True)
    args = parser.parse_args()
    manifests = [json.loads(p.read_text()) for p in sorted(args.directory.rglob("shard-*.json"))]
    print(f"Verified {verify(manifests, args.count)} collected tests across {args.count} shards")
