"""Collision-audited global routing for framed toroidal graph edges.

This module assigns global rigid translations to annular junction control
volumes and deterministic orthogonal centerline corridors to every framed edge
assembly.  It preserves the already-verified endpoint axial frames and signed
flux bookkeeping while making nonincident edge routing spatially disjoint under
a conservative tube-envelope test.

The routed centerline is a geometric placement contract only.  The bends do
not yet carry a constructed divergence-free vector field.  Dynamics and
physical units remain outside this layer.
"""

from __future__ import annotations

import math
from collections.abc import Hashable, Sequence
from dataclasses import dataclass

from .toroidal_annular_junction import AnnularJunctionControlVolume, AnnularPortFace
from .toroidal_framed_edge_assembly import (
    FramedToroidalEdgeAssembly,
    FramedToroidalEdgeNetwork,
)

_TOLERANCE = 1e-12
Point3D = tuple[float, float, float]
Vector3D = tuple[float, float, float]


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _point(values: Sequence[float], name: str = "point") -> Point3D:
    if len(values) != 3:
        raise ValueError(f"{name} must contain exactly three coordinates")
    return tuple(_finite(value, f"{name} coordinate") for value in values)


def _subtract(left: Point3D, right: Point3D) -> Vector3D:
    return tuple(a - b for a, b in zip(left, right, strict=True))


def _add(left: Point3D, right: Vector3D) -> Point3D:
    return tuple(a + b for a, b in zip(left, right, strict=True))


def _scale(vector: Vector3D, factor: float) -> Vector3D:
    return tuple(factor * value for value in vector)


def _dot(left: Vector3D, right: Vector3D) -> float:
    return math.fsum(a * b for a, b in zip(left, right, strict=True))


def _norm(vector: Vector3D) -> float:
    return math.sqrt(_dot(vector, vector))


def _unit(vector: Vector3D) -> Vector3D:
    magnitude = _norm(vector)
    if magnitude <= _TOLERANCE:
        raise ValueError("route segment must have positive length")
    return _scale(vector, 1.0 / magnitude)


def point_segment_distance(point: Point3D, start: Point3D, end: Point3D) -> float:
    """Return the Euclidean distance from a point to a finite segment."""
    direction = _subtract(end, start)
    denominator = _dot(direction, direction)
    if denominator <= _TOLERANCE:
        return _norm(_subtract(point, start))
    parameter = _dot(_subtract(point, start), direction) / denominator
    parameter = min(1.0, max(0.0, parameter))
    closest = _add(start, _scale(direction, parameter))
    return _norm(_subtract(point, closest))


def segment_distance(
    first_start: Point3D,
    first_end: Point3D,
    second_start: Point3D,
    second_end: Point3D,
) -> float:
    """Return the minimum Euclidean distance between two finite 3D segments.

    The implementation follows the standard closest-points calculation with
    explicit degeneracy handling for nearly point-like segments.
    """
    u = _subtract(first_end, first_start)
    v = _subtract(second_end, second_start)
    w = _subtract(first_start, second_start)
    a = _dot(u, u)
    b = _dot(u, v)
    c = _dot(v, v)
    d = _dot(u, w)
    e = _dot(v, w)

    if a <= _TOLERANCE and c <= _TOLERANCE:
        return _norm(_subtract(first_start, second_start))
    if a <= _TOLERANCE:
        return point_segment_distance(first_start, second_start, second_end)
    if c <= _TOLERANCE:
        return point_segment_distance(second_start, first_start, first_end)

    denominator = a * c - b * b
    s_numerator = denominator
    s_denominator = denominator
    t_numerator = denominator
    t_denominator = denominator

    if denominator <= _TOLERANCE:
        s_numerator = 0.0
        s_denominator = 1.0
        t_numerator = e
        t_denominator = c
    else:
        s_numerator = b * e - c * d
        t_numerator = a * e - b * d
        if s_numerator < 0.0:
            s_numerator = 0.0
            t_numerator = e
            t_denominator = c
        elif s_numerator > s_denominator:
            s_numerator = s_denominator
            t_numerator = e + b
            t_denominator = c

    if t_numerator < 0.0:
        t_numerator = 0.0
        if -d < 0.0:
            s_numerator = 0.0
        elif -d > a:
            s_numerator = s_denominator
        else:
            s_numerator = -d
            s_denominator = a
    elif t_numerator > t_denominator:
        t_numerator = t_denominator
        if -d + b < 0.0:
            s_numerator = 0.0
        elif -d + b > a:
            s_numerator = s_denominator
        else:
            s_numerator = -d + b
            s_denominator = a

    s = 0.0 if abs(s_numerator) <= _TOLERANCE else s_numerator / s_denominator
    t = 0.0 if abs(t_numerator) <= _TOLERANCE else t_numerator / t_denominator
    delta = _subtract(_add(first_start, _scale(u, s)), _add(second_start, _scale(v, t)))
    return _norm(delta)


