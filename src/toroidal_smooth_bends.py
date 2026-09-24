"""Smooth positive-Jacobian annular bends for globally routed toroidal edges.

The global routing layer supplies orthogonal centerlines with sharp corners.
This module replaces every 90-degree corner by an explicit quarter-circle
annular bend.  The bend map is smooth, has positive Jacobian whenever the bend
radius exceeds the annular outer radius, and carries the same signed axial flux
profile through the bend.

The current field is the contravariant Piola image of the straight annular
channel field.  In the quarter-bend coordinates the resulting physical vector
is simply the preserved annular density times the local unit tangent.

This remains a kinematic field construction.  It does not introduce dynamics
or physical units.
"""

from __future__ import annotations

import math
from collections.abc import Hashable, Sequence
from dataclasses import dataclass

from .toroidal_connector_topology import annular_connector_source_density
from .toroidal_framed_edge_assembly import FramedToroidalEdgeNetwork
from .toroidal_global_routing import (
    GlobalToroidalRouting,
    Point3D,
    RoutedEdgePlacement,
    Vector3D,
    _add,
    _dot,
    _norm,
    _scale,
    _subtract,
    _unit,
    build_global_toroidal_routing,
)

_TOLERANCE = 1e-12


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _cross(left: Vector3D, right: Vector3D) -> Vector3D:
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


