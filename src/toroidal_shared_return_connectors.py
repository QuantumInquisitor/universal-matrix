"""Place existing annular Piola transitions into the shared-route endpoint.

All four routed channels are trimmed to make room for their inlet and outlet
transitions. Proper rigid rotations preserve the signed current convention
for either axial direction. This is a static, dimensionless construction;
it supplies no collision-free motion or physical dynamics.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

from .toroidal_connector_topology import annular_connector_source_density
from .toroidal_framed_edge_assembly import AnnularPiolaTransition
from .toroidal_separated_channels import build_separated_framed_edge_network
from .toroidal_shared_return_route import (
    RoutedTubePiece,
    box_clearance,
    certify_shared_return_endpoint,
    move_inner_return_to_shared_route,
    routed_tube_pieces,
)
from .toroidal_smooth_bends import AnnularQuarterBend, SmoothGlobalToroidalRouting, build_smooth_global_toroidal_routing
from .vesica_tree_circulation import PORT_NODES, vesica_circulation

Point = tuple[float, float, float]
Bounds = tuple[Point, Point]
_TOLERANCE = 1e-10


def _point(point) -> Point:
    if len(point) != 3 or not all(math.isfinite(float(x)) for x in point):
        raise ValueError("point must have three finite coordinates")
    return tuple(float(x) for x in point)


def _box_signed_separation(left: Bounds, right: Bounds) -> float:
    """A nonnegative value proves disjoint box interiors; zero allows contact."""
    return max(max(a - d, c - b) for a, b, c, d in zip(left[0], left[1], right[0], right[1], strict=True))


@dataclass(frozen=True)
class PlacedAnnularTransition:
    transition: AnnularPiolaTransition
    origin: Point
    axis_sign: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "origin", _point(self.origin))
        if self.axis_sign not in (-1, 1):
            raise ValueError("axis_sign must be -1 or 1")

    def to_global(self, point) -> Point:
        x, y, z = _point(point)
        # diag(1, sign, sign) has determinant +1, including reversed currents.
        return (self.origin[0] + x, self.origin[1] + self.axis_sign * y,
                self.origin[2] + self.axis_sign * (z - self.transition.z_start))

    def to_local(self, point) -> Point:
        x, y, z = _point(point)
        return (x - self.origin[0], self.axis_sign * (y - self.origin[1]),
                self.transition.z_start + self.axis_sign * (z - self.origin[2]))

    def map_point(self, s: float, q: float, theta: float) -> Point:
        return self.to_global(self.transition.map_point(s, q, theta))

    def contains(self, point) -> bool:
        return self.transition._inverse_parameters(self.to_local(point)) is not None

    def current(self, point) -> Point:
        x, y, z = self.transition.current(self.to_local(point))
        return x, self.axis_sign * y, self.axis_sign * z

    @property
    def end(self) -> Point:
        return self.origin[0], self.origin[1], self.origin[2] + self.axis_sign * self.transition.length

    @property
    def bounds(self) -> Bounds:
        radius = max(self.transition.source_outer_radius, self.transition.target_outer_radius)
        return ((self.origin[0] - radius, self.origin[1] - radius, min(self.origin[2], self.end[2])),
                (self.origin[0] + radius, self.origin[1] + radius, max(self.origin[2], self.end[2])))


def _piece_contains(piece: RoutedTubePiece, point: Point) -> bool:
    if isinstance(piece.volume, AnnularQuarterBend):
        return piece.volume.inverse_parameters(point) is not None
    return piece.volume.penetration_margin(point) >= -_TOLERANCE


def _piece_current(piece: RoutedTubePiece, point: Point, flux: float) -> Point:
    if isinstance(piece.volume, AnnularQuarterBend):
        return piece.volume.current(point)
    straight = piece.volume
    if straight.penetration_margin(point) < -_TOLERANCE:
        return 0.0, 0.0, 0.0
    _, radius = straight.local_coordinates(point)
    density = annular_connector_source_density(flux, straight.inner_radius, straight.outer_radius, radius)
    return tuple(density * x for x in straight.direction)


@dataclass(frozen=True)
class ConnectedRoutedEdge:
    edge_index: int
    flux: float
    inlet: PlacedAnnularTransition
    pieces: tuple[RoutedTubePiece, ...]
    outlet: PlacedAnnularTransition

    def current_if_inside(self, point: Point) -> Point | None:
        # Interfaces have matching fields; select one chart rather than add
        # two copies of the same current on a shared face.
        if self.inlet.contains(point):
            return self.inlet.current(point)
        for piece in self.pieces:
            if _piece_contains(piece, point):
                return _piece_current(piece, point, self.flux)
        if self.outlet.contains(point):
            return self.outlet.current(point)
        return None


def _connect_edge(edge) -> ConnectedRoutedEdge:
    assembly, route = edge.route.assembly, edge.route
    sign = assembly.axis_sign
    inlet = PlacedAnnularTransition(assembly.inlet, route.source_frame.origin, sign)
    target = route.target_frame.origin
    outlet = PlacedAnnularTransition(assembly.outlet,
        (target[0], target[1], target[2] - sign * assembly.outlet.length), sign)
    pieces = list(routed_tube_pieces(edge))
    for piece, length in ((pieces[0], assembly.inlet.length), (pieces[-1], assembly.outlet.length)):
        if piece.volume.length <= length:
            raise ValueError("endpoint straight must be longer than its connector")
    pieces[0] = RoutedTubePiece(replace(pieces[0].volume, start=inlet.end))
    pieces[-1] = RoutedTubePiece(replace(pieces[-1].volume, end=outlet.origin))
    return ConnectedRoutedEdge(edge.edge_index, edge.route.edge.current, inlet, tuple(pieces), outlet)


@dataclass(frozen=True)
class ConnectedSharedReturnNetwork:
    routing: SmoothGlobalToroidalRouting
    edges: tuple[ConnectedRoutedEdge, ...]

    def current(self, point) -> Point:
        point = _point(point)
        for placement in self.routing.global_routing.junctions:
            junction = placement.junction
            delta = tuple(x - c for x, c in zip(point, placement.center, strict=True))
            if (junction.inner_radius <= math.hypot(delta[0], delta[1]) <= junction.outer_radius
                    and abs(delta[2]) <= junction.length / 2):
                local = tuple(x + c for x, c in zip(delta, junction.center, strict=True))
                return junction.current(local)
        for edge in self.edges:
            field = edge.current_if_inside(point)
            if field is not None:
                return field
        return 0.0, 0.0, 0.0

    def maximum_interface_residual(self) -> float:
        residuals = []
        for connected, routed in zip(self.edges, self.routing.edges, strict=True):
            for transition, s, piece in ((connected.inlet, 1.0, connected.pieces[0]),
                                          (connected.outlet, 0.0, connected.pieces[-1])):
                for q in (0.15, 0.4, 0.7, 0.9):
                    for theta in (0.0, 0.7, 2.0):
                        point = transition.map_point(s, q, theta)
                        a, b = transition.current(point), _piece_current(piece, point, connected.flux)
                        residuals.extend(abs(x - y) for x, y in zip(a, b, strict=True))
            for transition, s, node in ((connected.inlet, 0.0, routed.route.edge.source),
                                        (connected.outlet, 1.0, routed.route.edge.target)):
                placement = self.routing.global_routing.junction(node)
                for q in (0.15, 0.4, 0.7, 0.9):
                    for theta in (0.0, 0.7, 2.0):
                        point = transition.map_point(s, q, theta)
                        local = tuple(x - c + d for x, c, d in zip(
                            point, placement.center, placement.junction.center, strict=True))
                        a, b = transition.current(point), placement.junction.current(local)
                        residuals.extend(abs(x - y) for x, y in zip(a, b, strict=True))
        return max(residuals, default=0.0)


def attach_shared_return_connectors(routing: SmoothGlobalToroidalRouting) -> ConnectedSharedReturnNetwork:
    """Trim each channel and place its existing local transitions rigidly."""
    certify_shared_return_endpoint(routing)
    connected = ConnectedSharedReturnNetwork(routing, tuple(_connect_edge(edge) for edge in routing.edges))
    if connected.maximum_interface_residual() > _TOLERANCE:
        raise ValueError("placed connector fields do not match junction/channel interfaces")
    audit_connected_geometry(connected)
    return connected


def _nested_transition_gaps(left: PlacedAnnularTransition, right: PlacedAnnularTransition) -> tuple[float, float]:
    if (left.origin != right.origin or left.axis_sign != right.axis_sign
            or left.transition.length != right.transition.length):
        raise ValueError("overlapping transition boxes require a common axial chart")
    a, b = sorted((left.transition, right.transition), key=lambda t: t.source_inner_radius)
    gaps = b.source_inner_radius - a.source_outer_radius, b.target_inner_radius - a.target_outer_radius
    if min(gaps) < 0:
        raise ValueError("transition annuli lose radial order")
    return gaps


@dataclass(frozen=True)
class ConnectedGeometryAudit:
    connector_count: int
    nested_transition_pair_count: int
    minimum_transition_endpoint_gap: float
    minimum_transition_jacobian_bound: float
    minimum_unchanged_tube_clearance: float


def audit_connected_geometry(network: ConnectedSharedReturnNetwork) -> ConnectedGeometryAudit:
    """Conservative interior-disjointness audit, allowing intended face contact.

    The shared-route endpoint certificate covers the return tubes. Additional
    box checks cover the other tubes, junctions, and connector placement.
    Coaxial connector pairs use ordered radial interpolation instead of boxes.
    This is floating-point geometric evidence, not interval arithmetic.
    """
    certify_shared_return_endpoint(network.routing)
    if network.edges != tuple(_connect_edge(edge) for edge in network.routing.edges):
        raise ValueError("connected pieces must match the declared routing and transitions")
    unchanged = [edge.pieces for edge in network.edges[:2]]
    clearance = min(
        [box_clearance(a, b) for pieces in unchanged for i, a in enumerate(pieces) for b in pieces[i + 2:]]
        + [box_clearance(a, b) for a in unchanged[0] for b in unchanged[1]]
    )
    if clearance <= 0:
        raise ValueError("unchanged tubes lack conservative separation")
    connectors = tuple(t for edge in network.edges for t in (edge.inlet, edge.outlet))
    pieces = tuple(p for edge in network.edges for p in edge.pieces)
    junction_boxes = []
    for placement in network.routing.global_routing.junctions:
        x, y, z = placement.center
        radius, half = placement.junction.outer_radius, placement.junction.length / 2
        junction_boxes.append(((x - radius, y - radius, z - half), (x + radius, y + radius, z + half)))
    for i, a in enumerate(junction_boxes):
        for b in junction_boxes[i + 1:]:
            if _box_signed_separation(a, b) <= 0:
                raise ValueError("junction boxes overlap")
        for piece in pieces:
            if _box_signed_separation(a, piece.bounds) < 0:
                raise ValueError("routed piece box enters a junction")
    nested, gaps, jacobians = 0, [], []
    for i, connector in enumerate(connectors):
        transition = connector.transition
        jacobians.append(transition.length * min(transition.source_inner_radius, transition.target_inner_radius)
                         * min(transition.source_width, transition.target_width))
        for bounds in (*junction_boxes, *(piece.bounds for piece in pieces)):
            if _box_signed_separation(connector.bounds, bounds) < 0:
                raise ValueError("connector box overlaps a junction or routed piece interior")
        for other in connectors[i + 1:]:
            if _box_signed_separation(connector.bounds, other.bounds) < 0:
                gaps.extend(_nested_transition_gaps(connector, other))
                nested += 1
    return ConnectedGeometryAudit(len(connectors), nested, min(gaps, default=math.inf), min(jacobians), clearance)


def build_connected_shared_return_reference(current: float = 1.0) -> ConnectedSharedReturnNetwork:
    if not math.isfinite(current) or abs(current) <= _TOLERANCE:
        raise ValueError("reference current must be finite and nonzero")
    network = build_separated_framed_edge_network(
        vesica_circulation(current, return_split=0.4).edges, PORT_NODES, shell_gap=3.0,
    )
    reference = build_smooth_global_toroidal_routing(network.framed_network, bend_margin=0.05)
    return attach_shared_return_connectors(move_inner_return_to_shared_route(reference, 1.0))


def main() -> None:
    print("TOROIDAL CONNECTED SHARED RETURN ENDPOINT")
    for current in (1.0, -1.0):
        network = build_connected_shared_return_reference(current)
        audit = audit_connected_geometry(network)
        print(f"current={current:g}; interface_residual={network.maximum_interface_residual():.12g}")
        for name in audit.__dataclass_fields__:
            print(f"{name}={getattr(audit, name):.12g}")
    print("scope=static_vesica_junction_transition_routed_channel_assembly; intended_boundary_contact_allowed")
    print("not_a_collision_free_motion_or_general_fanout_or_new_dynamics")


if __name__ == "__main__":
    main()
