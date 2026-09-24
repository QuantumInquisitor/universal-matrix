"""Independent physical-coordinate checks and rejected counterfeit certificates."""

from dataclasses import replace
import math

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


def _polar_flux(field, center, normal, inner, outer):
    # Integrate physical area r dr dtheta without the map's Jacobian or
    # source-profile helper. The shifted angles avoid privileged meridians.
    center, normal = np.asarray(center), np.asarray(normal)
    basis = np.eye(3)[np.argmin(np.abs(normal))]
    first = np.cross(normal, basis)
    first /= np.linalg.norm(first)
    second = np.cross(normal, first)
    nodes, weights = np.polynomial.legendre.leggauss(6)
    contributions = []
    for node, weight in zip(nodes, weights, strict=True):
        radius = inner + (node + 1) * (outer - inner) / 2
        for index in range(11):
            angle = (index + 0.381) * 2 * math.pi / 11
            point = center + radius * (math.cos(angle) * first + math.sin(angle) * second)
            vector = field(tuple(point))
            assert vector is not None
            contributions.append(float(np.dot(vector, normal)) * radius * weight
                                 * (outer - inner) / 2 * 2 * math.pi / 11)
    return math.fsum(contributions)


def test_subtolerance_cap_displacement_with_real_interior_overlap_is_rejected(reference):
    original = reference.pieces[0].volume
    sign = reference.passage.transit.outlet.axis_sign
    delta = 5e-11
    moved = replace(original, start=(*original.start[:2], original.start[2] - sign * delta))
    counterfeit = replace(reference, pieces=(RoutedTubePiece(moved), *reference.pieces[1:]))
    witness = (original.start[0] + 2.2, original.start[1], original.start[2] - sign * delta / 2)
    assert 0 < moved.penetration_margin(witness) < 1e-10
    transition = reference.passage.transit.outlet
    local = transition.to_local(witness)
    axial_fraction = (local[2] - transition.transition.z_start) / transition.transition.length
    assert 0 < axial_fraction < 1
    assert transition.contains(witness)
    with pytest.raises(ValueError):
        audit_bore_downstream(counterfeit)


def test_crossed_nested_target_profiles_with_unchanged_flux_are_rejected(reference):
    host = _connect_edge(reference.routing.edges[1]).outlet
    altered = replace(reference.outlet, transition=replace(
        reference.outlet.transition, target_outer_radius=1.1))
    # The overlap is inside both collars, not merely their intended r=1 circle.
    fraction = 0.98
    low = max(altered.transition.radius(fraction, 0), host.transition.radius(fraction, 0))
    high = min(altered.transition.radius(fraction, 1), host.transition.radius(fraction, 1))
    assert high > low
    point = (altered.origin[0] + (low + high) / 2, altered.origin[1],
             altered.origin[2] + altered.axis_sign * fraction * altered.transition.length)
    assert altered.contains(point) and host.contains(point)
    assert altered.transition.flux == reference.outlet.transition.flux
    with pytest.raises(ValueError):
        audit_bore_downstream(replace(reference, outlet=altered))


@pytest.mark.parametrize("current", (2e-8, -2e-8))
def test_small_absolute_bend_flux_error_is_not_hidden_by_geometry_tolerance(current):
    original = build_bore_downstream_reference(current)
    index = next(i for i, piece in enumerate(original.pieces)
                 if isinstance(piece.volume, AnnularQuarterBend))
    bend = original.pieces[index].volume
    altered = replace(bend, flux=bend.flux + 1e-12)
    assert 0 < abs(altered.flux - bend.flux) < 1e-10
    pieces = list(original.pieces)
    pieces[index] = RoutedTubePiece(altered)
    with pytest.raises(ValueError):
        audit_bore_downstream(replace(original, pieces=tuple(pieces)))


