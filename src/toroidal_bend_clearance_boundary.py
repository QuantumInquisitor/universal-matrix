"""Sampled collision/no-collision frontier for toroidal bend spacing.

This module consumes the finite Vesica spacing scan without changing the graph,
fluxes, junctions, Piola connectors, or bend maps. It summarizes the first
collision-free sampled shell gap at each tested bend margin.

The frontier is a property of the tested finite grid and sampling resolution.
It is not a continuous clearance theorem or a physical scale law.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass

from .toroidal_bend_spacing_scan import (
    BendSpacingResult,
    scan_vesica_bend_spacing,
)


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _strict_axis(values: Iterable[float], name: str, *, positive: bool) -> tuple[float, ...]:
    axis = tuple(_finite(value, name) for value in values)
    if not axis:
        raise ValueError(f"{name} must be nonempty")
    if positive:
        if any(value <= 0.0 for value in axis):
            raise ValueError(f"{name} must be positive")
    elif any(value < 0.0 for value in axis):
        raise ValueError(f"{name} must be nonnegative")
    if len(set(axis)) != len(axis):
        raise ValueError(f"{name} must not contain duplicates")
    return tuple(sorted(axis))


@dataclass(frozen=True)
class ClearanceFrontierPoint:
    bend_margin: float
    minimum_collision_free_gap: float
    lower_colliding_gap: float | None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "bend_margin",
            _finite(self.bend_margin, "bend_margin"),
        )
        object.__setattr__(
            self,
            "minimum_collision_free_gap",
            _finite(
                self.minimum_collision_free_gap,
                "minimum_collision_free_gap",
            ),
        )
        if self.bend_margin <= 0.0:
            raise ValueError("bend_margin must be positive")
        if self.minimum_collision_free_gap < 0.0:
            raise ValueError("minimum_collision_free_gap must be nonnegative")
        if self.lower_colliding_gap is not None:
            lower = _finite(self.lower_colliding_gap, "lower_colliding_gap")
            if lower < 0.0:
                raise ValueError("lower_colliding_gap must be nonnegative")
            if lower >= self.minimum_collision_free_gap:
                raise ValueError(
                    "lower_colliding_gap must be below minimum_collision_free_gap"
                )
            object.__setattr__(self, "lower_colliding_gap", lower)


@dataclass(frozen=True)
class ClearanceBoundaryAudit:
    shell_gaps: tuple[float, ...]
    bend_margins: tuple[float, ...]
    results: tuple[BendSpacingResult, ...]
    frontier: tuple[ClearanceFrontierPoint, ...]
    unresolved_margins: tuple[float, ...]

    @property
    def sample_count(self) -> int:
        return len(self.results)

    @property
    def collision_free_count(self) -> int:
        return sum(result.collision_free for result in self.results)

    @property
    def collision_count(self) -> int:
        return self.sample_count - self.collision_free_count

    @property
    def mixed_outcome(self) -> bool:
        return self.collision_count > 0 and self.collision_free_count > 0


def sampled_clearance_frontier(
    results: Iterable[BendSpacingResult],
) -> tuple[tuple[ClearanceFrontierPoint, ...], tuple[float, ...]]:
    """Return the first sampled collision-free gap for each bend margin."""
    values = tuple(results)
    if not values:
        raise ValueError("results must be nonempty")

    by_margin: dict[float, list[BendSpacingResult]] = {}
    seen: set[tuple[float, float]] = set()
    for result in values:
        key = (result.shell_gap, result.bend_margin)
        if key in seen:
            raise ValueError("duplicate shell-gap/bend-margin sample")
        seen.add(key)
        by_margin.setdefault(result.bend_margin, []).append(result)

    frontier: list[ClearanceFrontierPoint] = []
    unresolved: list[float] = []
    for bend_margin in sorted(by_margin):
        row = sorted(by_margin[bend_margin], key=lambda item: item.shell_gap)
        first_free = next((item for item in row if item.collision_free), None)
        if first_free is None:
            unresolved.append(bend_margin)
            continue
        lower_colliding = [
            item.shell_gap
            for item in row
            if item.shell_gap < first_free.shell_gap and not item.collision_free
        ]
        frontier.append(
            ClearanceFrontierPoint(
                bend_margin=bend_margin,
                minimum_collision_free_gap=first_free.shell_gap,
                lower_colliding_gap=max(lower_colliding) if lower_colliding else None,
            )
        )

    return tuple(frontier), tuple(unresolved)


def audit_vesica_clearance_boundary(
    *,
    shell_gaps: Iterable[float] = (0.25, 1.0, 3.0, 10.0, 30.0),
    bend_margins: Iterable[float] = (0.005, 0.02, 0.05, 0.1, 0.25),
    current: float = 1.0,
    shell_width: float = 0.4,
    base_inner_radius: float = 2.0,
    phi_samples: int = 13,
    q_samples: int = 5,
    theta_samples: int = 24,
) -> ClearanceBoundaryAudit:
    """Audit the sampled Vesica clearance frontier on a deterministic grid."""
    gaps = _strict_axis(shell_gaps, "shell_gaps", positive=False)
    margins = _strict_axis(bend_margins, "bend_margins", positive=True)
    results = scan_vesica_bend_spacing(
        gaps,
        margins,
        current=current,
        shell_width=shell_width,
        base_inner_radius=base_inner_radius,
        phi_samples=phi_samples,
        q_samples=q_samples,
        theta_samples=theta_samples,
    )
    frontier, unresolved = sampled_clearance_frontier(results)
    return ClearanceBoundaryAudit(
        shell_gaps=gaps,
        bend_margins=margins,
        results=results,
        frontier=frontier,
        unresolved_margins=unresolved,
    )


def format_clearance_boundary_report(audit: ClearanceBoundaryAudit) -> str:
    grids = dict.fromkeys(result.sampling for result in audit.results)
    lines = [
        "TOROIDAL BEND CLEARANCE BOUNDARY",
        "evidence=finite_sampling_only; collision_free_means_no_collision_detected",
        "sampling=" + ";".join(grid.description if grid else "unspecified" for grid in grids),
        f"sample_count={audit.sample_count}",
        f"collision_count={audit.collision_count}",
        f"collision_free_count={audit.collision_free_count}",
        f"mixed_outcome={audit.mixed_outcome}",
    ]
    for point in audit.frontier:
        lines.append(
            "frontier="
            f"margin:{point.bend_margin:g},"
            f"first_free_gap:{point.minimum_collision_free_gap:g},"
            f"lower_colliding_gap:{point.lower_colliding_gap}"
        )
    if audit.unresolved_margins:
        lines.append(
            "unresolved_margins="
            + ",".join(f"{margin:g}" for margin in audit.unresolved_margins)
        )
    return "\n".join(lines)


def main() -> None:
    print(format_clearance_boundary_report(audit_vesica_clearance_boundary()))


if __name__ == "__main__":
    main()
