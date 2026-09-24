from __future__ import annotations

import math

import pytest

from src.graph_toroidal_flux_bundle import map_graph_currents_to_tori
from src.toroidal_annular_junction import connect_bundle_to_annular_junctions
from src.toroidal_framed_edge_assembly import build_framed_edge_network
from src.toroidal_global_routing import (
    build_global_toroidal_routing,
    point_segment_distance,
    segment_distance,
)
from src.vesica_tree_circulation import PORT_NODES, tree_circulation, vesica_circulation


def build_vesica_routing(current=1.2):
    circulation = vesica_circulation(current, return_split=0.4)
    bundle = map_graph_currents_to_tori(circulation.edges)
    junctions = connect_bundle_to_annular_junctions(bundle, PORT_NODES)
    framed = build_framed_edge_network(junctions)
    return build_global_toroidal_routing(framed)


def test_segment_distance_reference_cases():
    assert segment_distance((0, 0, 0), (1, 0, 0), (0, 2, 0), (1, 2, 0)) == pytest.approx(2.0)
    assert segment_distance((0, 0, 0), (2, 0, 0), (1, -1, 0), (1, 1, 0)) == pytest.approx(0.0)
    assert point_segment_distance((0.5, 1.0, 0.0), (0, 0, 0), (1, 0, 0)) == pytest.approx(1.0)


@pytest.mark.parametrize("current", [1.3, -1.3, 0.0])
def test_vesica_global_routes_preserve_endpoint_frames(current):
    routing = build_vesica_routing(current)

    assert routing.maximum_endpoint_frame_residual() < 1e-12
    for edge in routing.edges:
        first = edge.route[1]
        start = edge.route[0]
        last = edge.route[-1]
        before_last = edge.route[-2]
        assert first[0] == pytest.approx(start[0])
        assert first[1] == pytest.approx(start[1])
        expected_sign = edge.assembly.axis_sign
        assert expected_sign * (first[2] - start[2]) > 0.0
        assert last[0] == pytest.approx(before_last[0])
        assert last[1] == pytest.approx(before_last[1])
        assert expected_sign * (last[2] - before_last[2]) > 0.0
        assert edge.source_frame.axis == pytest.approx((0.0, 0.0, expected_sign))
        assert edge.target_frame.axis == pytest.approx((0.0, 0.0, expected_sign))
        assert edge.length > edge.assembly.total_length


def test_global_junction_placements_are_rigid_translations():
    routing = build_vesica_routing()
    local = routing.framed_network.junction_network

    for placed in routing.junctions:
        original = local.junction(placed.node)
        assert placed.junction.length == original.length
        assert placed.junction.inner_radius == original.inner_radius
        assert placed.junction.outer_radius == original.outer_radius
        assert placed.center[1:] == (0.0, 0.0)


def test_tree_global_routing_has_no_nonincident_edge_envelope_collisions():
    circulation = tree_circulation(
        rings=2,
        radial_current=-1.1,
        weave_current=0.14,
        weave_handedness=-1,
    )
    bundle = map_graph_currents_to_tori(
        circulation.edges,
        major_radius=2.0,
        minor_radius=0.3,
        gap=0.1,
    )
    junctions = connect_bundle_to_annular_junctions(
        bundle,
        circulation.geometry.nodes,
        outer_radius=1.8,
        junction_gap=0.2,
    )
    framed = build_framed_edge_network(
        junctions,
        connector_length=0.8,
        channel_length=1.1,
    )
    routing = build_global_toroidal_routing(
        framed,
        node_gap=1.0,
        edge_gap=0.6,
        route_padding=0.05,
    )

    assert routing.nonincident_edge_collision_count() == 0
    assert routing.minimum_nonincident_edge_clearance() > 0.0
    assert routing.minimum_edge_to_nonincident_junction_clearance() > 0.0
    assert routing.maximum_endpoint_frame_residual() < 1e-12


def test_every_edge_gets_unique_corridor_and_height():
    routing = build_vesica_routing()
    assert len({edge.lane_y for edge in routing.edges}) == len(routing.edges)
    assert len({edge.lane_height for edge in routing.edges}) == len(routing.edges)
    assert all(edge.lane_y > 0.0 and edge.lane_height > 0.0 for edge in routing.edges)


def test_route_clearance_grows_with_padding():
    base = build_vesica_routing()
    circulation = vesica_circulation(1.2, return_split=0.4)
    bundle = map_graph_currents_to_tori(circulation.edges)
    junctions = connect_bundle_to_annular_junctions(bundle, PORT_NODES)
    framed = build_framed_edge_network(junctions)
    padded = build_global_toroidal_routing(framed, route_padding=0.5)

    assert all(
        right.clearance_radius > left.clearance_radius
        for left, right in zip(base.edges, padded.edges, strict=True)
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"node_gap": -0.1},
        {"edge_gap": -0.1},
        {"route_padding": -0.1},
        {"node_gap": math.inf},
    ],
)
def test_invalid_global_routing_parameters_are_rejected(kwargs):
    circulation = vesica_circulation(1.0)
    bundle = map_graph_currents_to_tori(circulation.edges)
    junctions = connect_bundle_to_annular_junctions(bundle, PORT_NODES)
    framed = build_framed_edge_network(junctions)
    with pytest.raises(ValueError):
        build_global_toroidal_routing(framed, **kwargs)
