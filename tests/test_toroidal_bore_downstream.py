from __future__ import annotations

import math
from dataclasses import replace
from itertools import combinations, product

import numpy as np
import pytest

from src.toroidal_bore_downstream import (
    audit_bore_downstream,
    build_bore_downstream_reference,
)
from src.toroidal_shared_return_connectors import _connect_edge
from src.toroidal_shared_return_route import RoutedTubePiece
from src.toroidal_smooth_bends import AnnularQuarterBend


@pytest.fixture(scope="module", params=(1.0, -1.0))
def reference(request):
    return build_bore_downstream_reference(request.param)


def test_downstream_uses_existing_host_centerline_and_original_A_connector(reference):
    host = _connect_edge(reference.routing.edges[1])
    original = reference.routing.edges[0].route
    assert reference.pieces[0].volume.start == reference.passage.transit.outlet.end
    assert reference.pieces[0].volume.end == host.pieces[0].volume.end
    assert reference.outlet.transition == original.assembly.outlet
    assert reference.outlet.end == original.target_frame.origin
    assert reference.passage.outgoing == host.inlet
    assert reference.passage.incoming == _connect_edge(reference.routing.edges[3]).outlet
    for inner, outer in zip(reference.pieces, host.pieces, strict=True):
        assert (inner.volume.inner_radius, inner.volume.outer_radius) == (2.0, 2.4)
        assert inner.volume.end == outer.volume.end
        if isinstance(inner.volume, AnnularQuarterBend):
            assert inner.volume.corner == outer.volume.corner
            assert inner.volume.bend_radius == outer.volume.bend_radius
            assert inner.volume.flux == reference.flux


def test_inventory_has_every_changed_pair_once_and_excludes_retained_pairs(reference):
    audit = audit_bore_downstream(reference)
    changed, retained = audit.component_ids, audit.retained_component_ids
    required = set(combinations(changed, 2)) | set(product(changed, retained))
    actual = [(pair.left, pair.right) for pair in audit.pair_checks]
    assert len(actual) == len(set(actual))
    assert set(actual) == required
    assert not set(changed) & set(retained)
    assert audit.unresolved_pair_count == 0
    assert all(pair.bound is None or pair.bound > 0 for pair in audit.pair_checks)
    assert {pair.method for pair in audit.pair_checks} == {
        "opposite_caps", "boxes", "coaxial_shells", "shared_bend", "shared_straight", "nested_transitions",
    }
    assert len(audit.interfaces) == len(changed)
    assert all(item.sampled_relative_current_residual < 1e-10 for item in audit.interfaces)
    assert all(bound.determinant_lower_bound > 0 for bound in audit.jacobians)


def test_port_inventory_marks_B_open_and_A_attached_without_an_extra_C_port(reference):
    audit = audit_bore_downstream(reference)
    attached = {(p.node, p.edge_index): p.component for p in audit.junction_ports}
    assert attached["B", 0] is None
    assert attached["A", 0] == "A_edge0_connector"
    assert {edge for node, edge in attached if node == "C"} == {1, 3}
    assert all(component is not None for key, component in attached.items() if key != ("B", 0))
    openings = {boundary.name: boundary for boundary in audit.open_boundaries}
    assert set(openings) == {"B_edge0_port", "transit_inlet_near_C"}
    assert openings["B_edge0_port"].outward_flux == reference.flux
    assert openings["transit_inlet_near_C"].outward_flux == -reference.flux
    assert openings["B_edge0_port"].origin != openings["transit_inlet_near_C"].origin
    assert audit.net_open_boundary_flux == 0


def test_current_selects_one_chart_at_each_bore_and_downstream_interface(reference):
    for placed, end in ((reference.passage.transit.inlet, 1.0),
                         (reference.passage.transit.outlet, 0.0),
                         (reference.passage.transit.outlet, 1.0),
                         (reference.outlet, 0.0)):
        point = placed.map_point(end, 0.55, 0.71)
        expected = np.array(placed.current(point))
        assert np.linalg.norm(expected) > 0
        assert reference.current_if_inside(point) == pytest.approx(expected, rel=1e-10, abs=0)
        axis = np.array((0.0, 0.0, placed.axis_sign))
        for direction in (-1, 1):
            nearby = reference.current_if_inside(np.array(point) + direction * 1e-7 * axis)
            assert nearby is not None
            # The radial component grows linearly away from a taper endpoint;
            # compare the vector error to the nonzero axial profile scale.
            assert np.linalg.norm(np.array(nearby) - expected) < 2e-5 * np.linalg.norm(expected)


