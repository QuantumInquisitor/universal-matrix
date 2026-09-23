"""Published planar concurrency contract for the Sri Yantra core.

This module encodes the minimal concurrency conditions stated by Alessandro
Chiodo in "On the construction of the Sri Yantra", C. R. Mathematique 359
(2021), 377-397.

Chiodo labels the nine maximal isosceles triangles t1,...,t9 in order of their
bases from top to bottom. In that convention t1,...,t5 point downward and
t6,...,t9 point upward.

The paper specifies:
1. t3 and t7 are inscribed in the same circle;
2. seven apex-to-base-point incidences;
3. twelve three-line concurrency conditions.

These relations are a sourced incidence contract. They do not by themselves
supply all chamber-edge coordinates of the 43 subsidiary triangles.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from fractions import Fraction


class TriangleOrientation(IntEnum):
    DOWNWARD = -1
    UPWARD = 1


@dataclass(frozen=True, order=True)
class ChiodoTriangle:
    index: int
    orientation: TriangleOrientation

    def __post_init__(self) -> None:
        if self.index not in range(1, 10):
            raise ValueError("triangle index must be in 1..9")
        expected = (
            TriangleOrientation.DOWNWARD
            if self.index <= 5
            else TriangleOrientation.UPWARD
        )
        if self.orientation is not expected:
            raise ValueError("orientation must match Chiodo t1..t9 convention")

    @property
    def label(self) -> str:
        return f"t{self.index}"


TRIANGLES = tuple(
    ChiodoTriangle(
        index,
        TriangleOrientation.DOWNWARD if index <= 5 else TriangleOrientation.UPWARD,
    )
    for index in range(1, 10)
)
TRIANGLE_BY_INDEX = {item.index: item for item in TRIANGLES}


def triangle(index: int) -> ChiodoTriangle:
    try:
        return TRIANGLE_BY_INDEX[index]
    except KeyError as error:
        raise ValueError("triangle index must be in 1..9") from error


COMMON_CIRCUMCIRCLE_PAIR = (triangle(3), triangle(7))


@dataclass(frozen=True, order=True)
class ApexBaseIncidence:
    """Apex of the first triangle equals the base point of the second."""

    apex_triangle: ChiodoTriangle
    base_triangle: ChiodoTriangle


APEX_BASE_INCIDENCES = tuple(
    ApexBaseIncidence(triangle(apex), triangle(base))
    for apex, base in (
        (8, 1),
        (6, 2),
        (9, 3),
        (1, 6),
        (5, 7),
        (4, 8),
        (2, 9),
    )
)


@dataclass(frozen=True, order=True)
class ThreeLineConcurrency:
    """One condition (iii) in Chiodo ordered notation."""

    downward_leg: ChiodoTriangle
    base_triangle: ChiodoTriangle
    upward_leg: ChiodoTriangle

    def __post_init__(self) -> None:
        if self.downward_leg.orientation is not TriangleOrientation.DOWNWARD:
            raise ValueError("first triangle must be downward")
        if self.upward_leg.orientation is not TriangleOrientation.UPWARD:
            raise ValueError("third triangle must be upward")


THREE_LINE_CONCURRENCIES = tuple(
    ThreeLineConcurrency(triangle(down), triangle(base), triangle(up))
    for down, base, up in (
        (1, 2, 7),
        (2, 3, 7),
        (1, 3, 8),
        (1, 4, 6),
        (1, 5, 9),
        (4, 6, 9),
        (2, 7, 9),
        (3, 7, 8),
        (3, 8, 9),
        (4, 4, 8),
        (5, 5, 6),
        (2, 6, 6),
    )
)


@dataclass(frozen=True)
class ChiodoBaseParameters:
    """Four ordered base points P,Q,R,S on normalized diameter OT=[0,1]."""

    p: Fraction
    q: Fraction
    r: Fraction
    s: Fraction

    def __post_init__(self) -> None:
        values = tuple(Fraction(value) for value in (self.p, self.q, self.r, self.s))
        if not (Fraction(0) < values[0] < values[1] < values[2] < values[3] < Fraction(1)):
            raise ValueError("parameters must satisfy 0 < P < Q < R < S < 1")
        object.__setattr__(self, "p", values[0])
        object.__setattr__(self, "q", values[1])
        object.__setattr__(self, "r", values[2])
        object.__setattr__(self, "s", values[3])

    @property
    def triangle_base_points(self) -> dict[str, Fraction]:
        return {
            "t3": self.p,
            "t6": self.q,
            "t7": self.r,
            "t9": self.s,
        }


HUET_BASE_PARAMETERS = ChiodoBaseParameters(
    Fraction(332, 1000),
    Fraction(537, 1000),
    Fraction(602, 1000),
    Fraction(835, 1000),
)


def constraint_edges() -> frozenset[frozenset[ChiodoTriangle]]:
    """Return pairwise triangle relations induced by the sourced constraints.

    This is a constraint graph, not the 43-chamber adjacency graph.
    """
    edges: set[frozenset[ChiodoTriangle]] = {
        frozenset(COMMON_CIRCUMCIRCLE_PAIR)
    }
    for relation in APEX_BASE_INCIDENCES:
        edges.add(frozenset((relation.apex_triangle, relation.base_triangle)))
    for relation in THREE_LINE_CONCURRENCIES:
        labels = (
            relation.downward_leg,
            relation.base_triangle,
            relation.upward_leg,
        )
        for first_index in range(3):
            for second_index in range(first_index + 1, 3):
                if labels[first_index] != labels[second_index]:
                    edges.add(frozenset((labels[first_index], labels[second_index])))
    return frozenset(edges)


def constraint_degree(index: int) -> int:
    target = triangle(index)
    return sum(target in edge for edge in constraint_edges())


def every_triangle_participates() -> bool:
    involved = {member for edge in constraint_edges() for member in edge}
    return involved == set(TRIANGLES)


if len(TRIANGLES) != 9:
    raise RuntimeError("Chiodo contract must contain nine maximal triangles")
if sum(item.orientation is TriangleOrientation.DOWNWARD for item in TRIANGLES) != 5:
    raise RuntimeError("Chiodo convention must contain five downward triangles")
if sum(item.orientation is TriangleOrientation.UPWARD for item in TRIANGLES) != 4:
    raise RuntimeError("Chiodo convention must contain four upward triangles")
if len(APEX_BASE_INCIDENCES) != 7:
    raise RuntimeError("Chiodo condition (ii) must contain seven incidences")
if len(THREE_LINE_CONCURRENCIES) != 12:
    raise RuntimeError("Chiodo condition (iii) must contain twelve concurrencies")
if not every_triangle_participates():
    raise RuntimeError("every maximal triangle must participate in the sourced constraint graph")
