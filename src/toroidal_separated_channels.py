"""Edge-specific annular channel shells for incident-connector separation.

The common-channel framed-edge construction maps every edge toward one
identical channel annulus.  Same-face incident connectors therefore overlap
before reaching the channel.

This module assigns each graph edge a distinct annular channel shell ordered by
edge index.  The corresponding toroidal flux bundle uses one edge-specific
major radius per channel while preserving the signed graph current as the
poloidal cut flux.  Existing annular junction and framed-edge builders can then
operate unchanged.

Because junction face bands and channel shells share the same edge-index order,
the smooth radial interpolation preserves interval order and prevents
same-face connector overlap.

This is a geometric correction.  It does not yet prove that the later smooth
bends of incident edges remain disjoint.
"""

from __future__ import annotations

import math
from collections.abc import Hashable, Sequence
from dataclasses import dataclass

from .graph_toroidal_flux_bundle import (
    GraphToroidalFluxBundle,
    ToroidalChannelVolume,
)
from .toroidal_annular_junction import (
    AnnularJunctionNetwork,
    AnnularPortFace,
    connect_bundle_to_annular_junctions,
)
from .toroidal_framed_edge_assembly import (
    FramedToroidalEdgeAssembly,
    FramedToroidalEdgeNetwork,
    build_framed_edge_network,
)
from .vesica_tree_circulation import DirectedCurrent

_TOLERANCE = 1e-12


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


@dataclass(frozen=True)
class EdgeChannelShell:
    edge_index: int
    inner_radius: float
    outer_radius: float

    def __post_init__(self) -> None:
        if not isinstance(self.edge_index, int) or isinstance(self.edge_index, bool):
            raise TypeError("edge_index must be an integer")
        if self.edge_index < 0:
            raise ValueError("edge_index must be nonnegative")
        object.__setattr__(self, "inner_radius", _finite(self.inner_radius, "inner_radius"))
        object.__setattr__(self, "outer_radius", _finite(self.outer_radius, "outer_radius"))
        if self.inner_radius <= 0 or self.outer_radius <= self.inner_radius:
            raise ValueError("channel shell radii must be positive and ordered")

    @property
    def width(self) -> float:
        return self.outer_radius - self.inner_radius


def allocate_edge_channel_shells(
    edge_count: int,
    *,
    base_inner_radius: float = 2.0,
    shell_width: float = 0.4,
    shell_gap: float = 0.25,
) -> tuple[EdgeChannelShell, ...]:
    """Allocate globally ordered, pairwise-disjoint annular channel shells."""
    if not isinstance(edge_count, int) or isinstance(edge_count, bool):
        raise TypeError("edge_count must be an integer")
    if edge_count < 0:
        raise ValueError("edge_count must be nonnegative")
    base_inner_radius = _finite(base_inner_radius, "base_inner_radius")
    shell_width = _finite(shell_width, "shell_width")
    shell_gap = _finite(shell_gap, "shell_gap")
    if base_inner_radius <= 0 or shell_width <= 0 or shell_gap < 0:
        raise ValueError("shell geometry must be positive with nonnegative gap")

    step = shell_width + shell_gap
    return tuple(
        EdgeChannelShell(
            edge_index=index,
            inner_radius=base_inner_radius + index * step,
            outer_radius=base_inner_radius + index * step + shell_width,
        )
        for index in range(edge_count)
    )


@dataclass(frozen=True)
class SeparatedToroidalChannelBundle[NodeT: Hashable]:
    bundle: GraphToroidalFluxBundle[NodeT]
    shells: tuple[EdgeChannelShell, ...]

    def __post_init__(self) -> None:
        if len(self.bundle.channels) != len(self.shells):
            raise ValueError("every toroidal channel must have one channel shell")
        if tuple(shell.edge_index for shell in self.shells) != tuple(range(len(self.shells))):
            raise ValueError("shell edge indices must be consecutive")
        for channel, shell in zip(self.bundle.channels, self.shells, strict=True):
            if channel.edge_index != shell.edge_index:
                raise ValueError("channel and shell indices must match")
            field = channel.field
            if not math.isclose(
                field.major_radius - field.minor_radius,
                shell.inner_radius,
                abs_tol=_TOLERANCE,
            ):
                raise ValueError("toroidal cut inner radius must equal the shell inner radius")
            if not math.isclose(field.major_radius, shell.outer_radius, abs_tol=_TOLERANCE):
                raise ValueError("toroidal cut outer radius must equal the shell outer radius")

    @property
    def edges(self):
        return self.bundle.edges


