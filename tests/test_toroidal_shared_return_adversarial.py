"""Adversarial checks of geometric contracts independent of current amplitude."""

from dataclasses import replace

import pytest

from src.toroidal_separated_channels import build_separated_framed_edge_network
from src.toroidal_shared_return_connectors import (
    attach_shared_return_connectors,
    audit_connected_geometry,
    build_connected_shared_return_reference,
)
from src.toroidal_shared_return_route import (
    certify_shared_return_endpoint,
    move_inner_return_to_shared_route,
)
from src.toroidal_smooth_bends import (
    SmoothedRoutedEdge,
    _build_edge_bends,
    build_smooth_global_toroidal_routing,
)
from src.vesica_tree_circulation import PORT_NODES, vesica_circulation


@pytest.fixture(scope="module", params=(-2e-10, 2e-10))
def weak_current_network(request):
    # Above the public builder's nonzero threshold, but small enough that an
    # absolute field residual alone cannot establish geometric connection.
    return build_connected_shared_return_reference(request.param)


@pytest.mark.parametrize(
    "transition_name, endpoint",
    (("inlet", "source"), ("inlet", "target"),
     ("outlet", "source"), ("outlet", "target")),
)
def test_weak_current_cannot_hide_a_disconnected_interface(
    weak_current_network, transition_name, endpoint,
):
    routing = weak_current_network.routing
    edge = routing.edges[0]
    assembly = edge.route.assembly
    transition = getattr(assembly, transition_name)
    # This annulus is disjoint from both the port [0.5, 1.5] and the routed
    # channel [2.0, 2.4]. The original flux remains exactly unchanged.
    disconnected = replace(transition, **{
        f"{endpoint}_inner_radius": 3.0,
        f"{endpoint}_outer_radius": 3.4,
    })
    changed = replace(edge, route=replace(
        edge.route, assembly=replace(assembly, **{transition_name: disconnected}),
    ))
    altered = replace(routing, edges=(changed, *routing.edges[1:]))
    with pytest.raises(ValueError, match="interface annuli"):
        attach_shared_return_connectors(altered)
    placed = replace(getattr(weak_current_network.edges[0], transition_name), transition=disconnected)
    declared = replace(
        weak_current_network,
        routing=altered,
        edges=(replace(weak_current_network.edges[0], **{transition_name: placed}),
               *weak_current_network.edges[1:]),
    )
    with pytest.raises(ValueError, match="interface annuli"):
        audit_connected_geometry(declared)


@pytest.mark.parametrize("transition_name", ("inlet", "outlet"))
def test_weak_current_cannot_hide_a_fractional_flux_leak(weak_current_network, transition_name):
    routing = weak_current_network.routing
    edge = routing.edges[0]
    assembly = edge.route.assembly
    transition = getattr(assembly, transition_name)
    # The 0.1% discrepancy is smaller than legacy absolute flux tolerances.
    leaking = replace(transition, flux=transition.flux * 1.001)
    changed = replace(edge, route=replace(
        edge.route, assembly=replace(assembly, **{transition_name: leaking}),
    ))
    altered = replace(routing, edges=(changed, *routing.edges[1:]))
    with pytest.raises(ValueError, match="interface fluxes"):
        attach_shared_return_connectors(altered)


@pytest.mark.parametrize("shell_gap", (0.0, 1e-12))
def test_unresolved_radial_gap_cannot_become_a_strict_clearance_certificate(shell_gap):
    network = build_separated_framed_edge_network(
        vesica_circulation(1.0, return_split=0.4).edges,
        PORT_NODES,
        shell_gap=shell_gap,
    )
    routing = build_smooth_global_toroidal_routing(network.framed_network, bend_margin=0.05)
    with pytest.raises(ValueError, match="audit tolerance"):
        move_inner_return_to_shared_route(routing, 1.0)

    # Construct a valid shared centerline directly so the certificate itself
    # must reject the gap; it cannot rely on the movement helper's guard.
    inner, outer = routing.edges[2:]
    shared_route = replace(
        inner.route,
        route=outer.route.route,
        lane_y=outer.route.lane_y,
        lane_height=outer.route.lane_height,
        clearance_radius=outer.route.clearance_radius,
    )
    moved = SmoothedRoutedEdge(
        shared_route, _build_edge_bends(shared_route, outer.bends[0].bend_radius),
    )
    edges = (*routing.edges[:2], moved, outer)
    endpoint = replace(
        routing,
        edges=edges,
        global_routing=replace(routing.global_routing, edges=tuple(edge.route for edge in edges)),
    )
    with pytest.raises(ValueError, match="audit tolerance"):
        certify_shared_return_endpoint(endpoint)