@dataclass(frozen=True)
class GlobalJunctionPlacement[NodeT: Hashable]:
    """Rigid translation of one annular junction into the global frame."""

    junction: AnnularJunctionControlVolume[NodeT]
    center: Point3D

    def __post_init__(self) -> None:
        object.__setattr__(self, "center", _point(self.center, "center"))

    @property
    def node(self) -> NodeT:
        return self.junction.node

    @property
    def bounding_radius(self) -> float:
        return math.hypot(self.junction.outer_radius, self.junction.length / 2.0)

    def port_axis_point(self, edge_index: int) -> Point3D:
        """Return the global axis point at the selected annular port face."""
        port = self.junction.port_by_edge(edge_index)
        offset = (
            -self.junction.length / 2.0
            if port.face is AnnularPortFace.LOWER
            else self.junction.length / 2.0
        )
        return self.center[0], self.center[1], self.center[2] + offset


@dataclass(frozen=True)
class EdgeEndpointFrame[NodeT: Hashable]:
    node: NodeT
    origin: Point3D
    axis: Vector3D

    def __post_init__(self) -> None:
        object.__setattr__(self, "origin", _point(self.origin, "origin"))
        axis = _point(self.axis, "axis")
        unit = _unit(axis)
        object.__setattr__(self, "axis", unit)


@dataclass(frozen=True)
class RoutedEdgePlacement[NodeT: Hashable]:
    """Global centerline envelope for one framed edge assembly."""

    assembly: FramedToroidalEdgeAssembly[NodeT]
    source_frame: EdgeEndpointFrame[NodeT]
    target_frame: EdgeEndpointFrame[NodeT]
    route: tuple[Point3D, ...]
    clearance_radius: float
    lane_y: float
    lane_height: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "clearance_radius", _finite(self.clearance_radius, "clearance_radius"))
        object.__setattr__(self, "lane_y", _finite(self.lane_y, "lane_y"))
        object.__setattr__(self, "lane_height", _finite(self.lane_height, "lane_height"))
        if self.clearance_radius <= 0:
            raise ValueError("clearance_radius must be positive")
        if self.lane_height <= 0:
            raise ValueError("lane_height must be positive")
        route = tuple(_point(point, "route point") for point in self.route)
        if len(route) != 7:
            raise ValueError("orthogonal routed edge must contain seven route points")
        if any(_norm(_subtract(right, left)) <= _TOLERANCE for left, right in zip(route, route[1:])):
            raise ValueError("adjacent route points must be distinct")
        object.__setattr__(self, "route", route)
        if self.endpoint_frame_residual() > _TOLERANCE:
            raise ValueError("route endpoint tangents must match the declared frames")

    @property
    def edge_index(self) -> int:
        return self.assembly.edge_index

    @property
    def edge(self):
        return self.assembly.edge

    @property
    def segments(self) -> tuple[tuple[Point3D, Point3D], ...]:
        return tuple(zip(self.route, self.route[1:]))

    @property
    def length(self) -> float:
        return math.fsum(_norm(_subtract(end, start)) for start, end in self.segments)

    def endpoint_frame_residual(self) -> float:
        first = _unit(_subtract(self.route[1], self.route[0]))
        last = _unit(_subtract(self.route[-1], self.route[-2]))
        residuals = [
            *(abs(a - b) for a, b in zip(first, self.source_frame.axis, strict=True)),
            *(abs(a - b) for a, b in zip(last, self.target_frame.axis, strict=True)),
            *(
                abs(a - b)
                for a, b in zip(self.route[0], self.source_frame.origin, strict=True)
            ),
            *(
                abs(a - b)
                for a, b in zip(self.route[-1], self.target_frame.origin, strict=True)
            ),
        ]
        return max(residuals, default=0.0)


