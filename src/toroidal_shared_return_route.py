"""Move the inner Vesica return tube onto the outer return's centerline.

This opt-in reference candidate preserves annular shells, currents, and graph
port frames. It moves internal joins and straights together. Intermediate
states can collide; the starting geometry already does. Endpoint clearance
is certified separately from the finite intermediate collision diagnostic.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

from .toroidal_global_routing import _dot, _subtract
from .toroidal_incident_bend_audit import AnnularStraightSegment, BendSamplingGrid
from .toroidal_separated_channels import build_separated_framed_edge_network
from .toroidal_smooth_bends import (
    AnnularQuarterBend,
    SmoothedRoutedEdge,
    SmoothGlobalToroidalRouting,
    _build_edge_bends,
    build_smooth_global_toroidal_routing,
)
from .vesica_tree_circulation import PORT_NODES, vesica_circulation

Point = tuple[float, float, float]
_TOLERANCE = 1e-10


@dataclass(frozen=True)
class RoutedTubePiece:
    """One closed straight or bend volume, in along-route order."""

    volume: AnnularStraightSegment | AnnularQuarterBend

    @property
    def bounds(self) -> tuple[Point, Point]:
        volume = self.volume
        if isinstance(volume, AnnularQuarterBend):
            # Each centerline coordinate differs from the corner by at most R
            # for the axis-aligned reference routes accepted by this audit.
            radius = volume.bend_radius + volume.outer_radius
            return (
                tuple(x - radius for x in volume.corner),
                tuple(x + radius for x in volume.corner),
            )
        nonzero = [i for i, (a, b) in enumerate(zip(volume.start, volume.end, strict=True)) if a != b]
        if len(nonzero) != 1:
            raise ValueError("piece audit requires axis-aligned straights")
        # Exact axial extent avoids a spurious sqrt(epsilon) cap expansion
        # from normalizing a nearly unit floating-point direction.
        extents = tuple(0.0 if i == nonzero[0] else volume.outer_radius for i in range(3))
        return (
            tuple(min(a, b) - r for a, b, r in zip(volume.start, volume.end, extents, strict=True)),
            tuple(max(a, b) + r for a, b, r in zip(volume.start, volume.end, extents, strict=True)),
        )

    def penetration(self, point: Point) -> float:
        volume = self.volume
        if isinstance(volume, AnnularStraightSegment):
            return volume.penetration_margin(point)
        parameters = volume.inverse_parameters(point)
        if parameters is None:
            return -math.inf
        phi, q, theta = parameters
        radius = volume.inner_radius + q * volume.width
        planar_radius = volume.bend_radius - radius * math.cos(theta)
        return min(
            radius - volume.inner_radius, volume.outer_radius - radius,
            planar_radius * math.sin(phi), planar_radius * math.cos(phi),
        )

    def sample_points(self, sampling: BendSamplingGrid):
        volume = self.volume
        if isinstance(volume, AnnularStraightSegment):
            direction = volume.direction
            # Routes are axis-aligned; choose a deterministic transverse frame.
            axis = next(i for i, value in enumerate(direction) if abs(value) > 0.5)
            first, second = (axis + 1) % 3, (axis + 2) % 3
        for i in range(1, sampling.phi_samples):
            fraction = (i - sampling.phi_offset) / (sampling.phi_samples - 1)
            for j in range(1, sampling.q_samples - 1):
                q = (j - sampling.q_offset) / (sampling.q_samples - 1)
                for k in range(sampling.theta_samples):
                    theta = 2 * math.pi * (k + sampling.theta_offset) / sampling.theta_samples
                    if isinstance(volume, AnnularQuarterBend):
                        yield volume.map_point(fraction * math.pi / 2, q, theta)
                    else:
                        radius = volume.inner_radius + q * (volume.outer_radius - volume.inner_radius)
                        point = [a + fraction * (b - a) for a, b in zip(volume.start, volume.end, strict=True)]
                        point[first] += radius * math.cos(theta)
                        point[second] += radius * math.sin(theta)
                        yield tuple(point)


def routed_tube_pieces(edge: SmoothedRoutedEdge) -> tuple[RoutedTubePiece, ...]:
    """Expose actual trimmed straights and bends; reject unsupported axes."""
    if (len({bend.bend_radius for bend in edge.bends}) != 1
            or edge.bends != _build_edge_bends(edge.route, edge.bends[0].bend_radius)):
        raise ValueError("piece audit requires consistent uniform bends and channel shells")
    for start, end in edge.route.segments:
        delta = _subtract(end, start)
        if sum(value != 0.0 for value in delta) != 1:
            raise ValueError("piece audit requires axis-aligned routes")
    pieces = []
    channel = edge.route.assembly.channel
    for index in range(len(edge.bends) + 1):
        start = edge.route.route[0] if index == 0 else edge.bends[index - 1].end
        end = edge.route.route[-1] if index == len(edge.bends) else edge.bends[index].start
        pieces.append(RoutedTubePiece(AnnularStraightSegment(
            start, end, channel.inner_radius, channel.outer_radius,
        )))
        if index < len(edge.bends):
            pieces.append(RoutedTubePiece(edge.bends[index]))
    return tuple(pieces)


def box_clearance(left: RoutedTubePiece, right: RoutedTubePiece) -> float:
    """Nonnegative distance between conservative axis-aligned enclosing boxes."""
    low_a, high_a = left.bounds
    low_b, high_b = right.bounds
    return math.sqrt(math.fsum(
        max(0.0, a0 - b1, b0 - a1) ** 2
        for a0, a1, b0, b1 in zip(low_a, high_a, low_b, high_b, strict=True)
    ))


def move_inner_return_to_shared_route(
    reference: SmoothGlobalToroidalRouting, progress: float,
) -> SmoothGlobalToroidalRouting:
    """Bounded candidate: edge 2 approaches edge 3; all port frames stay fixed.

    The two edges must have the same ordered endpoints, port frames and
    separated shells. Seven corresponding axis-aligned route points and the
    uniform bend radius interpolate affinely. Other edges remain unchanged.
    Existing global envelope checks are recomputed on the changed routes.
    """
    progress = float(progress)
    if not math.isfinite(progress) or not 0 <= progress <= 1:
        raise ValueError("progress must be finite and in [0, 1]")
    if len(reference.edges) != 4:
        raise ValueError("candidate requires the four-edge Vesica reference")
    inner, outer = reference.edges[2:4]
    if (inner.route.source_frame != outer.route.source_frame
            or inner.route.target_frame != outer.route.target_frame):
        raise ValueError("return channels must have identical port frames")
    if inner.bends[0].outer_radius >= outer.bends[0].inner_radius:
        raise ValueError("return channel shells must be strictly separated")
    for edge in (inner, outer):
        routed_tube_pieces(edge)
        if len({bend.bend_radius for bend in edge.bends}) != 1:
            raise ValueError("candidate requires uniform bend radii on each edge")
    for (a0, a1), (b0, b1) in zip(inner.route.segments, outer.route.segments, strict=True):
        if _dot(_subtract(a1, a0), _subtract(b1, b0)) <= 0:
            raise ValueError("corresponding route segments must retain their directions")
    def blend(a, b):
        return a if a == b else (1 - progress) * a + progress * b
    radius = blend(inner.bends[0].bend_radius, outer.bends[0].bend_radius)
    route = replace(
        inner.route,
        route=tuple(tuple(blend(a, b) for a, b in zip(p, q, strict=True))
                    for p, q in zip(inner.route.route, outer.route.route, strict=True)),
        lane_y=blend(inner.route.lane_y, outer.route.lane_y),
        lane_height=blend(inner.route.lane_height, outer.route.lane_height),
        clearance_radius=max(inner.route.clearance_radius, inner.bends[0].outer_radius + radius),
    )
    moved = SmoothedRoutedEdge(route, _build_edge_bends(route, radius))
    edges = (*reference.edges[:2], moved, outer)
    global_routing = replace(reference.global_routing, edges=tuple(edge.route for edge in edges))
    return SmoothGlobalToroidalRouting(global_routing, edges, reference.bend_margin)


@dataclass(frozen=True)
class SharedRouteCertificate:
    shell_gap: float
    minimum_jacobian_margin: float
    minimum_nonadjacent_piece_clearance: float
    minimum_other_edge_clearance: float
    nonincident_junction_clearance: float


def certify_shared_return_endpoint(routing: SmoothGlobalToroidalRouting) -> SharedRouteCertificate:
    """Certify the two shared routed tubes, not a collision-free motion.

    Same-piece shells are separated by radius; consecutive straight/bend
    interiors occupy opposite sides of their interface plane. Nonadjacent
    pieces and all pieces of the other edges must have disjoint enclosing
    boxes. The outer tube supplies bounds for both nested shells.
    """
    if len(routing.edges) != 4:
        raise ValueError("certificate requires the four-edge reference")
    inner, outer = routing.edges[2:4]
    routed_tube_pieces(inner)
    if inner.route.route != outer.route.route:
        raise ValueError("shared endpoint requires identical routes")
    if any(a.bend_radius != b.bend_radius for a, b in zip(inner.bends, outer.bends, strict=True)):
        raise ValueError("shared endpoint requires identical bend radii")
    gap = outer.bends[0].inner_radius - inner.bends[0].outer_radius
    if gap <= 0:
        raise ValueError("nested shells must have positive separation")
    pieces = routed_tube_pieces(outer)
    nonadjacent = min(box_clearance(a, b) for i, a in enumerate(pieces) for b in pieces[i + 2:])
    other = min(box_clearance(a, b) for a in pieces for edge in routing.edges[:2]
                for b in routed_tube_pieces(edge))
    junction = routing.global_routing.minimum_edge_to_nonincident_junction_clearance()
    if min(nonadjacent, other, junction) <= _TOLERANCE:
        raise ValueError("conservative piece or junction bounds do not certify clearance")
    return SharedRouteCertificate(gap, routing.minimum_jacobian_margin(), nonadjacent, other, junction)


def _affine_box_separation(a0, a1, b0, b1) -> float:
    """One fixed separating coordinate for boxes moving affinely in time."""
    lo_a0, hi_a0 = a0.bounds
    lo_a1, hi_a1 = a1.bounds
    lo_b0, hi_b0 = b0.bounds
    lo_b1, hi_b1 = b1.bounds
    return max(
        max(min(lo_a0[i] - hi_b0[i], lo_a1[i] - hi_b1[i]),
            min(lo_b0[i] - hi_a0[i], lo_b1[i] - hi_a1[i]))
        for i in range(3)
    )


def certify_unchanged_edge_separation(reference: SmoothGlobalToroidalRouting) -> float:
    """Bound self separation and clearance from edges 0/1 for the entire move.

    The affine move retains every segment's axis and direction; therefore
    each enclosing-box face is affine. One coordinate separating a pair at
    both ends separates it for every progress value. Edge 3 is deliberately
    excluded here: intersections with it are present during the move.
    """
    start = move_inner_return_to_shared_route(reference, 0.0)
    end = move_inner_return_to_shared_route(reference, 1.0)
    before, after = (routed_tube_pieces(state.edges[2]) for state in (start, end))
    bounds = [
        _affine_box_separation(before[i], after[i], before[j], after[j])
        for i in range(len(before)) for j in range(i + 2, len(before))
    ]
    bounds.extend(
        _affine_box_separation(a, b, other, other)
        for a, b in zip(before, after, strict=True)
        for edge in reference.edges[:2] for other in routed_tube_pieces(edge)
    )
    minimum = min(bounds)
    if minimum <= _TOLERANCE:
        raise ValueError("affine boxes do not certify self/unchanged-edge separation")
    return minimum


@dataclass(frozen=True)
class SampledRouteCollision:
    other_edge: int
    moved_piece: int
    other_piece: int
    point: Point
    penetration: float


def sample_moved_return_collisions(
    routing: SmoothGlobalToroidalRouting,
    sampling: BendSamplingGrid = BendSamplingGrid(13, 5, 24, 0.5, 0.5, 0.5),
) -> tuple[SampledRouteCollision, ...]:
    """Bidirectional volume sampling of every moved-edge/other-edge piece pair.

    Positive box clearance safely excludes a pair. Overlapping boxes trigger
    samples from both volumes and strict membership in both. No detections on
    these finite spatial/time grids do not establish continuous clearance.
    """
    moved = routed_tube_pieces(routing.edges[2])
    collisions = []
    for other_index, edge in enumerate(routing.edges):
        if other_index == 2:
            continue
        for i, left in enumerate(moved):
            for j, right in enumerate(routed_tube_pieces(edge)):
                if box_clearance(left, right) > _TOLERANCE:
                    continue
                best = None
                for source in (left, right):
                    for point in source.sample_points(sampling):
                        penetration = min(left.penetration(point), right.penetration(point))
                        if penetration > _TOLERANCE and (best is None or penetration > best.penetration):
                            best = SampledRouteCollision(other_index, i, j, point, penetration)
                if best is not None:
                    collisions.append(best)
    return tuple(collisions)


def main() -> None:
    network = build_separated_framed_edge_network(
        vesica_circulation(1.0, return_split=0.4).edges, PORT_NODES, shell_gap=3.0,
    )
    reference = build_smooth_global_toroidal_routing(network.framed_network, bend_margin=0.05)
    grid = BendSamplingGrid(13, 5, 24, 0.5, 0.5, 0.5)
    print("TOROIDAL SHARED RETURN ROUTE CANDIDATE")
    print(f"sampling={grid.description}; scope=moved_return_vs_all_other_routed_pieces")
    for progress in (0.0, 0.25, 0.5, 0.75, 1.0):
        routing = move_inner_return_to_shared_route(reference, progress)
        collisions = sample_moved_return_collisions(routing, grid)
        print(f"progress={progress:g}; collision_pairs={len(collisions)}; "
              f"max_penetration={max((w.penetration for w in collisions), default=0):.12g}; "
              f"interface_residual={routing.maximum_interface_residual():.12g}; "
              f"minimum_jacobian={routing.minimum_jacobian_margin():.12g}")
    certificate = certify_shared_return_endpoint(move_inner_return_to_shared_route(reference, 1.0))
    for name in certificate.__dataclass_fields__:
        print(f"endpoint_{name}={getattr(certificate, name):.12g}")
    print(f"continuous_self_and_edges_0_1_bound={certify_unchanged_edge_separation(reference):.12g}")
    print("endpoint_scope=routed_return_tubes; not_full_connector_embedding_or_collision_free_motion")


if __name__ == "__main__":
    main()
