from __future__ import annotations

import math

import pytest

from src.sri_yantra_spherical_topology_control import (
    SPHERICAL_TOPOLOGY_CONTROL,
    PlanarNormalization,
    chamber_incidence_signature,
    forward_stereographic,
    inverse_stereographic,
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
        math.isclose(sphere_norm(point), 1.0, abs_tol=1e-12) for point in control.node_points
    )


def test_spherical_control_is_injective_and_roundtrips_to_the_planar_complex():
    control = SPHERICAL_TOPOLOGY_CONTROL

    assert mapped_nodes_are_injective(control)
    assert planar_roundtrip_closes(control)


def test_selected_chamber_vertices_remain_in_the_open_northern_hemisphere():
    assert selected_vertices_lie_in_open_northern_hemisphere(SPHERICAL_TOPOLOGY_CONTROL)


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
    edge_count = 0
    for candidate_id in system.selected_candidate_ids:
        vertices = system.candidates[candidate_id].vertex_ids
        for first_id, second_id in zip(vertices, vertices[1:] + vertices[:1], strict=True):
            start, end = system.nodes[first_id], system.nodes[second_id]
            edge_count += 1
            for parameter in (0.0, 0.125, 0.5, 0.875, 1.0):
                spherical = lift_segment_point(start, end, parameter, control.normalization)
                recovered = recover_planar_point(spherical, control.normalization)
                expected = (
                    start[0] + parameter * (end[0] - start[0]),
                    start[1] + parameter * (end[1] - start[1]),
                )
                assert math.dist(recovered, expected) < 1e-12
                assert sphere_norm(spherical) == pytest.approx(1.0, abs=1e-12)
    assert edge_count == 129


def test_no_topology_change_occurs_in_the_homeomorphic_control():
    assert not topology_change_detected(SPHERICAL_TOPOLOGY_CONTROL)


@pytest.mark.parametrize("invalid", [math.nan, math.inf, -math.inf])
def test_nonfinite_normalization_coordinates_and_parameters_are_rejected(invalid):
    with pytest.raises(ValueError, match="finite"):
        PlanarNormalization(invalid, 1.0)
    with pytest.raises(ValueError, match="finite"):
        PlanarNormalization(0.0, invalid)
    with pytest.raises(ValueError, match="finite"):
        inverse_stereographic((invalid, 0.0))
    with pytest.raises(ValueError, match="finite"):
        forward_stereographic((0.0, 0.0, invalid))
    with pytest.raises(ValueError, match="finite"):
        lift_segment_point((0, 0), (1, 0), invalid, PlanarNormalization(0, 1))


def test_off_sphere_and_singular_or_overflowing_chart_points_are_rejected():
    with pytest.raises(ValueError, match="unit sphere"):
        forward_stereographic((0, 0, 2))
    with pytest.raises(ValueError, match="south pole"):
        forward_stereographic((0, 0, -1))
    with pytest.raises(ValueError, match="finite"):
        inverse_stereographic((1e308, 0))


def test_control_edge_is_not_silently_replaced_by_a_great_circle():
    # A generic stereographic image of a line lies on a small circle.
    normalization = PlanarNormalization(0.0, 1.0)
    samples = [lift_segment_point((0.1, 0.2), (0.6, 0.2), t, normalization) for t in (0, 0.5, 1)]
    a, middle, b = samples
    normal = (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    assert abs(sum(n * p for n, p in zip(normal, middle, strict=True))) > 1e-3
