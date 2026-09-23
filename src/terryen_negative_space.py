"""Equal-sphere and negative-space diagnostics for Terryen candidate geometries.

The source-reported Terryen counts do not uniquely determine coordinates. This
module works only with the explicit regular-polytope candidates recorded by
terryology_audit. Every center set is normalized to the unit sphere before an
equal-radius family is constructed.

For centers c_i and radius r, the occupied region is the union of closed balls

    U_r = union_i {x : ||x - c_i||^2 <= r^2}.

The negative space is its complement. The scalar field

    g_r(x) = min_i (||x - c_i||^2 - r^2)

is positive in negative space and zero on its piecewise-spherical boundary.

The topology calculation uses the Cech nerve of the balls. Finite
intersections of Euclidean balls are convex, so the nerve has the homotopy type
of their union. Alexander duality then identifies beta_(d-1) of the union in
R^d with the number of bounded complementary components.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from functools import cache
from itertools import combinations
from math import comb, isfinite, sqrt

from .terryology_audit import terryen_candidate_vertices

Point = tuple[float, ...]
Simplex = tuple[int, ...]
_DEFAULT_TOLERANCE = 1e-10


def _dot(left: Sequence[float], right: Sequence[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True))


def _norm_squared(point: Sequence[float]) -> float:
    return _dot(point, point)


def _distance_squared(left: Sequence[float], right: Sequence[float]) -> float:
    return sum((a - b) ** 2 for a, b in zip(left, right, strict=True))


def _normalized(vector: Sequence[float]) -> Point:
    values = tuple(float(value) for value in vector)
    norm = sqrt(_norm_squared(values))
    if norm <= _DEFAULT_TOLERANCE:
        raise ValueError("a direction or center cannot be the zero vector")
    return tuple(value / norm for value in values)


@cache
def terryen_unit_centers(key: str) -> tuple[Point, ...]:
    """Return the candidate centers normalized to a common unit radius."""
    vertices = terryen_candidate_vertices(key)
    centers = tuple(_normalized(vertex) for vertex in vertices)
    dimension = len(centers[0])
    if any(len(center) != dimension for center in centers):
        raise RuntimeError("candidate centers must have a common dimension")
    if any(abs(_norm_squared(center) - 1.0) > _DEFAULT_TOLERANCE for center in centers):
        raise RuntimeError("candidate-center normalization failed")
    return centers


@dataclass(frozen=True)
class SphereEquation:
    """One closed equal-radius ball and its implicit boundary equation."""

    center: Point
    radius: float

    def residual(self, point: Sequence[float]) -> float:
        """Return ||point - center|| squared minus radius squared."""
        values = tuple(float(value) for value in point)
        if len(values) != len(self.center):
            raise ValueError("point dimension does not match the sphere center")
        return _distance_squared(values, self.center) - self.radius * self.radius

    def contains(self, point: Sequence[float], tolerance: float = 0.0) -> bool:
        """Return whether the point lies in the closed ball."""
        return self.residual(point) <= tolerance


def equal_sphere_equations(key: str, radius: float) -> tuple[SphereEquation, ...]:
    """Construct the explicit equal-ball family for one Terryen candidate."""
    radius = float(radius)
    if not isfinite(radius) or radius < 0.0:
        raise ValueError("radius must be finite and nonnegative")
    return tuple(SphereEquation(center, radius) for center in terryen_unit_centers(key))


def negative_space_margin(key: str, radius: float, point: Sequence[float]) -> float:
    """Return the implicit negative-space field g_r(point).

    Positive values are outside every ball, zero is the exposed
    piecewise-spherical boundary, and negative values are in the occupied union.
    """
    equations = equal_sphere_equations(key, radius)
    return min(equation.residual(point) for equation in equations)


def is_in_negative_space(
    key: str,
    radius: float,
    point: Sequence[float],
    tolerance: float = 0.0,
) -> bool:
    """Return whether a point is outside every closed ball."""
    return negative_space_margin(key, radius, point) > tolerance


def central_void_radial_distance(
    key: str,
    radius: float,
    direction: Sequence[float],
) -> float | None:
    """Return the first sphere-boundary hit on a ray from the origin.

    The origin must still be in negative space, hence radius must be below one.
    None means the ray escapes without meeting the ball union. Within each
    certified cavity window every direction has a finite first hit.
    """
    radius = float(radius)
    if not isfinite(radius) or not 0.0 <= radius < 1.0:
        raise ValueError("radial extraction requires a finite radius in [0, 1)")
    unit_direction = _normalized(direction)
    centers = terryen_unit_centers(key)
    if len(unit_direction) != len(centers[0]):
        raise ValueError("direction dimension does not match the candidate")

    constant = 1.0 - radius * radius
    hits: list[float] = []
    for center in centers:
        projection = _dot(unit_direction, center)
        discriminant = projection * projection - constant
        if discriminant < -_DEFAULT_TOLERANCE:
            continue
        root = projection - sqrt(max(0.0, discriminant))
        if root >= -_DEFAULT_TOLERANCE:
            hits.append(max(0.0, root))
    return min(hits) if hits else None


def central_void_boundary_point(
    key: str,
    radius: float,
    direction: Sequence[float],
) -> Point | None:
    """Return the first central-void boundary point along a ray."""
    unit_direction = _normalized(direction)
    distance = central_void_radial_distance(key, radius, unit_direction)
    if distance is None:
        return None
    return tuple(distance * component for component in unit_direction)


@dataclass(frozen=True)
class _Ball:
    center: Point
    radius_squared: float


def _solve_linear_system(
    matrix: Sequence[Sequence[float]],
    vector: Sequence[float],
) -> tuple[float, ...] | None:
    size = len(vector)
    augmented = [
        [*(float(value) for value in row), float(vector[index])]
        for index, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) <= 1e-12:
            return None
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if abs(factor) <= 1e-15:
                continue
            augmented[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(
                    augmented[row], augmented[column], strict=True
                )
            ]
    return tuple(augmented[row][-1] for row in range(size))


@cache
def _circumball(key: str, support: Simplex) -> _Ball | None:
    points = tuple(terryen_unit_centers(key)[index] for index in support)
    if len(points) == 1:
        return _Ball(points[0], 0.0)

    origin = points[0]
    vectors = tuple(
        tuple(value - base for value, base in zip(point, origin, strict=True))
        for point in points[1:]
    )
    gram = tuple(tuple(_dot(left, right) for right in vectors) for left in vectors)
    coefficients = _solve_linear_system(
        gram,
        tuple(_norm_squared(vector) / 2.0 for vector in vectors),
    )
    if coefficients is None:
        return None

    center = tuple(
        origin[axis]
        + sum(
            coefficient * vector[axis]
            for coefficient, vector in zip(coefficients, vectors, strict=True)
        )
        for axis in range(len(origin))
    )
    return _Ball(center, _distance_squared(center, origin))


def _covers(ball: _Ball, points: Iterable[Point]) -> bool:
    return all(
        _distance_squared(ball.center, point)
        <= ball.radius_squared + _DEFAULT_TOLERANCE
        for point in points
    )


@cache
def _minimum_enclosing_ball(key: str, simplex: Simplex) -> _Ball:
    points = tuple(terryen_unit_centers(key)[index] for index in simplex)
    best: _Ball | None = None
    for support_size in range(1, len(simplex) + 1):
        for support in combinations(simplex, support_size):
            candidate = _circumball(key, support)
            if candidate is None:
                continue
            if best is not None and candidate.radius_squared >= best.radius_squared:
                continue
            if _covers(candidate, points):
                best = candidate
    if best is None:
        raise RuntimeError("failed to construct a minimum enclosing ball")
    return best


def cech_critical_radius(key: str, simplex: Sequence[int]) -> float:
    """Return the first radius at which the indexed balls share a point."""
    centers = terryen_unit_centers(key)
    canonical = tuple(sorted(int(index) for index in simplex))
    if not canonical or len(set(canonical)) != len(canonical):
        raise ValueError("simplex must contain distinct center indices")
    if canonical[0] < 0 or canonical[-1] >= len(centers):
        raise IndexError("simplex center index is out of range")
    return sqrt(max(0.0, _minimum_enclosing_ball(key, canonical).radius_squared))


def _gf2_rank(columns: Iterable[int]) -> int:
    pivots: dict[int, int] = {}
    for column in columns:
        while column:
            pivot = column.bit_length() - 1
            previous = pivots.get(pivot)
            if previous is None:
                pivots[pivot] = column
                break
            column ^= previous
    return len(pivots)


@dataclass(frozen=True)
class CechTopology:
    """Homology of the Cech skeleton needed for complement components."""

    key: str
    ambient_dimension: int
    radius: float
    simplex_counts: tuple[int, ...]
    boundary_ranks: tuple[int, ...]
    betti_numbers: tuple[int, ...]
    bounded_negative_space_components: int


def _full_simplex_topology(key: str, radius: float) -> CechTopology:
    centers = terryen_unit_centers(key)
    dimension = len(centers[0])
    point_count = len(centers)
    counts = tuple(
        comb(point_count, simplex_dimension + 1)
        for simplex_dimension in range(dimension + 1)
    )
    ranks = (
        0,
        *(comb(point_count - 1, dimension_index) for dimension_index in range(1, dimension + 1)),
    )
    betti = tuple(
        counts[index] - ranks[index] - ranks[index + 1]
        for index in range(dimension)
    )
    return CechTopology(key, dimension, radius, counts, ranks, betti, betti[-1])


@cache
def cech_topology(key: str, radius: float) -> CechTopology:
    """Compute mod-2 Betti numbers through codimension one.

    Simplices through ambient dimension are sufficient for beta_(d-1).
    Radius one is a fast exact terminal case because the origin belongs to
    every unit-center ball, making the complete nerve contractible.
    """
    radius = float(radius)
    if not isfinite(radius) or radius < 0.0:
        raise ValueError("radius must be finite and nonnegative")
    if radius >= 1.0:
        return _full_simplex_topology(key, radius)

    centers = terryen_unit_centers(key)
    dimension = len(centers[0])
    threshold_squared = radius * radius + 1e-12
    levels = tuple(
        tuple(
            simplex
            for simplex in combinations(range(len(centers)), simplex_size)
            if _minimum_enclosing_ball(key, simplex).radius_squared <= threshold_squared
        )
        for simplex_size in range(1, dimension + 2)
    )
    index_maps = tuple(
        {simplex: index for index, simplex in enumerate(level)} for level in levels
    )

    ranks = [0]
    for simplex_dimension in range(1, dimension + 1):
        face_indices = index_maps[simplex_dimension - 1]
        columns: list[int] = []
        for simplex in levels[simplex_dimension]:
            column = 0
            for removed in range(len(simplex)):
                face = simplex[:removed] + simplex[removed + 1 :]
                column |= 1 << face_indices[face]
            columns.append(column)
        ranks.append(_gf2_rank(columns))

    counts = tuple(len(level) for level in levels)
    betti = tuple(
        counts[index] - ranks[index] - ranks[index + 1]
        for index in range(dimension)
    )
    return CechTopology(
        key=key,
        ambient_dimension=dimension,
        radius=radius,
        simplex_counts=counts,
        boundary_ranks=tuple(ranks),
        betti_numbers=betti,
        bounded_negative_space_components=betti[-1],
    )


@dataclass(frozen=True)
class NegativeSpaceWindow:
    """Certified radius interval for one bounded central complement component."""

    key: str
    birth_radius: float
    death_radius: float = 1.0

    def contains(self, radius: float) -> bool:
        """Use the closed-ball convention: birth is included, death is not."""
        return self.birth_radius <= radius < self.death_radius


_CAVITY_BIRTH_RADII = {
    "tetra_terryen": sqrt(8.0 / 9.0),
    "huntyen": sqrt(2.0 / 3.0),
    "mira": sqrt(2.0 / 3.0),
    "aubreyen": sqrt((2.0 - 2.0 / sqrt(5.0)) / 3.0),
    "heavenly": 1.0 / sqrt(2.0),
}


def terryen_negative_space_window(key: str) -> NegativeSpaceWindow:
    """Return the candidate's analytically derived central-cavity interval."""
    try:
        birth = _CAVITY_BIRTH_RADII[key]
    except KeyError as error:
        terryen_unit_centers(key)
        raise ValueError(f"no cavity window recorded for Terryen candidate: {key}") from error
    return NegativeSpaceWindow(key, birth)


