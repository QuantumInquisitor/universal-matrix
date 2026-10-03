"""Model identity gates, without new distributed replay or restart dynamics."""

import copy
import json
from pathlib import Path

import numpy as np
import pytest

from scripts.export_fold_material_viewer_frames import adapt
from scripts.material_model_identity import point_powered_identity
from scripts.report_fold_material_persistence import advance, checkpoint, restore_checkpoint
from scripts.report_fold_material_supply import initial_state


def source():
    return json.loads(
        Path("docs/experiments/material-viewer-source.json").read_text(encoding="utf-8")
    )


def test_legacy_export_is_explicitly_labeled_and_does_not_mutate_source():
    report = source()
    report.pop("model_identity", None)
    before = copy.deepcopy(report)
    exported = adapt(report)
    assert exported["model_identity"] == point_powered_identity()
    assert exported["source_identity_basis"] == "legacy-point-assumption"
    assert report == before
    report["model_identity"] = point_powered_identity()
    explicit = adapt(report)
    assert explicit["source_identity_basis"] == "explicit-point-identity"
    assert explicit["frames"] == exported["frames"]


@pytest.mark.parametrize(
    "identity",
    [
        None,
        {},
        "point",
        dict(point_powered_identity(), inertia_model="distributed-reference-quadrature-v1"),
        dict(point_powered_identity(), state_layout="material-passive-node5-edge2-v1"),
        dict(point_powered_identity(), energy_ownership="connector-potential-split-across-nodes"),
        dict(point_powered_identity(), extra="unknown"),
    ],
)
def test_explicit_foreign_or_malformed_identity_never_falls_back(identity):
    report = source()
    report["model_identity"] = identity
    with pytest.raises(ValueError, match="inertia"):
        adapt(report)
    saved = checkpoint(initial_state())
    saved["model_identity"] = identity
    with pytest.raises(ValueError, match="inertia"):
        advance(saved, 0.001)


@pytest.mark.parametrize(
    "change",
    [
        lambda d: d.pop("model_identity"),
        lambda d: d.update(schema="fold-distributed-graph-trajectories-v1"),
        lambda d: d["sizes"].__setitem__(1, 0.5),
        lambda d: d["edges"][0].__setitem__(1, 2),
        lambda d: d["sizes"].__setitem__(0, True),
        lambda d: d["edges"][0].__setitem__(0, False),
        lambda d: d["edges"][0].__setitem__(0, 0.0),
        lambda d: d["edges"][0].__setitem__(2, True),
        lambda d: d["state"].pop(),
        lambda d: d["state"].__setitem__(0, float("nan")),
    ],
)
def test_checkpoint_rejects_missing_identity_topology_or_state_corruption(change):
    saved = checkpoint(initial_state())
    change(saved)
    with pytest.raises(ValueError):
        restore_checkpoint(saved)


def test_typed_finite_roundtrip_retains_nonzero_ledgers_and_legacy_numerics():
    raw = initial_state()
    blocks = raw[:36].reshape(4, 9)
    blocks[:, 5:] = np.arange(16).reshape(4, 4) * 1e-9
    raw[36:] = np.arange(12) * 1e-9
    saved = checkpoint(raw)
    restored = restore_checkpoint(json.loads(json.dumps(saved, allow_nan=False)))
    np.testing.assert_array_equal(restored, raw)
    restored[0] += 0.01
    assert saved["state"][0] == raw[0]
    typed = advance(saved, 0.001)
    legacy = advance(raw, 0.001)
    np.testing.assert_array_equal(typed["final_state"], legacy["final_state"])
    np.testing.assert_array_equal(restore_checkpoint(typed["checkpoint"]), typed["final_state"])
    assert typed["model_identity"] == point_powered_identity()
    assert max(typed["max_group_residual_j"].values()) < 1e-10


def test_known_distributed_report_schema_cannot_be_reinterpreted_as_powered():
    report = source()
    report["schema"] = "fold-distributed-graph-trajectories-v1"
    with pytest.raises(ValueError, match="schema"):
        adapt(report)


def test_foreign_case_identity_cannot_hide_under_legacy_report():
    report = source()
    report.pop("model_identity", None)
    report["cases"]["powered"]["model_identity"] = dict(
        point_powered_identity(), inertia_model="distributed-reference-quadrature-v1"
    )
    with pytest.raises(ValueError, match="inertia"):
        adapt(report)


@pytest.mark.parametrize("schema", [True, 1.0, "1"])
def test_legacy_schema_must_be_exact_integer_one(schema):
    report = source()
    report["schema"] = schema
    with pytest.raises(ValueError, match="schema"):
        adapt(report)