def test_finite_difference_bend_maps_support_positive_jacobians_and_cap_planes(reference):
    for piece in reference.pieces:
        bend = piece.volume
        if not isinstance(bend, AnnularQuarterBend):
            continue
        lower_bound = (bend.bend_radius - bend.outer_radius) * bend.inner_radius * bend.width
        assert lower_bound > 0
        for phi, q, theta in ((0.19, 0.17, 0.2), (0.61, 0.83, 2.3), (1.27, 0.37, 1.1)):
            parameters = np.array((phi, q, theta))
            columns = []
            for axis in np.eye(3):
                delta = 1e-5 * axis
                columns.append((np.array(bend.map_point(*(parameters + delta)))
                                - bend.map_point(*(parameters - delta))) / (2e-5))
            determinant = np.linalg.det(np.column_stack(columns))
            radius = bend.inner_radius + q * bend.width
            exact = (bend.bend_radius - radius * math.cos(theta)) * radius * bend.width
            assert determinant == pytest.approx(exact, rel=1e-7)
            assert determinant >= lower_bound
            point = np.array(bend.map_point(phi, q, theta))
            assert np.dot(point - bend.start, bend.source_tangent) > 0
            assert np.dot(point - bend.end, bend.target_tangent) < 0


def test_signed_flux_survives_every_downstream_bend_and_nested_outlet(reference):
    expected = 0.4 * reference.current
    for piece in reference.pieces:
        bend = piece.volume
        if isinstance(bend, AnnularQuarterBend):
            measured = _polar_flux(reference.current_if_inside,
                bend.centerline_point(0.47), bend.tangent(0.47), bend.inner_radius, bend.outer_radius)
            assert measured == pytest.approx(expected, rel=3e-11, abs=0)
    placed = reference.outlet
    for fraction in (0.19, 0.73, 0.97):
        center = (*placed.origin[:2], placed.origin[2] + placed.axis_sign * fraction * placed.transition.length)
        measured = _polar_flux(reference.current_if_inside, center, (0, 0, placed.axis_sign),
            placed.transition.radius(fraction, 0), placed.transition.radius(fraction, 1))
        assert measured == pytest.approx(expected, rel=3e-11, abs=0)


def test_opposite_open_fluxes_are_spatially_distinct_and_not_an_attachment(reference):
    boundaries = {boundary.name: boundary for boundary in audit_bore_downstream(reference).open_boundaries}
    placement = reference.routing.global_routing.junction("B")
    port = placement.junction.port_by_edge(0)
    sign = reference.passage.transit.inlet.axis_sign
    center = placement.port_axis_point(0)

    def junction_field(point):
        local = tuple(x - c + d for x, c, d in zip(
            point, placement.center, placement.junction.center, strict=True))
        return placement.junction.current(local)

    b_flux = _polar_flux(junction_field, center, (0, 0, sign), port.inner_radius, port.outer_radius)
    inlet = reference.passage.transit.inlet
    inlet_flux = _polar_flux(reference.current_if_inside, inlet.origin, (0, 0, -sign),
        inlet.transition.source_inner_radius, inlet.transition.source_outer_radius)
    assert b_flux == pytest.approx(0.4 * reference.current, rel=3e-11, abs=0)
    assert inlet_flux == pytest.approx(-b_flux, rel=3e-11, abs=0)
    assert boundaries["B_edge0_port"].origin == center
    assert boundaries["B_edge0_port"].outward_normal == (0, 0, sign)
    assert b_flux == pytest.approx(boundaries["B_edge0_port"].outward_flux, rel=3e-11, abs=0)
    assert boundaries["transit_inlet_near_C"].origin == inlet.origin
    assert boundaries["transit_inlet_near_C"].outward_normal == (0, 0, -sign)
    assert inlet_flux == pytest.approx(boundaries["transit_inlet_near_C"].outward_flux, rel=3e-11, abs=0)
    assert np.linalg.norm(np.array(center) - inlet.origin) > 50
    b_face_point = (center[0] + (port.inner_radius + port.outer_radius) / 2, center[1], center[2])
    assert reference.current_if_inside(b_face_point) is None
    assert np.linalg.norm(junction_field(b_face_point)) > 0
