from __future__ import annotations

import pytest

from src.toroidal_incident_bend_audit import (
    _endpoint_bend_and_straight,
    audit_incident_bend_collisions,
)
from src.toroidal_separated_channels import build_separated_framed_edge_network
from src.vesica_tree_circulation import (
    PORT_NODES,
    tree_circulation,
    vesica_circulation,
)


@pytest.mark.parametrize("current", [1.0, -1.0])
def test_separated_vesica_connectors_still_collide_at_endpoint_bends(current):
    circulation = vesica_circulation(current, return_split=0.4)
    separated = build_separated_framed_edge_network(
        circulation.edges,
        PORT_NODES,
        shell_width=0.4,
        shell_gap=0.25,
    )
    audit = audit_incident_bend_collisions(separated)

    assert audit.collision_count > 0
    assert audit.affected_nodes
    assert audit.maximum_penetration > 0.0
    assert all(
        item.bending_edge_index != item.straight_edge_index
        for item in audit.collisions
    )


def test_zero_current_vesica_has_no_incident_bend_collisions():
    circulation = vesica_circulation(0.0)
    separated = build_separated_framed_edge_network(
        circulation.edges,
        PORT_NODES,
    )
    audit = audit_incident_bend_collisions(separated)

    assert audit.collision_count == 0
    assert audit.affected_nodes == frozenset()
    assert audit.maximum_penetration == 0.0


def test_tree_reference_still_exposes_incident_bend_collision():
    circulation = tree_circulation(
        rings=2,
        radial_current=-1.1,
        weave_current=0.14,
        weave_handedness=-1,
    )
    separated = build_separated_framed_edge_network(
        circulation.edges,
        circulation.geometry.nodes,
        shell_width=0.3,
        shell_gap=0.2,
        junction_outer_radius=1.8,
        junction_gap=0.2,
        connector_length=0.8,
        channel_length=1.1,
    )
    audit = audit_incident_bend_collisions(
        separated,
        bend_margin=0.3,
        edge_gap=0.6,
        phi_samples=19,
        q_samples=7,
        theta_samples=32,
    )

    assert audit.collision_count > 0
    assert audit.maximum_penetration > 0.0


def test_audit_returns_reproducible_collision_witnesses():
    circulation = vesica_circulation(1.0, return_split=0.4)
    separated = build_separated_framed_edge_network(
        circulation.edges,
        PORT_NODES,
    )
    first = audit_incident_bend_collisions(
        separated,
        phi_samples=17,
        q_samples=7,
        theta_samples=32,
    )
    second = audit_incident_bend_collisions(
        separated,
        phi_samples=17,
        q_samples=7,
        theta_samples=32,
    )

    assert first.collisions == second.collisions


def test_shifted_collision_witnesses_lie_in_both_actual_volumes():
    circulation = vesica_circulation(1.0, return_split=0.4)
    separated = build_separated_framed_edge_network(
        circulation.edges, PORT_NODES, shell_gap=3.0
    )
    audit = audit_incident_bend_collisions(
        separated, bend_margin=0.05, phi_samples=13, q_samples=5, theta_samples=24,
        phi_offset=0.5, q_offset=0.5, theta_offset=0.5,
    )
    assert audit.collision_count == 2
    edges = {edge.edge_index: edge for edge in audit.smooth_routing.edges}
    for witness in audit.collisions:
        bend, _ = _endpoint_bend_and_straight(edges[witness.bending_edge_index], witness.node)
        _, straight = _endpoint_bend_and_straight(edges[witness.straight_edge_index], witness.node)
        assert 0.0 < witness.witness_q < 1.0
        assert bend.map_point(
            witness.witness_phi, witness.witness_q, witness.witness_theta
        ) == pytest.approx(witness.witness_point)
        assert straight.penetration_margin(witness.witness_point) == pytest.approx(
            witness.maximum_penetration
        )
        assert witness.maximum_penetration > 0.19


@pytest.mark.parametrize(
    "kwargs",
    [
        {"phi_samples": 3},
        {"q_samples": 2},
        {"theta_samples": 7},
    ],
)
def test_invalid_sampling_resolution_is_rejected(kwargs):
    circulation = vesica_circulation(1.0)
    separated = build_separated_framed_edge_network(
        circulation.edges,
        PORT_NODES,
    )
    with pytest.raises(ValueError):
        audit_incident_bend_collisions(separated, **kwargs)
