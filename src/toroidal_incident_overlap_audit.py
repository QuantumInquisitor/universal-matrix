"""Audit same-face incident connector overlap in framed toroidal networks.

Annular junction ports on one face are disjoint radial bands.  The current
framed-edge construction then maps every incident edge toward the same
straightened toroidal channel annulus.  For two nonzero edges sharing a face,
that continuous radial interpolation necessarily loses disjointness before the
channel end.

This module measures that obstruction directly.  It does not alter the
connector or propose physical dynamics.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Hashable
from dataclasses import dataclass

from .toroidal_annular_junction import AnnularPortFace
from .toroidal_framed_edge_assembly import (
    FramedToroidalEdgeAssembly,
    FramedToroidalEdgeNetwork,
)

_TOLERANCE = 1e-12


@dataclass(frozen=True)
class AnnularInterval:
    inner_radius: float
    outer_radius: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.inner_radius) or not math.isfinite(self.outer_radius):
            raise ValueError("annular interval radii must be finite")
        if self.inner_radius <= 0 or self.outer_radius <= self.inner_radius:
            raise ValueError("annular interval radii must be positive and ordered")

    @property
    def width(self) -> float:
        return self.outer_radius - self.inner_radius

    def overlap_width(self, other: AnnularInterval) -> float:
        return max(
            0.0,
            min(self.outer_radius, other.outer_radius)
            - max(self.inner_radius, other.inner_radius),
        )


@dataclass(frozen=True)
class IncidentConnectorOverlap[NodeT: Hashable]:
    node: NodeT
    face: AnnularPortFace
    first_edge_index: int
    second_edge_index: int
    first_overlap_progress: float
    terminal_overlap_width: float

    def __post_init__(self) -> None:
        if self.first_edge_index >= self.second_edge_index:
            raise ValueError("overlap edge indices must be strictly ordered")
        if not 0.0 <= self.first_overlap_progress <= 1.0:
            raise ValueError("first_overlap_progress must lie in [0, 1]")
        if self.terminal_overlap_width <= 0.0:
            raise ValueError("terminal overlap width must be positive")


def _outward_interval(
    assembly: FramedToroidalEdgeAssembly,
    node,
    progress: float,
) -> AnnularInterval:
    """Return connector annulus at normalized distance from junction to channel."""
    progress = float(progress)
    if not math.isfinite(progress) or not 0.0 <= progress <= 1.0:
        raise ValueError("progress must lie in [0, 1]")

    if node == assembly.edge.source:
        transition = assembly.inlet
        s = progress
    elif node == assembly.edge.target:
        transition = assembly.outlet
        s = 1.0 - progress
    else:
        raise ValueError("node must be one endpoint of the assembly edge")

    return AnnularInterval(
        transition.radius(s, 0.0),
        transition.radius(s, 1.0),
    )


def _junction_face(
    network: FramedToroidalEdgeNetwork,
    assembly: FramedToroidalEdgeAssembly,
    node,
) -> AnnularPortFace:
    junction = network.junction_network.junction(node)
    return junction.port_by_edge(assembly.edge_index).face


def _first_overlap_progress(
    left: FramedToroidalEdgeAssembly,
    right: FramedToroidalEdgeAssembly,
    node,
) -> float:
    """Find the first connector progress where two annular intervals overlap."""
    if _outward_interval(left, node, 0.0).overlap_width(
        _outward_interval(right, node, 0.0)
    ) > _TOLERANCE:
        return 0.0

    terminal = _outward_interval(left, node, 1.0).overlap_width(
        _outward_interval(right, node, 1.0)
    )
    if terminal <= _TOLERANCE:
        return 1.0

    lower = 0.0
    upper = 1.0
    for _ in range(80):
        midpoint = 0.5 * (lower + upper)
        overlap = _outward_interval(left, node, midpoint).overlap_width(
            _outward_interval(right, node, midpoint)
        )
        if overlap > _TOLERANCE:
            upper = midpoint
        else:
            lower = midpoint
    return upper


@dataclass(frozen=True)
class IncidentConnectorOverlapAudit[NodeT: Hashable]:
    overlaps: tuple[IncidentConnectorOverlap[NodeT], ...]

    @property
    def pair_count(self) -> int:
        return len(self.overlaps)

    @property
    def affected_nodes(self) -> frozenset[NodeT]:
        return frozenset(item.node for item in self.overlaps)

    @property
    def earliest_overlap_progress(self) -> float:
        return min(
            (item.first_overlap_progress for item in self.overlaps),
            default=math.inf,
        )

    @property
    def maximum_terminal_overlap_width(self) -> float:
        return max(
            (item.terminal_overlap_width for item in self.overlaps),
            default=0.0,
        )


def audit_incident_connector_overlap[NodeT: Hashable](
    network: FramedToroidalEdgeNetwork[NodeT],
) -> IncidentConnectorOverlapAudit[NodeT]:
    """Audit nonzero incident edges that share one annular junction face."""
    assemblies_by_index = {
        assembly.edge_index: assembly for assembly in network.assemblies
    }
    overlaps = []

    for junction in network.junction_network.junctions:
        groups: dict[AnnularPortFace, list[int]] = defaultdict(list)
        for port in junction.ports:
            assembly = assemblies_by_index[port.edge_index]
            if abs(assembly.edge.current) <= _TOLERANCE:
                continue
            groups[port.face].append(port.edge_index)

        for face, edge_indices in groups.items():
            ordered = sorted(edge_indices)
            for first_position, first_index in enumerate(ordered):
                for second_index in ordered[first_position + 1 :]:
                    first = assemblies_by_index[first_index]
                    second = assemblies_by_index[second_index]
                    terminal = _outward_interval(
                        first, junction.node, 1.0
                    ).overlap_width(
                        _outward_interval(second, junction.node, 1.0)
                    )
                    if terminal <= _TOLERANCE:
                        continue
                    overlaps.append(
                        IncidentConnectorOverlap(
                            node=junction.node,
                            face=face,
                            first_edge_index=first_index,
                            second_edge_index=second_index,
                            first_overlap_progress=_first_overlap_progress(
                                first,
                                second,
                                junction.node,
                            ),
                            terminal_overlap_width=terminal,
                        )
                    )

    return IncidentConnectorOverlapAudit(tuple(overlaps))
