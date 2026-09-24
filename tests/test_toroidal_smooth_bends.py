from __future__ import annotations

import math

import pytest

from src.graph_toroidal_flux_bundle import map_graph_currents_to_tori
from src.toroidal_annular_junction import connect_bundle_to_annular_junctions
from src.toroidal_framed_edge_assembly import build_framed_edge_network
from src.toroidal_smooth_bends import (
    AnnularQuarterBend,
    build_smooth_global_toroidal_routing,
)
from src.vesica_tree_circulation import PORT_NODES, tree_circulation, vesica_circulation


def build_vesica_smooth(current=1.2):
    circulation = vesica_circulation(current, return_split=0.4)
    bundle = map_graph_currents_to_tori(circulation.edges)
    junctions = connect_bundle_to_annular_junctions(bundle, PORT_NODES)
    framed = build_framed_edge_network(junctions)
    return build_smooth_global_toroidal_routing(framed)


def test_quarter_bend_geometry_and_endpoint_tangents():
    bend = AnnularQuarterBend(
        corner=(0.0, 0.0, 0.0),
        source_tangent=(0.0, 0.0, 1.0),
        target_tangent=(0.0, 1.0, 0.0),
        bend_radius=2.0,
        inner_radius=0.4,
        outer_radius=1.2,
        flux=1.3,
    )

    assert bend.start == pytest.approx((0.0, 0.0, -2.0))
    assert bend.end == pytest.approx((0.0, 2.0, 0.0))
    assert bend.tangent(0.0) == pytest.approx((0.0, 0.0, 1.0))
    assert bend.tangent(math.pi / 2) == pytest.approx((0.0, 1.0, 0.0))
    assert bend.minimum_jacobian_scale == pytest.approx(0.4)


def test_quarter_bend_map_roundtrips_parameters():
    bend = AnnularQuarterBend(
        corner=(1.0, -0.5, 0.25),
        source_tangent=(1.0, 0.0, 0.0),
        target_tangent=(0.0, 0.0, -1.0),
        bend_radius=2.5,
        inner_radius=0.6,
        outer_radius=1.4,
        flux=-0.8,
    )
    point = bend.map_point(0.63, 0.37, -0.44)
    parameters = bend.inverse_parameters(point)
    assert parameters is not None
    phi, q, theta = parameters
    assert phi == pytest.approx(0.63, abs=1e-12)
    assert q == pytest.approx(0.37, abs=1e-12)
    assert theta == pytest.approx(-0.44, abs=1e-12)


@pytest.mark.parametrize("flux", [1.4, -0.9, 0.0])
def test_bend_current_matches_adjacent_straight_profile(flux):
    bend = AnnularQuarterBend(
        corner=(0.0, 0.0, 0.0),
        source_tangent=(0.0, 0.0, 1.0),
        target_tangent=(1.0, 0.0, 0.0),
        bend_radius=2.0,
        inner_radius=0.5,
        outer_radius=1.3,
        flux=flux,
    )
    assert bend.interface_vector_residual() < 1e-12


def test_bend_current_is_numerically_divergence_free_inside():
    bend = AnnularQuarterBend(
        corner=(0.0, 0.0, 0.0),
        source_tangent=(0.0, 0.0, 1.0),
        target_tangent=(0.0, 1.0, 0.0),
        bend_radius=2.4,
        inner_radius=0.5,
        outer_radius=1.2,
        flux=1.1,
    )
    point = bend.map_point(0.7, 0.45, 0.4)
    errors = []
    for h in (2e-4, 1e-4, 5e-5):
        divergence = 0.0
        for axis in range(3):
            plus = list(point)
            minus = list(point)
            plus[axis] += h
            minus[axis] -= h
            divergence += (
                bend.current(tuple(plus))[axis] - bend.current(tuple(minus))[axis]
            ) / (2 * h)
        errors.append(abs(divergence))
    assert errors[-1] < 2e-6
    assert errors[-1] < errors[0] / 5


def test_jacobian_stays_positive_over_entire_annulus():
    bend = AnnularQuarterBend(
        corner=(0.0, 0.0, 0.0),
        source_tangent=(0.0, 1.0, 0.0),
        target_tangent=(-1.0, 0.0, 0.0),
        bend_radius=2.0,
        inner_radius=0.3,
        outer_radius=1.5,
        flux=0.7,
    )
    minimum = min(
        bend.jacobian_scale(radius, theta)
        for radius in (bend.inner_radius, 0.9, bend.outer_radius)
        for theta in (0.0, math.pi / 3, math.pi, 5 * math.pi / 3)
    )
    assert minimum > 0.0
    assert minimum == pytest.approx(bend.minimum_jacobian_scale)


def test_vesica_smooth_routing_preserves_interfaces_and_collision_certificate():
    smooth = build_vesica_smooth()
    assert smooth.maximum_interface_residual() < 1e-12
    assert smooth.minimum_jacobian_margin() > 0.0
    assert smooth.minimum_collision_certificate() > 0.0
    assert all(edge.trimmed_straights_have_positive_length() for edge in smooth.edges)
    assert all(edge.envelope_contains_bends() for edge in smooth.edges)


def test_tree_smooth_routing_is_collision_certified():
    circulation = tree_circulation(
        rings=2,
        radial_current=-1.0,
        weave_current=0.12,
        weave_handedness=1,
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
    smooth = build_smooth_global_toroidal_routing(
        framed,
        bend_margin=0.3,
        node_gap=1.0,
        edge_gap=0.6,
    )

    assert smooth.maximum_interface_residual() < 1e-12
    assert smooth.minimum_jacobian_margin() > 0.0
    assert smooth.minimum_collision_certificate() > 0.0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"bend_margin": 0.0},
        {"bend_margin": -0.1},
        {"bend_margin": math.inf},
    ],
)
def test_invalid_bend_margin_is_rejected(kwargs):
    circulation = vesica_circulation(1.0)
    bundle = map_graph_currents_to_tori(circulation.edges)
    junctions = connect_bundle_to_annular_junctions(bundle, PORT_NODES)
    framed = build_framed_edge_network(junctions)
    with pytest.raises(ValueError):
        build_smooth_global_toroidal_routing(framed, **kwargs)


def test_bend_rejects_nonorthogonal_tangents_and_tight_radius():
    with pytest.raises(ValueError, match="orthogonal"):
        AnnularQuarterBend(
            corner=(0, 0, 0),
            source_tangent=(1, 0, 0),
            target_tangent=(1, 1, 0),
            bend_radius=2.0,
            inner_radius=0.5,
            outer_radius=1.0,
            flux=1.0,
        )
    with pytest.raises(ValueError, match="exceed"):
        AnnularQuarterBend(
            corner=(0, 0, 0),
            source_tangent=(1, 0, 0),
            target_tangent=(0, 1, 0),
            bend_radius=1.0,
            inner_radius=0.5,
            outer_radius=1.0,
            flux=1.0,
        )
