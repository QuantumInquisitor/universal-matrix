from __future__ import annotations

import math

import numpy as np
import pytest

from src.graph_toroidal_flux_bundle import map_graph_currents_to_tori
from src.toroidal_annular_junction import (
    AnnularPortFace,
    build_annular_junction_control_volume,
    connect_bundle_to_annular_junctions,
)
from src.toroidal_connector_topology import ANNULAR_PORT
from src.vesica_tree_circulation import (
    DirectedCurrent,
    FlowChannel,
    PORT_NODES,
    tree_circulation,
    vesica_circulation,
)


def gauss_integral(function, lower, upper, count=36):
    nodes, weights = np.polynomial.legendre.leggauss(count)
    points = (upper + lower) / 2 + (upper - lower) / 2 * nodes
    return (upper - lower) / 2 * sum(
        weight * function(point)
        for point, weight in zip(points, weights, strict=True)
    )


def test_annular_ports_preserve_two_inlet_one_outlet_transport_plan():
    currents = (
        DirectedCurrent("a", "n", 2.0, FlowChannel.TREE_OUTER),
        DirectedCurrent("b", "n", 1.0, FlowChannel.TREE_OUTER),
        DirectedCurrent("n", "c", 3.0, FlowChannel.TREE_OUTER),
    )
    junction = build_annular_junction_control_volume("n", currents)

    assert junction.total_outward_flux == pytest.approx(0.0, abs=1e-12)
    assert all(port.topology is ANNULAR_PORT for port in junction.ports)
    assert junction.port_by_edge(0).face is AnnularPortFace.LOWER
    assert junction.port_by_edge(1).face is AnnularPortFace.LOWER
    assert junction.port_by_edge(2).face is AnnularPortFace.UPPER
    transfers = junction.transport_plan()
    assert [(item.inlet_edge_index, item.outlet_edge_index, item.flux) for item in transfers] == [
        (0, 2, 2.0),
        (1, 2, 1.0),
    ]


def test_each_annular_port_surface_integrates_to_its_signed_outward_flux():
    currents = (
        DirectedCurrent("a", "n", 1.7, FlowChannel.TREE_OUTER),
        DirectedCurrent("n", "b", 0.6, FlowChannel.TREE_OUTER),
        DirectedCurrent("n", "c", 1.1, FlowChannel.TREE_OUTER),
    )
    junction = build_annular_junction_control_volume(
        "n",
        currents,
        inner_radius=0.4,
        outer_radius=1.6,
    )

    for port in junction.ports:
        measured = 2 * math.pi * gauss_integral(
            lambda radius: radius * junction.outward_normal_density(port.edge_index, radius),
            port.inner_radius,
            port.outer_radius,
        )
        assert measured == pytest.approx(port.outward_flux, abs=2e-12)


def test_annular_boundary_profile_matches_piola_connector_source_profile():
    currents = (
        DirectedCurrent("a", "n", 1.3, FlowChannel.TREE_OUTER),
        DirectedCurrent("n", "b", 1.3, FlowChannel.TREE_OUTER),
    )
    junction = build_annular_junction_control_volume("n", currents)
    for port in junction.ports:
        for q in (0.1, 0.25, 0.5, 0.75, 0.9):
            radius = port.inner_radius + port.width * q
            assert junction.connector_profile_residual(port.edge_index, radius) < 1e-12


def test_axisymmetric_junction_field_is_divergence_free_interior():
    currents = (
        DirectedCurrent("a", "n", 2.0, FlowChannel.TREE_OUTER),
        DirectedCurrent("b", "n", 1.0, FlowChannel.TREE_OUTER),
        DirectedCurrent("n", "c", 0.75, FlowChannel.TREE_OUTER),
        DirectedCurrent("n", "d", 2.25, FlowChannel.TREE_OUTER),
    )
    junction = build_annular_junction_control_volume("n", currents, length=1.4)
    point = (0.93, 0.17, 0.11)

    errors = []
    for h in (2e-4, 1e-4, 5e-5):
        divergence = 0.0
        for axis in range(3):
            plus = list(point)
            minus = list(point)
            plus[axis] += h
            minus[axis] -= h
            divergence += (
                junction.current(tuple(plus))[axis] - junction.current(tuple(minus))[axis]
            ) / (2 * h)
        errors.append(abs(divergence))
    assert errors[-1] < 1e-6
    assert errors[-1] < errors[0] / 6


def test_side_walls_have_zero_current_normal_component():
    currents = (
        DirectedCurrent("a", "n", 1.0, FlowChannel.TREE_OUTER),
        DirectedCurrent("n", "b", 1.0, FlowChannel.TREE_OUTER),
    )
    junction = build_annular_junction_control_volume("n", currents)
    for radius in (junction.inner_radius, junction.outer_radius):
        for z in (-0.3, 0.0, 0.3):
            current = junction.current((radius, 0.0, z))
            assert current[0] == pytest.approx(0.0, abs=1e-12)
            assert current[2] == pytest.approx(0.0, abs=1e-12)
    assert junction.side_wall_flux == 0.0


def test_vesica_annular_network_preserves_graph_flux_and_connector_profiles():
    circulation = vesica_circulation(-2.2, return_split=0.4)
    bundle = map_graph_currents_to_tori(circulation.edges)
    network = connect_bundle_to_annular_junctions(bundle, PORT_NODES)

    assert network.edge_flux_residual() < 1e-12
    assert network.maximum_node_balance_residual() < 1e-12
    assert network.maximum_connector_profile_residual() < 1e-12
    assert network.junctions_are_disjoint()


def test_tree_annular_network_preserves_all_conservative_nodes():
    circulation = tree_circulation(
        rings=2,
        radial_current=-1.5,
        weave_current=0.17,
        weave_handedness=1,
    )
    bundle = map_graph_currents_to_tori(circulation.edges)
    network = connect_bundle_to_annular_junctions(
        bundle,
        circulation.geometry.nodes,
        outer_radius=1.8,
        junction_gap=0.2,
    )

    assert network.edge_flux_residual() < 1e-12
    assert network.maximum_node_balance_residual() < 1e-12
    assert network.maximum_connector_profile_residual() < 1e-12


def test_zero_current_edge_still_receives_an_annular_port():
    currents = (
        DirectedCurrent("n", "a", 0.0, FlowChannel.TREE_OUTER),
    )
    junction = build_annular_junction_control_volume("n", currents)
    port = junction.port_by_edge(0)
    assert port.topology is ANNULAR_PORT
    assert port.magnitude == 0.0
    assert port.face is AnnularPortFace.UPPER
    assert junction.outward_normal_density(0, (port.inner_radius + port.outer_radius) / 2) == 0.0


def test_unbalanced_annular_junction_is_rejected():
    currents = (
        DirectedCurrent("a", "n", 1.0, FlowChannel.TREE_OUTER),
        DirectedCurrent("n", "b", 0.4, FlowChannel.TREE_OUTER),
    )
    with pytest.raises(ValueError, match="not conservative"):
        build_annular_junction_control_volume("n", currents)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"length": 0.0},
        {"inner_radius": 0.0},
        {"inner_radius": 1.0, "outer_radius": 1.0},
        {"outer_radius": math.inf},
    ],
)
def test_invalid_annular_junction_geometry_is_rejected(kwargs):
    currents = (
        DirectedCurrent("a", "n", 1.0, FlowChannel.TREE_OUTER),
        DirectedCurrent("n", "b", 1.0, FlowChannel.TREE_OUTER),
    )
    with pytest.raises(ValueError):
        build_annular_junction_control_volume("n", currents, **kwargs)
