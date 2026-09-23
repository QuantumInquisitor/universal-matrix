"""Explicit graph-to-volume coupling for conservative current channels.

Each directed graph edge is assigned one disjoint translated solid-ring torus.
The edge's signed current is used as the torus's signed poloidal cut flux.
Translation preserves the divergence-free field construction, and disjoint
supports make the summed three-dimensional current divergence-free wherever
the individual fields are.

The source/target incidence of the graph is retained independently from the
spatial placement of the tubes. This module therefore preserves channel flux
and graph divergence exactly, but it does not yet claim that graph nodes are
physical three-dimensional junctions.
"""

from __future__ import annotations

import math
from collections.abc import Hashable, Sequence
from dataclasses import dataclass
from .conservative_toroidal_field import ToroidalContentCurrent
from .vesica_tree_circulation import DirectedCurrent, graph_divergence

Point3D = tuple[float, float, float]


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


@dataclass(frozen=True)
class ToroidalChannelVolume[NodeT: Hashable]:
    """One graph edge represented by one translated toroidal flux domain."""

    edge_index: int
    edge: DirectedCurrent[NodeT]
    center_z: float
    major_radius: float
    minor_radius: float

    def __post_init__(self) -> None:
        if not isinstance(self.edge_index, int) or isinstance(self.edge_index, bool):
            raise TypeError("edge_index must be an integer")
        if self.edge_index < 0:
            raise ValueError("edge_index must be nonnegative")
        object.__setattr__(self, "center_z", _finite(self.center_z, "center_z"))
        object.__setattr__(self, "major_radius", _finite(self.major_radius, "major_radius"))
        object.__setattr__(self, "minor_radius", _finite(self.minor_radius, "minor_radius"))
        ToroidalContentCurrent(
            major_radius=self.major_radius,
            minor_radius=self.minor_radius,
            poloidal_flux=self.edge.current,
            toroidal_flux=0.0,
        )

    @property
    def field(self) -> ToroidalContentCurrent:
        """Return the local divergence-free toroidal field for this channel."""
        return ToroidalContentCurrent(
            major_radius=self.major_radius,
            minor_radius=self.minor_radius,
            poloidal_flux=self.edge.current,
            toroidal_flux=0.0,
        )

    @property
    def oriented_cut_flux(self) -> float:
        """Return the flux in the graph edge source-to-target orientation."""
        return self.edge.current

    @property
    def axial_interval(self) -> tuple[float, float]:
        """Return the closed z interval occupied by the torus support."""
        return self.center_z - self.minor_radius, self.center_z + self.minor_radius

    def local_point(self, point: Sequence[float]) -> Point3D:
        """Translate a global point into this torus local coordinate system."""
        if len(point) != 3:
            raise ValueError("point must contain exactly three coordinates")
        x, y, z = (_finite(value, "coordinate") for value in point)
        return x, y, z - self.center_z

    def current(self, point: Sequence[float]) -> Point3D:
        """Evaluate this translated channel field in global Cartesian axes."""
        return self.field.current(self.local_point(point))

    def stream_function(self, point: Sequence[float]) -> float:
        """Evaluate the translated poloidal stream function."""
        return self.field.stream_function(self.local_point(point))

    def contains_domain_point(self, point: Sequence[float]) -> bool:
        """Return whether a point lies inside the assigned solid torus domain."""
        x, y, z = self.local_point(point)
        rho = math.hypot(x, y)
        return (rho - self.major_radius) ** 2 + z**2 < self.minor_radius**2


