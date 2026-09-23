"""Exact coordinate and incidence contract for all five Platonic solids.

The tetrahedron, cube, and octahedron recover geometry already present in the
stella and six-gate layers.  The icosahedron and dodecahedron are represented
over the exact quadratic field Q(phi), where ``phi**2 = phi + 1``.

This is a finite Euclidean reference layer.  It does not assign elemental,
physical, or cosmological meanings to the five solids.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from itertools import combinations, product
from math import sqrt

from .canonical_kernel import BOUNDARY_GATES
from .stella_octangula_register_bridge import (
    STELLA_VERTICES,
    gate_coordinate,
    tetrahedron_vertices,
)


@dataclass(frozen=True)
class PhiNumber:
    """Exact number ``rational + golden * phi`` with rational coefficients."""

    rational: Fraction = Fraction(0)
    golden: Fraction = Fraction(0)

    def __post_init__(self) -> None:
        object.__setattr__(self, "rational", Fraction(self.rational))
        object.__setattr__(self, "golden", Fraction(self.golden))

    @staticmethod
    def coerce(value: PhiNumber | int | Fraction) -> PhiNumber:
        if isinstance(value, PhiNumber):
            return value
        return PhiNumber(Fraction(value))

    def __add__(self, other: PhiNumber | int | Fraction) -> PhiNumber:
        other = self.coerce(other)
        return PhiNumber(self.rational + other.rational, self.golden + other.golden)

    __radd__ = __add__

    def __neg__(self) -> PhiNumber:
        return PhiNumber(-self.rational, -self.golden)

    def __sub__(self, other: PhiNumber | int | Fraction) -> PhiNumber:
        return self + -self.coerce(other)

    def __rsub__(self, other: PhiNumber | int | Fraction) -> PhiNumber:
        return self.coerce(other) - self

    def __mul__(self, other: PhiNumber | int | Fraction) -> PhiNumber:
        other = self.coerce(other)
        # phi^2 = phi + 1
        return PhiNumber(
            self.rational * other.rational + self.golden * other.golden,
            self.rational * other.golden
            + self.golden * other.rational
            + self.golden * other.golden,
        )

    __rmul__ = __mul__

    def inverse(self) -> PhiNumber:
        """Return the exact multiplicative inverse in ``Q(phi)``."""
        field_norm = (
            self.rational * self.rational + self.rational * self.golden - self.golden * self.golden
        )
        if field_norm == 0:
            raise ZeroDivisionError("cannot invert zero in Q(phi)")
        return PhiNumber(
            (self.rational + self.golden) / field_norm,
            -self.golden / field_norm,
        )

    def __truediv__(self, divisor: PhiNumber | int | Fraction) -> PhiNumber:
        return self * self.coerce(divisor).inverse()

    def __float__(self) -> float:
        phi = (1 + sqrt(5)) / 2
        return float(self.rational) + float(self.golden) * phi


ZERO = PhiNumber(0)
ONE = PhiNumber(1)
PHI = PhiNumber(0, 1)
INVERSE_PHI = PhiNumber(-1, 1)

Coordinate = tuple[PhiNumber, PhiNumber, PhiNumber]
Edge = tuple[Coordinate, Coordinate]
Face = tuple[Coordinate, ...]


def _coordinate(x: PhiNumber | int, y: PhiNumber | int, z: PhiNumber | int) -> Coordinate:
    return PhiNumber.coerce(x), PhiNumber.coerce(y), PhiNumber.coerce(z)


def _coordinate_key(coordinate: Coordinate) -> tuple[float, float, float]:
    return tuple(float(component) for component in coordinate)


def _sorted_coordinates(coordinates) -> tuple[Coordinate, ...]:
    return tuple(sorted(set(coordinates), key=_coordinate_key))


def dot(left: Coordinate, right: Coordinate) -> PhiNumber:
    """Return the exact Q(phi) dot product."""
    return sum((a * b for a, b in zip(left, right, strict=True)), ZERO)


def squared_distance(left: Coordinate, right: Coordinate) -> PhiNumber:
    """Return exact squared Euclidean distance in Q(phi)."""
    difference = tuple(a - b for a, b in zip(left, right, strict=True))
    return dot(difference, difference)


def cross(left: Coordinate, right: Coordinate) -> Coordinate:
    """Return the exact three-dimensional cross product."""
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def central_mirror(coordinate: Coordinate) -> Coordinate:
    """Reflect one exact coordinate through the common center."""
    return tuple(-component for component in coordinate)


def _lift_integer_coordinates(coordinates) -> tuple[Coordinate, ...]:
    return _sorted_coordinates(_coordinate(*coordinate) for coordinate in coordinates)


TETRAHEDRON_VERTICES = _lift_integer_coordinates(tetrahedron_vertices(1))
MIRROR_TETRAHEDRON_VERTICES = _lift_integer_coordinates(tetrahedron_vertices(-1))
CUBE_VERTICES = _lift_integer_coordinates(STELLA_VERTICES)
OCTAHEDRON_VERTICES = _lift_integer_coordinates(gate_coordinate(label) for label in BOUNDARY_GATES)

ICOSAHEDRON_VERTICES = _sorted_coordinates(
    coordinate
    for first_sign, second_sign in product((-1, 1), repeat=2)
    for coordinate in (
        _coordinate(first_sign, 0, second_sign * PHI),
        _coordinate(second_sign * PHI, first_sign, 0),
        _coordinate(0, second_sign * PHI, first_sign),
    )
)

DODECAHEDRON_VERTICES = _sorted_coordinates(
    [_coordinate(x, y, z) for x, y, z in product((-1, 1), repeat=3)]
    + [
        coordinate
        for first_sign, second_sign in product((-1, 1), repeat=2)
        for coordinate in (
            _coordinate(0, first_sign * INVERSE_PHI, second_sign * PHI),
            _coordinate(first_sign * INVERSE_PHI, second_sign * PHI, 0),
            _coordinate(second_sign * PHI, 0, first_sign * INVERSE_PHI),
        )
    ]
)


@dataclass(frozen=True)
class PlatonicSolid:
    """One regular convex polyhedron in an exact centered realization."""

    name: str
    vertices: tuple[Coordinate, ...]
    edge_squared: PhiNumber
    face_size: int


PLATONIC_SOLIDS = (
    PlatonicSolid("tetrahedron", TETRAHEDRON_VERTICES, PhiNumber(8), 3),
    PlatonicSolid("cube", CUBE_VERTICES, PhiNumber(4), 4),
    PlatonicSolid("octahedron", OCTAHEDRON_VERTICES, PhiNumber(2), 3),
    PlatonicSolid("dodecahedron", DODECAHEDRON_VERTICES, PhiNumber(8, -4), 5),
    PlatonicSolid("icosahedron", ICOSAHEDRON_VERTICES, PhiNumber(4), 3),
)

DUAL_SOLID_NAMES = {
    "tetrahedron": "tetrahedron",
    "cube": "octahedron",
    "octahedron": "cube",
    "dodecahedron": "icosahedron",
    "icosahedron": "dodecahedron",
}


def platonic_solid(name: str) -> PlatonicSolid:
    """Return one named Platonic solid."""
    try:
        return next(solid for solid in PLATONIC_SOLIDS if solid.name == name)
    except StopIteration as error:
        raise ValueError(f"unknown Platonic solid: {name}") from error


@cache
def solid_edges(name: str) -> tuple[Edge, ...]:
    """Derive all edges as vertex pairs at the solid's edge distance."""
    solid = platonic_solid(name)
    return tuple(
        (left, right)
        for left, right in combinations(solid.vertices, 2)
        if squared_distance(left, right) == solid.edge_squared
    )


