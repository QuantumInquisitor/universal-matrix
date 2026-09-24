from __future__ import annotations

import math
from dataclasses import replace

import numpy as np
import pytest

from src.toroidal_junction_bore_passage import (
    build_junction_bore_passage,
    certify_junction_bore_passage,
)
from src.toroidal_shared_prefix_fanout import build_shared_prefix_fanout_experiment
from src.toroidal_shared_return_route import RoutedTubePiece


@pytest.fixture(scope="module", params=(1.0, -1.0))
def passage(request):
    return build_junction_bore_passage(request.param)


def _cut_flux(passage, z, inner, outer):
    nodes, weights = np.polynomial.legendre.leggauss(8)
    center = passage.junction.center
    theta_count = 8
    contributions = []
    # Physical polar area r dr dtheta, independent of the Piola Jacobian.
    for node, weight in zip(nodes, weights, strict=True):
        radius = inner + (node + 1.0) * (outer - inner) / 2.0
        for index in range(theta_count):
            theta = (index + 0.31) * 2.0 * math.pi / theta_count
            point = (center[0] + radius * math.cos(theta), center[1] + radius * math.sin(theta), z)
            contributions.append(passage.current(point)[2] * passage.incoming.axis_sign
                                 * radius * weight * (outer - inner) / 2.0
                                 * 2.0 * math.pi / theta_count)
    return math.fsum(contributions)


def _transition_cut(placed, s):
    return (placed.origin[2] + placed.axis_sign * s * placed.transition.length,
            placed.transition.radius(s, 0.0), placed.transition.radius(s, 1.0))


def test_actual_c_junction_and_its_host_transitions_are_preserved(passage):
    current = float(passage.incoming.axis_sign)
    original = build_shared_prefix_fanout_experiment(current).original
    assert passage.junction == original.global_routing.junction("C")
    assert passage.incoming.transition == original.edges[3].route.assembly.outlet
    assert passage.outgoing.transition == original.edges[1].route.assembly.inlet
    assert passage.incoming.end == passage.junction.port_axis_point(3)
    assert passage.outgoing.origin == passage.junction.port_axis_point(1)
    assert passage.incoming.transition.flux == pytest.approx(0.6 * current)
    assert passage.outgoing.transition.flux == pytest.approx(0.6 * current)
    assert passage.transit.flux == pytest.approx(0.4 * current)


def test_default_analytic_bounds_leave_resolved_radial_clearance(passage):
    certificate = certify_junction_bore_passage(passage)
    assert certificate.incoming_collar_radial_gap == pytest.approx(9.8)
    assert certificate.central_radial_gap == pytest.approx(0.3)
    assert certificate.outgoing_collar_radial_gap == pytest.approx(3.0)
    assert certificate.minimum_radial_gap == pytest.approx(0.3)
    assert certificate.minimum_transition_jacobian_bound == pytest.approx(0.01)


def test_six_interfaces_are_continuous_and_selected_once(passage):
    interfaces = (
        (passage.incoming, 0.0), (passage.incoming, 1.0),
        (passage.outgoing, 0.0), (passage.outgoing, 1.0),
        (passage.transit.inlet, 1.0), (passage.transit.outlet, 0.0),
    )
    for placed, s in interfaces:
        for q in (0.25, 0.65):
            point = placed.map_point(s, q, 0.9)
            expected = np.array(placed.current(point))
            assert np.linalg.norm(expected) > 0
            assert passage.current(point) == pytest.approx(expected, rel=2e-10, abs=2e-11)
            for dz in (-1e-8, 1e-8):
                adjacent = (point[0], point[1], point[2] + dz)
                assert passage.current(adjacent) == pytest.approx(expected, rel=2e-6, abs=2e-6)


def test_separate_signed_host_and_transit_fluxes_survive_five_axial_regions(passage):
    incoming, outgoing, transit = passage.incoming, passage.outgoing, passage.transit
    before, after, bore = (passage.incoming_collar.volume, passage.outgoing_collar.volume,
                           transit.pieces[0].volume)
    first = _transition_cut(transit.inlet, 0.35)
    last = _transition_cut(transit.outlet, 0.65)
    host_in = _transition_cut(incoming, 0.4)
    host_out = _transition_cut(outgoing, 0.6)
    junction = passage.junction.junction
    regions = (
        (first[0], (before.inner_radius, before.outer_radius), first[1:]),
        (host_in[0], host_in[1:], (bore.inner_radius, bore.outer_radius)),
        (passage.junction.center[2], (junction.inner_radius, junction.outer_radius),
         (bore.inner_radius, bore.outer_radius)),
        (host_out[0], host_out[1:], (bore.inner_radius, bore.outer_radius)),
        (last[0], (after.inner_radius, after.outer_radius), last[1:]),
    )
    for z, host_annulus, transit_annulus in regions:
        assert _cut_flux(passage, z, *host_annulus) == pytest.approx(
            incoming.transition.flux, rel=2e-10, abs=2e-12
        )
        assert _cut_flux(passage, z, *transit_annulus) == pytest.approx(
            transit.flux, rel=2e-10, abs=2e-12
        )
        gap_radius = (transit_annulus[1] + host_annulus[0]) / 2.0
        assert passage.current((passage.junction.center[0] + gap_radius,
                                passage.junction.center[1], z)) == (0.0, 0.0, 0.0)