@dataclass(frozen=True)
class CenterSymmetryDiagnostic:
    """Distance, centering, and central-mirror checks for a center set."""

    key: str
    dimension: int
    point_count: int
    centroid_residual: float
    common_radius_residual: float
    squared_distance_shells: tuple[float, ...]
    shell_multiplicities: tuple[int, ...]
    uniform_distance_profile: bool
    mirror_permutation: tuple[int, ...] | None

    @property
    def centrally_symmetric(self) -> bool:
        return self.mirror_permutation is not None


def _mirror_permutation(centers: tuple[Point, ...]) -> tuple[int, ...] | None:
    permutation: list[int] = []
    for center in centers:
        target = tuple(-component for component in center)
        match = next(
            (
                index
                for index, candidate in enumerate(centers)
                if _distance_squared(target, candidate) <= 1e-20
            ),
            None,
        )
        if match is None:
            return None
        permutation.append(match)
    return tuple(permutation)


def terryen_center_symmetry(key: str) -> CenterSymmetryDiagnostic:
    """Audit equal radius, centering, distance shells, and central mirroring."""
    centers = terryen_unit_centers(key)
    dimension = len(centers[0])
    centroid = tuple(
        sum(center[axis] for center in centers) / len(centers)
        for axis in range(dimension)
    )
    profiles = tuple(
        tuple(
            sorted(
                round(_distance_squared(center, other), 12)
                for other in centers
                if other != center
            )
        )
        for center in centers
    )
    shells = tuple(sorted(set(profiles[0])))
    multiplicities = tuple(profiles[0].count(shell) for shell in shells)
    return CenterSymmetryDiagnostic(
        key=key,
        dimension=dimension,
        point_count=len(centers),
        centroid_residual=sqrt(_norm_squared(centroid)),
        common_radius_residual=max(abs(_norm_squared(center) - 1.0) for center in centers),
        squared_distance_shells=shells,
        shell_multiplicities=multiplicities,
        uniform_distance_profile=len(set(profiles)) == 1,
        mirror_permutation=_mirror_permutation(centers),
    )


