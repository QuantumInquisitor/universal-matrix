from __future__ import annotations

import math

from src.sri_yantra_spherical_topology_control import (
    SPHERICAL_TOPOLOGY_CONTROL,
    chamber_incidence_signature,
    lift_segment_point,
    mapped_nodes_are_injective,
    mirror_equivariant,
    planar_roundtrip_closes,
    recover_planar_point,
    ring_cycle_signature,
    selected_vertices_lie_in_open_northern_hemisphere,
    sphere_norm,
    topology_change_detected,
)


def test_all_spherical_control_nodes_lie_on_the_unit_sphere():
    control = SPHERICAL_TOPOLOGY_CONTROL

    assert all(
        math.isclose(sphere_norm(point), 1.0, abs_tol=1e-12)
        for point in control.node_points
    )


def test_spherical_control_is_injective_and_roundtrips_to_the_planar_complex():
    control = SPHERICAL_TOPOLOGY_CONTROL

    assert mapped_nodes_are_injective(control)
    assert planar_roundtrip_closes(control)


def test_selected_chamber_vertices_remain_in_the_open_northern_hemisphere():
    assert selected_vertices_lie_in_open_northern_hemisphere(
        SPHERICAL_TOPOLOGY_CONTROL
    )


def test_planar_mirror_commutes_with_the_spherical_control_lift():
    assert mirror_equivariant(SPHERICAL_TOPOLOGY_CONTROL)


def test_complete_43_chamber_incidence_is_carried_without_reindexing():
    control = SPHERICAL_TOPOLOGY_CONTROL

    assert len(chamber_incidence_signature(control)) == 43
    assert control.chamber_count == 43
    assert control.ring_counts == (1, 8, 10, 10, 14)
    assert control.ring_vertex_counts == (3, 16, 20, 20, 28)
    assert control.chamber_edge_count == 129


def test_all_four_ring_cycles_survive_the_control_lift():
    signature = ring_cycle_signature(SPHERICAL_TOPOLOGY_CONTROL)

    assert tuple(item[0] for item in signature) == (
        "eight",
        "inner_ten",
        "outer_ten",
        "fourteen",
    )
    assert tuple(item[1] for item in signature) == (8, 10, 10, 14)


def test_lifted_edge_path_is_the_image_of_the_complete_planar_segment():
    control = SPHERICAL_TOPOLOGY_CONTROL
    system = control.planar
    central = system.candidates[system.central_candidate_id]
    first_id, second_id = central.vertex_ids[:2]
    start = system.nodes[first_id]
    end = system.nodes[second_id]

    for parameter in (0.0, 0.125, 0.5, 0.875, 1.0):
        spherical = lift_segment_point(
            start,
            end,
            parameter,
            control.normalization,
        )
        recovered = recover_planar_point(
            spherical,
            control.normalization,
        )
        expected = (
            start[0] + parameter * (end[0] - start[0]),
            start[1] + parameter * (end[1] - start[1]),
        )
        assert math.isclose(recovered[0], expected[0], abs_tol=1e-12)
        assert math.isclose(recovered[1], expected[1], abs_tol=1e-12)


def test_no_topology_change_occurs_in_the_homeomorphic_control():
    assert not topology_change_detected(SPHERICAL_TOPOLOGY_CONTROL)
