"""Bounded parameter checks for the static four-edge construction.

These cases exercise existing builders, rather than expand the fixed-reference
API or claim that an entire parameter interval is collision-free.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from src.toroidal_separated_channels import build_separated_framed_edge_network
from src.toroidal_shared_return_connectors import (
    attach_shared_return_connectors,
    audit_connected_geometry,
)
from src.toroidal_shared_return_route import (
    certify_shared_return_endpoint,
    move_inner_return_to_shared_route,
)
from src.toroidal_smooth_bends import build_smooth_global_toroidal_routing
from src.vesica_tree_circulation import PORT_NODES, vesica_circulation


# current, return split, shell gap, bend margin, connector length.
# Paired extremes stress current sign/magnitude and transition length without
# an expensive Cartesian scan. Every shell gap is positive and well resolved.
SUPPORTED_CASES = (
    pytest.param((0.001, 0.15, 3.0, 0.05, 0.25), id="small-current-short-connectors"),
    pytest.param((-8.0, 0.85, 3.0, 0.05, 4.0), id="negative-current-long-connectors"),
    pytest.param((2.0, 0.5, 0.5, 0.05, 1.0), id="equal-return-small-shell-gap"),
    pytest.param((-0.125, 0.1, 1.0, 0.1, 0.5), id="negative-asymmetric-return"),
    pytest.param((5.0, 0.9, 6.0, 0.2, 2.0), id="wide-shell-gap"),
    pytest.param((1.0, 0.4, 3.0, 0.001, 1.0), id="small-positive-bend-margin"),
)


def _endpoint(parameters):
    current, split, gap, margin, length = parameters
    framed = build_separated_framed_edge_network(
        vesica_circulation(current, return_split=split).edges,
        PORT_NODES,
        shell_gap=gap,
        connector_length=length,
    )
    reference = build_smooth_global_toroidal_routing(framed.framed_network, bend_margin=margin)
    return move_inner_return_to_shared_route(reference, 1.0)


@pytest.fixture(scope="module", params=SUPPORTED_CASES)
def varied_network(request):
    return request.param, attach_shared_return_connectors(_endpoint(request.param))


def test_parameter_cases_preserve_geometry_and_graph_currents(varied_network):
    parameters, network = varied_network
    current, split, gap, _, length = parameters
    certificate = certify_shared_return_endpoint(network.routing)
    audit = audit_connected_geometry(network)
    assert certificate.shell_gap == pytest.approx(gap)
    assert min(
        certificate.minimum_jacobian_margin,
        certificate.minimum_nonadjacent_piece_clearance,
        certificate.minimum_other_edge_clearance,
        certificate.nonincident_junction_clearance,
        audit.minimum_transition_jacobian_bound,
        audit.minimum_unchanged_tube_clearance,
    ) > 0
    assert audit.connector_count == 8
    assert audit.nested_transition_pair_count == 2
    assert audit.minimum_transition_endpoint_gap == 0.0  # Intended port contact.
    assert [edge.flux for edge in network.edges] == pytest.approx(
        (current, current, current * split, current * (1.0 - split))
    )
    for edge in network.edges:
        assert edge.inlet.transition.length == length
        assert edge.outlet.transition.length == length
        assert edge.pieces[0].volume.length > 0
        assert edge.pieces[-1].volume.length > 0


def test_parameter_cases_match_all_interfaces_in_the_global_field(varied_network):
    parameters, network = varied_network
    tolerance = 2e-11 * abs(parameters[0])
    assert network.maximum_interface_residual() < tolerance
    for edge in network.edges:
        for placed in (edge.inlet, edge.outlet):
            for s in (0.0, 1.0):
                for q in (0.2, 0.65):
                    point = placed.map_point(s, q, 1.1)
                    assert network.current(point) == pytest.approx(
                        placed.current(point), rel=2e-11, abs=tolerance
                    )


def test_global_current_has_the_signed_flux_on_physical_planar_cuts(varied_network):
    _, network = varied_network
    nodes, weights = np.polynomial.legendre.leggauss(8)
    theta_count = 12
    # Integrate J dot n against r dr dtheta in global Cartesian coordinates.
    # This does not reuse transition Jacobians or flux_measure_density.
    for edge in network.edges:
        for placed in (edge.inlet, edge.outlet):
            for s in (0.2, 0.8):
                inner = placed.transition.radius(s, 0.0)
                outer = placed.transition.radius(s, 1.0)
                radii = inner + (nodes + 1.0) * (outer - inner) / 2.0
                radial_weights = weights * (outer - inner) / 2.0
                z = placed.origin[2] + placed.axis_sign * s * placed.transition.length
                contributions = []
                for radius, weight in zip(radii, radial_weights, strict=True):
                    for index in range(theta_count):
                        theta = (index + 0.37) * 2.0 * math.pi / theta_count
                        point = (
                            placed.origin[0] + radius * math.cos(theta),
                            placed.origin[1] + radius * math.sin(theta),
                            z,
                        )
                        contributions.append(
                            network.current(point)[2] * placed.axis_sign * radius * weight
                            * 2.0 * math.pi / theta_count
                        )
                assert math.fsum(contributions) == pytest.approx(
                    edge.flux, rel=2e-10, abs=2e-12 * abs(edge.flux)
                )


def test_positive_but_unresolved_bend_clearance_is_conservatively_rejected():
    endpoint = _endpoint((1.0, 0.4, 3.0, 1e-11, 1.0))
    # Rejection is lack of a resolved bound, not evidence of a collision.
    with pytest.raises(ValueError, match="bounds do not certify clearance"):
        attach_shared_return_connectors(endpoint)


def test_builder_generated_overlong_connectors_cannot_be_attached():
    endpoint = _endpoint((1.0, 0.4, 3.0, 0.05, 100.0))
    with pytest.raises(ValueError, match="longer than its connector"):
        attach_shared_return_connectors(endpoint)