@cache
def solid_faces(name: str) -> tuple[Face, ...]:
    """Derive regular faces as induced cycles of the edge graph."""
    solid = platonic_solid(name)
    edge_sets = {frozenset(edge) for edge in solid_edges(name)}
    faces = []
    for candidate in combinations(solid.vertices, solid.face_size):
        induced_edges = [
            edge for edge in combinations(candidate, 2) if frozenset(edge) in edge_sets
        ]
        degrees = Counter(vertex for edge in induced_edges for vertex in edge)
        if len(induced_edges) == solid.face_size and set(degrees.values()) == {2}:
            faces.append(candidate)
    return tuple(faces)


def face_center(face: Face) -> Coordinate:
    """Return the exact centroid of one regular face."""
    if len(face) < 3:
        raise ValueError("a face must contain at least three vertices")
    return tuple(sum((vertex[axis] for vertex in face), ZERO) / len(face) for axis in range(3))


def dual_vertices(name: str) -> tuple[Coordinate, ...]:
    """Return vertices whose outward rays match the named solid's face centers."""
    if name == "tetrahedron":
        return MIRROR_TETRAHEDRON_VERTICES
    return platonic_solid(DUAL_SOLID_NAMES[name]).vertices


def dual_face_center_matches(name: str) -> tuple[tuple[Coordinate, Coordinate], ...]:
    """Match every face-center ray to exactly one vertex of the dual solid."""
    candidates = dual_vertices(name)
    matches = []
    for face in solid_faces(name):
        center = face_center(face)
        aligned = tuple(
            vertex
            for vertex in candidates
            if cross(center, vertex) == (ZERO, ZERO, ZERO) and float(dot(center, vertex)) > 0
        )
        if len(aligned) != 1:
            raise RuntimeError(f"{name} face did not have exactly one outward dual ray")
        matches.append((center, aligned[0]))
    return tuple(matches)


def solid_signature(name: str) -> tuple[int, int, int]:
    """Return the derived ``(vertices, edges, faces)`` signature."""
    solid = platonic_solid(name)
    return len(solid.vertices), len(solid_edges(name)), len(solid_faces(name))


if len(ICOSAHEDRON_VERTICES) != 12 or len(DODECAHEDRON_VERTICES) != 20:
    raise RuntimeError("golden-ratio coordinate generation produced an invalid vertex count")
if set(TETRAHEDRON_VERTICES) | set(MIRROR_TETRAHEDRON_VERTICES) != set(CUBE_VERTICES):
    raise RuntimeError("the mirrored tetrahedron pair must partition the stella cube")
