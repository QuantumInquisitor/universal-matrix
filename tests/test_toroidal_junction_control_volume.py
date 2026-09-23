from __future__ import annotations

import math

import numpy as np
import pytest

from src.graph_toroidal_flux_bundle import map_graph_currents_to_tori
from src.toroidal_junction_control_volume import (
    PortSide,
    build_junction_control_volume,
    connect_toroidal_bundle_with_junctions,
)
from src.vesica_tree_circulation import (
    DirectedCurrent,
    FlowChannel,
    PORT_NODES,
    tree_circulation,
    vesica_circulation,
)


def gauss_integral(function, lower, upper, count=32):
    nodes, weights = np.polynomial.legendre.leggauss(count)
    points = (upper + lower) / 2 + (upper - lower) / 2 * nodes
    return (upper - lower) / 2 * sum(
        weight * function(point)
        for point, weight in zip(points, weights, strict=True)
    )


def test_one_connected_junction_routes_two_inlets_to_one_outlet():
    currents = (
        DirectedCurrent("a", "n", 2.0, FlowChannel.TREE_OUTER),
        DirectedCurrent("b", "n", 1.0, FlowChannel.TREE_OUTER),
        DirectedCurrent("n", "c", 3.0, FlowChannel.TREE_OUTER),
    )
    junction = build_junction_control_volume("n", currents, width=1.2, height=0.8)

    assert junction.total_outward_flux == pytest.approx(0.0, abs=1e-12)
    assert len(junction.lanes) == 2
    assert junction.lanes_are_disjoint()
    assert junction.maximum_port_flux_residual() < 1e-12
    assert junction.port_by_edge(0).side is PortSide.INLET
    assert junction.port_by_edge(1).side is PortSide.INLET
    assert junction.port_by_edge(2).side is PortSide.OUTLET
    assert junction.measured_port_flux(0) == pytest.approx(-2.0)
    assert junction.measured_port_flux(1) == pytest.approx(-1.0)
    assert junction.measured_port_flux(2) == pytest.approx(3.0)


def test_lane_profile_integrates_to_the_declared_transfer_flux():
    currents = (
        DirectedCurrent("a", "n", 2.0, FlowChannel.TREE_OUTER),
        DirectedCurrent("n", "b", 2.0, FlowChannel.TREE_OUTER),
    )
    junction = build_junction_control_volume("n", currents, width=1.0, height=0.7)
    lane = junction.lanes[0]

    measured = gauss_integral(
        lambda y: gauss_integral(
            lambda z: lane.profile(y, z),
            lane.z_lower,
            lane.z_upper,
        ),
        lane.y_lower,
        lane.y_upper,
    )
    assert measured == pytest.approx(lane.flux, abs=1e-12)


def test_junction_field_is_divergence_free_and_has_zero_side_wall_flux():
    currents = (
        DirectedCurrent("a", "n", 1.25, FlowChannel.TREE_OUTER),
        DirectedCurrent("n", "b", 1.25, FlowChannel.TREE_OUTER),
    )
    junction = build_junction_control_volume("n", currents)
    lane = junction.lanes[0]
    point = (
        junction.center[0],
        junction.center[1] + (lane.y_lower + lane.y_upper) / 2,
        junction.center[2],
    )

    divergence = 0.0
    h = 1e-5
    for axis in range(3):
        plus = list(point)
        minus = list(point)
        plus[axis] += h
        minus[axis] -= h
        divergence += (junction.current(plus)[axis] - junction.current(minus)[axis]) / (2 * h)
    assert divergence == pytest.approx(0.0, abs=1e-12)
    assert junction.side_wall_flux == 0.0


def test_vesica_network_replaces_node_balance_with_explicit_control_volumes():
    circulation = vesica_circulation(-2.1, return_split=0.35)
    bundle = map_graph_currents_to_tori(circulation.edges)
    network = connect_toroidal_bundle_with_junctions(bundle, PORT_NODES)

    assert len(network.junctions) == 3
    assert network.edge_interface_residual() < 1e-12
    assert network.maximum_node_balance_residual() < 1e-12
    assert network.junction_boxes_are_disjoint()
    for channel in bundle.channels:
        edge = channel.edge
        assert network.junction(edge.source).measured_port_flux(channel.edge_index) == pytest.approx(
            edge.current
        )
        assert network.junction(edge.target).measured_port_flux(channel.edge_index) == pytest.approx(
            -edge.current
        )


def test_tree_network_preserves_every_toroidal_edge_interface():
    circulation = tree_circulation(
        rings=2,
        radial_current=1.7,
        weave_current=-0.13,
        weave_handedness=-1,
    )
    bundle = map_graph_currents_to_tori(
        circulation.edges,
        major_radius=2.4,
        minor_radius=0.22,
        gap=0.08,
    )
    network = connect_toroidal_bundle_with_junctions(
        bundle,
        circulation.geometry.nodes,
        junction_width=2.0,
        junction_height=0.5,
        lane_gap=0.005,
        junction_gap=0.1,
    )

    assert network.edge_interface_residual() < 1e-12
    assert network.maximum_node_balance_residual() < 1e-12
    assert all(junction.maximum_port_flux_residual() < 1e-12 for junction in network.junctions)


def test_zero_current_incident_edge_gets_a_zero_port_without_a_lane():
    currents = (
        DirectedCurrent("a", "n", 0.0, FlowChannel.TREE_OUTER),
    )
    junction = build_junction_control_volume("n", currents)
    assert len(junction.ports) == 1
    assert junction.ports[0].side is PortSide.ZERO
    assert junction.lanes == ()
    assert junction.measured_port_flux(0) == 0.0


def test_unbalanced_node_is_rejected():
    currents = (
        DirectedCurrent("a", "n", 1.0, FlowChannel.TREE_OUTER),
        DirectedCurrent("n", "b", 0.25, FlowChannel.TREE_OUTER),
    )
    with pytest.raises(ValueError, match="not conservative"):
        build_junction_control_volume("n", currents)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"length": 0.0},
        {"width": 0.0},
        {"height": math.inf},
        {"lane_gap": -0.1},
    ],
)
def test_invalid_junction_geometry_is_rejected(kwargs):
    currents = (
        DirectedCurrent("a", "n", 1.0, FlowChannel.TREE_OUTER),
        DirectedCurrent("n", "b", 1.0, FlowChannel.TREE_OUTER),
    )
    with pytest.raises(ValueError):
        build_junction_control_volume("n", currents, **kwargs)
