"""Numerical planar reconstruction of the Huet/Chiodo Sri Yantra core.

The input is the Huet base-point choice P,Q,R,S quoted by Chiodo.  The nine
maximal isosceles triangles are represented after Chiodo's anticlockwise
quarter-turn: their common symmetry axis is the normalized segment OT=[0,1].

Each triangle is determined by:
- its apex coordinate on OT,
- its base-point coordinate on OT,
- the slope of its upper leg.

The remaining coordinates are solved from Chiodo's published conditions
(i)-(iii).  This module reconstructs the same concurrent geometry
algebraically.  It is not yet a literal simulation of every compass-and-
straightedge operation in the paper.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from .sri_yantra_chiodo_concurrency import (
    APEX_BASE_INCIDENCES,
    HUET_BASE_PARAMETERS,
    THREE_LINE_CONCURRENCIES,
)

_TOLERANCE = 1e-11


@dataclass(frozen=True)
class PlanarTriangle:
    index: int
    apex_x: float
    base_x: float
    upper_slope: float

    @property
    def half_height(self) -> float:
        return self.upper_slope * (self.base_x - self.apex_x)

    @property
    def upper_base_vertex(self) -> tuple[float, float]:
        return self.base_x, self.half_height

    @property
    def lower_base_vertex(self) -> tuple[float, float]:
        return self.base_x, -self.half_height

    @property
    def apex(self) -> tuple[float, float]:
        return self.apex_x, 0.0

    @property
    def vertices(self) -> tuple[tuple[float, float], ...]:
        return self.apex, self.upper_base_vertex, self.lower_base_vertex

    def upper_leg_y(self, x: float) -> float:
        return self.upper_slope * (float(x) - self.apex_x)


@dataclass(frozen=True)
class HuetPlanarSolution:
    triangles: tuple[PlanarTriangle, ...]

    def triangle(self, index: int) -> PlanarTriangle:
        if index not in range(1, 10):
            raise ValueError("triangle index must be in 1..9")
        return self.triangles[index - 1]

    @property
    def base_points(self) -> tuple[float, ...]:
        return tuple(item.base_x for item in self.triangles)


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _bisect_single_root(function, lower: float, upper: float) -> float:
    """Find the unique sign-changing root selected in the interval."""
    samples = 4096
    previous_x = lower
    previous_y = function(previous_x)
    brackets: list[tuple[float, float]] = []

    for step in range(1, samples + 1):
        x = lower + (upper - lower) * step / samples
        y = function(x)
        if math.isfinite(previous_y) and math.isfinite(y):
            if previous_y == 0.0:
                brackets.append((previous_x, previous_x))
            elif y == 0.0 or previous_y * y < 0.0:
                brackets.append((previous_x, x))
        previous_x, previous_y = x, y

    unique = []
    for first, second in brackets:
        if not unique or abs(first - unique[-1][0]) > 1e-8:
            unique.append((first, second))
    if len(unique) != 1:
        raise RuntimeError(
            f"expected one admissible Chiodo branch root, found {len(unique)}"
        )

    lo, hi = unique[0]
    if lo == hi:
        return lo
    flo = function(lo)
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        fmid = function(mid)
        if abs(fmid) < 1e-15:
            return mid
        if flo * fmid <= 0.0:
            hi = mid
        else:
            lo = mid
            flo = fmid
    return 0.5 * (lo + hi)


def solve_huet_planar_core() -> HuetPlanarSolution:
    """Reconstruct the nine concurrent maximal triangles for Huet's parameters."""
    p = float(HUET_BASE_PARAMETERS.p)
    q = float(HUET_BASE_PARAMETERS.q)
    r = float(HUET_BASE_PARAMETERS.r)
    s = float(HUET_BASE_PARAMETERS.s)

    # t3 and t7 lie in the same circle with diameter OT=[0,1].
    h3 = math.sqrt(p * (1.0 - p))
    h7 = math.sqrt(r * (1.0 - r))
    m3 = h3 / (p - 1.0)
    m7 = h7 / r

    # Direct consequences of Chiodo condition (iii).
    m2 = m7 * p / (p - s)
    m9 = m2 * (r - s) / (r - p)
    b8 = (m3 - m9 * p) / (m3 - m9)
    m4 = m9 * (q - p) / (q - b8)

    def branch_state(b1: float):
        m8 = m3 * (r - 1.0) / (r - b1)
        m1 = m8 * (p - b1) / (p - q)
        b2 = m1 * q / (m1 - m7)
        m6 = m2 * (q - s) / (q - b2)
        b4 = (m1 * q - m6 * b2) / (m1 - m6)
        residual = m4 * (b4 - b8) - m8 * (b4 - b1)
        return residual, (m8, m1, b2, m6, b4)

    def branch_residual(b1: float) -> float:
        try:
            return _finite(branch_state(b1)[0], "branch residual")
        except (ZeroDivisionError, ValueError):
            return math.nan

    # The Huet branch has the base of t1 between O and the base of t3.
    epsilon = 1e-10
    b1 = _bisect_single_root(branch_residual, epsilon, p - epsilon)
    residual, (m8, m1, b2, m6, b4) = branch_state(b1)
    if abs(residual) > _TOLERANCE:
        raise RuntimeError("selected Chiodo branch failed its closure equation")

    b5 = (m1 * q - m9 * p) / (m1 - m9)
    m5 = m6 * (b5 - b2) / (b5 - r)

    apex = {
        1: q,
        2: s,
        3: 1.0,
        4: b8,
        5: r,
        6: b2,
        7: 0.0,
        8: b1,
        9: p,
    }
    base = {
        1: b1,
        2: b2,
        3: p,
        4: b4,
        5: b5,
        6: q,
        7: r,
        8: b8,
        9: s,
    }
    slope = {
        1: m1,
        2: m2,
        3: m3,
        4: m4,
        5: m5,
        6: m6,
        7: m7,
        8: m8,
        9: m9,
    }

    triangles = tuple(
        PlanarTriangle(index, apex[index], base[index], slope[index])
        for index in range(1, 10)
    )
    solution = HuetPlanarSolution(triangles)

    if any(item.half_height <= 0.0 for item in triangles):
        raise RuntimeError("all reconstructed triangle half-heights must be positive")
    if tuple(sorted(solution.base_points)) != solution.base_points:
        raise RuntimeError("Huet solution must preserve Chiodo t1..t9 base ordering")
    if maximum_concurrency_residual(solution) > _TOLERANCE:
        raise RuntimeError("reconstructed Huet geometry failed concurrency")
    return solution


