import math

import numpy as np
import pytest

from src.lynchpin_finite_panel_control import (
    audit_core_cycle,
    deformation_metrics,
    panel_speed_bound,
    panel_vertices,
    pentagon_coefficients,
    separation_bound,
)
from src.lynchpin_geometry_audit import LYNCHPIN_PANELS
from src.lynchpin_relative_motion_control import compliant_rays, reference_rays


def test_full_pentagons_reuse_shared_ray_edges_and_four_dimensional_regular_shape():
    rays = reference_rays(4)
    for index, (i, j) in enumerate(LYNCHPIN_PANELS):
        vertices = panel_vertices(0, 4, index)
        np.testing.assert_allclose(vertices[0], 0, atol=1e-14)
        np.testing.assert_allclose(vertices[1], rays[i], atol=1e-14)
        np.testing.assert_allclose(vertices[-1], rays[j], atol=1e-14)
        np.testing.assert_allclose(
            np.linalg.norm(np.roll(vertices, -1, axis=0) - vertices, axis=1), 1, atol=1e-14
        )


@pytest.mark.parametrize("dimension", (3, 4))
def test_deformation_matches_independent_equal_ray_gram_eigenvalues(dimension):
    original = reference_rays(dimension)
    for phase in (0, 0.2, 0.5, 0.8, 1):
        rays = compliant_rays(phase, dimension)
        for index, (i, j) in enumerate(LYNCHPIN_PANELS):
            initial_cosine = original[i] @ original[j]
            current_cosine = rays[i] @ rays[j]
            expected = sorted(
                (
                    math.sqrt((1 + current_cosine) / (1 + initial_cosine)),
                    math.sqrt((1 - current_cosine) / (1 - initial_cosine)),
                )
            )
            actual = deformation_metrics(phase, dimension, index)
            np.testing.assert_allclose(actual["principal_stretches"], expected, atol=1e-14)
            assert actual["area_ratio"] == pytest.approx(math.prod(expected))
            assert min(actual["principal_stretches"]) > 0


@pytest.mark.parametrize("dimension", (3, 4))
def test_velocity_bound_dominates_independently_differentiated_vertices(dimension):
    h = 1e-6
    for phase in (0.1, 0.25, 0.4, 0.7, 0.9):
        for panel in range(6):
            numerical = (
                panel_vertices(phase + h, dimension, panel, 0.15)
                - panel_vertices(phase - h, dimension, panel, 0.15)
            ) / (2 * h)
            assert (
                max(np.linalg.norm(numerical, axis=1))
                <= panel_speed_bound(dimension, panel, 0.15) + 1e-8
            )


@pytest.mark.parametrize("dimension", (3, 4))
def test_all_panel_pairs_cover_the_whole_cycle_with_positive_bounds(dimension):
    result = audit_core_cycle(dimension)
    assert result["accepted"]
    assert result["pair_count"] == 15
    assert not result["complete_hinge_assembly_certified"]
    for pair in result["pairs"]:
        leaves = sorted(pair["leaves"], key=lambda x: x["interval"][0])
        assert leaves[0]["interval"][0] == 0
        assert leaves[-1]["interval"][1] == 1
        assert all(
            a["interval"][1] == b["interval"][0]
            for a, b in zip(leaves[:-1], leaves[1:], strict=True)
        )
        assert all(
            leaf["status"] == "clear" and leaf["clearance_lower_bound"] > 0 for leaf in leaves
        )


@pytest.mark.parametrize("dimension", (3, 4))
def test_separating_plane_is_valid_for_known_offset_polygons(dimension):
    left = np.zeros((4, dimension))
    left[:, :2] = ((0, 0), (1, 0), (1, 1), (0, 1))
    right = left.copy()
    right[:, -1] += 2
    result = separation_bound(left, right)
    assert result["lower_bound"] == pytest.approx(2)
    assert result["witness_distance"] == pytest.approx(2)
    axis = np.array(result["axis"])
    assert np.min(right @ axis) - np.max(left @ axis) == pytest.approx(result["lower_bound"])


def test_untrimmed_adjacent_panels_intersect_at_the_intended_hinge():
    # Panels 01 and 02 share the origin-to-ray-0 edge. Their full offsets overlap.
    a, b = panel_vertices(0.3, 3, 0), panel_vertices(0.3, 3, 1)
    np.testing.assert_allclose(a[:2], b[:2], atol=1e-14)
    assert separation_bound(a, b)["witness_distance"] < 0.02
    assert np.all(pentagon_coefficients(0.15) >= 0.15 - 1e-14)


def test_excessive_thickness_is_rejected_as_geometry_not_certified():
    result = audit_core_cycle(3, thickness=10, maximum_depth=0)
    assert not result["accepted"]
    assert any(
        leaf["status"] == "offset_overlap_witness"
        for pair in result["pairs"]
        for leaf in pair["leaves"]
    )


@pytest.mark.parametrize("collar", (-1, 0.3, float("nan"), True, 1j))
def test_invalid_collar_rejected(collar):
    with pytest.raises(ValueError):
        pentagon_coefficients(collar)
