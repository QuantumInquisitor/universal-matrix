from __future__ import annotations

import math

import numpy as np
import pytest

from src.graph_toroidal_flux_bundle import map_graph_currents_to_tori
from src.toroidal_annular_junction import connect_bundle_to_annular_junctions
from src.toroidal_framed_edge_assembly import (
    AnnularPiolaTransition,
    StraightenedCutOpenToroidalChannel,
    build_framed_edge_network,
)
from src.vesica_tree_circulation import (
    PORT_NODES,
    tree_circulation,
    vesica_circulation,
)


def test_general_annular_transition_is_divergence_free():
    transition = AnnularPiolaTransition(
        0.5,
        1.1,
        1.4,
        2.0,
        1.3,
        1.7,
    )
    point = transition.map_point(0.43, 0.37, 0.29)
    errors = []
    for h in (2e-4, 1e-4, 5e-5):
        divergence = 0.0
        for axis in range(3):
            plus = list(point)
            minus = list(point)
            plus[axis] += h
            minus[axis] -= h
            divergence += (
                transition.current(plus)[axis] - transition.current(minus)[axis]
            ) / (2 * h)
        errors.append(abs(divergence))
    assert errors[-1] < 5e-7
    assert errors[-1] < errors[0] / 8


@pytest.mark.parametrize("flux", [1.2, -0.7, 0.0])
def test_straightened_cut_open_channel_matches_original_torus_cut(flux):
    from src.conservative_toroidal_field import ToroidalContentCurrent

    field = ToroidalContentCurrent(2.2, 0.5, flux, 0.0)
    channel = StraightenedCutOpenToroidalChannel(field, length=1.4, z_start=0.8)
    for q in (0.1, 0.3, 0.5, 0.75, 0.9):
        radius = channel.inner_radius + (channel.outer_radius - channel.inner_radius) * q
        assert channel.original_cut_vector_residual(radius) < 1e-12
    assert channel.source_outward_flux == -flux
    assert channel.target_outward_flux == flux


def test_positive_vesica_edge_assembly_closes_flux_and_vectors():
    circulation = vesica_circulation(1.5, return_split=0.4)
    bundle = map_graph_currents_to_tori(circulation.edges)
    junctions = connect_bundle_to_annular_junctions(bundle, PORT_NODES)
    framed = build_framed_edge_network(junctions)

    assert framed.maximum_interface_residual() < 1e-12
    assert framed.maximum_flux_chain_residual() < 1e-12
    assert framed.maximum_endpoint_vector_residual() < 1e-12
    assert all(assembly.axis_sign == 1 for assembly in framed.assemblies)


def test_negative_vesica_edge_assembly_uses_axis_flip_and_still_matches():
    circulation = vesica_circulation(-1.5, return_split=0.4)
    bundle = map_graph_currents_to_tori(circulation.edges)
    junctions = connect_bundle_to_annular_junctions(bundle, PORT_NODES)
    framed = build_framed_edge_network(junctions)

    assert framed.maximum_interface_residual() < 1e-12
    assert framed.maximum_flux_chain_residual() < 1e-12
    assert framed.maximum_endpoint_vector_residual() < 1e-12
    assert all(assembly.axis_sign == -1 for assembly in framed.assemblies)


def test_zero_current_edge_assemblies_remain_explicit_and_zero():
    circulation = vesica_circulation(0.0)
    bundle = map_graph_currents_to_tori(circulation.edges)
    junctions = connect_bundle_to_annular_junctions(bundle, PORT_NODES)
    framed = build_framed_edge_network(junctions)

    assert len(framed.assemblies) == len(circulation.edges)
    assert framed.maximum_interface_residual() == 0.0
    assert framed.maximum_flux_chain_residual() == 0.0
    assert framed.maximum_endpoint_vector_residual() == 0.0
    assert all(assembly.axis_sign == 1 for assembly in framed.assemblies)


def test_tree_network_builds_one_framed_assembly_per_graph_edge():
    circulation = tree_circulation(
        rings=2,
        radial_current=-1.1,
        weave_current=0.14,
        weave_handedness=-1,
    )
    bundle = map_graph_currents_to_tori(circulation.edges)
    junctions = connect_bundle_to_annular_junctions(
        bundle,
        circulation.geometry.nodes,
        outer_radius=1.8,
        junction_gap=0.2,
    )
    framed = build_framed_edge_network(
        junctions,
        connector_length=0.8,
        channel_length=1.3,
    )

    assert len(framed.assemblies) == len(circulation.edges)
    assert framed.maximum_interface_residual() < 1e-12
    assert framed.maximum_flux_chain_residual() < 1e-12
    assert framed.maximum_endpoint_vector_residual() < 1e-12


def test_transition_jacobian_is_positive_for_mismatched_annuli():
    transition = AnnularPiolaTransition(
        0.4,
        0.9,
        1.5,
        2.3,
        -0.8,
        1.2,
    )
    assert min(
        transition.jacobian_determinant(s, q)
        for s in (0.0, 0.2, 0.5, 0.8, 1.0)
        for q in (0.0, 0.25, 0.5, 0.75, 1.0)
    ) > 0.0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"connector_length": 0.0},
        {"channel_length": 0.0},
        {"connector_length": math.inf},
    ],
)
def test_invalid_edge_assembly_lengths_are_rejected(kwargs):
    circulation = vesica_circulation(1.0)
    bundle = map_graph_currents_to_tori(circulation.edges)
    junctions = connect_bundle_to_annular_junctions(bundle, PORT_NODES)
    with pytest.raises(ValueError):
        build_framed_edge_network(junctions, **kwargs)
