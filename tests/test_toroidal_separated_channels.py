from __future__ import annotations

import math

import pytest

from src.toroidal_incident_overlap_audit import audit_incident_connector_overlap
from src.toroidal_separated_channels import (
    allocate_edge_channel_shells,
    build_separated_framed_edge_network,
    map_graph_currents_to_separated_tori,
    maximum_same_face_connector_overlap,
    minimum_same_face_connector_gap,
)
from src.vesica_tree_circulation import (
    PORT_NODES,
    tree_circulation,
    vesica_circulation,
)


def test_shell_allocator_is_ordered_and_pairwise_disjoint():
    shells = allocate_edge_channel_shells(
        5,
        base_inner_radius=2.0,
        shell_width=0.4,
        shell_gap=0.3,
    )
    assert len(shells) == 5
    assert all(shell.width == pytest.approx(0.4) for shell in shells)
    assert all(
        right.inner_radius - left.outer_radius == pytest.approx(0.3)
        for left, right in zip(shells, shells[1:])
    )


def test_separated_bundle_cut_annuli_match_allocated_shells():
    circulation = vesica_circulation(1.2, return_split=0.4)
    separated = map_graph_currents_to_separated_tori(circulation.edges)

    for channel, shell in zip(
        separated.bundle.channels,
        separated.shells,
        strict=True,
    ):
        field = channel.field
        assert field.major_radius - field.minor_radius == pytest.approx(shell.inner_radius)
        assert field.major_radius == pytest.approx(shell.outer_radius)
        assert field.poloidal_flux == pytest.approx(channel.edge.current)


@pytest.mark.parametrize("current", [1.0, -1.0])
def test_vesica_separated_channels_remove_same_face_connector_overlap(current):
    circulation = vesica_circulation(current, return_split=0.4)
    result = build_separated_framed_edge_network(
        circulation.edges,
        PORT_NODES,
        shell_gap=0.3,
    )

    audit = audit_incident_connector_overlap(result.framed_network)
    assert audit.pair_count == 0
    assert maximum_same_face_connector_overlap(result.framed_network) == 0.0
    assert minimum_same_face_connector_gap(result.framed_network) >= -1e-12
    assert result.minimum_terminal_shell_gap() == pytest.approx(0.3)
    assert result.framed_network.maximum_interface_residual() < 1e-12
    assert result.framed_network.maximum_flux_chain_residual() < 1e-12
    assert result.framed_network.maximum_endpoint_vector_residual() < 1e-12


def test_tree_separated_channels_remove_connector_overlap():
    circulation = tree_circulation(
        rings=2,
        radial_current=-1.1,
        weave_current=0.14,
        weave_handedness=-1,
    )
    result = build_separated_framed_edge_network(
        circulation.edges,
        circulation.geometry.nodes,
        shell_width=0.3,
        shell_gap=0.2,
        junction_outer_radius=1.8,
        junction_gap=0.2,
        connector_length=0.8,
        channel_length=1.1,
    )

    assert audit_incident_connector_overlap(result.framed_network).pair_count == 0
    assert maximum_same_face_connector_overlap(result.framed_network, samples=61) == 0.0
    assert minimum_same_face_connector_gap(result.framed_network, samples=61) >= -1e-12


def test_zero_current_vesica_remains_explicit():
    circulation = vesica_circulation(0.0)
    result = build_separated_framed_edge_network(circulation.edges, PORT_NODES)

    assert len(result.framed_network.assemblies) == len(circulation.edges)
    assert all(assembly.edge.current == 0.0 for assembly in result.framed_network.assemblies)
    assert audit_incident_connector_overlap(result.framed_network).pair_count == 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"base_inner_radius": 0.0},
        {"shell_width": 0.0},
        {"shell_gap": -0.1},
        {"axial_gap": -0.1},
        {"shell_width": math.inf},
    ],
)
def test_invalid_separated_channel_geometry_is_rejected(kwargs):
    circulation = vesica_circulation(1.0)
    with pytest.raises(ValueError):
        map_graph_currents_to_separated_tori(circulation.edges, **kwargs)


def test_shell_allocator_rejects_invalid_edge_count():
    with pytest.raises(ValueError):
        allocate_edge_channel_shells(-1)
    with pytest.raises(TypeError):
        allocate_edge_channel_shells(2.5)