def tetra_mirror_completion_matches_huntyen() -> bool:
    """Verify that the unit tetrahedron plus its mirror is the unit cube."""
    tetrahedron = terryen_unit_centers("tetra_terryen")
    completion = {
        tuple(round(component, 12) for component in center)
        for vertex in tetrahedron
        for center in (vertex, tuple(-component for component in vertex))
    }
    cube = {
        tuple(round(component, 12) for component in center)
        for center in terryen_unit_centers("huntyen")
    }
    return completion == cube


def orthographic_basis_4d(
    view_direction: Sequence[float] = (1.0, 2.0, 3.0, 4.0),
) -> tuple[Point, Point, Point]:
    """Build a deterministic orthonormal 3-frame perpendicular to a 4D view."""
    view = _normalized(view_direction)
    if len(view) != 4:
        raise ValueError("the 4D view direction must have four components")

    basis: list[Point] = []
    for axis in range(4):
        vector = tuple(1.0 if index == axis else 0.0 for index in range(4))
        projection = _dot(vector, view)
        work = tuple(
            value - projection * normal
            for value, normal in zip(vector, view, strict=True)
        )
        for previous in basis:
            projection = _dot(work, previous)
            work = tuple(
                value - projection * direction
                for value, direction in zip(work, previous, strict=True)
            )
        length = sqrt(_norm_squared(work))
        if length > 1e-12:
            basis.append(tuple(value / length for value in work))
        if len(basis) == 3:
            break
    if len(basis) != 3:
        raise RuntimeError("failed to construct a 4D projection basis")
    return basis[0], basis[1], basis[2]


