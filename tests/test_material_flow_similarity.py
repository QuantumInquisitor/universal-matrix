import math

import numpy as np
import pytest

from scripts import report_material_flow_similarity as audit
from scripts.report_fold_kinematics import kinematics
from scripts.report_material_flow_similarity import (
    analytic_hub_ratio,
    hub_ratio,
    normalized_distances,
    report,
)


def test_similarity_invariance_and_anisotropic_negative_control():
    state = kinematics((1, math.pi / 12))
    ids, points = state["ids"], state["position"]
    labels, expected = normalized_distances(ids, points)
    rotation = np.array(((0, 0, 1), (1, 0, 0), (0, 1, 0)))
    for scale in (0.001, 0.9, 1.1, 100):
        pair_ids, actual = normalized_distances(ids, scale * points @ rotation + (1, -2, 3))
        assert pair_ids == labels
        np.testing.assert_allclose(actual, expected, atol=1e-12, rtol=0)
    _, changed = normalized_distances(ids, points * (1, 2, 1))
    assert np.max(abs(changed - expected)) > 1e-4


@pytest.mark.parametrize("scale", (0.9, 1, 1.1))
@pytest.mark.parametrize("length", (0.01, 0.1, 1))
def test_independent_hub_ratio_endpoints_and_basis_sign(scale, length):
    assert analytic_hub_ratio(0) == pytest.approx(1, abs=1e-14)
    assert analytic_hub_ratio(math.pi / 6) == pytest.approx(2 / 3, abs=1e-14)
    for theta in (0, math.pi / 12, math.pi / 6):
        measured = hub_ratio(kinematics((scale, theta), length_m=length))
        assert measured == pytest.approx(analytic_hub_ratio(theta), abs=1e-14)
    assert hub_ratio(kinematics((scale, math.pi / 12), length_m=length)) < 1


def test_cross_adapter_report_and_scope():
    result = report()
    assert len(result["point_ids"]) == 22
    assert result["labeled_pair_count"] == 231
    assert len(result["samples"]) == 17
    initial, midpoint, final = (result["samples"][i] for i in (0, 8, 16))
    assert initial["q"][0] == midpoint["q"][0] == final["q"][0] == 1
    assert midpoint["material_shape_change"] > 1e-4
    assert final["material_shape_change"] < 1e-12
    for row in result["samples"]:
        assert row["common_scale_difference"] < 1e-12
        assert row["material_scale_only_error"] < 1e-12
        assert row["flow_common_scale_error"] < 1e-12
    for flag in (
        "actual_material_to_flow_correspondence",
        "arbitrary_nonlinear_correspondence_ruled_out",
        "clearance_audited",
        "physical_attachment_validated",
    ):
        assert result[flag] is False


def test_rejects_changed_owner_order(monkeypatch):
    calls = 0

    def changed(q):
        nonlocal calls
        state = kinematics(q)
        calls += 1
        if calls == 2:
            state["ids"] = state["ids"][::-1]
        return state

    monkeypatch.setattr(audit, "kinematics", changed)
    with pytest.raises(ValueError, match="owner identities"):
        report()


@pytest.mark.parametrize(
    "ids,points",
    [
        (["a", "a"], [[0, 0, 0], [1, 0, 0]]),
        (["a", "b"], [[0, 0, 0], [0, 0, 0]]),
        (["a", "b"], [[0, 0, 0], [math.nan, 0, 0]]),
        (["a", "b"], [[0, 0], [1, 0]]),
    ],
)
def test_rejects_ambiguous_or_degenerate_points(ids, points):
    with pytest.raises(ValueError):
        normalized_distances(ids, points)