@dataclass(frozen=True)
class GraphToroidalFluxBundle[NodeT: Hashable]:
    """A one-to-one map from graph current edges to disjoint toroidal volumes."""

    channels: tuple[ToroidalChannelVolume[NodeT], ...]
    gap: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "gap", _finite(self.gap, "gap"))
        if self.gap < 0:
            raise ValueError("gap must be nonnegative")
        if tuple(channel.edge_index for channel in self.channels) != tuple(range(len(self.channels))):
            raise ValueError("channel edge indices must be consecutive from zero")
        if not self.supports_are_disjoint():
            raise ValueError("toroidal channel supports must be disjoint")

    @property
    def edges(self) -> tuple[DirectedCurrent[NodeT], ...]:
        return tuple(channel.edge for channel in self.channels)

    def supports_are_disjoint(self) -> bool:
        """Check pairwise disjointness using the exact axial support intervals."""
        ordered = sorted(self.channels, key=lambda channel: channel.center_z)
        return all(
            left.axial_interval[1] <= right.axial_interval[0]
            for left, right in zip(ordered, ordered[1:])
        )

    def active_domain_count(self, point: Sequence[float]) -> int:
        """Count assigned toroidal domains containing the supplied point."""
        return sum(channel.contains_domain_point(point) for channel in self.channels)

    def current(self, point: Sequence[float]) -> Point3D:
        """Return the sum of all translated channel currents."""
        values = [channel.current(point) for channel in self.channels]
        return tuple(math.fsum(value[axis] for value in values) for axis in range(3))

    def oriented_channel_fluxes(self) -> tuple[float, ...]:
        """Return every mapped cut flux in original graph-edge order."""
        return tuple(channel.oriented_cut_flux for channel in self.channels)

    def node_flux_divergence(self, nodes: Sequence[NodeT]) -> dict[NodeT, float]:
        """Recover graph divergence from the mapped channel flux ledger."""
        return graph_divergence(nodes, self.edges)

    def maximum_overlap_count(self) -> int:
        """Return the maximum number of support intervals overlapping in z."""
        if not self.channels:
            return 0
        events = []
        for channel in self.channels:
            lower, upper = channel.axial_interval
            events.append((lower, 1))
            events.append((upper, -1))
        events.sort(key=lambda item: (item[0], item[1]))
        active = maximum = 0
        for _, change in events:
            active += change
            maximum = max(maximum, active)
        return maximum


def map_graph_currents_to_tori[NodeT: Hashable](
    currents: Sequence[DirectedCurrent[NodeT]],
    *,
    major_radius: float = 2.0,
    minor_radius: float = 0.4,
    gap: float = 0.2,
    center_z: float = 0.0,
) -> GraphToroidalFluxBundle[NodeT]:
    """Assign every graph edge a deterministic, disjoint toroidal flux volume.

    All tori share one major/minor radius and are translated only along z.
    Neighboring centers are separated by 2*minor_radius + gap. The bundle is
    centered around center_z as a whole.

    The canonical local cut orientation is declared to represent the graph
    edge source-to-target orientation. Therefore a negative graph current
    becomes a negative measured poloidal flux without changing the graph edge.
    """
    major_radius = _finite(major_radius, "major_radius")
    minor_radius = _finite(minor_radius, "minor_radius")
    gap = _finite(gap, "gap")
    center_z = _finite(center_z, "center_z")
    if gap < 0:
        raise ValueError("gap must be nonnegative")
    ToroidalContentCurrent(
        major_radius=major_radius,
        minor_radius=minor_radius,
        poloidal_flux=0.0,
        toroidal_flux=0.0,
    )

    ordered = tuple(currents)
    spacing = 2 * minor_radius + gap
    midpoint = (len(ordered) - 1) / 2
    channels = tuple(
        ToroidalChannelVolume(
            edge_index=index,
            edge=edge,
            center_z=center_z + (index - midpoint) * spacing,
            major_radius=major_radius,
            minor_radius=minor_radius,
        )
        for index, edge in enumerate(ordered)
    )
    return GraphToroidalFluxBundle(channels=channels, gap=gap)


def flux_mapping_residual[NodeT: Hashable](bundle: GraphToroidalFluxBundle[NodeT]) -> float:
    """Return the largest difference between graph current and mapped cut flux."""
    return max(
        (
            abs(channel.edge.current - channel.oriented_cut_flux)
            for channel in bundle.channels
        ),
        default=0.0,
    )
