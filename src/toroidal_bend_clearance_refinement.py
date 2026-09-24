"""Refine sampled toroidal bend-clearance brackets without assuming monotonicity.

The coarse clearance-boundary audit identifies the first collision-free sampled
shell gap at each tested bend margin. This module samples only inside each
resolved coarse collision/free bracket and records a narrower sampled bracket.

A refined bracket remains a numerical finite-grid result. The implementation
also reports re-entrant collision behavior instead of assuming that increasing
shell gap must produce a globally monotone clearance transition.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .toroidal_bend_clearance_boundary import (
    ClearanceBoundaryAudit,
    audit_vesica_clearance_boundary,
)
from .toroidal_bend_spacing_scan import (
    BendSpacingResult,
    evaluate_vesica_bend_spacing,
)


_TOLERANCE = 1e-12


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def refinement_axis(
    lower_gap: float,
    upper_gap: float,
    *,
    subdivisions: int = 4,
) -> tuple[float, ...]:
    """Return a uniform sampled axis including both coarse bracket endpoints."""
    lower_gap = _finite(lower_gap, "lower_gap")
    upper_gap = _finite(upper_gap, "upper_gap")
    if lower_gap < 0.0:
        raise ValueError("lower_gap must be nonnegative")
    if upper_gap <= lower_gap:
        raise ValueError("upper_gap must exceed lower_gap")
    if (
        not isinstance(subdivisions, int)
        or isinstance(subdivisions, bool)
        or subdivisions < 2
    ):
        raise ValueError("subdivisions must be an integer at least two")
    width = upper_gap - lower_gap
    return tuple(
        lower_gap + width * index / subdivisions
        for index in range(subdivisions + 1)
    )


@dataclass(frozen=True)
class RefinedClearanceRow:
    bend_margin: float
    coarse_lower_colliding_gap: float
    coarse_first_free_gap: float
    results: tuple[BendSpacingResult, ...]

    def __post_init__(self) -> None:
        bend_margin = _finite(self.bend_margin, "bend_margin")
        lower = _finite(
            self.coarse_lower_colliding_gap,
            "coarse_lower_colliding_gap",
        )
        upper = _finite(self.coarse_first_free_gap, "coarse_first_free_gap")
        if bend_margin <= 0.0:
            raise ValueError("bend_margin must be positive")
        if lower < 0.0 or upper <= lower:
            raise ValueError("coarse clearance bracket must be positive and ordered")
        if len(self.results) < 3:
            raise ValueError("refined row must contain at least three samples")

        ordered = tuple(sorted(self.results, key=lambda result: result.shell_gap))
        if ordered != self.results:
            raise ValueError("refined row results must be ordered by shell gap")
        gaps = tuple(result.shell_gap for result in ordered)
        if len(set(gaps)) != len(gaps):
            raise ValueError("refined row shell gaps must be unique")
        if any(
            not math.isclose(
                result.bend_margin,
                bend_margin,
                rel_tol=0.0,
                abs_tol=_TOLERANCE,
            )
            for result in ordered
        ):
            raise ValueError("all refined row results must share bend_margin")
        if not math.isclose(
            gaps[0],
            lower,
            rel_tol=0.0,
            abs_tol=_TOLERANCE,
        ):
            raise ValueError("first refined sample must equal coarse lower gap")
        if not math.isclose(
            gaps[-1],
            upper,
            rel_tol=0.0,
            abs_tol=_TOLERANCE,
        ):
            raise ValueError("last refined sample must equal coarse free gap")
        if ordered[0].collision_free:
            raise ValueError("coarse lower endpoint must remain colliding")
        if not ordered[-1].collision_free:
            raise ValueError("coarse upper endpoint must remain collision-free")

        object.__setattr__(self, "bend_margin", bend_margin)
        object.__setattr__(self, "coarse_lower_colliding_gap", lower)
        object.__setattr__(self, "coarse_first_free_gap", upper)

    @property
    def shell_gaps(self) -> tuple[float, ...]:
        return tuple(result.shell_gap for result in self.results)

    @property
    def collision_free_mask(self) -> tuple[bool, ...]:
        return tuple(result.collision_free for result in self.results)

    @property
    def transition_count(self) -> int:
        mask = self.collision_free_mask
        return sum(left != right for left, right in zip(mask, mask[1:]))

    @property
    def reentrant_collision(self) -> bool:
        """Return True when a collision appears after a sampled free point."""
        seen_free = False
        for free in self.collision_free_mask:
            if free:
                seen_free = True
            elif seen_free:
                return True
        return False

    @property
    def first_collision_free_result(self) -> BendSpacingResult:
        return next(result for result in self.results if result.collision_free)

    @property
    def refined_lower_colliding_result(self) -> BendSpacingResult:
        first_free = self.first_collision_free_result
        candidates = tuple(
            result
            for result in self.results
            if result.shell_gap < first_free.shell_gap and not result.collision_free
        )
        if not candidates:
            raise RuntimeError("refined row lost its lower colliding sample")
        return candidates[-1]

    @property
    def refined_bracket(self) -> tuple[float, float]:
        return (
            self.refined_lower_colliding_result.shell_gap,
            self.first_collision_free_result.shell_gap,
        )

    @property
    def coarse_width(self) -> float:
        return self.coarse_first_free_gap - self.coarse_lower_colliding_gap

    @property
    def refined_width(self) -> float:
        lower, upper = self.refined_bracket
        return upper - lower


@dataclass(frozen=True)
class ClearanceRefinementAudit:
    coarse: ClearanceBoundaryAudit
    rows: tuple[RefinedClearanceRow, ...]
    left_censored_margins: tuple[float, ...]
    unresolved_margins: tuple[float, ...]
    subdivisions: int

    @property
    def refined_sample_count(self) -> int:
        return sum(len(row.results) for row in self.rows)

    @property
    def any_reentrant_collision(self) -> bool:
        return any(row.reentrant_collision for row in self.rows)


def refine_vesica_clearance_boundary(
    coarse: ClearanceBoundaryAudit | None = None,
    *,
    subdivisions: int = 4,
    current: float = 1.0,
    shell_width: float = 0.4,
    base_inner_radius: float = 2.0,
    phi_samples: int = 13,
    q_samples: int = 5,
    theta_samples: int = 24,
) -> ClearanceRefinementAudit:
    """Refine every resolved coarse collision/free bracket."""
    if (
        not isinstance(subdivisions, int)
        or isinstance(subdivisions, bool)
        or subdivisions < 2
    ):
        raise ValueError("subdivisions must be an integer at least two")
    if coarse is None:
        coarse = audit_vesica_clearance_boundary(
            current=current,
            shell_width=shell_width,
            base_inner_radius=base_inner_radius,
            phi_samples=phi_samples,
            q_samples=q_samples,
            theta_samples=theta_samples,
        )

    coarse_lookup = {
        (result.shell_gap, result.bend_margin): result
        for result in coarse.results
    }
    rows: list[RefinedClearanceRow] = []
    left_censored: list[float] = []

    for point in coarse.frontier:
        if point.lower_colliding_gap is None:
            left_censored.append(point.bend_margin)
            continue

        axis = refinement_axis(
            point.lower_colliding_gap,
            point.minimum_collision_free_gap,
            subdivisions=subdivisions,
        )
        lower_result = coarse_lookup[
            (point.lower_colliding_gap, point.bend_margin)
        ]
        upper_result = coarse_lookup[
            (point.minimum_collision_free_gap, point.bend_margin)
        ]
        interior = tuple(
            evaluate_vesica_bend_spacing(
                gap,
                point.bend_margin,
                current=current,
                shell_width=shell_width,
                base_inner_radius=base_inner_radius,
                phi_samples=phi_samples,
                q_samples=q_samples,
                theta_samples=theta_samples,
            )
            for gap in axis[1:-1]
        )
        rows.append(
            RefinedClearanceRow(
                bend_margin=point.bend_margin,
                coarse_lower_colliding_gap=point.lower_colliding_gap,
                coarse_first_free_gap=point.minimum_collision_free_gap,
                results=(lower_result, *interior, upper_result),
            )
        )

    return ClearanceRefinementAudit(
        coarse=coarse,
        rows=tuple(rows),
        left_censored_margins=tuple(left_censored),
        unresolved_margins=coarse.unresolved_margins,
        subdivisions=subdivisions,
    )


def format_clearance_refinement_report(audit: ClearanceRefinementAudit) -> str:
    lines = [
        "TOROIDAL BEND CLEARANCE REFINEMENT",
        f"coarse_sample_count={audit.coarse.sample_count}",
        f"refined_row_count={len(audit.rows)}",
        f"refined_sample_count={audit.refined_sample_count}",
        f"subdivisions={audit.subdivisions}",
        f"any_reentrant_collision={audit.any_reentrant_collision}",
    ]
    for row in audit.rows:
        lower, upper = row.refined_bracket
        lines.append(
            "row="
            f"margin:{row.bend_margin:g},"
            f"coarse:[{row.coarse_lower_colliding_gap:g},{row.coarse_first_free_gap:g}],"
            f"refined:[{lower:g},{upper:g}],"
            f"transitions:{row.transition_count},"
            f"reentrant:{row.reentrant_collision}"
        )
    if audit.left_censored_margins:
        lines.append(
            "left_censored_margins="
            + ",".join(f"{margin:g}" for margin in audit.left_censored_margins)
        )
    if audit.unresolved_margins:
        lines.append(
            "unresolved_margins="
            + ",".join(f"{margin:g}" for margin in audit.unresolved_margins)
        )
    return "\n".join(lines)


def main() -> None:
    print(format_clearance_refinement_report(refine_vesica_clearance_boundary()))


if __name__ == "__main__":
    main()