@dataclass(frozen=True)
class AnnularQuarterBend:
    """One 90-degree annular tube bend with flux-preserving Piola current."""

    corner: Point3D
    source_tangent: Vector3D
    target_tangent: Vector3D
    bend_radius: float
    inner_radius: float
    outer_radius: float
    flux: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "corner", tuple(_finite(v, "corner coordinate") for v in self.corner))
        source = _unit(tuple(_finite(v, "source tangent") for v in self.source_tangent))
        target = _unit(tuple(_finite(v, "target tangent") for v in self.target_tangent))
        if abs(_dot(source, target)) > 1e-10:
            raise ValueError("quarter-bend tangents must be orthogonal")
        object.__setattr__(self, "source_tangent", source)
        object.__setattr__(self, "target_tangent", target)
        for name in ("bend_radius", "inner_radius", "outer_radius", "flux"):
            object.__setattr__(self, name, _finite(getattr(self, name), name))
        if self.inner_radius <= 0 or self.outer_radius <= self.inner_radius:
            raise ValueError("annular radii must be positive and ordered")
        if self.bend_radius <= self.outer_radius:
            raise ValueError("bend radius must exceed the annular outer radius")
        binormal = _unit(_cross(source, target))
        object.__setattr__(self, "_binormal", binormal)

    @property
    def width(self) -> float:
        return self.outer_radius - self.inner_radius

    @property
    def start(self) -> Point3D:
        return _add(self.corner, _scale(self.source_tangent, -self.bend_radius))

    @property
    def end(self) -> Point3D:
        return _add(self.corner, _scale(self.target_tangent, self.bend_radius))

    @property
    def minimum_jacobian_scale(self) -> float:
        """Minimum Cartesian Piola Jacobian factor relative to a straight tube."""
        return 1.0 - self.outer_radius / self.bend_radius

    def tangent(self, phi: float) -> Vector3D:
        phi = _finite(phi, "phi")
        return tuple(
            math.cos(phi) * a + math.sin(phi) * b
            for a, b in zip(self.source_tangent, self.target_tangent, strict=True)
        )

    def normal(self, phi: float) -> Vector3D:
        phi = _finite(phi, "phi")
        return tuple(
            -math.sin(phi) * a + math.cos(phi) * b
            for a, b in zip(self.source_tangent, self.target_tangent, strict=True)
        )

    def centerline_point(self, phi: float) -> Point3D:
        phi = _finite(phi, "phi")
        if phi < -_TOLERANCE or phi > math.pi / 2 + _TOLERANCE:
            raise ValueError("phi must lie in [0, pi/2]")
        phi = min(math.pi / 2, max(0.0, phi))
        return _add(
            self.corner,
            tuple(
                self.bend_radius
                * (
                    (math.sin(phi) - 1.0) * source
                    + (1.0 - math.cos(phi)) * target
                )
                for source, target in zip(
                    self.source_tangent,
                    self.target_tangent,
                    strict=True,
                )
            ),
        )

    def map_point(self, phi: float, q: float, theta: float) -> Point3D:
        phi = _finite(phi, "phi")
        q = _finite(q, "q")
        theta = _finite(theta, "theta")
        if phi < -_TOLERANCE or phi > math.pi / 2 + _TOLERANCE:
            raise ValueError("phi must lie in [0, pi/2]")
        if q < -_TOLERANCE or q > 1.0 + _TOLERANCE:
            raise ValueError("q must lie in [0, 1]")
        phi = min(math.pi / 2, max(0.0, phi))
        q = min(1.0, max(0.0, q))
        radius = self.inner_radius + self.width * q
        center = self.centerline_point(phi)
        normal = self.normal(phi)
        offset = tuple(
            radius * math.cos(theta) * n + radius * math.sin(theta) * b
            for n, b in zip(normal, self._binormal, strict=True)
        )
        return _add(center, offset)

    def inverse_parameters(self, point: Sequence[float]) -> tuple[float, float, float] | None:
        if len(point) != 3:
            raise ValueError("point must contain exactly three coordinates")
        point = tuple(_finite(value, "coordinate") for value in point)
        center = _add(
            _add(self.corner, _scale(self.source_tangent, -self.bend_radius)),
            _scale(self.target_tangent, self.bend_radius),
        )
        relative = _subtract(point, center)
        source_component = _dot(relative, self.source_tangent)
        target_component = _dot(relative, self.target_tangent)
        binormal_component = _dot(relative, self._binormal)

        phi = math.atan2(source_component, -target_component)
        if phi < -_TOLERANCE or phi > math.pi / 2 + _TOLERANCE:
            return None
        phi = min(math.pi / 2, max(0.0, phi))
        planar_distance = math.hypot(source_component, target_component)
        radial_normal = self.bend_radius - planar_distance
        radius = math.hypot(radial_normal, binormal_component)
        if radius < self.inner_radius - _TOLERANCE or radius > self.outer_radius + _TOLERANCE:
            return None
        radius = min(self.outer_radius, max(self.inner_radius, radius))
        q = (radius - self.inner_radius) / self.width
        theta = math.atan2(binormal_component, radial_normal)
        return phi, q, theta

    def current(self, point: Sequence[float]) -> Vector3D:
        parameters = self.inverse_parameters(point)
        if parameters is None:
            return 0.0, 0.0, 0.0
        phi, q, _ = parameters
        radius = self.inner_radius + self.width * q
        density = annular_connector_source_density(
            self.flux,
            self.inner_radius,
            self.outer_radius,
            radius,
        )
        return _scale(self.tangent(phi), density)

    def jacobian_scale(self, radius: float, theta: float) -> float:
        radius = _finite(radius, "radius")
        theta = _finite(theta, "theta")
        if radius < self.inner_radius - _TOLERANCE or radius > self.outer_radius + _TOLERANCE:
            raise ValueError("radius must lie in the annulus")
        return 1.0 - radius * math.cos(theta) / self.bend_radius

    def interface_vector_residual(self) -> float:
        residuals = []
        for phi, tangent in (
            (0.0, self.source_tangent),
            (math.pi / 2, self.target_tangent),
        ):
            for q in (0.1, 0.25, 0.5, 0.75, 0.9):
                radius = self.inner_radius + self.width * q
                density = annular_connector_source_density(
                    self.flux,
                    self.inner_radius,
                    self.outer_radius,
                    radius,
                )
                point = self.map_point(phi, q, 0.0)
                actual = self.current(point)
                expected = _scale(tangent, density)
                residuals.extend(
                    abs(a - b) for a, b in zip(actual, expected, strict=True)
                )
        return max(residuals, default=0.0)


@dataclass(frozen=True)
class SmoothedRoutedEdge[NodeT: Hashable]:
    route: RoutedEdgePlacement[NodeT]
    bends: tuple[AnnularQuarterBend, ...]

    def __post_init__(self) -> None:
        if len(self.bends) != len(self.route.route) - 2:
            raise ValueError("every internal route corner must have one bend")
        if self.maximum_interface_residual() > _TOLERANCE:
            raise ValueError("bend vectors do not match adjacent straight fields")
        if self.minimum_jacobian_margin() <= 0.0:
            raise ValueError("smooth bends must have positive Jacobian margin")
        if not self.trimmed_straights_have_positive_length():
            raise ValueError("bend radius is too large for one routed segment")

    @property
    def edge_index(self) -> int:
        return self.route.edge_index

    def maximum_interface_residual(self) -> float:
        return max((bend.interface_vector_residual() for bend in self.bends), default=0.0)

    def minimum_jacobian_margin(self) -> float:
        return min((bend.minimum_jacobian_scale for bend in self.bends), default=math.inf)

    def trimmed_straights_have_positive_length(self) -> bool:
        points = self.route.route
        radii = [bend.bend_radius for bend in self.bends]
        segment_lengths = [
            _norm(_subtract(right, left))
            for left, right in zip(points, points[1:])
        ]
        for index, length in enumerate(segment_lengths):
            trim = 0.0
            if index > 0:
                trim += radii[index - 1]
            if index < len(radii):
                trim += radii[index]
            if length <= trim + _TOLERANCE:
                return False
        return True

    def envelope_contains_bends(self) -> bool:
        """Certify bends lie inside the already collision-audited route envelope.

        A quarter-bend centerline stays within one bend radius of the original
        two-segment corner.  Adding the annular outer radius bounds the entire
        curved volume.  The global route envelope was deliberately expanded by
        at least the maximum bend radius.
        """
        outer = self.route.assembly.channel.outer_radius
        return all(
            self.route.clearance_radius + _TOLERANCE >= outer + bend.bend_radius
            for bend in self.bends
        )


