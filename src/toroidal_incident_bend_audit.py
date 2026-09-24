"""Audit collisions between incident smooth bends and neighboring straight shells.

Edge-specific annular channel shells remove the coaxial connector-overlap
obstruction. The next geometric question is whether those shells remain
disjoint when one incident edge begins a smooth quarter bend while another
edge sharing the same junction face is still travelling along its endpoint
straight segment.

This module samples the actual annular bend volume produced by
toroidal_smooth_bends and tests it against the exact finite annular
straight segment of every other nonzero same-face incident edge.

The audit is numerical and diagnostic. It does not alter flux conservation or
introduce a dynamics law.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Hashable, Sequence
from dataclasses import dataclass

from .toroidal_annular_junction import AnnularPortFace
from .toroidal_separated_channels import SeparatedFramedEdgeNetwork
from .toroidal_smooth_bends import (
    AnnularQuarterBend,
    SmoothedRoutedEdge,
    SmoothGlobalToroidalRouting,
    build_smooth_global_toroidal_routing,
)

_TOLERANCE = 1e-10
Point3D = tuple[float, float, float]


@dataclass(frozen=True)
class BendSamplingGrid:
    """Finite volume sampler; offsets are fractions of one grid interval.

    Zero offsets preserve the original grid. Positive phi/q offsets move
    samples toward the preceding interval; theta offsets rotate the periodic
    grid. A shifted grid supplements, rather than certifies, the original.
    """

    phi_samples: int = 25
    q_samples: int = 9
    theta_samples: int = 48
    phi_offset: float = 0.0
    q_offset: float = 0.0
    theta_offset: float = 0.0

    def __post_init__(self) -> None:
        for name, minimum in (("phi_samples", 4), ("q_samples", 3), ("theta_samples", 8)):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
                raise ValueError(f"{name} must be an integer at least {minimum}")
        for name in ("phi_offset", "q_offset", "theta_offset"):
            value = float(getattr(self, name))
            if not math.isfinite(value) or not 0.0 <= value < 1.0:
                raise ValueError(f"{name} must be finite and in [0, 1)")
            object.__setattr__(self, name, value)

    @property
    def description(self) -> str:
        return (
            f"phi:{self.phi_samples},q:{self.q_samples},theta:{self.theta_samples},"
            f"offsets:[{self.phi_offset:g},{self.q_offset:g},{self.theta_offset:g}]"
        )


def _dot(left: Sequence[float], right: Sequence[float]) -> float:
    return math.fsum(a * b for a, b in zip(left, right, strict=True))


def _subtract(left: Sequence[float], right: Sequence[float]) -> Point3D:
    return tuple(a - b for a, b in zip(left, right, strict=True))


def _add(left: Sequence[float], right: Sequence[float]) -> Point3D:
    return tuple(a + b for a, b in zip(left, right, strict=True))


def _scale(vector: Sequence[float], factor: float) -> Point3D:
    return tuple(factor * value for value in vector)


def _norm(vector: Sequence[float]) -> float:
    return math.sqrt(_dot(vector, vector))


@dataclass(frozen=True)
class AnnularStraightSegment:
    start: Point3D
    end: Point3D
    inner_radius: float
    outer_radius: float

    def __post_init__(self) -> None:
        if self.inner_radius <= 0 or self.outer_radius <= self.inner_radius:
            raise ValueError("straight-shell radii must be positive and ordered")
        if _norm(_subtract(self.end, self.start)) <= _TOLERANCE:
            raise ValueError("straight segment must have positive length")

    @property
    def direction(self) -> Point3D:
        delta = _subtract(self.end, self.start)
        length = _norm(delta)
        return _scale(delta, 1.0 / length)

    @property
    def length(self) -> float:
        return _norm(_subtract(self.end, self.start))

    def local_coordinates(self, point: Sequence[float]) -> tuple[float, float]:
        delta = _subtract(point, self.start)
        direction = self.direction
        axial = _dot(delta, direction)
        closest = _add(self.start, _scale(direction, axial))
        radial = _norm(_subtract(point, closest))
        return axial, radial

    def penetration_margin(self, point: Sequence[float]) -> float:
        axial, radial = self.local_coordinates(point)
        axial_margin = min(axial, self.length - axial)
        radial_margin = min(
            radial - self.inner_radius,
            self.outer_radius - radial,
        )
        return min(axial_margin, radial_margin)


@dataclass(frozen=True)
class IncidentBendCollision[NodeT: Hashable]:
    node: NodeT
    face: AnnularPortFace
    bending_edge_index: int
    straight_edge_index: int
    maximum_penetration: float
    witness_point: Point3D
    witness_phi: float
    witness_q: float
    witness_theta: float

    def __post_init__(self) -> None:
        if self.bending_edge_index == self.straight_edge_index:
            raise ValueError("collision must involve distinct graph edges")
        if self.maximum_penetration <= 0:
            raise ValueError("collision witness must have positive penetration")


@dataclass(frozen=True)
class IncidentBendCollisionAudit[NodeT: Hashable]:
    smooth_routing: SmoothGlobalToroidalRouting[NodeT]
    collisions: tuple[IncidentBendCollision[NodeT], ...]
    sampling: BendSamplingGrid = BendSamplingGrid()

    @property
    def collision_count(self) -> int:
        return len(self.collisions)

    @property
    def affected_nodes(self) -> frozenset[NodeT]:
        return frozenset(item.node for item in self.collisions)

    @property
    def maximum_penetration(self) -> float:
        return max(
            (item.maximum_penetration for item in self.collisions),
            default=0.0,
        )


def _endpoint_bend_and_straight(
    edge: SmoothedRoutedEdge,
    node,
) -> tuple[AnnularQuarterBend, AnnularStraightSegment]:
    route = edge.route.route
    if node == edge.route.edge.source:
        bend = edge.bends[0]
        straight = AnnularStraightSegment(
            start=route[0],
            end=bend.start,
            inner_radius=edge.route.assembly.channel.inner_radius,
            outer_radius=edge.route.assembly.channel.outer_radius,
        )
    elif node == edge.route.edge.target:
        bend = edge.bends[-1]
        straight = AnnularStraightSegment(
            start=bend.end,
            end=route[-1],
            inner_radius=edge.route.assembly.channel.inner_radius,
            outer_radius=edge.route.assembly.channel.outer_radius,
        )
    else:
        raise ValueError("node must be one endpoint of the routed edge")
    return bend, straight


def _sample_bend_against_straight(
    bend: AnnularQuarterBend,
    straight: AnnularStraightSegment,
    *,
    sampling: BendSamplingGrid,
) -> tuple[float, Point3D, float, float, float] | None:
    best = None
    for phi_index in range(1, sampling.phi_samples):
        phi = (math.pi / 2) * (phi_index - sampling.phi_offset) / (sampling.phi_samples - 1)
        for q_index in range(1, sampling.q_samples - 1):
            q = (q_index - sampling.q_offset) / (sampling.q_samples - 1)
            for theta_index in range(sampling.theta_samples):
                theta = 2 * math.pi * (theta_index + sampling.theta_offset) / sampling.theta_samples
                point = bend.map_point(phi, q, theta)
                penetration = straight.penetration_margin(point)
                if penetration <= _TOLERANCE:
                    continue
                if best is None or penetration > best[0]:
                    best = (penetration, point, phi, q, theta)
    return best


def audit_incident_bend_collisions[NodeT: Hashable](
    separated_network: SeparatedFramedEdgeNetwork[NodeT],
    *,
    bend_margin: float = 0.25,
    node_gap: float = 1.0,
    edge_gap: float = 0.5,
    phi_samples: int = 25,
    q_samples: int = 9,
    theta_samples: int = 48,
    phi_offset: float = 0.0,
    q_offset: float = 0.0,
    theta_offset: float = 0.0,
) -> IncidentBendCollisionAudit[NodeT]:
    sampling = BendSamplingGrid(
        phi_samples, q_samples, theta_samples, phi_offset, q_offset, theta_offset
    )

    smooth = build_smooth_global_toroidal_routing(
        separated_network.framed_network,
        bend_margin=bend_margin,
        node_gap=node_gap,
        edge_gap=edge_gap,
    )
    smooth_by_index = {edge.edge_index: edge for edge in smooth.edges}
    collisions = []

    for junction in separated_network.junction_network.junctions:
        groups: dict[AnnularPortFace, list[int]] = defaultdict(list)
        for port in junction.ports:
            assembly = separated_network.framed_network.assemblies[port.edge_index]
            if abs(assembly.edge.current) <= _TOLERANCE:
                continue
            groups[port.face].append(port.edge_index)

        for face, edge_indices in groups.items():
            ordered = sorted(edge_indices)
            for bending_index in ordered:
                bending_edge = smooth_by_index[bending_index]
                bend, _ = _endpoint_bend_and_straight(
                    bending_edge,
                    junction.node,
                )
                for straight_index in ordered:
                    if straight_index == bending_index:
                        continue
                    straight_edge = smooth_by_index[straight_index]
                    _, straight = _endpoint_bend_and_straight(
                        straight_edge,
                        junction.node,
                    )
                    witness = _sample_bend_against_straight(
                        bend,
                        straight,
                        sampling=sampling,
                    )
                    if witness is None:
                        continue
                    penetration, point, phi, q, theta = witness
                    collisions.append(
                        IncidentBendCollision(
                            node=junction.node,
                            face=face,
                            bending_edge_index=bending_index,
                            straight_edge_index=straight_index,
                            maximum_penetration=penetration,
                            witness_point=point,
                            witness_phi=phi,
                            witness_q=q,
                            witness_theta=theta,
                        )
                    )

    return IncidentBendCollisionAudit(
        smooth_routing=smooth,
        collisions=tuple(collisions),
        sampling=sampling,
    )
