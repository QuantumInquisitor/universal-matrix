"""Exact higher-dimensional regular-family and E8 root geometry.

This module extends the finite geometry audit without assigning a physical
meaning to any added coordinate.  For arbitrary dimension it constructs the
three regular convex families that persist in dimensions five and above:
simplex, hypercube, and cross polytope.

It also constructs the 240-root E8 configuration in exact integer coordinates
scaled by two.  The existing 24-cell enters E8 through its D4 facet-normal
system.  That inclusion is exact mathematics, not evidence that physical space
has eight dimensions or that E8 is a fundamental symmetry of nature.
"""

from __future__ import annotations

from collections import Counter
from functools import cache
from itertools import combinations, product

from .twenty_four_cell_bridge import TWENTY_FOUR_CELL_FACET_NORMALS

Coordinate = tuple[int, ...]
E8_DIMENSION = 8
E8_ROOT_COUNT = 240
E8_SQUARED_NORM = 8


def _require_dimension(dimension: int) -> None:
    if dimension < 1:
        raise ValueError("dimension must be at least one")


@cache
def hypercube_vertices(dimension: int) -> tuple[Coordinate, ...]:
    """Return the exact vertices of the n-cube ``{-1, +1}^n``."""
    _require_dimension(dimension)
    return tuple(product((-1, 1), repeat=dimension))


@cache
def cross_polytope_vertices(dimension: int) -> tuple[Coordinate, ...]:
    """Return the exact vertices ``+/- e_i`` of the n-cross-polytope."""
    _require_dimension(dimension)
    vertices = []
    for axis in range(dimension):
        for sign in (-1, 1):
            vertex = [0] * dimension
            vertex[axis] = sign
            vertices.append(tuple(vertex))
    return tuple(vertices)


@cache
def centered_simplex_vertices(dimension: int) -> tuple[Coordinate, ...]:
    """Return an exact regular n-simplex in the sum-zero hyperplane of R^(n+1).

    Vertex i has coordinate ``dimension`` in slot i and ``-1`` elsewhere.
    The n+1 vertices therefore have equal norm, equal pairwise inner product,
    and zero centroid using only integer arithmetic.
    """
    _require_dimension(dimension)
    width = dimension + 1
    return tuple(
        tuple(dimension if axis == vertex_index else -1 for axis in range(width))
        for vertex_index in range(width)
    )


def dot(left: Coordinate, right: Coordinate) -> int:
    """Return the exact Euclidean dot product of equal-length coordinates."""
    if len(left) != len(right):
        raise ValueError("coordinates must have equal length")
    return sum(a * b for a, b in zip(left, right, strict=True))


def squared_distance(left: Coordinate, right: Coordinate) -> int:
    """Return exact squared Euclidean distance."""
    if len(left) != len(right):
        raise ValueError("coordinates must have equal length")
    return sum((a - b) ** 2 for a, b in zip(left, right, strict=True))


def central_mirror(coordinate: Coordinate) -> Coordinate:
    """Apply point inversion through the origin."""
    return tuple(-component for component in coordinate)


def mirror_closed(coordinates: tuple[Coordinate, ...]) -> bool:
    """Return whether a finite coordinate set is closed under central inversion."""
    coordinate_set = set(coordinates)
    return {central_mirror(vertex) for vertex in coordinate_set} == coordinate_set


def mirrored_simplex_compound(dimension: int) -> tuple[Coordinate, ...]:
    """Return a simplex together with its central mirror.

    For dimension three this is the abstract analogue of pairing a tetrahedron
    with its inverted tetrahedron.  In higher dimensions the compound remains
    mirror closed, but it is not identified with the n-cross-polytope.
    """
    simplex = centered_simplex_vertices(dimension)
    return tuple(sorted({*simplex, *(central_mirror(vertex) for vertex in simplex)}))


def hypercube_projection_multiplicities(
    dimension: int,
) -> tuple[tuple[Coordinate, int], ...]:
    """Drop one axis from an n-cube and count the resulting (n-1)-cube image."""
    if dimension < 2:
        raise ValueError("projection requires dimension at least two")
    counts = Counter(vertex[:-1] for vertex in hypercube_vertices(dimension))
    return tuple(sorted(counts.items()))


def cross_polytope_projection_multiplicities(
    dimension: int,
) -> tuple[tuple[Coordinate, int], ...]:
    """Drop one axis from an n-cross-polytope and retain projection multiplicity."""
    if dimension < 2:
        raise ValueError("projection requires dimension at least two")
    counts = Counter(vertex[:-1] for vertex in cross_polytope_vertices(dimension))
    return tuple(sorted(counts.items()))


def persistent_regular_families(dimension: int) -> tuple[str, ...]:
    """Return the regular convex families that exist in every dimension >= 5."""
    if dimension < 5:
        raise ValueError("the persistent-family classification starts at dimension five")
    return ("simplex", "hypercube", "cross_polytope")