def apex_base_residuals(solution: HuetPlanarSolution) -> tuple[float, ...]:
    return tuple(
        solution.triangle(relation.apex_triangle.index).apex_x
        - solution.triangle(relation.base_triangle.index).base_x
        for relation in APEX_BASE_INCIDENCES
    )


def concurrency_residuals(solution: HuetPlanarSolution) -> tuple[float, ...]:
    residuals = []
    for relation in THREE_LINE_CONCURRENCIES:
        down = solution.triangle(relation.downward_leg.index)
        middle = solution.triangle(relation.base_triangle.index)
        up = solution.triangle(relation.upward_leg.index)
        x = middle.base_x
        residuals.append(down.upper_leg_y(x) - up.upper_leg_y(x))
    return tuple(residuals)


def maximum_concurrency_residual(solution: HuetPlanarSolution) -> float:
    values = apex_base_residuals(solution) + concurrency_residuals(solution)
    return max((abs(value) for value in values), default=0.0)


def common_circumcircle_residual(solution: HuetPlanarSolution) -> float:
    """Maximum squared-radius residual for t3 and t7 against diameter OT circle."""
    center_x = 0.5
    radius_squared = 0.25
    residuals = []
    for index in (3, 7):
        for x, y in solution.triangle(index).vertices:
            residuals.append(abs((x - center_x) ** 2 + y**2 - radius_squared))
    return max(residuals)


def maximal_triangle_segments(
    solution: HuetPlanarSolution,
) -> tuple[tuple[tuple[float, float], tuple[float, float]], ...]:
    """Return all 27 finite edge segments of the nine maximal triangles."""
    segments = []
    for item in solution.triangles:
        apex, upper, lower = item.vertices
        segments.extend(((apex, upper), (apex, lower), (upper, lower)))
    return tuple(segments)


HUET_PLANAR_SOLUTION = solve_huet_planar_core()
