"""Audit geometric dependence on zero-current latent Tree pathways.

The Flower-derived Tree keeps same-ring weave edges in the declared topology
even when weave_current == 0. The separated toroidal geometry currently
allocates channel shells and annular junction ports for every declared edge,
including those zero-current paths.

This module compares two representations of the same Tree circulation:

1. full topology: zero-current weave pathways remain present geometrically;
2. active-only topology: only nonzero-current directed edges are built.

The audit measures the geometric difference without deciding which semantics is
correct. A persistent living geometry may intentionally retain dormant
pathways; a current-support geometry may instead want them absent or contracted.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .toroidal_separated_channels import build_separated_framed_edge_network
from .vesica_tree_circulation import DirectedCurrent, tree_circulation

_TOLERANCE = 1e-12


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _active_edges(edges: tuple[DirectedCurrent, ...]) -> tuple[DirectedCurrent, ...]:
    return tuple(edge for edge in edges if abs(edge.current) > _TOLERANCE)


@dataclass(frozen=True)
class LatentPathGeometryAudit:
    rings: int
    full_edge_count: int
    active_edge_count: int
    latent_edge_count: int
    latent_port_count: int
    minimum_center_shift: float
    maximum_center_shift: float
    maximum_major_radius_residual: float
    minimum_active_port_width_ratio: float
    maximum_active_port_width_difference: float

    def __post_init__(self) -> None:
        if (
            not isinstance(self.rings, int)
            or isinstance(self.rings, bool)
            or self.rings < 1
        ):
            raise ValueError("rings must be a positive integer")
        for name in (
            "full_edge_count",
            "active_edge_count",
            "latent_edge_count",
            "latent_port_count",
        ):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer")
        for name in (
            "minimum_center_shift",
            "maximum_center_shift",
            "maximum_major_radius_residual",
            "minimum_active_port_width_ratio",
            "maximum_active_port_width_difference",
        ):
            object.__setattr__(self, name, _finite(getattr(self, name), name))
        if self.full_edge_count != self.active_edge_count + self.latent_edge_count:
            raise ValueError("edge counts must partition into active and latent")
        if self.maximum_major_radius_residual < 0.0:
            raise ValueError("maximum_major_radius_residual must be nonnegative")
        if self.minimum_active_port_width_ratio <= 0.0:
            raise ValueError("minimum_active_port_width_ratio must be positive")
        if self.maximum_active_port_width_difference < 0.0:
            raise ValueError("maximum_active_port_width_difference must be nonnegative")

    @property
    def center_shift_is_uniform(self) -> bool:
        return math.isclose(
            self.minimum_center_shift,
            self.maximum_center_shift,
            rel_tol=0.0,
            abs_tol=1e-12,
        )

    @property
    def active_port_geometry_changes(self) -> bool:
        return (
            self.minimum_active_port_width_ratio < 1.0 - 1e-12
            or self.maximum_active_port_width_difference > 1e-12
        )


def audit_tree_latent_path_geometry(
    rings: int = 2,
    *,
    radial_current: float = 1.0,
    shell_gap: float = 0.25,
    shell_width: float = 0.4,
    base_inner_radius: float = 2.0,
    axial_gap: float = 0.2,
) -> LatentPathGeometryAudit:
    """Compare full latent-path geometry with active-current-only geometry."""
    if (
        not isinstance(rings, int)
        or isinstance(rings, bool)
        or rings < 1
    ):
        raise ValueError("rings must be a positive integer")
    radial_current = _finite(radial_current, "radial_current")
    if abs(radial_current) <= _TOLERANCE:
        raise ValueError("radial_current must be nonzero")
    shell_gap = _finite(shell_gap, "shell_gap")
    shell_width = _finite(shell_width, "shell_width")
    base_inner_radius = _finite(base_inner_radius, "base_inner_radius")
    axial_gap = _finite(axial_gap, "axial_gap")

    circulation = tree_circulation(
        rings,
        radial_current=radial_current,
        weave_current=0.0,
    )
    full_edges = circulation.edges
    active_edges = _active_edges(full_edges)
    nodes = circulation.geometry.nodes

    full = build_separated_framed_edge_network(
        full_edges,
        nodes,
        shell_gap=shell_gap,
        shell_width=shell_width,
        base_inner_radius=base_inner_radius,
        axial_gap=axial_gap,
    )
    active = build_separated_framed_edge_network(
        active_edges,
        nodes,
        shell_gap=shell_gap,
        shell_width=shell_width,
        base_inner_radius=base_inner_radius,
        axial_gap=axial_gap,
    )

    full_channels = {
        channel.edge: channel
        for channel in full.separated_bundle.bundle.channels
    }
    active_channels = {
        channel.edge: channel
        for channel in active.separated_bundle.bundle.channels
    }
    if set(active_channels) != set(active_edges):
        raise RuntimeError("active-only channel map does not match active edges")
    if not set(active_channels) <= set(full_channels):
        raise RuntimeError("full topology lost an active channel")

    center_shifts = []
    radius_residuals = []
    width_ratios = []
    width_differences = []

    for edge, active_channel in active_channels.items():
        full_channel = full_channels[edge]
        center_shifts.append(
            full_channel.center_z - active_channel.center_z
        )
        radius_residuals.append(
            abs(full_channel.major_radius - active_channel.major_radius)
        )

        for node in (edge.source, edge.target):
            full_port = full.junction_network.junction(node).port_by_edge(
                full_channel.edge_index
            )
            active_port = active.junction_network.junction(node).port_by_edge(
                active_channel.edge_index
            )
            width_ratios.append(full_port.width / active_port.width)
            width_differences.append(abs(full_port.width - active_port.width))

    current_by_index = {
        channel.edge_index: channel.edge.current
        for channel in full.separated_bundle.bundle.channels
    }
    latent_port_count = sum(
        1
        for junction in full.junction_network.junctions
        for port in junction.ports
        if abs(current_by_index[port.edge_index]) <= _TOLERANCE
    )

    return LatentPathGeometryAudit(
        rings=rings,
        full_edge_count=len(full_edges),
        active_edge_count=len(active_edges),
        latent_edge_count=len(full_edges) - len(active_edges),
        latent_port_count=latent_port_count,
        minimum_center_shift=min(center_shifts, default=0.0),
        maximum_center_shift=max(center_shifts, default=0.0),
        maximum_major_radius_residual=max(radius_residuals, default=0.0),
        minimum_active_port_width_ratio=min(width_ratios, default=1.0),
        maximum_active_port_width_difference=max(width_differences, default=0.0),
    )


def format_latent_path_report(
    audits: tuple[LatentPathGeometryAudit, ...],
) -> str:
    lines = ["TOROIDAL LATENT PATH GEOMETRY AUDIT"]
    for audit in audits:
        lines.append(
            "rings="
            f"{audit.rings},"
            f"full_edges:{audit.full_edge_count},"
            f"active_edges:{audit.active_edge_count},"
            f"latent_edges:{audit.latent_edge_count},"
            f"latent_ports:{audit.latent_port_count},"
            f"center_shift:[{audit.minimum_center_shift:.12g},"
            f"{audit.maximum_center_shift:.12g}],"
            f"major_radius_residual:{audit.maximum_major_radius_residual:.12g},"
            f"min_active_port_width_ratio:{audit.minimum_active_port_width_ratio:.12g},"
            f"max_active_port_width_difference:{audit.maximum_active_port_width_difference:.12g}"
        )
    return "\n".join(lines)


def main() -> None:
    audits = tuple(audit_tree_latent_path_geometry(rings) for rings in (1, 2, 3))
    print(format_latent_path_report(audits))


if __name__ == "__main__":
    main()