@cache
def e8_roots_scaled() -> tuple[Coordinate, ...]:
    """Return all 240 E8 roots in exact coordinates scaled uniformly by two.

    The first family contains 112 vectors obtained from permutations of
    ``(+/-2, +/-2, 0, ..., 0)``.  The second contains 128 sign vectors in
    ``{+/-1}^8`` with an even number of negative entries.  Every root has
    squared norm eight.
    """
    roots: set[Coordinate] = set()

    for first_axis, second_axis in combinations(range(E8_DIMENSION), 2):
        for first_sign, second_sign in product((-2, 2), repeat=2):
            root = [0] * E8_DIMENSION
            root[first_axis] = first_sign
            root[second_axis] = second_sign
            roots.add(tuple(root))

    for signs in product((-1, 1), repeat=E8_DIMENSION):
        negative_count = sum(sign < 0 for sign in signs)
        if negative_count % 2 == 0:
            roots.add(tuple(signs))

    return tuple(sorted(roots))


_E8_ROOT_SET = frozenset(e8_roots_scaled())


def e8_root_family_counts() -> tuple[tuple[int, int], ...]:
    """Return ``(nonzero-coordinate count, root count)`` for the two E8 shells."""
    counts = Counter(sum(component != 0 for component in root) for root in e8_roots_scaled())
    return tuple(sorted(counts.items()))


def e8_reflect(vector: Coordinate, root: Coordinate) -> Coordinate:
    """Reflect one scaled E8 root in the hyperplane normal to another."""
    if vector not in _E8_ROOT_SET or root not in _E8_ROOT_SET:
        raise ValueError("vector and root must both belong to the scaled E8 root system")

    numerator = 2 * dot(vector, root)
    denominator = dot(root, root)
    if numerator % denominator:
        raise RuntimeError("E8 reflection coefficient left the integer coordinate lattice")

    coefficient = numerator // denominator
    reflected = tuple(
        component - coefficient * root_component
        for component, root_component in zip(vector, root, strict=True)
    )
    if reflected not in _E8_ROOT_SET:
        raise RuntimeError("E8 reflection escaped the root system")
    return reflected


def e8_antipodal_pair_count() -> int:
    """Return the number of unordered central-mirror pairs among the E8 roots."""
    unseen = set(e8_roots_scaled())
    pair_count = 0
    while unseen:
        root = unseen.pop()
        mirror = central_mirror(root)
        if mirror not in unseen:
            raise RuntimeError("E8 root set lost central-mirror closure")
        unseen.remove(mirror)
        pair_count += 1
    return pair_count


def e8_nearest_neighbor_count(root: Coordinate) -> int:
    """Return the number of nearest E8 roots adjacent to one root-polytope vertex."""
    if root not in _E8_ROOT_SET:
        raise ValueError("root must belong to the scaled E8 root system")
    nearest_squared_distance = min(
        squared_distance(root, other) for other in _E8_ROOT_SET if other != root
    )
    return sum(
        squared_distance(root, other) == nearest_squared_distance
        for other in _E8_ROOT_SET
        if other != root
    )


def embed_24_cell_dual_in_e8() -> tuple[Coordinate, ...]:
    """Embed the existing 24-cell's D4 facet normals as an exact E8 subsystem.

    The 24-cell facet normals are the 24 D4 roots ``(+/-1, +/-1, 0, 0)`` and
    permutations.  Multiplying by two and padding four zero coordinates places
    them exactly inside the integer-scaled E8 root system above.
    """
    embedded = tuple(
        sorted(
            tuple(2 * component for component in normal) + (0, 0, 0, 0)
            for normal in TWENTY_FOUR_CELL_FACET_NORMALS
        )
    )
    if not set(embedded) <= _E8_ROOT_SET:
        raise RuntimeError("the embedded D4 subsystem must lie inside E8")
    return embedded


def d4_subsystem_reflection_closed() -> bool:
    """Check closure of the embedded 24-cell dual under its own root reflections."""
    subsystem = frozenset(embed_24_cell_dual_in_e8())
    for vector in subsystem:
        for root in subsystem:
            if e8_reflect(vector, root) not in subsystem:
                return False
    return True


if len(e8_roots_scaled()) != E8_ROOT_COUNT:
    raise RuntimeError("the exact E8 construction must contain 240 roots")
if {dot(root, root) for root in e8_roots_scaled()} != {E8_SQUARED_NORM}:
    raise RuntimeError("all scaled E8 roots must have squared norm eight")
if not mirror_closed(e8_roots_scaled()):
    raise RuntimeError("the E8 root configuration must be centrally symmetric")
if len(embed_24_cell_dual_in_e8()) != 24:
    raise RuntimeError("the embedded D4 subsystem must contain 24 roots")