def project_4d_point(
    point: Sequence[float],
    view_direction: Sequence[float] = (1.0, 2.0, 3.0, 4.0),
) -> tuple[float, float, float]:
    """Orthographically project one 4D point into the controlled 3-frame."""
    values = tuple(float(value) for value in point)
    if len(values) != 4:
        raise ValueError("a projected 4D point must have four components")
    basis = orthographic_basis_4d(view_direction)
    return tuple(_dot(values, direction) for direction in basis)  # type: ignore[return-value]


@dataclass(frozen=True)
class HeavenlyProjectionDiagnostic:
    """Quality checks for the default 24-cell projection into 3D."""

    normalized_view_direction: Point
    basis: tuple[Point, Point, Point]
    projected_centers: tuple[tuple[float, float, float], ...]
    distinct_projected_centers: int
    orthonormal_residual: float
    mirror_residual: float


def heavenly_projection_diagnostic(
    view_direction: Sequence[float] = (1.0, 2.0, 3.0, 4.0),
) -> HeavenlyProjectionDiagnostic:
    """Project Heavenly without the collisions caused by simply dropping W."""
    normalized_view = _normalized(view_direction)
    basis = orthographic_basis_4d(normalized_view)
    centers = terryen_unit_centers("heavenly")
    projected = tuple(
        tuple(_dot(center, direction) for direction in basis) for center in centers
    )
    distinct = len(
        {
            tuple(round(component, 12) for component in point)
            for point in projected
        }
    )
    orthonormal_residual = max(
        abs(_dot(left, right) - (1.0 if left_index == right_index else 0.0))
        for left_index, left in enumerate(basis)
        for right_index, right in enumerate(basis)
    )
    mirror = _mirror_permutation(centers)
    if mirror is None:
        raise RuntimeError("the Heavenly candidate must be centrally symmetric")
    mirror_residual = max(
        abs(projected[index][axis] + projected[opposite][axis])
        for index, opposite in enumerate(mirror)
        for axis in range(3)
    )
    return HeavenlyProjectionDiagnostic(
        normalized_view_direction=normalized_view,
        basis=basis,
        projected_centers=projected,
        distinct_projected_centers=distinct,
        orthonormal_residual=orthonormal_residual,
        mirror_residual=mirror_residual,
    )
