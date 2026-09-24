from __future__ import annotations

import math
from dataclasses import replace

import numpy as np
import pytest

from src.toroidal_fixed_interface_obstruction import (
    audit_fixed_bend_interfaces,
    find_mid_annulus_interface_witness,
)
from src.toroidal_incident_bend_audit import AnnularStraightSegment, _endpoint_bend_and_straight
from src.toroidal_separated_channels import build_separated_framed_edge_network
from src.toroidal_smooth_bends import AnnularQuarterBend, build_smooth_global_toroidal_routing
from src.vesica_tree_circulation import PORT_NODES, vesica_circulation


def _pair():
    bend = AnnularQuarterBend(
        corner=(0.0, 0.0, 0.0), source_tangent=(0.0, -1.0, 0.0),
        target_tangent=(0.0, 0.0, 1.0), bend_radius=2.0,
        inner_radius=0.8, outer_radius=1.2, flux=0.4,
    )
    straight = AnnularStraightSegment((0.0, 0.0, -5.0), (0.0, 0.0, 5.0), 2.1, 2.2)
    return bend, straight


@pytest.mark.parametrize("flux", (-2.0, 0.4, 3.0))
def test_analytic_witness_has_independent_geometric_membership(flux):
    bend, straight = _pair()
    bend = replace(bend, flux=flux)
    witness = find_mid_annulus_interface_witness(bend, straight, phi=0.0)
    assert witness is not None
    x, y, z = witness.point
    assert y == pytest.approx(2.0)  # End face plane.
    assert math.hypot(x, z) == pytest.approx(1.0)  # Interior annulus circle.
    assert math.hypot(x, y) == pytest.approx(2.15)  # Neighbor radial midpoint.
    assert -5.0 < z < 5.0
    assert witness.straight_penetration == pytest.approx(0.05)
    assert bend.inverse_parameters(witness.point) == pytest.approx((0.0, 0.5, witness.theta))


def test_finite_segment_checks_both_axial_branches():
    bend, straight = _pair()
    clipped = replace(straight, end=(0.0, 0.0, -0.2))
    witness = find_mid_annulus_interface_witness(bend, clipped, phi=0.0)
    assert witness is not None
    assert witness.point[2] < -0.2
    reversed_segment = replace(clipped, start=clipped.end, end=clipped.start)
    reverse = find_mid_annulus_interface_witness(bend, reversed_segment, phi=0.0)
    assert reverse is not None
    assert reverse.point == pytest.approx(witness.point)


def test_infinite_cylinder_overlap_outside_finite_segment_is_not_reported():
    bend, straight = _pair()
    distant = replace(straight, start=(0.0, 0.0, 2.0), end=(0.0, 0.0, 3.0))
    assert find_mid_annulus_interface_witness(bend, distant, phi=0.0) is None


@pytest.mark.parametrize("inner", (math.sqrt(5), 2.5))
def test_tangent_mid_circle_or_separated_shell_has_no_strict_witness(inner):
    bend, straight = _pair()
    straight = replace(straight, inner_radius=inner, outer_radius=inner + 0.1)
    assert find_mid_annulus_interface_witness(bend, straight, phi=0.0) is None


def test_unsupported_offset_and_alignment_return_no_witness():
    bend, straight = _pair()
    offset = replace(straight, start=(0.1, 0.0, -5.0), end=(0.1, 0.0, 5.0))
    tilted = replace(straight, end=(0.0, 1.0, 5.0))
    for candidate in (offset, tilted):
        assert find_mid_annulus_interface_witness(bend, candidate, phi=0.0) is None


@pytest.mark.parametrize("phi", (-0.1, 0.7, math.pi, float("nan")))
def test_interior_or_invalid_phi_cannot_be_claimed_as_fixed_interface(phi):
    bend, straight = _pair()
    with pytest.raises(ValueError, match="end face"):
        find_mid_annulus_interface_witness(bend, straight, phi=phi)


@pytest.mark.parametrize("scale", (0.5, 2.0))
def test_witness_survives_rotation_translation_and_scaling(scale):
    bend, straight = _pair()
    rotation = np.array(((1.0, 2.0, 2.0), (2.0, 1.0, -2.0), (-2.0, 2.0, -1.0))) / 3
    assert np.linalg.det(rotation) == pytest.approx(1.0)
    def vector(value):
        return tuple(rotation @ value)
    def point(value):
        return tuple(scale * (rotation @ value) + (2.0, -3.0, 1.0))
    transformed = replace(
        bend, corner=point(bend.corner), source_tangent=vector(bend.source_tangent),
        target_tangent=vector(bend.target_tangent), bend_radius=scale * bend.bend_radius,
        inner_radius=scale * bend.inner_radius, outer_radius=scale * bend.outer_radius,
    )
    neighbor = AnnularStraightSegment(
        point(straight.start), point(straight.end), scale * straight.inner_radius,
        scale * straight.outer_radius,
    )
    witness = find_mid_annulus_interface_witness(transformed, neighbor, phi=0.0)
    assert witness is not None
    assert witness.straight_penetration == pytest.approx(scale * 0.05)
    assert transformed.inverse_parameters(witness.point)[:2] == pytest.approx((0.0, 0.5))


def test_reference_obstructions_are_independent_of_volume_sampling_and_extend_inward():
    circulation = vesica_circulation(1.0, return_split=0.4)
    network = build_separated_framed_edge_network(circulation.edges, PORT_NODES, shell_gap=3.0)
    audit = audit_fixed_bend_interfaces(network, bend_margin=0.05)
    assert audit.examined_interface_count == 8
    assert audit.obstruction_count == 2
    assert {str(item.node) for item in audit.obstructions} == {"cusp_a", "cusp_b"}
    routing = build_smooth_global_toroidal_routing(network.framed_network, bend_margin=0.05)
    edges = {edge.edge_index: edge for edge in routing.edges}
    for item in audit.obstructions:
        assert (item.bending_edge_index, item.straight_edge_index) == (2, 3)
        witness = item.witness
        assert witness.straight_penetration == pytest.approx(0.2)
        bend, _ = _endpoint_bend_and_straight(edges[2], item.node)
        _, straight = _endpoint_bend_and_straight(edges[3], item.node)
        # Verify the actual reference volumes, not only a face-to-shell touch.
        inward_phi = 1e-5 if witness.phi == 0.0 else math.pi / 2 - 1e-5
        interior = bend.map_point(inward_phi, witness.q, witness.theta)
        assert straight.penetration_margin(interior) > 0.19
        assert bend.inverse_parameters(witness.point) is not None
        assert bend.interface_vector_residual() < 1e-10
