"""Explicit conical graph lift of the Huet complex, a Meru candidate control.

The height profile is an engine choice, not a sourced historical Meru metric.
Complete edges follow the cone. Replacing them with straight chords between
root vertices is a different construction and generally breaks concurrency.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .sri_yantra_chambers import ChamberComplex, extract_chambers
from .sri_yantra_huet_planar import HUET_PLANAR_SOLUTION


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


@dataclass(frozen=True)
class ConeMetric:
    """A chosen radial height profile with an invertible horizontal projection."""

    height: float = 1.0
    horizontal_scale: float = 1.0
    center_x: float = 0.5
    radius: float = 0.5

    def __post_init__(self):
        for name in ("height", "horizontal_scale", "center_x", "radius"):
            object.__setattr__(self, name, _finite(getattr(self, name), name))
        if self.height < 0 or self.horizontal_scale <= 0 or self.radius <= 0:
            raise ValueError("height must be nonnegative; scale and radius must be positive")

    def lift(self, point: tuple[float, float]) -> tuple[float, float, float]:
        dx = _finite(_finite(point[0], "x") - self.center_x, "centered x")
        y = _finite(point[1], "y")
        rho = _finite(math.hypot(dx, y) / self.radius, "normalized radius")
        if rho > 1 + 1e-10:
            raise ValueError("point is outside the candidate base disk")
        return (
            _finite(self.horizontal_scale * dx, "lifted x"),
            _finite(self.horizontal_scale * y, "lifted y"),
            _finite(self.height * (1 - rho), "lifted z"),
        )

    def recover(self, point: tuple[float, float, float]) -> tuple[float, float]:
        x, y, z = (_finite(v, "spatial coordinate") for v in point)
        planar = (
            _finite(x / self.horizontal_scale + self.center_x, "recovered x"),
            _finite(y / self.horizontal_scale, "recovered y"),
        )
        expected = self.lift(planar)
        if abs(z - expected[2]) > 1e-10 * max(1, self.height):
            raise ValueError("point is not on the specified candidate surface")
        return planar

    def edge_point(self, start, end, parameter: float):
        t = _finite(parameter, "edge parameter")
        if not 0 <= t <= 1:
            raise ValueError("edge parameter must be in [0,1]")
        return self.lift(((1 - t) * start[0] + t * end[0], (1 - t) * start[1] + t * end[1]))


@dataclass(frozen=True)
class MeruCandidate:
    planar: ChamberComplex
    metric: ConeMetric
    vertices: tuple[tuple[float, float, float], ...]

    def edge_point(self, edge_index: int, parameter: float):
        a, b = self.planar.edges[edge_index]
        return self.metric.edge_point(self.planar.vertices[a], self.planar.vertices[b], parameter)


def derive_meru_candidate(metric: ConeMetric | None = None) -> MeruCandidate:
    metric = ConeMetric() if metric is None else metric
    planar = extract_chambers()
    return MeruCandidate(planar, metric, tuple(metric.lift(p) for p in planar.vertices))


@dataclass(frozen=True)
class StraightRootAudit:
    """Vertical separation of root chords at their shared projected vertices."""

    broken_vertex_ids: tuple[int, ...]
    maximum_height_spread: float


def audit_straight_root_chords(candidate: MeruCandidate, tolerance: float = 1e-9):
    """Detect false 3D concurrency after lifting only the nine roots' corners."""
    tolerance = _finite(tolerance, "tolerance")
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    roots = tuple(t.vertices for t in HUET_PLANAR_SOLUTION.triangles)
    edges = tuple((a, b) for t in roots for a, b in zip(t, t[1:] + t[:1], strict=True))
    broken, spreads = [], []
    for index, (x, y) in enumerate(candidate.planar.vertices):
        heights = []
        for a, b in edges:
            dx, dy = b[0] - a[0], b[1] - a[1]
            length = math.hypot(dx, dy)
            distance = abs(dx * (y - a[1]) - dy * (x - a[0])) / length
            t = ((x - a[0]) * dx + (y - a[1]) * dy) / length**2
            if distance <= candidate.planar.tolerance and -1e-9 <= t <= 1 + 1e-9:
                heights.append(
                    (1 - t) * candidate.metric.lift(a)[2] + t * candidate.metric.lift(b)[2]
                )
        spread = max(heights) - min(heights) if heights else 0.0
        spreads.append(spread)
        if spread > tolerance:
            broken.append(index)
    return StraightRootAudit(tuple(broken), max(spreads))


if __name__ == "__main__":
    candidate = derive_meru_candidate()
    print("Candidate cone height:", candidate.metric.height)
    print("Chambers:", len(candidate.planar.chamber_ids))
    print("Complete lifted atomic edges:", len(candidate.planar.edges))
    print(
        "Ring circuits:", tuple(len(candidate.planar.ring_cycle(r)) for r in candidate.planar.rings)
    )
    audit = audit_straight_root_chords(candidate)
    print("Straight-root substitution breaks projected vertices:", len(audit.broken_vertex_ids))
    print("Maximum root-chord height spread:", audit.maximum_height_spread)
