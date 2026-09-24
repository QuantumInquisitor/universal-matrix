"""Compare incident bend collision detection across finite sampling grids.

Increasing density and shifting grid points can expose missed collisions.
Agreement across these grids is a diagnostic, never a clearance certificate.
The incident bend/straight audit does not cover every possible network pair.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass

from .toroidal_bend_spacing_scan import BendSpacingResult, evaluate_vesica_bend_spacing
from .toroidal_incident_bend_audit import BendSamplingGrid

DEFAULT_GRIDS = tuple(
    BendSamplingGrid(phi, q, theta, shift, shift, shift)
    for phi, q, theta in ((13, 5, 24), (21, 9, 48), (33, 13, 64))
    for shift in (0.0, 0.5)
)


@dataclass(frozen=True)
class SamplingReliabilityAudit:
    results: tuple[BendSpacingResult, ...]

    def __post_init__(self) -> None:
        if len(self.results) < 2:
            raise ValueError("at least two sampling results are required")
        if len({(item.shell_gap, item.bend_margin) for item in self.results}) != 1:
            raise ValueError("sampling results must describe the same geometry")
        if any(item.sampling is None for item in self.results):
            raise ValueError("sampling provenance is required")

    @property
    def collision_detected(self) -> bool:
        return any(result.collision_count > 0 for result in self.results)

    @property
    def classification_changes(self) -> bool:
        return len({result.collision_free for result in self.results}) > 1

    @property
    def maximum_sampled_penetration(self) -> float:
        return max(result.maximum_penetration for result in self.results)


def audit_vesica_sampling_reliability(
    shell_gap: float,
    bend_margin: float,
    *,
    grids: Iterable[BendSamplingGrid] = DEFAULT_GRIDS,
    current: float = 1.0,
) -> SamplingReliabilityAudit:
    """Hold geometry fixed and vary only the requested sampling grids."""
    grids = tuple(grids)
    if len(set(grids)) < 2:
        raise ValueError("at least two distinct sampling grids are required")
    return SamplingReliabilityAudit(tuple(
        evaluate_vesica_bend_spacing(shell_gap, bend_margin, current=current, **asdict(grid))
        for grid in grids
    ))


def format_sampling_reliability_report(audits: Iterable[SamplingReliabilityAudit]) -> str:
    lines = [
        "TOROIDAL SAMPLING RELIABILITY",
        "scope=nonzero_same_face_incident_bend_vs_straight",
        "evidence=finite_sampling_only; no_collision_detected_is_not_certified_clearance",
    ]
    for audit in audits:
        reference = audit.results[0]
        outcome = "collision_detected" if audit.collision_detected else "no_collision_detected"
        lines.append(
            f"case=gap:{reference.shell_gap:g},margin:{reference.bend_margin:g},"
            f"outcome:{outcome},classification_changes:{audit.classification_changes},"
            f"maximum_sampled_penetration:{audit.maximum_sampled_penetration:.12g}"
        )
        for result in audit.results:
            lines.append(
                f"sampling=[{result.sampling.description}],"
                f"detected_collisions:{result.collision_count},"
                f"sampled_penetration:{result.maximum_penetration:.12g}"
            )
    return "\n".join(lines)


def main() -> None:
    cases = ((3.0, 0.05), (8.25, 0.005), (30.0, 0.05))
    print(format_sampling_reliability_report(
        audit_vesica_sampling_reliability(gap, margin) for gap, margin in cases
    ))


if __name__ == "__main__":
    main()
