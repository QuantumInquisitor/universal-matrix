"""Parameter scan for incident bend clearance in separated toroidal shells.

The incident-bend audit established collisions for the first tested separated-
shell geometry.  This module asks a narrower question before any junction
redesign: can the same graph, fluxes, annular Piola connectors, and smooth bend
maps become incident-collision-free by changing only shell gaps and bend
curvature?

The scan is geometric and dimensionless. Zero detected collisions on a finite
grid do not establish continuous clearance or a physical scale law.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass

from .toroidal_incident_bend_audit import BendSamplingGrid, audit_incident_bend_collisions
from .toroidal_separated_channels import build_separated_framed_edge_network
from .vesica_tree_circulation import PORT_NODES, vesica_circulation


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


@dataclass(frozen=True)
class BendSpacingResult:
    shell_gap: float
    bend_margin: float
    collision_count: int
    maximum_penetration: float
    sampling: BendSamplingGrid | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "shell_gap", _finite(self.shell_gap, "shell_gap"))
        object.__setattr__(self, "bend_margin", _finite(self.bend_margin, "bend_margin"))
        object.__setattr__(
            self,
            "maximum_penetration",
            _finite(self.maximum_penetration, "maximum_penetration"),
        )
        if self.shell_gap < 0:
            raise ValueError("shell_gap must be nonnegative")
        if self.bend_margin <= 0:
            raise ValueError("bend_margin must be positive")
        if self.collision_count < 0:
            raise ValueError("collision_count must be nonnegative")
        if self.maximum_penetration < 0:
            raise ValueError("maximum_penetration must be nonnegative")

    @property
    def collision_free(self) -> bool:
        """Compatibility name: no collision was detected on this finite grid."""
        return self.collision_count == 0


def evaluate_vesica_bend_spacing(
    shell_gap: float,
    bend_margin: float,
    *,
    current: float = 1.0,
    shell_width: float = 0.4,
    base_inner_radius: float = 2.0,
    phi_samples: int = 17,
    q_samples: int = 7,
    theta_samples: int = 32,
    phi_offset: float = 0.0,
    q_offset: float = 0.0,
    theta_offset: float = 0.0,
) -> BendSpacingResult:
    """Evaluate one Vesica separated-shell/bend parameter point."""
    shell_gap = _finite(shell_gap, "shell_gap")
    bend_margin = _finite(bend_margin, "bend_margin")
    current = _finite(current, "current")
    shell_width = _finite(shell_width, "shell_width")
    base_inner_radius = _finite(base_inner_radius, "base_inner_radius")
    if shell_gap < 0:
        raise ValueError("shell_gap must be nonnegative")
    if bend_margin <= 0:
        raise ValueError("bend_margin must be positive")
    if shell_width <= 0 or base_inner_radius <= 0:
        raise ValueError("shell geometry must be positive")

    circulation = vesica_circulation(current, return_split=0.4)
    separated = build_separated_framed_edge_network(
        circulation.edges,
        PORT_NODES,
        base_inner_radius=base_inner_radius,
        shell_width=shell_width,
        shell_gap=shell_gap,
    )
    audit = audit_incident_bend_collisions(
        separated,
        bend_margin=bend_margin,
        phi_samples=phi_samples,
        q_samples=q_samples,
        theta_samples=theta_samples,
        phi_offset=phi_offset,
        q_offset=q_offset,
        theta_offset=theta_offset,
    )
    return BendSpacingResult(
        shell_gap=shell_gap,
        bend_margin=bend_margin,
        collision_count=audit.collision_count,
        maximum_penetration=audit.maximum_penetration,
        sampling=audit.sampling,
    )


def scan_vesica_bend_spacing(
    shell_gaps: Iterable[float],
    bend_margins: Iterable[float],
    *,
    current: float = 1.0,
    shell_width: float = 0.4,
    base_inner_radius: float = 2.0,
    phi_samples: int = 13,
    q_samples: int = 5,
    theta_samples: int = 24,
) -> tuple[BendSpacingResult, ...]:
    """Evaluate a deterministic Cartesian parameter grid."""
    gaps = tuple(float(value) for value in shell_gaps)
    margins = tuple(float(value) for value in bend_margins)
    if not gaps or not margins:
        raise ValueError("scan axes must be nonempty")
    return tuple(
        evaluate_vesica_bend_spacing(
            shell_gap,
            bend_margin,
            current=current,
            shell_width=shell_width,
            base_inner_radius=base_inner_radius,
            phi_samples=phi_samples,
            q_samples=q_samples,
            theta_samples=theta_samples,
        )
        for shell_gap in gaps
        for bend_margin in margins
    )


def first_collision_free_result(
    results: Iterable[BendSpacingResult],
) -> BendSpacingResult | None:
    """Return the first collision-free parameter point in input order."""
    return next((result for result in results if result.collision_free), None)