@dataclass(frozen=True)
class GlobalToroidalRouting[NodeT: Hashable]:
    """Collision-audited global placement of junctions and routed edge envelopes."""

    framed_network: FramedToroidalEdgeNetwork[NodeT]
    junctions: tuple[GlobalJunctionPlacement[NodeT], ...]
    edges: tuple[RoutedEdgePlacement[NodeT], ...]
    node_gap: float
    edge_gap: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "node_gap", _finite(self.node_gap, "node_gap"))
        object.__setattr__(self, "edge_gap", _finite(self.edge_gap, "edge_gap"))
        if self.node_gap < 0 or self.edge_gap < 0:
            raise ValueError("routing gaps must be nonnegative")
        if len({placement.node for placement in self.junctions}) != len(self.junctions):
            raise ValueError("global junction nodes must be unique")
        if tuple(edge.edge_index for edge in self.edges) != tuple(range(len(self.edges))):
            raise ValueError("routed edge indices must be consecutive")
        if self.maximum_endpoint_frame_residual() > _TOLERANCE:
            raise ValueError("global routing endpoint frame mismatch")
        if self.minimum_nonincident_edge_clearance() < -_TOLERANCE:
            raise ValueError("nonincident routed edge envelopes overlap")
        if self.minimum_edge_to_nonincident_junction_clearance() < -_TOLERANCE:
            raise ValueError("routed edge envelope intersects a nonincident junction")

    def junction(self, node: NodeT) -> GlobalJunctionPlacement[NodeT]:
        try:
            return next(item for item in self.junctions if item.node == node)
        except StopIteration as error:
            raise ValueError("unknown global junction node") from error

    def maximum_endpoint_frame_residual(self) -> float:
        return max((edge.endpoint_frame_residual() for edge in self.edges), default=0.0)

    def minimum_nonincident_edge_clearance(self) -> float:
        clearances = []
        for index, left in enumerate(self.edges):
            left_nodes = {left.edge.source, left.edge.target}
            for right in self.edges[index + 1 :]:
                if left_nodes & {right.edge.source, right.edge.target}:
                    continue
                centerline_distance = min(
                    segment_distance(a0, a1, b0, b1)
                    for a0, a1 in left.segments
                    for b0, b1 in right.segments
                )
                clearances.append(
                    centerline_distance - left.clearance_radius - right.clearance_radius
                )
        return min(clearances, default=math.inf)

    def minimum_edge_to_nonincident_junction_clearance(self) -> float:
        clearances = []
        for edge in self.edges:
            incident = {edge.edge.source, edge.edge.target}
            for junction in self.junctions:
                if junction.node in incident:
                    continue
                centerline_distance = min(
                    point_segment_distance(junction.center, start, end)
                    for start, end in edge.segments
                )
                clearances.append(
                    centerline_distance - edge.clearance_radius - junction.bounding_radius
                )
        return min(clearances, default=math.inf)

    def nonincident_edge_collision_count(self) -> int:
        count = 0
        for index, left in enumerate(self.edges):
            left_nodes = {left.edge.source, left.edge.target}
            for right in self.edges[index + 1 :]:
                if left_nodes & {right.edge.source, right.edge.target}:
                    continue
                distance = min(
                    segment_distance(a0, a1, b0, b1)
                    for a0, a1 in left.segments
                    for b0, b1 in right.segments
                )
                if distance < left.clearance_radius + right.clearance_radius - _TOLERANCE:
                    count += 1
        return count


