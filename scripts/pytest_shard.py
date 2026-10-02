"""File-preserving pytest partition with complete collection/execution evidence."""

import hashlib
import json
from pathlib import Path

import pytest


def owner(nodeid, count):
    path = nodeid.split("::", 1)[0].replace("\\", "/")
    return int.from_bytes(hashlib.sha256(path.encode()).digest()[:8], "big") % count


def pytest_addoption(parser):
    parser.addoption("--suite-shard-index", type=int, default=0)
    parser.addoption("--suite-shard-count", type=int, default=1)
    parser.addoption("--suite-shard-manifest", required=True)


def pytest_configure(config):
    index, count = config.getoption("suite_shard_index"), config.getoption("suite_shard_count")
    if not 1 <= count <= 64 or not 0 <= index < count:
        raise pytest.UsageError("shard index must be in [0,count), count in [1,64]")
    config._suite_manifest = dict(index=index, count=count, collected=[], selected=[], completed=[])
    config.pluginmanager.register(ExecutionRecorder(config), "suite-execution-recorder")


class ExecutionRecorder:
    def __init__(self, config):
        self.config = config

    def pytest_runtest_logreport(self, report):
        if report.when == "teardown":
            self.config._suite_manifest["completed"].append(report.nodeid)


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config, items):
    manifest = config._suite_manifest
    manifest["collected"] = [item.nodeid for item in items]
    selected, excluded = [], []
    for item in items:
        target = (
            selected if owner(item.nodeid, manifest["count"]) == manifest["index"] else excluded
        )
        target.append(item)
    manifest["selected"] = [item.nodeid for item in selected]
    items[:] = selected
    config.hook.pytest_deselected(items=excluded)


def pytest_sessionfinish(session, exitstatus):
    manifest = session.config._suite_manifest
    if exitstatus == 5 and manifest["collected"] and not manifest["selected"]:
        session.exitstatus = 0  # A legitimately empty partition, not an empty suite.
    manifest["exitstatus"] = int(session.exitstatus)
    path = Path(session.config.getoption("suite_shard_manifest"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
