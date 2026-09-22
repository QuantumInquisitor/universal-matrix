"""Exact 24-cell bridge generated from the stella tetrahedral edge roots.

At a common squared radius of four, the regular 24-cell vertex set is the
disjoint union of the sixteen tesseract vertices and the eight vertices of a
radius-matched 16-cell.  The same set is generated bottom-up by even Clifford
products of the twelve directed edge roots of either stella tetrahedron.

This module supplies finite geometry and symmetry contracts only.  It does not
assign the 24-cell a physical or cosmological interpretation.
"""

from __future__ import annotations

from collections import Counter
from functools import cache
from itertools import combinations, product

from .four_dimensional_polytope_bridge import (
    CROSS_POLYTOPE_VERTICES,
    TESSERACT_VERTICES,
    transform_coordinate_4d,
)
from .stella_octangula_register_bridge import tetrahedron_vertices

Coordinate3D = tuple[int, int, int]
Coordinate4D = tuple[int, int, int, int]
VertexPermutation = tuple[int, ...]

RADIUS_MATCHED_16_CELL_VERTICES = tuple(
    tuple(2 * component for component in vertex) for vertex in CROSS_POLYTOPE_VERTICES
)

TWENTY_FOUR_CELL_VERTICES = tuple(sorted({*TESSERACT_VERTICES, *RADIUS_MATCHED_16_CELL_VERTICES}))

TRIALITY_HADAMARD = (
    (1, 1, 1, 1),
    (1, 1, -1, -1),
    (1, -1, 1, -1),
    (1, -1, -1, 1),
)