def _assembly_clearance_radius(assembly: FramedToroidalEdgeAssembly) -> float:
    return max(
        assembly.source_port.outer_radius,
        assembly.target_port.outer_radius,
        assembly.inlet.source_outer_radius,
        assembly.inlet.target_outer_radius,
        assembly.channel.outer_radius,
        assembly.outlet.source_outer_radius,
        assembly.outlet.target_outer_radius,
    )


def build_global_toroidal_routing[NodeT: Hashable](
    framed_network: FramedToroidalEdgeNetwork[NodeT],
    *,
    node_gap: float = 1.0,
    edge_gap: float = 0.5,
    route_padding: float = 0.1,
) -> GlobalToroidalRouting[NodeT]:
    """Build a deterministic collision-audited orthogonal global routing.

    All junction axes remain parallel to global +z, so junction placement is a
    rigid translation.  Each edge receives a unique positive y corridor and a
    unique symmetric high/low z level.  The route starts and ends along ``axis_sign * +z``, preserving the signed
    endpoint frame contract established by the framed assembly.
    """
    node_gap = _finite(node_gap, "node_gap")
    edge_gap = _finite(edge_gap, "edge_gap")
    route_padding = _finite(route_padding, "route_padding")
    if node_gap < 0 or edge_gap < 0 or route_padding < 0:
        raise ValueError("routing gaps and padding must be nonnegative")

    local_junctions = framed_network.junction_network.junctions
    assemblies = framed_network.assemblies
    maximum_edge_radius = max(
        (_assembly_clearance_radius(assembly) + route_padding for assembly in assemblies),
        default=1.0,
    )
    maximum_junction_bound = max(
        (
            math.hypot(junction.outer_radius, junction.length / 2.0)
            for junction in local_junctions
        ),
        default=1.0,
    )

    node_spacing = 2.0 * (maximum_edge_radius + maximum_junction_bound) + node_gap
    edge_spacing = 2.0 * maximum_edge_radius + edge_gap
    maximum_half_length = max(
        (junction.length / 2.0 for junction in local_junctions),
        default=0.5,
    )
    base_height = maximum_half_length + maximum_edge_radius + edge_gap

    midpoint = (len(local_junctions) - 1) / 2.0
    junctions = tuple(
        GlobalJunctionPlacement(
            junction=junction,
            center=((index - midpoint) * node_spacing, 0.0, 0.0),
        )
        for index, junction in enumerate(local_junctions)
    )
    by_node = {placement.node: placement for placement in junctions}

    routed = []
    for assembly in assemblies:
        source = by_node[assembly.edge.source]
        target = by_node[assembly.edge.target]
        source_origin = source.port_axis_point(assembly.edge_index)
        target_origin = target.port_axis_point(assembly.edge_index)
        lane_y = (assembly.edge_index + 1) * edge_spacing
        lane_height = base_height + (assembly.edge_index + 1) * edge_spacing

        axis_sign = assembly.axis_sign
        source_level = axis_sign * lane_height
        target_level = -axis_sign * lane_height
        endpoint_axis = (0.0, 0.0, float(axis_sign))
        route = (
            source_origin,
            (source_origin[0], 0.0, source_level),
            (source_origin[0], lane_y, source_level),
            (source_origin[0], lane_y, target_level),
            (target_origin[0], lane_y, target_level),
            (target_origin[0], 0.0, target_level),
            target_origin,
        )
        routed.append(
            RoutedEdgePlacement(
                assembly=assembly,
                source_frame=EdgeEndpointFrame(assembly.edge.source, source_origin, endpoint_axis),
                target_frame=EdgeEndpointFrame(assembly.edge.target, target_origin, endpoint_axis),
                route=route,
                clearance_radius=_assembly_clearance_radius(assembly) + route_padding,
                lane_y=lane_y,
                lane_height=lane_height,
            )
        )

    result = GlobalToroidalRouting(
        framed_network=framed_network,
        junctions=junctions,
        edges=tuple(routed),
        node_gap=node_gap,
        edge_gap=edge_gap,
    )
    if result.nonincident_edge_collision_count() != 0:
        raise RuntimeError("global toroidal routing contains a nonincident edge collision")
    return result
