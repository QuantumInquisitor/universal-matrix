"""Uniform geometric-scale covariance audit for toroidal bend clearance.

The existing bend-clearance scan varies shell gap and bend margin while other
lengths remain fixed.  This module asks a different, stricter question: if the
*entire* geometric construction is enlarged or reduced by one positive
similarity factor, does the numerical collision classification remain
unchanged and does dimensional penetration scale linearly?

This is a geometric similarity audit.  It does not establish a physical scale
law, recursive dynamics, or Flower/Tree scale invariance.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .toroidal_incident_bend_audit import audit_incident_bend_collisions
from .toroidal_separated_channels import build_separated_framed_edge_network
from .vesica_tree_circulation import PORT_NODES, vesica_circulation


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


@dataclass(frozen=True)
class ToroidalGeometryLengths:
    """Reference length set for the separated-shell routed geometry."""

    base_inner_radius: float = 2.0
    shell_width: float = 0.4
    axial_gap: float = 0.2
    junction_length: float = 1.0
    junction_inner_radius: float = 0.5
    junction_outer_radius: float = 1.5
    junction_gap: float = 0.25
    connector_length: float = 1.0
    channel_length: float = 1.0
    node_gap: float = 1.0
    edge_gap: float = 0.5

    def __post_init__(self) -> None:
        positive = (
            "base_inner_radius",
            "shell_width",
            "junction_length",
            "junction_inner_radius",
            "junction_outer_radius",
            "connector_length",
            "channel_length",
        )
        nonnegative = ("axial_gap", "junction_gap", "node_gap", "edge_gap")
        for name in positive:
            value = _finite(getattr(self, name), name)
            if value <= 0.0:
                raise ValueError(f"{name} must be positive")
            object.__setattr__(self, name, value)
        for name in nonnegative:
            value = _finite(getattr(self, name), name)
            if value < 0.0:
                raise ValueError(f"{name} must be nonnegative")
            object.__setattr__(self, name, value)
        if self.junction_outer_radius <= self.junction_inner_radius:
            raise ValueError(
                "junction_outer_radius must exceed junction_inner_radius"
            )

    def scaled(self, factor: float) -> "ToroidalGeometryLengths":
        factor = _finite(factor, "factor")
        if factor <= 0.0:
            raise ValueError("factor must be positive")
        return ToroidalGeometryLengths(
            base_inner_radius=self.base_inner_radius * factor,
            shell_width=self.shell_width * factor,
            axial_gap=self.axial_gap * factor,
            junction_length=self.junction_length * factor,
            junction_inner_radius=self.junction_inner_radius * factor,
            junction_outer_radius=self.junction_outer_radius * factor,
            junction_gap=self.junction_gap * factor,
            connector_length=self.connector_length * factor,
            channel_length=self.channel_length * factor,
            node_gap=self.node_gap * factor,
            edge_gap=self.edge_gap * factor,
        )


@dataclass(frozen=True)
class SimilarityClearanceResult:
    scale_factor: float
    reference_shell_gap: float
    reference_bend_margin: float
    collision_count: int
    maximum_penetration: float

    def __post_init__(self) -> None:
        for name in (
            "scale_factor",
            "reference_shell_gap",
            "reference_bend_margin",
            "maximum_penetration",
        ):
            object.__setattr__(self, name, _finite(getattr(self, name), name))
        if self.scale_factor <= 0.0:
            raise ValueError("scale_factor must be positive")
        if self.reference_shell_gap < 0.0:
            raise ValueError("reference_shell_gap must be nonnegative")
        if self.reference_bend_margin <= 0.0:
            raise ValueError("reference_bend_margin must be positive")
        if self.collision_count < 0:
            raise ValueError("collision_count must be nonnegative")
        if self.maximum_penetration < 0.0:
            raise ValueError("maximum_penetration must be nonnegative")

    @property
    def collision_free(self) -> bool:
        return self.collision_count == 0

    @property
    def scaled_shell_gap(self) -> float:
        return self.reference_shell_gap * self.scale_factor

    @property
    def scaled_bend_margin(self) -> float:
        return self.reference_bend_margin * self.scale_factor

    @property
    def normalized_penetration(self) -> float:
        return self.maximum_penetration / self.scale_factor


def evaluate_vesica_similarity_clearance(
    reference_shell_gap: float,
    reference_bend_margin: float,
    scale_factor: float,
    *,
    current: float = 1.0,
    geometry: ToroidalGeometryLengths = ToroidalGeometryLengths(),
    phi_samples: int = 13,
    q_samples: int = 5,
    theta_samples: int = 24,
) -> SimilarityClearanceResult:
    """Evaluate one uniformly scaled Vesica clearance case."""
    reference_shell_gap = _finite(reference_shell_gap, "reference_shell_gap")
    reference_bend_margin = _finite(
        reference_bend_margin,
        "reference_bend_margin",
    )
    scale_factor = _finite(scale_factor, "scale_factor")
    current = _finite(current, "current")
    if reference_shell_gap < 0.0:
        raise ValueError("reference_shell_gap must be nonnegative")
    if reference_bend_margin <= 0.0:
        raise ValueError("reference_bend_margin must be positive")
    if scale_factor <= 0.0:
        raise ValueError("scale_factor must be positive")

    scaled = geometry.scaled(scale_factor)
    circulation = vesica_circulation(current, return_split=0.4)
    network = build_separated_framed_edge_network(
        circulation.edges,
        PORT_NODES,
        base_inner_radius=scaled.base_inner_radius,
        shell_width=scaled.shell_width,
        shell_gap=reference_shell_gap * scale_factor,
        axial_gap=scaled.axial_gap,
        junction_length=scaled.junction_length,
        junction_inner_radius=scaled.junction_inner_radius,
        junction_outer_radius=scaled.junction_outer_radius,
        junction_gap=scaled.junction_gap,
        connector_length=scaled.connector_length,
        channel_length=scaled.channel_length,
    )
    audit = audit_incident_bend_collisions(
        network,
        bend_margin=reference_bend_margin * scale_factor,
        node_gap=scaled.node_gap,
        edge_gap=scaled.edge_gap,
        phi_samples=phi_samples,
        q_samples=q_samples,
        theta_samples=theta_samples,
    )
    return SimilarityClearanceResult(
        scale_factor=scale_factor,
        reference_shell_gap=reference_shell_gap,
        reference_bend_margin=reference_bend_margin,
        collision_count=audit.collision_count,
        maximum_penetration=audit.maximum_penetration,
    )


def similarity_family(
    reference_shell_gap: float,
    reference_bend_margin: float,
    scale_factors: tuple[float, ...] = (0.5, 1.0, 2.0),
    **kwargs,
) -> tuple[SimilarityClearanceResult, ...]:
    if not scale_factors:
        raise ValueError("scale_factors must be nonempty")
    return tuple(
        evaluate_vesica_similarity_clearance(
            reference_shell_gap,
            reference_bend_margin,
            scale_factor,
            **kwargs,
        )
        for scale_factor in scale_factors
    )


def format_similarity_report(
    families: tuple[tuple[SimilarityClearanceResult, ...], ...],
) -> str:
    lines = ["TOROIDAL UNIFORM SCALE SIMILARITY"]
    for family in families:
        if not family:
            continue
        reference = family[0]
        lines.append(
            "case="
            f"gap:{reference.reference_shell_gap:g},"
            f"margin:{reference.reference_bend_margin:g}"
        )
        for result in family:
            lines.append(
                "scale="
                f"{result.scale_factor:g},"
                f"collision_count:{result.collision_count},"
                f"penetration:{result.maximum_penetration:.12g},"
                f"normalized_penetration:{result.normalized_penetration:.12g}"
            )
    return "\n".join(lines)


def main() -> None:
    cases = (
        (2.5, 0.05),
        (3.0, 0.05),
        (6.5, 0.005),
        (8.25, 0.005),
    )
    families = tuple(
        similarity_family(gap, margin)
        for gap, margin in cases
    )
    print(format_similarity_report(families))


if __name__ == "__main__":
    main()