def dot(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    """Return the exact Euclidean dot product of equal-length coordinates."""
    if len(left) != len(right):
        raise ValueError("coordinates must have equal length")
    return sum(a * b for a, b in zip(left, right, strict=True))


def squared_distance(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    """Return exact squared Euclidean distance."""
    if len(left) != len(right):
        raise ValueError("coordinates must have equal length")
    return sum((a - b) ** 2 for a, b in zip(left, right, strict=True))


def tetrahedral_edge_roots(parity: int) -> tuple[Coordinate3D, ...]:
    """Return the twelve directed unit-scale roots of one stella tetrahedron."""
    vertices = tetrahedron_vertices(parity)
    roots = {
        tuple((right[axis] - left[axis]) // 2 for axis in range(3))
        for left in vertices
        for right in vertices
        if left != right
    }
    return tuple(sorted(roots))


TETRAHEDRAL_EDGE_ROOTS = tetrahedral_edge_roots(1)


def edge_root_spinor_product(left: Coordinate3D, right: Coordinate3D) -> Coordinate4D:
    """Return the common-radius 4D spinor product of two A3 edge roots.

    Each root has squared norm two.  The unnormalized result
    ``(cross_xyz, dot)`` is therefore twice the corresponding unit spinor and
    lies directly in the integer 24-cell coordinate set.
    """
    if left not in TETRAHEDRAL_EDGE_ROOTS or right not in TETRAHEDRAL_EDGE_ROOTS:
        raise ValueError("both inputs must be directed tetrahedral edge roots")
    cross = (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )
    spinor = (*cross, dot(left, right))
    if spinor not in TWENTY_FOUR_CELL_VERTICES:
        raise RuntimeError("edge-root product escaped the 24-cell")
    return spinor


def twenty_four_cell_vertices_from_tetrahedron(parity: int) -> tuple[Coordinate4D, ...]:
    """Generate all 24 vertices from either stella tetrahedron's edge roots."""
    roots = tetrahedral_edge_roots(parity)
    return tuple(
        sorted({edge_root_spinor_product(left, right) for left in roots for right in roots})
    )


@cache
def twenty_four_cell_edges() -> tuple[tuple[Coordinate4D, Coordinate4D], ...]:
    """Return the 96 vertex pairs at the regular edge distance."""
    return tuple(
        (left, right)
        for left, right in combinations(TWENTY_FOUR_CELL_VERTICES, 2)
        if squared_distance(left, right) == 4
    )


@cache
def twenty_four_cell_triangular_faces() -> tuple[tuple[Coordinate4D, ...], ...]:
    """Return the 96 triangular cliques of the edge graph."""
    edge_sets = {frozenset(edge) for edge in twenty_four_cell_edges()}
    return tuple(
        triangle
        for triangle in combinations(TWENTY_FOUR_CELL_VERTICES, 3)
        if all(frozenset(edge) in edge_sets for edge in combinations(triangle, 2))
    )


TWENTY_FOUR_CELL_FACET_NORMALS = tuple(
    sorted(
        {
            tuple(signs[axes.index(axis)] if axis in axes else 0 for axis in range(4))
            for axes in combinations(range(4), 2)
            for signs in product((-1, 1), repeat=2)
        }
    )
)


@cache
def twenty_four_cell_facets() -> tuple[tuple[Coordinate4D, ...], ...]:
    """Return the 24 six-vertex octahedral facets, one per D4 normal."""
    return tuple(
        tuple(vertex for vertex in TWENTY_FOUR_CELL_VERTICES if dot(normal, vertex) == 2)
        for normal in TWENTY_FOUR_CELL_FACET_NORMALS
    )


def triality_transform(vertex: Coordinate4D) -> Coordinate4D:
    """Apply the extra Hadamard involution that extends B4 to 24-cell symmetry."""
    if vertex not in TWENTY_FOUR_CELL_VERTICES:
        raise ValueError("vertex must belong to the 24-cell")
    transformed = tuple(dot(row, vertex) // 2 for row in TRIALITY_HADAMARD)
    if transformed not in TWENTY_FOUR_CELL_VERTICES:
        raise RuntimeError("triality transform escaped the 24-cell")
    return transformed


def _vertex_permutation(transform) -> VertexPermutation:
    indices = {vertex: index for index, vertex in enumerate(TWENTY_FOUR_CELL_VERTICES)}
    return tuple(indices[transform(vertex)] for vertex in TWENTY_FOUR_CELL_VERTICES)


@cache
def twenty_four_cell_symmetry_permutations() -> tuple[VertexPermutation, ...]:
    """Generate the full 1,152-element 24-cell symmetry action on vertices."""
    b4_generator_frames = (
        (-1, 2, 3, 4),
        (2, 1, 3, 4),
        (1, 3, 2, 4),
        (1, 2, 4, 3),
    )
    generators = tuple(
        _vertex_permutation(lambda vertex, frame=frame: transform_coordinate_4d(vertex, frame))
        for frame in b4_generator_frames
    ) + (_vertex_permutation(triality_transform),)

    identity = tuple(range(len(TWENTY_FOUR_CELL_VERTICES)))
    group = {identity}
    frontier = [identity]
    while frontier:
        permutation = frontier.pop()
        for generator in generators:
            composed = tuple(generator[permutation[index]] for index in identity)
            if composed not in group:
                group.add(composed)
                frontier.append(composed)
    return tuple(sorted(group))


def projected_xyz_multiplicities() -> tuple[tuple[Coordinate3D, int], ...]:
    """Return exact multiplicities after dropping W from all 24 vertices."""
    counts = Counter(vertex[:3] for vertex in TWENTY_FOUR_CELL_VERTICES)
    return tuple(sorted(counts.items()))


if len(TWENTY_FOUR_CELL_VERTICES) != 24:
    raise RuntimeError("the 24-cell bridge requires exactly 24 vertices")
if any(dot(vertex, vertex) != 4 for vertex in TWENTY_FOUR_CELL_VERTICES):
    raise RuntimeError("all 24-cell vertices must share squared radius four")
if set(tetrahedral_edge_roots(-1)) != set(TETRAHEDRAL_EDGE_ROOTS):
    raise RuntimeError("both stella tetrahedra must induce the same A3 edge roots")
