import pytest

from src.canonical_kernel import BOUNDARY_GATES, N_CORE
from src.seed_matrix_bridge import (
    assignment_gate_ids,
    center_core_states,
    elemental_gate_pairs,
    gate_assignments,
)
from src.sevenfold_seed_contract import SeedModel


def test_seed_center_contains_complete_core_without_seven_way_partition():
    assert center_core_states() == tuple(range(N_CORE))
    assert len(center_core_states()) == 108


def test_all_opposite_preserving_gate_orientations_remain_available():
    assignments = gate_assignments()

    assert len(assignments) == 48
    assert len(set(assignments)) == 48
    assert all(set(assignment) == set(BOUNDARY_GATES) for assignment in assignments)


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
    pairs = elemental_gate_pairs(model, gate_assignments()[17])
    assert len(pairs) == 3
    assert {name for pair in pairs for name in (pair[0], pair[2])} == {
        mode_name
        for mode_name in {
            pair[0] for pair in elemental_gate_pairs(model, gate_assignments()[0])
        }
        | {
            pair[2] for pair in elemental_gate_pairs(model, gate_assignments()[0])
        }
    }


def test_invalid_gate_assignment_is_rejected():
    with pytest.raises(ValueError):
        assignment_gate_ids(("X_POS",) * 6)
