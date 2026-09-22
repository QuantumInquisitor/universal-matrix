import pytest

from src.canonical_kernel import BOUNDARY_GATES, N_CORE
from src.seed_matrix_bridge import (
    assignment_determinant,
    assignment_gate_ids,
    center_core_states,
    elemental_gate_pairs,
    gate_assignments,
)
from src.sevenfold_seed_contract import SeedModel, reciprocal_pairs


def test_seed_center_contains_complete_core_without_seven_way_partition():
    assert center_core_states() == tuple(range(N_CORE))
    assert len(center_core_states()) == 108


def test_all_opposite_preserving_signed_frames_remain_available():
    assignments = gate_assignments()

    assert len(assignments) == 48
    assert len(set(assignments)) == 48
    assert all(set(assignment) == set(BOUNDARY_GATES) for assignment in assignments)


def test_signed_frames_split_evenly_between_rotations_and_reflections():
    determinants = [assignment_determinant(frame) for frame in gate_assignments()]

    assert determinants.count(1) == 24
    assert determinants.count(-1) == 24


@pytest.mark.parametrize("assignment", gate_assignments())
def test_opposite_seed_positions_map_to_opposite_spatial_gates(assignment):
    for near, far in ((0, 3), (1, 4), (2, 5)):
        near_axis, near_sign = assignment[near].split("_")
        far_axis, far_sign = assignment[far].split("_")
        assert near_axis == far_axis
        assert {near_sign, far_sign} == {"POS", "NEG"}


def test_assignment_maps_to_exact_six_boundary_node_ids():
    ids = assignment_gate_ids(gate_assignments()[0])
    assert set(ids) == set(range(108, 114))


@pytest.mark.parametrize("model", list(SeedModel))
def test_every_elemental_model_can_label_any_valid_gate_frame(model):
    assignment = gate_assignments()[17]
    expected = tuple(
        (
            left.name,
            assignment[left.position - 1],
            right.name,
            assignment[right.position - 1],
        )
        for left, right in reciprocal_pairs(model)
    )

    assert elemental_gate_pairs(model, assignment) == expected


def test_bijective_assignment_that_breaks_opposite_pairs_is_rejected():
    invalid_frame = (
        "X_POS",
        "X_NEG",
        "Y_POS",
        "Y_NEG",
        "Z_POS",
        "Z_NEG",
    )

    with pytest.raises(ValueError, match="opposite Seed positions"):
        assignment_gate_ids(invalid_frame)


def test_reflected_frame_is_reported_exactly():
    reflected = (
        "X_NEG",
        "Y_POS",
        "Z_POS",
        "X_POS",
        "Y_NEG",
        "Z_NEG",
    )

    assert assignment_determinant(reflected) == -1


def test_proper_rotation_is_reported_exactly():
    proper = (
        "X_POS",
        "Y_POS",
        "Z_POS",
        "X_NEG",
        "Y_NEG",
        "Z_NEG",
    )

    assert assignment_determinant(proper) == 1


def test_invalid_gate_assignment_is_rejected():
    with pytest.raises(ValueError):
        assignment_gate_ids(("X_POS",) * 6)
