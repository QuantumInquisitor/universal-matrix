"""A local annular transit through a different route's junction bore.

The existing C junction and its two port transitions are unchanged. Another
current contracts before those transitions, crosses the empty central bore,
and expands afterward. This certifies only the finite coaxial passage, not
the surrounding fan-out network, a side exit, or a collision-free motion.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .toroidal_framed_edge_assembly import AnnularPiolaTransition
from .toroidal_global_routing import GlobalJunctionPlacement
from .toroidal_incident_bend_audit import AnnularStraightSegment
from .toroidal_shared_prefix_fanout import build_shared_prefix_fanout_experiment
from .toroidal_shared_return_connectors import (
    ConnectedRoutedEdge,
    PlacedAnnularTransition,
    _piece_contains,
    _piece_current,
)
from .toroidal_shared_return_route import RoutedTubePiece, routed_tube_pieces

Point = tuple[float, float, float]
_TOLERANCE = 1e-10


@dataclass(frozen=True)
class JunctionBorePassage:
    junction: GlobalJunctionPlacement
    incoming: PlacedAnnularTransition
    outgoing: PlacedAnnularTransition
    incoming_collar: RoutedTubePiece
    outgoing_collar: RoutedTubePiece
    transit: ConnectedRoutedEdge

    def junction_current_if_inside(self, point: Point) -> Point | None:
        junction = self.junction.junction
        delta = tuple(x - c for x, c in zip(point, self.junction.center, strict=True))
        if (junction.inner_radius <= math.hypot(delta[0], delta[1]) <= junction.outer_radius
                and abs(delta[2]) <= junction.length / 2):
            local = tuple(x + c for x, c in zip(delta, junction.center, strict=True))
            return junction.current(local)
        return None

    def current(self, point) -> Point:
        if len(point) != 3 or not all(math.isfinite(float(x)) for x in point):
            raise ValueError("point must have three finite coordinates")
        point = tuple(float(x) for x in point)
        field = self.junction_current_if_inside(point)
        if field is not None:
            return field
        for placed in (self.incoming, self.outgoing):
            if placed.contains(point):
                return placed.current(point)
        for collar, placed in ((self.incoming_collar, self.incoming),
                                (self.outgoing_collar, self.outgoing)):
            if _piece_contains(collar, point):
                return _piece_current(collar, point, placed.transition.flux)
        field = self.transit.current_if_inside(point)
        return (0.0, 0.0, 0.0) if field is None else field


@dataclass(frozen=True)
class BorePassageCertificate:
    incoming_collar_radial_gap: float
    central_radial_gap: float
    outgoing_collar_radial_gap: float
    minimum_transition_jacobian_bound: float

    @property
    def minimum_radial_gap(self) -> float:
        return min(self.incoming_collar_radial_gap, self.central_radial_gap,
                   self.outgoing_collar_radial_gap)


def _annulus_matches(transition, side: str, annulus) -> bool:
    return all(math.isclose(getattr(transition, f"{side}_{name}"), getattr(annulus, name),
                            rel_tol=0.0, abs_tol=_TOLERANCE)
               for name in ("inner_radius", "outer_radius"))


def certify_junction_bore_passage(passage: JunctionBorePassage) -> BorePassageCertificate:
    """Bound separation across three coaxial axial intervals analytically.

    Radius is a convex interpolation along each transition. In the middle
    interval the transit's constant outer radius lies below every host inner
    radius, including the junction bore. Checks use floating-point bounds.
    """
    incoming, outgoing, transit = passage.incoming, passage.outgoing, passage.transit
    collars = (passage.incoming_collar, passage.outgoing_collar)
    if (len(transit.pieces) != 1
            or not all(isinstance(p.volume, AnnularStraightSegment) for p in (*collars, *transit.pieces))):
        raise ValueError("local passage requires straight collars and one bore straight")
    before, after, bore = (p.volume for p in (*collars, *transit.pieces))
    placed = (incoming, outgoing, transit.inlet, transit.outlet)
    sign = incoming.axis_sign
    center = passage.junction.center
    if any(min(p.transition.source_inner_radius, p.transition.target_inner_radius,
               p.transition.source_width, p.transition.target_width) <= _TOLERANCE for p in placed):
        raise ValueError("passage annular radii and widths must exceed the audit tolerance")
    if any(p.axis_sign != sign or p.origin[:2] != center[:2] for p in placed):
        raise ValueError("all passage transitions must share the junction axis and direction")
    for straight in (before, after, bore):
        if (straight.start[:2] != center[:2] or straight.end[:2] != center[:2]
                or sign * (straight.end[2] - straight.start[2]) <= 0):
            raise ValueError("all passage straights must follow the common directed axis")
    source_port = passage.junction.junction.port_by_edge(3)
    target_port = passage.junction.junction.port_by_edge(1)
    junction = passage.junction.junction
    if {p.edge_index for p in junction.ports} != {1, 3}:
        raise ValueError("local host must contain exactly the two declared junction ports")
    for port in (source_port, target_port):
        if (port.node != junction.node
                or any(not math.isclose(getattr(port, radius), getattr(junction, radius),
                                        rel_tol=0.0, abs_tol=_TOLERANCE)
                       for radius in ("inner_radius", "outer_radius"))
                or port.flux_coordinate_lower != 0.0
                or not math.isclose(port.flux_coordinate_upper, abs(port.outward_flux),
                                    rel_tol=1e-12, abs_tol=0.0)):
            raise ValueError("each host port must span the junction annulus and its full flux range")
    if (incoming.end != passage.junction.port_axis_point(3)
            or outgoing.origin != passage.junction.port_axis_point(1)
            or sign * (outgoing.origin[2] - incoming.end[2]) <= 0):
        raise ValueError("host transitions must attach to the declared C junction faces")
    if (before.end != incoming.origin or after.start != outgoing.end
            or transit.inlet.origin != before.start or transit.inlet.end != before.end
            or bore.start != transit.inlet.end or bore.end != transit.outlet.origin
            or transit.outlet.origin != after.start or transit.outlet.end != after.end):
        raise ValueError("passage pieces must share their declared axial interfaces")
    for transition, side, annulus in (
        (incoming.transition, "source", before), (incoming.transition, "target", source_port),
        (outgoing.transition, "source", target_port), (outgoing.transition, "target", after),
        (transit.inlet.transition, "target", bore), (transit.outlet.transition, "source", bore),
    ):
        if not _annulus_matches(transition, side, annulus):
            raise ValueError("passage interface annuli must match")
    fluxes = (incoming.transition.flux, outgoing.transition.flux,
              -source_port.outward_flux, target_port.outward_flux)
    if fluxes[0] * sign <= 0:
        raise ValueError("host flux orientation must match its junction faces")
    if any(not math.isclose(fluxes[0], value, rel_tol=1e-12, abs_tol=0.0) for value in fluxes[1:]):
        raise ValueError("host flux must match both junction ports")
    if any(not math.isclose(transit.flux, p.transition.flux, rel_tol=1e-12, abs_tol=0.0)
           for p in (transit.inlet, transit.outlet)):
        raise ValueError("transit flux must agree through the passage")
    gaps = (
        before.inner_radius - max(transit.inlet.transition.source_outer_radius, bore.outer_radius),
        min(incoming.transition.source_inner_radius, incoming.transition.target_inner_radius,
            passage.junction.junction.inner_radius,
            outgoing.transition.source_inner_radius, outgoing.transition.target_inner_radius) - bore.outer_radius,
        after.inner_radius - max(bore.outer_radius, transit.outlet.transition.target_outer_radius),
    )
    if min(gaps) <= _TOLERANCE:
        raise ValueError("radial bounds do not certify passage clearance")
    jacobians = [p.transition.length * min(p.transition.source_inner_radius, p.transition.target_inner_radius)
                 * min(p.transition.source_width, p.transition.target_width) for p in placed]
    if not all(math.isfinite(value) and value > 0 for value in jacobians):
        raise ValueError("passage Jacobian bounds must be finite and positive")
    return BorePassageCertificate(*gaps, min(jacobians))


def build_junction_bore_passage(
    current: float = 1.0, *, bore_inner: float = 0.1, bore_outer: float = 0.2,
    taper_length: float = 1.0,
) -> JunctionBorePassage:
    """Retain the fan-out reference's C junction and its two port transitions.

    The transit has edge 0's annulus and signed current at both open ends.
    It is not attached to the rest of edge 0 here. Collar intervals are only
    a finite local environment, not a replacement global routing contract.
    """
    if not math.isfinite(taper_length) or taper_length <= 0:
        raise ValueError("taper_length must be finite and positive")
    reference = build_shared_prefix_fanout_experiment(current).original
    junction = reference.global_routing.junction("C")
    entering = reference.edges[3].route.assembly
    leaving = reference.edges[1].route.assembly
    carried = reference.edges[0].route.assembly
    available = min(routed_tube_pieces(reference.edges[3])[-1].volume.length - entering.outlet.length,
                    routed_tube_pieces(reference.edges[1])[0].volume.length - leaving.inlet.length)
    if taper_length >= available:
        raise ValueError("taper collars must fit the existing straight sections before their bends")
    sign = entering.axis_sign
    def shift(point, distance):
        return point[0], point[1], point[2] + sign * distance
    incoming = PlacedAnnularTransition(entering.outlet,
        shift(junction.port_axis_point(3), -entering.outlet.length), sign)
    outgoing = PlacedAnnularTransition(leaving.inlet, junction.port_axis_point(1), sign)
    first, last = shift(incoming.origin, -taper_length), shift(outgoing.end, taper_length)
    inner, outer, flux = carried.channel.inner_radius, carried.channel.outer_radius, carried.edge.current
    inlet = PlacedAnnularTransition(AnnularPiolaTransition(
        inner, outer, bore_inner, bore_outer, flux, taper_length), first, sign)
    outlet = PlacedAnnularTransition(AnnularPiolaTransition(
        bore_inner, bore_outer, inner, outer, flux, taper_length), outgoing.end, sign)
    transit = ConnectedRoutedEdge(0, flux, inlet, (RoutedTubePiece(AnnularStraightSegment(
        inlet.end, outlet.origin, bore_inner, bore_outer)),), outlet)
    passage = JunctionBorePassage(junction, incoming, outgoing,
        RoutedTubePiece(AnnularStraightSegment(first, incoming.origin,
            entering.channel.inner_radius, entering.channel.outer_radius)),
        RoutedTubePiece(AnnularStraightSegment(outgoing.end, last,
            leaving.channel.inner_radius, leaving.channel.outer_radius)), transit)
    certify_junction_bore_passage(passage)
    return passage


def main() -> None:
    print("TOROIDAL LOCAL JUNCTION BORE PASSAGE")
    for current in (1.0, -1.0):
        passage = build_junction_bore_passage(current)
        certificate = certify_junction_bore_passage(passage)
        print(f"current={current:g}; host_flux={passage.incoming.transition.flux:g}; "
              f"transit_flux={passage.transit.flux:g}")
        for name in certificate.__dataclass_fields__:
            print(f"{name}={getattr(certificate, name):.12g}")
    print("scope=finite_coaxial_passage_through_unchanged_C_junction_and_port_transitions")
    print("open_ends_unattached; not_global_fanout_or_side_exit_or_safe_motion")


if __name__ == "__main__":
    main()
