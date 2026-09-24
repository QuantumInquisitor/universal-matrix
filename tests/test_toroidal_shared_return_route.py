from __future__ import annotations

import math
from dataclasses import replace

import numpy as np
import pytest

from src.toroidal_incident_bend_audit import BendSamplingGrid
from src.toroidal_separated_channels import build_separated_framed_edge_network
from src.toroidal_shared_return_route import (
    box_clearance,
    certify_shared_return_endpoint,
    certify_unchanged_edge_separation,
    move_inner_return_to_shared_route,
    routed_tube_pieces,
    sample_moved_return_collisions,
)
from src.toroidal_smooth_bends import AnnularQuarterBend, build_smooth_global_toroidal_routing
from src.vesica_tree_circulation import PORT_NODES, vesica_circulation


def _reference(current=1.0):
    network = build_separated_framed_edge_network(
        vesica_circulation(current, return_split=0.4).edges, PORT_NODES, shell_gap=3.0,
    )
    return build_smooth_global_toroidal_routing(network.framed_network, bend_margin=0.05)


@pytest.fixture(scope="module")
def reference():
    return _reference()


def test_initial_state_is_exactly_the_existing_reference(reference):
    assert move_inner_return_to_shared_route(reference, 0.0) == reference


@pytest.mark.parametrize("progress", (0.0, 0.25, 0.5, 0.75, 1.0))
def test_motion_preserves_ports_shells_currents_and_local_regularity(reference, progress):
    moved = move_inner_return_to_shared_route(reference, progress)
    for i in (0, 1, 3):
        assert moved.edges[i] is reference.edges[i]
    before, after = reference.edges[2], moved.edges[2]
    assert after.route.source_frame == before.route.source_frame
    assert after.route.target_frame == before.route.target_frame
    assert after.route.assembly is before.route.assembly
    assert after.route.route[0] == before.route.route[0]
    assert after.route.route[-1] == before.route.route[-1]
    assert after.trimmed_straights_have_positive_length()
    assert after.minimum_jacobian_margin() > 0.0
    assert moved.maximum_interface_residual() < 1e-10
    assert moved.global_routing.maximum_endpoint_frame_residual() < 1e-12
    assert moved.global_routing.edges[2] is after.route
    assert moved.global_routing.minimum_edge_to_nonincident_junction_clearance() > 27.0


@pytest.mark.parametrize("current", (-1.0, 1.0))
@pytest.mark.parametrize("progress", (0.0, 0.5, 1.0))
def test_signed_flux_through_changed_bend_is_preserved(current, progress):
    routing = move_inner_return_to_shared_route(_reference(current), progress)
    nodes, weights = np.polynomial.legendre.leggauss(8)
    bend = routing.edges[2].bends[0]
    h, phi, theta_count = 1e-5, 0.7, 24
    contributions = []
    for q, weight in zip((nodes + 1) / 2, weights / 2, strict=True):
        for theta in np.arange(theta_count) * (2 * math.pi / theta_count):
            def surface(q_value, theta_value):
                return np.array(bend.map_point(phi, q_value, theta_value))
            dq = (surface(q + h, theta) - surface(q - h, theta)) / (2 * h)
            dt = (surface(q, theta + h) - surface(q, theta - h)) / (2 * h)
            field = bend.current(bend.map_point(phi, q, theta))
            contributions.append(np.dot(field, np.cross(dq, dt)) * weight * 2 * math.pi / theta_count)
    assert math.fsum(contributions) == pytest.approx(0.4 * current, rel=2e-8, abs=2e-8)


def test_shared_endpoint_has_geometric_bounds_independent_of_sampling(reference):
    endpoint = move_inner_return_to_shared_route(reference, 1.0)
    certificate = certify_shared_return_endpoint(endpoint)
    assert endpoint.edges[2].route.route == endpoint.edges[3].route.route
    assert certificate.shell_gap == pytest.approx(3.0)
    assert certificate.minimum_jacobian_margin > 0.0039
    assert certificate.minimum_nonadjacent_piece_clearance == pytest.approx(math.sqrt(2) * 0.05)
    assert certificate.minimum_other_edge_clearance == pytest.approx(1.0)
    assert certificate.nonincident_junction_clearance > 27.0
    assert certify_unchanged_edge_separation(reference) == pytest.approx(0.05)


def test_endpoint_certificate_refuses_an_intermediate_state(reference):
    with pytest.raises(ValueError, match="identical routes"):
        certify_shared_return_endpoint(move_inner_return_to_shared_route(reference, 0.75))


def test_piece_boxes_enclose_independent_surface_and_end_samples(reference):
    state = move_inner_return_to_shared_route(reference, 0.75)
    for edge in state.edges:
        pieces = routed_tube_pieces(edge)
        for piece in pieces:
            low, high = piece.bounds
            for point in piece.sample_points(BendSamplingGrid(7, 4, 12, 0.5, 0.5, 0.5)):
                assert all(a - 1e-10 <= x <= b + 1e-10 for a, x, b in zip(low, point, high, strict=True))
            volume = piece.volume
            if isinstance(volume, AnnularQuarterBend):
                boundary = [volume.map_point(phi, 1.0, theta) for phi in (0.0, 0.7, math.pi / 2)
                            for theta in np.arange(32) * math.pi / 16]
            else:
                axis = next(i for i in range(3) if volume.start[i] != volume.end[i])
                boundary = []
                for center in (volume.start, volume.end):
                    for other_axis in set(range(3)) - {axis}:
                        for sign in (-1, 1):
                            point = list(center)
                            point[other_axis] += sign * volume.outer_radius
                            boundary.append(point)
            for point in boundary:
                assert all(a - 1e-10 <= x <= b + 1e-10 for a, x, b in zip(low, point, high, strict=True))
        # Nonadjacent portions of the moved tube do not self-intersect here.
        if edge.edge_index == 2:
            assert min(box_clearance(a, b) for i, a in enumerate(pieces) for b in pieces[i + 2:]) > 0


def test_piece_audit_rejects_bends_inconsistent_with_route_channel(reference):
    edge = reference.edges[2]
    altered = replace(edge, bends=tuple(replace(bend, flux=2.0) for bend in edge.bends))
    with pytest.raises(ValueError, match="consistent uniform bends"):
        routed_tube_pieces(altered)


@pytest.mark.parametrize("progress", (0.0, 0.75, 1.0))
def test_all_piece_sampler_verifies_witnesses_and_exposes_unsafe_transition(reference, progress):
    routing = move_inner_return_to_shared_route(reference, progress)
    collisions = sample_moved_return_collisions(routing)
    if progress == 1.0:
        assert collisions == ()
        return
    assert collisions
    assert {item.other_edge for item in collisions} == {3}
    moved = routed_tube_pieces(routing.edges[2])
    neighbor = routed_tube_pieces(routing.edges[3])
    for witness in collisions:
        assert moved[witness.moved_piece].penetration(witness.point) > 0
        assert neighbor[witness.other_piece].penetration(witness.point) > 0
    if progress == 0.75:
        # Moving the joins can introduce other intersecting piece pairs.
        assert len(collisions) > 2


@pytest.mark.parametrize("progress", (-0.01, 1.01, float("nan"), float("inf")))
def test_invalid_progress_is_rejected(reference, progress):
    with pytest.raises(ValueError, match="progress"):
        move_inner_return_to_shared_route(reference, progress)