def map_graph_currents_to_separated_tori[NodeT: Hashable](
    currents: Sequence[DirectedCurrent[NodeT]],
    *,
    base_inner_radius: float = 2.0,
    shell_width: float = 0.4,
    shell_gap: float = 0.25,
    axial_gap: float = 0.2,
    center_z: float = 0.0,
) -> SeparatedToroidalChannelBundle[NodeT]:
    """Map graph currents to edge-specific toroidal cut annuli."""
    ordered = tuple(currents)
    shells = allocate_edge_channel_shells(
        len(ordered),
        base_inner_radius=base_inner_radius,
        shell_width=shell_width,
        shell_gap=shell_gap,
    )
    axial_gap = _finite(axial_gap, "axial_gap")
    center_z = _finite(center_z, "center_z")
    if axial_gap < 0:
        raise ValueError("axial_gap must be nonnegative")

    spacing = 2.0 * shell_width + axial_gap
    midpoint = (len(ordered) - 1) / 2.0
    channels = tuple(
        ToroidalChannelVolume(
            edge_index=index,
            edge=edge,
            center_z=center_z + (index - midpoint) * spacing,
            major_radius=shell.outer_radius,
            minor_radius=shell.width,
        )
        for index, (edge, shell) in enumerate(zip(ordered, shells, strict=True))
    )
    bundle = GraphToroidalFluxBundle(channels=channels, gap=axial_gap)
    return SeparatedToroidalChannelBundle(bundle=bundle, shells=shells)


@dataclass(frozen=True)
class SeparatedFramedEdgeNetwork[NodeT: Hashable]:
    separated_bundle: SeparatedToroidalChannelBundle[NodeT]
    junction_network: AnnularJunctionNetwork[NodeT]
    framed_network: FramedToroidalEdgeNetwork[NodeT]

    def minimum_terminal_shell_gap(self) -> float:
        shells = self.separated_bundle.shells
        return min(
            (
                right.inner_radius - left.outer_radius
                for left, right in zip(shells, shells[1:])
            ),
            default=math.inf,
        )


def build_separated_framed_edge_network[NodeT: Hashable](
    currents: Sequence[DirectedCurrent[NodeT]],
    nodes: Sequence[NodeT],
    *,
    base_inner_radius: float = 2.0,
    shell_width: float = 0.4,
    shell_gap: float = 0.25,
    axial_gap: float = 0.2,
    junction_length: float = 1.0,
    junction_inner_radius: float = 0.5,
    junction_outer_radius: float = 1.5,
    junction_gap: float = 0.25,
    connector_length: float = 1.0,
    channel_length: float = 1.0,
) -> SeparatedFramedEdgeNetwork[NodeT]:
    separated = map_graph_currents_to_separated_tori(
        currents,
        base_inner_radius=base_inner_radius,
        shell_width=shell_width,
        shell_gap=shell_gap,
        axial_gap=axial_gap,
    )
    junctions = connect_bundle_to_annular_junctions(
        separated.bundle,
        nodes,
        length=junction_length,
        inner_radius=junction_inner_radius,
        outer_radius=junction_outer_radius,
        junction_gap=junction_gap,
    )
    framed = build_framed_edge_network(
        junctions,
        connector_length=connector_length,
        channel_length=channel_length,
    )
    return SeparatedFramedEdgeNetwork(
        separated_bundle=separated,
        junction_network=junctions,
        framed_network=framed,
    )


def _outward_interval(
    assembly: FramedToroidalEdgeAssembly,
    node,
    progress: float,
) -> tuple[float, float]:
    progress = _finite(progress, "progress")
    if not 0.0 <= progress <= 1.0:
        raise ValueError("progress must lie in [0, 1]")
    if node == assembly.edge.source:
        transition = assembly.inlet
        s = progress
    elif node == assembly.edge.target:
        transition = assembly.outlet
        s = 1.0 - progress
    else:
        raise ValueError("node must be one edge endpoint")
    return transition.radius(s, 0.0), transition.radius(s, 1.0)


def minimum_same_face_connector_gap[NodeT: Hashable](
    framed_network: FramedToroidalEdgeNetwork[NodeT],
    *,
    samples: int = 101,
) -> float:
    """Return the minimum radial gap among same-face nonzero connectors."""
    if not isinstance(samples, int) or isinstance(samples, bool) or samples < 2:
        raise ValueError("samples must be an integer at least two")
    assemblies = {assembly.edge_index: assembly for assembly in framed_network.assemblies}
    gaps = []

    for junction in framed_network.junction_network.junctions:
        for face in (AnnularPortFace.LOWER, AnnularPortFace.UPPER):
            edge_indices = [
                port.edge_index
                for port in junction.ports
                if port.face is face and abs(assemblies[port.edge_index].edge.current) > _TOLERANCE
            ]
            edge_indices.sort()
            for left_index, right_index in zip(edge_indices, edge_indices[1:]):
                left = assemblies[left_index]
                right = assemblies[right_index]
                for sample in range(samples):
                    progress = sample / (samples - 1)
                    _, left_outer = _outward_interval(left, junction.node, progress)
                    right_inner, _ = _outward_interval(right, junction.node, progress)
                    gaps.append(right_inner - left_outer)
    return min(gaps, default=math.inf)


def maximum_same_face_connector_overlap[NodeT: Hashable](
    framed_network: FramedToroidalEdgeNetwork[NodeT],
    *,
    samples: int = 101,
) -> float:
    gap = minimum_same_face_connector_gap(framed_network, samples=samples)
    if math.isinf(gap):
        return 0.0
    return max(0.0, -gap)