@dataclass(frozen=True)
class SmoothGlobalToroidalRouting[NodeT: Hashable]:
    global_routing: GlobalToroidalRouting[NodeT]
    edges: tuple[SmoothedRoutedEdge[NodeT], ...]
    bend_margin: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "bend_margin", _finite(self.bend_margin, "bend_margin"))
        if self.bend_margin <= 0:
            raise ValueError("bend_margin must be positive")
        if self.maximum_interface_residual() > _TOLERANCE:
            raise ValueError("smooth global routing has a bend interface mismatch")
        if self.minimum_jacobian_margin() <= 0:
            raise ValueError("smooth global routing lost positive Jacobian")
        if not all(edge.envelope_contains_bends() for edge in self.edges):
            raise ValueError("collision envelope does not contain every smooth bend")
        if self.global_routing.minimum_nonincident_edge_clearance() <= 0:
            raise ValueError("expanded global envelopes are not collision-free")
        if self.global_routing.minimum_edge_to_nonincident_junction_clearance() <= 0:
            raise ValueError("expanded routing intersects a nonincident junction")

    def maximum_interface_residual(self) -> float:
        return max((edge.maximum_interface_residual() for edge in self.edges), default=0.0)

    def minimum_jacobian_margin(self) -> float:
        return min((edge.minimum_jacobian_margin() for edge in self.edges), default=math.inf)

    def minimum_collision_certificate(self) -> float:
        return min(
            self.global_routing.minimum_nonincident_edge_clearance(),
            self.global_routing.minimum_edge_to_nonincident_junction_clearance(),
        )


def _build_edge_bends(
    routed: RoutedEdgePlacement[NodeT],
    bend_radius: float,
) -> tuple[AnnularQuarterBend, ...]:
    points = routed.route
    bends = []
    for index in range(1, len(points) - 1):
        source_tangent = _unit(_subtract(points[index], points[index - 1]))
        target_tangent = _unit(_subtract(points[index + 1], points[index]))
        bends.append(
            AnnularQuarterBend(
                corner=points[index],
                source_tangent=source_tangent,
                target_tangent=target_tangent,
                bend_radius=bend_radius,
                inner_radius=routed.assembly.channel.inner_radius,
                outer_radius=routed.assembly.channel.outer_radius,
                flux=routed.edge.current,
            )
        )
    return tuple(bends)


def build_smooth_global_toroidal_routing[NodeT: Hashable](
    framed_network: FramedToroidalEdgeNetwork[NodeT],
    *,
    bend_margin: float = 0.25,
    node_gap: float = 1.0,
    edge_gap: float = 0.5,
) -> SmoothGlobalToroidalRouting[NodeT]:
    """Build globally collision-audited routing with smooth annular 90-degree bends."""
    bend_margin = _finite(bend_margin, "bend_margin")
    if bend_margin <= 0:
        raise ValueError("bend_margin must be positive")

    bend_radii = tuple(
        assembly.channel.outer_radius + bend_margin
        for assembly in framed_network.assemblies
    )
    maximum_bend_radius = max(bend_radii, default=bend_margin)
    global_routing = build_global_toroidal_routing(
        framed_network,
        node_gap=node_gap,
        edge_gap=edge_gap,
        route_padding=maximum_bend_radius,
    )
    edges = tuple(
        SmoothedRoutedEdge(
            route=routed,
            bends=_build_edge_bends(routed, bend_radius),
        )
        for routed, bend_radius in zip(
            global_routing.edges,
            bend_radii,
            strict=True,
        )
    )
    return SmoothGlobalToroidalRouting(
        global_routing=global_routing,
        edges=edges,
        bend_margin=bend_margin,
    )
