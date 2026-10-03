from collections import Counter
from itertools import combinations

import numpy as np
import pytest
from scipy.optimize import linprog

from src.lynchpin_connected_control import (
    ATTACHMENT_RADIUS,
    BRIDGE_LENGTH,
    BRIDGE_RADIUS,
    HUB_RADIUS,
    _intervals,
    audit_connected_cycle,
    bodies,
    contact_check,
    scene,
)
from src.lynchpin_relative_motion_control import compliant_rays


def test_bond_graph_connects_all_material_bodies():
    parts = bodies()
    edges = []
    counts = Counter()
    for left, right in combinations(parts, 2):
        contact, _, _ = contact_check(left, right)
        counts[contact] += 1
        if contact != "separated":
            edges.append((left["name"], right["name"]))
    assert counts == {"separated": 195, "inside_shared_hub": 24, "inside_attachment_ball": 12}
    visited = {parts[0]["name"]}
    while True:
        following = (
            visited | {b for a, b in edges if a in visited} | {a for a, b in edges if b in visited}
        )
        if following == visited:
            break
        visited = following
    assert len(visited) == 22


@pytest.mark.parametrize("dimension", (3, 4))
def test_bridge_anchors_are_bonded_and_contact_regions_are_bounded(dimension):
    parts = {p["name"]: p for p in bodies()}
    for bridge in [p for p in parts.values() if p["kind"] == "bridge"]:
        hub = parts[f"hub-{bridge['hub']}"]
        panel = parts[f"panel-{bridge['panel']}"]
        np.testing.assert_array_equal(bridge["coefficients"][0], hub["coefficients"][0])
        # Independent convex membership of the bridge tip in its panel.
        coefficients = panel["coefficients"]
        membership = linprog(
            np.zeros(len(coefficients)),
            A_eq=np.vstack((coefficients.T, np.ones(len(coefficients)))),
            b_eq=np.r_[bridge["coefficients"][1], 1],
            bounds=(0, None),
            method="highs",
        )
        assert membership.success
        for phase in (0, 0.13, 0.5, 0.75, 1):
            rays = compliant_rays(phase, dimension)
            ends = bridge["coefficients"] @ rays
            assert np.linalg.norm(ends[1] - ends[0]) == pytest.approx(BRIDGE_LENGTH)
            _, _, prefix = contact_check(panel, bridge)
            assert np.linalg.norm(
                (bridge["coefficients"][1] - prefix[1]) @ rays
            ) + BRIDGE_RADIUS == pytest.approx(ATTACHMENT_RADIUS)
    for a, b in combinations(parts.values(), 2):
        if a["kind"] == b["kind"] == "bridge" and a["hub"] == b["hub"]:
            _, tail_a, tail_b = contact_check(a, b)
            for body, tail in ((a, tail_a), (b, tail_b)):
                for phase in (0, 0.5, 1):
                    assert np.linalg.norm(
                        (tail[0] - body["coefficients"][0]) @ compliant_rays(phase, dimension)
                    ) + BRIDGE_RADIUS == pytest.approx(HUB_RADIUS)


@pytest.mark.parametrize("dimension", (3, 4))
def test_breathing_scales_every_body_and_closes_cycle(dimension):
    for phase in (0, 0.25, 0.5, 0.75, 1):
        scale = 1 + 0.1 * np.sin(2 * np.pi * phase)
        for reference, breath in zip(
            scene(phase, dimension, 0), scene(phase, dimension), strict=True
        ):
            np.testing.assert_allclose(
                breath["vertices"], scale * np.array(reference["vertices"]), atol=1e-14
            )
            assert breath["offset_radius"] == pytest.approx(scale * reference["offset_radius"])
    for start, end in zip(scene(0, dimension), scene(1, dimension), strict=True):
        np.testing.assert_allclose(start["vertices"], end["vertices"], atol=1e-14)


def test_audit_rejects_actual_overlap_and_preserves_unresolved_status():
    point = np.array([[0.5, 0, 0, 0]])
    assert _intervals(point, point, 0.1, 3, 1)[0]["status"] == "overlap_witness"
    moving = np.array([[0, 0, 0, 0.5]])
    assert _intervals(0.98 * moving, moving, 0.001, 3, 0)[0]["status"] == "unresolved"


@pytest.mark.parametrize("depth", (-1, 13, True, 0.5))
def test_invalid_depth_is_rejected(depth):
    with pytest.raises(ValueError):
        audit_connected_cycle(maximum_depth=depth)
