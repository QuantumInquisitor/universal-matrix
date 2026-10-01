"""Controls for material-tree versus Seed/Vesica recursive correspondence."""

import numpy as np
import pytest

from scripts.report_fold_recursive_seed_correspondence import (
    MAX_AUDIT_DEPTH,
    RECIPROCAL_RING_PAIRS,
    binary_axis_tree,
    contained_vesica_exact_depth,
    material_exact_level,
    mirror_closed_four_address_subsets,
    report,
    vesica_mirror_pairs,
)


@pytest.fixture(scope="module")
def result():
    return report()


def test_material_and_vesica_recursions_are_not_silently_identified(result):
    comparison = result["direct_topology_comparison"]
    assert comparison["material_children_per_node"] == 2
    assert comparison["vesica_children_per_vessel"] == 12
    assert not comparison["direct_edge_scale_match"]
    assert not comparison["same_recursive_graph"]
    assert not result["material_tree_identified_with_full_vesica_recursion"]
    assert not result["full_vesica_recursion_replaced"]


def test_alternating_scale_cadence_matches_exactly(result):
    for row in result["alternating_scale_cadence"]:
        assert row["scale_error"] < 1e-15
    assert [row["stage"] for row in result["alternating_scale_cadence"]] == [
        "contained_vessel",
        "seed_circle",
        "contained_vessel",
        "seed_circle",
    ]


def test_two_material_levels_match_vesica_scale_but_not_branch_count(result):
    row = result["two_material_levels_vs_one_vesica_step"]
    assert row["material_descendants"] == 4
    assert row["vesica_addresses"] == 12
    assert row["scale_match"]
    assert not row["count_match"]


def test_vesica_mirror_partition_has_six_pairs_and_fifteen_four_subsets(result):
    pairs = vesica_mirror_pairs()
    assert len(pairs) == 6
    assert len({index for pair in pairs for index in pair}) == 12
    for left, right in pairs:
        assert left != right
    subsets = mirror_closed_four_address_subsets()
    assert len(subsets) == 15
    assert len(set(subsets)) == 15
    assert all(len(row) == 4 for row in subsets)
    assert result["vesica_mirror_pair_count"] == 6
    assert result["mirror_closed_four_address_subset_count"] == 15


def test_binary_seed_axis_candidates_match_material_counts_scale_containment_and_mirror(result):
    assert result["binary_seed_axis_candidate_count"] == 3
    for candidate in result["binary_seed_axis_candidates"]:
        assert tuple(candidate["axis_pair"]) in RECIPROCAL_RING_PAIRS
        assert candidate["maximum_containment_failure"] == 0
        assert candidate["maximum_mirror_center_error"] < 1e-14
        assert candidate["maximum_radius_error"] < 1e-14
        for row in candidate["levels"]:
            assert row["count"] == row["expected_count"] == 2 ** row["depth"]
            assert all(abs(node["radius"] - row["expected_scale"]) < 1e-14 for node in row["nodes"])


def test_three_axis_candidates_are_symmetry_related_but_not_selected_canonical(result):
    finals = []
    for candidate in result["binary_seed_axis_candidates"]:
        centers = np.asarray([node["center"] for node in candidate["levels"][1]["nodes"]])
        finals.append(np.sort(np.linalg.norm(centers, axis=1)))
    for row in finals[1:]:
        np.testing.assert_allclose(row, finals[0], rtol=0, atol=1e-14)
    assert not result["binary_axis_candidate_is_canonical"]


def test_spatial_and_joint_claim_boundaries_remain_open(result):
    assert not result["spatial_material_body_placement_validated"]
    assert not result["physical_joint_correspondence_validated"]


@pytest.mark.parametrize("depth", [-1, 4, True, 1.5, None])
def test_invalid_material_depth_rejected(depth):
    with pytest.raises(ValueError):
        material_exact_level(depth)


@pytest.mark.parametrize("depth", [-1, True, 1.5, None])
def test_invalid_vesica_depth_rejected(depth):
    with pytest.raises(ValueError):
        contained_vesica_exact_depth(depth)


@pytest.mark.parametrize("pair", [(1, 2), (0, 3), (1, 5), None])
def test_invalid_axis_candidate_rejected(pair):
    with pytest.raises(ValueError):
        binary_axis_tree(pair)


def test_max_audit_depth_is_current_material_depth_three():
    assert MAX_AUDIT_DEPTH == 3
