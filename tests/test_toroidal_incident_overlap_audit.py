from __future__ import annotations

import math

import pytest

from src.graph_toroidal_flux_bundle import map_graph_currents_to_tori
from src.toroidal_annular_junction import connect_bundle_to_annular_junctions
from src.toroidal_framed_edge_assembly import build_framed_edge_network
from src.toroidal_incident_overlap_audit import (
    audit_incident_connector_overlap,
)
from src.vesica_tree_circulation import (
    PORT_NODES,
    tree_circulation,
    vesica_circulation,
)


def framed_vesica(current=1.0):
    circulation = vesica_circulation(current, return_split=0.4)
    bundle = map_graph_currents_to_tori(circulation.edges)
    junctions = connect_bundle_to_annular_junctions(bundle, PORT_NODES)
    return build_framed_edge_network(junctions)


def test_positive_vesica_has_two_same_face_overlap_pairs():
    audit = audit_incident_connector_overlap(framed_vesica(1.0))

    assert audit.pair_count == 2
    assert len(audit.affected_nodes) == 2
    assert 0.0 < audit.earliest_overlap_progress < 1.0
    assert audit.maximum_terminal_overlap_width > 0.0


def test_negative_vesica_has_the_same_overlap_obstruction():
    positive = audit_incident_connector_overlap(framed_vesica(1.0))
    negative = audit_incident_connector_overlap(framed_vesica(-1.0))

    assert negative.pair_count == positive.pair_count
    assert negative.maximum_terminal_overlap_width == pytest.approx(
        positive.maximum_terminal_overlap_width
    )


def test_zero_current_vesica_has_no_nonzero_overlap_pairs():
    audit = audit_incident_connector_overlap(framed_vesica(0.0))
    assert audit.pair_count == 0
    assert audit.affected_nodes == frozenset()
    assert math.isinf(audit.earliest_overlap_progress)
    assert audit.maximum_terminal_overlap_width == 0.0


def test_overlap_is_absent_at_port_face_and_present_at_common_channel_end():
    network = framed_vesica(1.0)
    audit = audit_incident_connector_overlap(network)
    assert audit.pair_count > 0

    item = audit.overlaps[0]
    assert item.first_overlap_progress > 0.0
    assert item.first_overlap_progress < 1.0
    assert item.terminal_overlap_width == pytest.approx(
        network.assemblies[item.first_edge_index].channel.outer_radius
        - network.assemblies[item.first_edge_index].channel.inner_radius
    )


def test_tree_network_exposes_same_face_incident_overlap():
    circulation = tree_circulation(
        rings=2,
        radial_current=1.2,
        weave_current=0.15,
        weave_handedness=1,
    )
    bundle = map_graph_currents_to_tori(circulation.edges)
    junctions = connect_bundle_to_annular_junctions(
        bundle,
        circulation.geometry.nodes,
        outer_radius=1.8,
        junction_gap=0.2,
    )
    framed = build_framed_edge_network(junctions)
    audit = audit_incident_connector_overlap(framed)

    assert audit.pair_count > 0
    assert audit.affected_nodes
    assert 0.0 < audit.earliest_overlap_progress < 1.0


def test_every_reported_pair_uses_distinct_edges():
    audit = audit_incident_connector_overlap(framed_vesica(1.0))
    assert all(
        item.first_edge_index < item.second_edge_index
        for item in audit.overlaps
    )
