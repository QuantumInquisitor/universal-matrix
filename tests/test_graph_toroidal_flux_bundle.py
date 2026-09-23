from __future__ import annotations

import math

import numpy as np
import pytest

from src.graph_toroidal_flux_bundle import (
    flux_mapping_residual,
    map_graph_currents_to_tori,
)
from src.vesica_tree_circulation import (
    PORT_NODES,
    tree_circulation,
    vesica_circulation,
)


def gauss_integral(function, lower, upper, count=24):
    nodes, weights = np.polynomial.legendre.leggauss(count)
    points = (upper + lower) / 2 + (upper - lower) / 2 * nodes
    return (upper - lower) / 2 * sum(
        weight * function(point)
        for point, weight in zip(points, weights, strict=True)
    )


def test_vesica_edges_map_one_to_one_with_exact_signed_flux():
    circulation = vesica_circulation(2.4, return_split=0.3)
    bundle = map_graph_currents_to_tori(circulation.edges)

    assert len(bundle.channels) == len(circulation.edges) == 4
    assert bundle.oriented_channel_fluxes() == tuple(edge.current for edge in circulation.edges)
    assert flux_mapping_residual(bundle) == 0.0
    assert bundle.supports_are_disjoint()
    assert bundle.maximum_overlap_count() == 1
    assert bundle.node_flux_divergence(PORT_NODES) == circulation.divergence


def test_tree_bundle_preserves_every_edge_current_and_node_balance():
    circulation = tree_circulation(
        rings=2,
        radial_current=-1.7,
        weave_current=0.23,
        weave_handedness=-1,
    )
    bundle = map_graph_currents_to_tori(
        circulation.edges,
        major_radius=2.5,
        minor_radius=0.25,
        gap=0.1,
    )

    assert len(bundle.channels) == len(circulation.edges)
    assert bundle.oriented_channel_fluxes() == tuple(edge.current for edge in circulation.edges)
    assert bundle.node_flux_divergence(circulation.geometry.nodes) == circulation.divergence
    assert max(
        abs(value)
        for value in bundle.node_flux_divergence(circulation.geometry.nodes).values()
    ) < 1e-12


def test_translated_tube_surface_integral_recovers_original_edge_current():
    circulation = vesica_circulation(-1.35)
    bundle = map_graph_currents_to_tori(
        circulation.edges,
        major_radius=2.2,
        minor_radius=0.6,
        gap=0.4,
        center_z=3.0,
    )
    channel = bundle.channels[2]
    field = channel.field
    R, a, z0 = field.major_radius, field.minor_radius, channel.center_z

    def inner_cut(rho):
        return 2 * math.pi * rho * channel.current((rho, 0.0, z0))[2]

    measured = gauss_integral(inner_cut, R - a, R)
    assert measured == pytest.approx(channel.edge.current, abs=1e-12)


def test_summed_field_is_locally_divergence_free_inside_each_disjoint_tube():
    circulation = vesica_circulation(0.8, return_split=0.4)
    bundle = map_graph_currents_to_tori(
        circulation.edges,
        major_radius=2.0,
        minor_radius=0.3,
        gap=0.3,
    )

    for channel in bundle.channels:
        point = (channel.major_radius + 0.08, 0.05, channel.center_z + 0.07)
        assert bundle.active_domain_count(point) == 1
        errors = []
        for h in (1e-3, 5e-4, 2.5e-4):
            divergence = 0.0
            for axis in range(3):
                plus = list(point)
                minus = list(point)
                plus[axis] += h
                minus[axis] -= h
                divergence += (
                    bundle.current(plus)[axis] - bundle.current(minus)[axis]
                ) / (2 * h)
            errors.append(abs(divergence))
        assert errors[-1] < errors[0] / 8
        assert errors[-1] < 3e-5


def test_zero_edge_still_has_an_assigned_domain_but_zero_field():
    circulation = vesica_circulation(0.0)
    bundle = map_graph_currents_to_tori(circulation.edges)
    assert len(bundle.channels) == 4
    channel = bundle.channels[0]
    point = (channel.major_radius, 0.0, channel.center_z)
    assert channel.contains_domain_point(point)
    assert channel.current(point) == (0.0, 0.0, 0.0)


def test_bundle_is_centered_and_channel_domains_do_not_overlap():
    circulation = vesica_circulation(1.0)
    bundle = map_graph_currents_to_tori(
        circulation.edges,
        minor_radius=0.5,
        gap=0.25,
        center_z=7.0,
    )
    centers = tuple(channel.center_z for channel in bundle.channels)
    assert sum(centers) / len(centers) == pytest.approx(7.0)
    assert bundle.maximum_overlap_count() == 1

    for left, right in zip(bundle.channels, bundle.channels[1:]):
        assert right.axial_interval[0] - left.axial_interval[1] == pytest.approx(0.25)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"gap": -0.1},
        {"minor_radius": 0.0},
        {"major_radius": 0.5, "minor_radius": 0.5},
        {"center_z": math.inf},
    ],
)
def test_invalid_bundle_geometry_is_rejected(kwargs):
    with pytest.raises(ValueError):
        map_graph_currents_to_tori(vesica_circulation(1.0).edges, **kwargs)
