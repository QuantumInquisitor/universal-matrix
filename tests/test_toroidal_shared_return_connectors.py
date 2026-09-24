from __future__ import annotations

import math
from dataclasses import replace

import numpy as np
import pytest

from src.toroidal_shared_return_connectors import (
    PlacedAnnularTransition,
    attach_shared_return_connectors,
    audit_connected_geometry,
    build_connected_shared_return_reference,
)


@pytest.fixture(scope="module", params=(1.0, -1.0))
def connected(request):
    return build_connected_shared_return_reference(request.param)


def test_all_eight_transitions_fit_and_preserve_original_graph_ports(connected):
    for edge, route in zip(connected.edges, connected.routing.edges, strict=True):
        assert edge.inlet.origin == route.route.source_frame.origin
        assert edge.outlet.end == route.route.target_frame.origin
        assert edge.inlet.end == edge.pieces[0].volume.start
        assert edge.outlet.origin == edge.pieces[-1].volume.end
        assert edge.pieces[0].volume.length > 0
        assert edge.pieces[-1].volume.length > 0
        assert edge.flux == route.route.edge.current
    assert connected.maximum_interface_residual() < 1e-12
    assert connected.edges[2].pieces[0].volume.length == pytest.approx(216.1)


def test_geometry_audit_allows_port_boundary_contact_but_no_interior_overlap(connected):
    audit = audit_connected_geometry(connected)
    assert audit.connector_count == 8
    assert audit.nested_transition_pair_count == 2
    assert audit.minimum_transition_endpoint_gap == 0.0
    assert audit.minimum_transition_jacobian_bound == pytest.approx(0.2)
    assert audit.minimum_unchanged_tube_clearance > 0.07
    inner, outer = connected.edges[2:]
    for name in ("inlet", "outlet"):
        a, b = getattr(inner, name).transition, getattr(outer, name).transition
        for s in (0.01, 0.25, 0.5, 0.75, 0.99):
            assert b.radius(s, 0.0) - a.radius(s, 1.0) > 0


def test_placed_map_roundtrips_and_retains_positive_orientation(connected):
    for edge in connected.edges:
        for placed in (edge.inlet, edge.outlet):
            parameter = np.array((0.4, 0.6, 0.7))
            h = 1e-5
            def position(p):
                return np.array(placed.map_point(*p))
            numerical = np.column_stack([(position(parameter + h * axis) - position(parameter - h * axis)) / (2 * h)
                                         for axis in np.eye(3)])
            assert np.linalg.det(numerical) == pytest.approx(
                placed.transition.jacobian_determinant(parameter[0], parameter[1]), rel=2e-8)
            local = placed.transition.map_point(*parameter)
            assert placed.to_local(placed.to_global(local)) == pytest.approx(local, abs=1e-12)


def test_signed_flux_integrates_correctly_through_every_placed_connector(connected):
    nodes, weights = np.polynomial.legendre.leggauss(8)
    h, theta_count, s = 1e-5, 24, 0.4
    for edge in connected.edges:
        for placed in (edge.inlet, edge.outlet):
            contributions = []
            for q, weight in zip((nodes + 1) / 2, weights / 2, strict=True):
                for theta in np.arange(theta_count) * 2 * math.pi / theta_count:
                    def surface(q_value, theta_value):
                        return np.array(placed.map_point(s, q_value, theta_value))
                    dq = (surface(q + h, theta) - surface(q - h, theta)) / (2 * h)
                    dt = (surface(q, theta + h) - surface(q, theta - h)) / (2 * h)
                    point = placed.map_point(s, q, theta)
                    contributions.append(np.dot(connected.current(point), np.cross(dq, dt))
                                         * weight * 2 * math.pi / theta_count)
            assert math.fsum(contributions) == pytest.approx(edge.flux, rel=3e-8, abs=3e-8)


def test_composite_field_is_divergence_free_inside_transitions(connected):
    h = 1e-5
    for edge in connected.edges:
        for placed in (edge.inlet, edge.outlet):
            point = np.array(placed.map_point(0.4, 0.55, 0.7))
            divergence = math.fsum(
                (connected.current(point + h * axis)[i] - connected.current(point - h * axis)[i]) / (2 * h)
                for i, axis in enumerate(np.eye(3))
            )
            assert abs(divergence) < 2e-7


def test_shared_interface_current_is_selected_once_and_is_continuous(connected):
    for edge in connected.edges:
        for placed in (edge.inlet, edge.outlet):
            for s in (0.0, 1.0):
                point = placed.map_point(s, 0.45, 0.7)
                expected = np.array(placed.current(point))
                assert connected.current(point) == pytest.approx(expected, abs=1e-12)
                for delta in (-1e-7, 1e-7):
                    nearby = tuple(np.array(point) + (0.0, 0.0, delta))
                    assert connected.current(nearby) == pytest.approx(expected, abs=2e-5)
    assert connected.current((1e6, 1e6, 1e6)) == (0.0, 0.0, 0.0)


def test_geometry_audit_rejects_unrelated_placed_pieces(connected):
    edge = connected.edges[2]
    moved = replace(edge.inlet, origin=(edge.inlet.origin[0] + 0.1, *edge.inlet.origin[1:]))
    altered = replace(connected, edges=(*connected.edges[:2], replace(edge, inlet=moved), connected.edges[3]))
    with pytest.raises(ValueError, match="must match"):
        audit_connected_geometry(altered)


def test_overlong_transition_is_rejected_before_route_trimming(connected):
    routing = connected.routing
    edge = routing.edges[2]
    assembly = edge.route.assembly
    inlet = replace(assembly.inlet, length=300.0)
    channel = replace(assembly.channel, z_start=inlet.z_end)
    outlet = replace(assembly.outlet, z_start=channel.z_end)
    altered_assembly = replace(assembly, inlet=inlet, channel=channel, outlet=outlet)
    altered_edge = replace(edge, route=replace(edge.route, assembly=altered_assembly))
    altered_routing = replace(routing, edges=(*routing.edges[:2], altered_edge, routing.edges[3]))
    with pytest.raises(ValueError, match="longer than its connector"):
        attach_shared_return_connectors(altered_routing)


@pytest.mark.parametrize("current", (0.0, float("inf"), float("nan")))
def test_invalid_reference_current_is_rejected(current):
    with pytest.raises(ValueError, match="finite and nonzero"):
        build_connected_shared_return_reference(current)


def test_invalid_placement_axis_is_rejected(connected):
    with pytest.raises(ValueError, match="axis_sign"):
        PlacedAnnularTransition(connected.edges[0].inlet.transition, (0.0, 0.0, 0.0), 0)