def test_target_connector_gap_closes_only_at_the_zero_current_circle(reference):
    inner, outer = reference.outlet, _connect_edge(reference.routing.edges[1]).outlet
    for fraction in (0.0, 0.17, 0.5, 0.91, 0.99):
        actual = outer.transition.radius(fraction, 0) - inner.transition.radius(fraction, 1)
        expected = 3 * (1 - (3 * fraction**2 - 2 * fraction**3))
        assert actual == pytest.approx(expected, rel=3e-11)
        assert actual > 0
    assert outer.transition.radius(1, 0) == inner.transition.radius(1, 1) == 1
    for theta in (0.0, 0.31, 1.4, 2.8):
        point = inner.map_point(1.0, 1.0, theta)
        assert inner.current(point) == pytest.approx((0.0, 0.0, 0.0), abs=1e-13)
        assert outer.current(point) == pytest.approx((0.0, 0.0, 0.0), abs=1e-13)
    contacts = [p for p in audit_bore_downstream(reference).pair_checks if p.contact == "A_target_circle"]
    assert len(contacts) == 1
    assert {contacts[0].left, contacts[0].right} == {"A_edge0_connector", "edge1_outlet"}


def test_continuity_equation_in_the_new_taper_and_bend(reference):
    taper = reference.outlet
    bend = next(p.volume for p in reference.pieces if isinstance(p.volume, AnnularQuarterBend))
    for point in (np.array(taper.map_point(0.4, 0.57, 0.61)), np.array(bend.map_point(0.67, 0.57, 0.61))):
        h = 2e-6
        divergence = math.fsum(
            (reference.current_if_inside(point + h * axis)[i]
             - reference.current_if_inside(point - h * axis)[i]) / (2 * h)
            for i, axis in enumerate(np.eye(3))
        )
        assert abs(divergence) < 2e-7


@pytest.mark.parametrize("current", (2e-10, -2e-10, 0.25, -2.0, 10.0))
def test_supported_current_magnitudes_preserve_geometry_and_signed_trace(current):
    candidate = build_bore_downstream_reference(current)
    audit = audit_bore_downstream(candidate)
    assert candidate.flux == pytest.approx(0.4 * current, rel=1e-15, abs=0)
    assert candidate.pieces[0].volume.inner_radius == 2.0
    assert all(boundary.outward_flux != 0 for boundary in audit.open_boundaries)
    assert max(interface.sampled_relative_current_residual for interface in audit.interfaces) < 1e-10
    # Physical polar area at the bore middle, without the transition Jacobian.
    nodes, weights = np.polynomial.legendre.leggauss(6)
    values = []
    center = candidate.passage.junction.center
    for node, weight in zip(nodes, weights, strict=True):
        radius = 0.1 + (node + 1) * 0.1 / 2
        for theta in np.arange(9) * 2 * math.pi / 9 + 0.31:
            point = (center[0] + radius * math.cos(theta), radius * math.sin(theta), center[2])
            values.append(candidate.current_if_inside(point)[2] * math.copysign(1, current)
                          * radius * weight * 0.1 / 2 * 2 * math.pi / 9)
    assert math.fsum(values) == pytest.approx(candidate.flux, rel=2e-10, abs=0)


@pytest.mark.parametrize("current", (0.0, 1e-10, -1e-10, math.nan, math.inf, -math.inf, 1e308, True, "invalid"))
def test_unsupported_current_is_rejected(current):
    with pytest.raises(ValueError, match="current"):
        build_bore_downstream_reference(current)


@pytest.mark.parametrize("change", ("omit_piece", "reverse_axis", "resize_shell", "replace_current"))
def test_modified_reference_cannot_keep_the_previous_audit(reference, change):
    if change == "omit_piece":
        changed = replace(reference, pieces=reference.pieces[1:])
    elif change == "reverse_axis":
        changed = replace(reference, outlet=replace(reference.outlet, axis_sign=-reference.outlet.axis_sign))
    elif change == "resize_shell":
        first = RoutedTubePiece(replace(reference.pieces[0].volume, outer_radius=2.5))
        changed = replace(reference, pieces=(first, *reference.pieces[1:]))
    else:
        changed = replace(reference, current=reference.current * 0.9)
    with pytest.raises(ValueError, match="modified candidate"):
        audit_bore_downstream(changed)


@pytest.mark.parametrize("point", ((1, 2), (1, 2, math.nan), (math.inf, 0, 0), None))
def test_partial_evaluator_rejects_nonfinite_or_malformed_points(reference, point):
    with pytest.raises(ValueError, match="point"):
        reference.current_if_inside(point)


def test_partial_evaluator_excludes_host_shell_and_missing_B_connection(reference):
    center = reference.passage.junction.center
    assert reference.current_if_inside((center[0] + 1.0, center[1], center[2])) is None
    b = reference.routing.global_routing.junction("B")
    port_center = b.port_axis_point(0)
    assert reference.current_if_inside((port_center[0] + 1.0, port_center[1], port_center[2])) is None
