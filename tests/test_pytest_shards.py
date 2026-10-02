"""Exercise real pytest collection, partitioning, failures and manifest rejection."""

import copy
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.pytest_shard import owner
from scripts.verify_pytest_shards import verify


def run(tmp_path, index, count):
    manifest = tmp_path / f"shard-{index}.json"
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "scripts.pytest_shard",
            "--suite-shard-index",
            str(index),
            "--suite-shard-count",
            str(count),
            "--suite-shard-manifest",
            str(manifest),
            str(tmp_path),
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return result.returncode, json.loads(manifest.read_text())


@pytest.fixture(scope="module")
def manifests(tmp_path_factory):
    path = tmp_path_factory.mktemp("partition")
    for n in range(12):
        (path / f"test_example_{n}.py").write_text(
            "import pytest\n@pytest.mark.parametrize('value',[1,2,3])\n"
            "def test_value(value): assert value > 0\n"
        )
    result = [run(path, i, 8) for i in range(8)]
    assert all(code == 0 for code, _ in result)
    return [m for _, m in result]


def test_full_collection_exactly_once(manifests):
    assert verify(manifests, 8) == 36
    assert owner("tests/a.py::test_x[1]", 8) == owner("tests/a.py::test_y", 8)


@pytest.mark.parametrize("fault", ["missing", "duplicate", "failed", "collection", "execution"])
def test_rejects_broken_coverage(manifests, fault):
    m = copy.deepcopy(manifests)
    nonempty = next(x for x in m if x["selected"])
    if fault == "missing":
        m.pop()
    elif fault == "duplicate":
        m[-1] = m[0]
    elif fault == "failed":
        m[0]["exitstatus"] = 1
    elif fault == "collection":
        m[0]["collected"].pop()
    else:
        nonempty["completed"].pop()
    with pytest.raises(ValueError):
        verify(m, 8)


def test_real_failure_is_not_hidden(tmp_path):
    (tmp_path / "test_failure.py").write_text("def test_failure(): assert False\n")
    code, manifest = run(tmp_path, 0, 1)
    assert code == 1
    with pytest.raises(ValueError):
        verify([manifest], 1)