def test_composite_current_is_divergence_free_inside_each_taper(passage):
    h = 2e-6
    for placed in (passage.incoming, passage.outgoing, passage.transit.inlet, passage.transit.outlet):
        for s in (0.35, 0.65):
            point = np.array(placed.map_point(s, 0.55, 0.7))
            divergence = math.fsum(
                (passage.current(point + h * axis)[i] - passage.current(point - h * axis)[i]) / (2.0 * h)
                for i, axis in enumerate(np.eye(3))
            )
            assert abs(divergence) < 2e-6


@pytest.mark.parametrize("bore_inner,bore_outer,taper_length", (
    (0.05, 0.45, 0.25),
    (0.2, 0.3, 4.0),
    (0.05, 0.15, 2.0),
))
def test_bounded_bore_and_taper_variants(bore_inner, bore_outer, taper_length):
    changed = build_junction_bore_passage(
        -2.0, bore_inner=bore_inner, bore_outer=bore_outer, taper_length=taper_length
    )
    certificate = certify_junction_bore_passage(changed)
    assert certificate.minimum_radial_gap == pytest.approx(0.5 - bore_outer)
    assert certificate.minimum_transition_jacobian_bound > 0
    assert changed.transit.inlet.transition.length == taper_length
    assert changed.transit.outlet.transition.length == taper_length
    for placed in (changed.transit.inlet, changed.transit.outlet):
        assert _cut_flux(changed, *_transition_cut(placed, 0.4)) == pytest.approx(-0.8, rel=2e-10)
    assert _cut_flux(changed, changed.junction.center[2], bore_inner, bore_outer) == pytest.approx(-0.8, rel=2e-10)


def test_touching_the_host_bore_is_not_certified():
    with pytest.raises(ValueError, match="radial bounds do not certify passage clearance"):
        build_junction_bore_passage(bore_outer=0.5)


@pytest.mark.parametrize("component", ("bore", "incoming_collar"))
def test_disconnected_altered_straights_are_rejected(passage, component):
    if component == "bore":
        original = passage.transit.pieces[0].volume
        moved = replace(original, start=(*original.start[:2], original.start[2] + 0.1))
        changed = replace(passage, transit=replace(passage.transit, pieces=(RoutedTubePiece(moved),)))
    else:
        original = passage.incoming_collar.volume
        moved = replace(original, end=(*original.end[:2], original.end[2] + 0.1))
        changed = replace(passage, incoming_collar=RoutedTubePiece(moved))
    with pytest.raises(ValueError, match="declared axial interfaces"):
        certify_junction_bore_passage(changed)


@pytest.mark.parametrize("domain_change", ({"inner_radius": 0.75}, {"outer_radius": 1.25}))
def test_host_domain_cannot_clip_its_preserved_port_annuli(passage, domain_change):
    clipped_junction = replace(passage.junction.junction, **domain_change)
    changed = replace(passage, junction=replace(passage.junction, junction=clipped_junction))
    with pytest.raises(ValueError, match="junction"):
        certify_junction_bore_passage(changed)


@pytest.mark.parametrize("bore_inner,bore_outer", ((1e-100, 2e-100), (1e-170, 2e-170)))
def test_bore_below_resolved_geometry_scale_is_rejected(bore_inner, bore_outer):
    with pytest.raises(ValueError, match="audit tolerance"):
        build_junction_bore_passage(bore_inner=bore_inner, bore_outer=bore_outer)


def test_weak_host_flux_cannot_reverse_the_declared_port_orientation(passage):
    junction = passage.junction.junction
    reversed_ports = tuple(
        replace(port, outward_flux=-1e-14 * port.outward_flux,
                flux_coordinate_lower=0.0, flux_coordinate_upper=1e-14 * abs(port.outward_flux))
        for port in junction.ports
    )
    incoming = replace(passage.incoming, transition=replace(
        passage.incoming.transition, flux=-1e-14 * passage.incoming.transition.flux
    ))
    outgoing = replace(passage.outgoing, transition=replace(
        passage.outgoing.transition, flux=-1e-14 * passage.outgoing.transition.flux
    ))
    changed = replace(
        passage,
        junction=replace(passage.junction, junction=replace(junction, ports=reversed_ports)),
        incoming=incoming,
        outgoing=outgoing,
    )
    with pytest.raises(ValueError, match="host flux orientation"):
        certify_junction_bore_passage(changed)


def test_taper_must_fit_the_actual_reference_straights():
    with pytest.raises(ValueError, match="straight sections"):
        build_junction_bore_passage(taper_length=1000.0)


@pytest.mark.parametrize("current", (2e-10, -2e-10))
def test_resolved_weak_currents_preserve_separate_signed_fluxes(current):
    weak = build_junction_bore_passage(current)
    junction = weak.junction.junction
    bore = weak.transit.pieces[0].volume
    z = weak.junction.center[2]
    assert _cut_flux(weak, z, junction.inner_radius, junction.outer_radius) == pytest.approx(
        0.6 * current, rel=2e-10, abs=0.0
    )
    assert _cut_flux(weak, z, bore.inner_radius, bore.outer_radius) == pytest.approx(
        0.4 * current, rel=2e-10, abs=0.0
    )
