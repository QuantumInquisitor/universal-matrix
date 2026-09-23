"""Numerically extract the Huet Sri Yantra chambers from finite triangle edges.

No chamber counts or circuit sizes enter the extraction. We split the edges at
their intersections, walk the planar faces, and compute dual-graph distance
from the exterior. Odd coverage by the nine generators selects the chambers;
for the Huet reference, coverage equals exterior depth on every bounded face.
The resulting odd-depth groups form four vertex-contact cycles and a center.

This is a floating-point geometry checkpoint, not a proof for the entire
four-parameter Chiodo family or for any spherical/Meru realization.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass

from .sri_yantra_huet_planar import HUET_PLANAR_SOLUTION

type Point = tuple[float, float]
type Edge = tuple[int, int]
type Triangle = tuple[Point, Point, Point]


def _subtract(a: Point, b: Point) -> Point:
    return a[0] - b[0], a[1] - b[1]


def _cross(a: Point, b: Point) -> float:
    return a[0] * b[1] - a[1] * b[0]


def _area(points: tuple[Point, ...]) -> float:
    return sum(_cross(a, b) for a, b in zip(points, points[1:] + points[:1], strict=False)) / 2


def _segment_distance(p: Point, a: Point, b: Point) -> float:
    u, v = _subtract(b, a), _subtract(p, a)
    parameter = max(0.0, min(1.0, (u[0] * v[0] + u[1] * v[1]) / math.dist(a, b) ** 2))
    return math.dist(p, (a[0] + parameter * u[0], a[1] + parameter * u[1]))


def _interior_sample(boundary, vertices, edges, tolerance) -> Point:
    # Move left from a CCW edge midpoint, by less than the distance to any
    # other graph edge. This works for concave faces too, unlike a centroid.
    a, b = max(
        zip(boundary, boundary[1:] + boundary[:1], strict=True),
        key=lambda edge: math.dist(vertices[edge[0]], vertices[edge[1]]),
    )
    p, q = vertices[a], vertices[b]
    midpoint = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    clearance = min(
        _segment_distance(midpoint, vertices[c], vertices[d]) for c, d in edges if {a, b} != {c, d}
    )
    offset = clearance / 4
    if offset <= 2 * tolerance:
        raise ValueError("face interior is unresolved at the requested tolerance")
    dx, dy = _subtract(q, p)
    length = math.hypot(dx, dy)
    return midpoint[0] - offset * dy / length, midpoint[1] + offset * dx / length


@dataclass(frozen=True)
class PlanarFace:
    """CCW bounded face; boundary keeps collinear incidence vertices."""

    boundary: tuple[int, ...]
    corners: tuple[int, ...]
    area: float
    depth: int
    generators: tuple[int, ...]

    @property
    def is_chamber(self) -> bool:
        return len(self.generators) % 2 == 1


@dataclass(frozen=True)
class ChamberComplex:
    vertices: tuple[Point, ...]
    edges: tuple[Edge, ...]
    faces: tuple[PlanarFace, ...]
    exterior_boundary: tuple[int, ...]
    # Face identifiers use -1 for the exterior, otherwise an index into faces.
    face_adjacency: tuple[Edge, ...]
    tolerance: float

    @property
    def chamber_ids(self) -> tuple[int, ...]:
        return tuple(i for i, face in enumerate(self.faces) if face.is_chamber)

    @property
    def rings(self) -> tuple[tuple[int, ...], ...]:
        """Groups ordered from exterior inward, without prescribed sizes."""
        depths = sorted({self.faces[i].depth for i in self.chamber_ids})
        return tuple(
            tuple(i for i in self.chamber_ids if self.faces[i].depth == depth) for depth in depths
        )

    @property
    def chamber_contacts(self) -> tuple[Edge, ...]:
        """Shared-vertex contacts, distinct from shared-edge face adjacency."""
        return tuple(
            (i, j)
            for k, i in enumerate(self.chamber_ids)
            for j in self.chamber_ids[k + 1 :]
            if set(self.faces[i].boundary) & set(self.faces[j].boundary)
        )

    def ring_cycle(self, ring: tuple[int, ...]) -> tuple[int, ...]:
        """Traverse a connected degree-two contact circuit (or singleton)."""
        if len(ring) == 1:
            return ring
        neighbors = {i: [] for i in ring}
        for i, j in self.chamber_contacts:
            if i in neighbors and j in neighbors:
                neighbors[i].append(j)
                neighbors[j].append(i)
        if not ring or any(len(items) != 2 for items in neighbors.values()):
            raise ValueError("ring does not form a vertex-contact cycle")
        cycle = [min(ring)]
        previous, current = cycle[0], min(neighbors[cycle[0]])
        while current != cycle[0]:
            if current in cycle:
                raise ValueError("ring contains a premature repeated vertex")
            cycle.append(current)
            following = next(i for i in neighbors[current] if i != previous)
            previous, current = current, following
        if set(cycle) != set(ring):
            raise ValueError("ring contains disconnected cycles")
        return tuple(cycle)


def extract_chambers(
    triangles: tuple[Triangle, ...] | None = None, *, tolerance: float = 1e-9
) -> ChamberComplex:
    """Extract a connected nine-triangle arrangement and its odd-coverage cells.

    ``tolerance`` is relative to the largest bounding-box side. Coordinates are
    normalized before intersection and incidence tests. Collinear overlapping
    edges and unresolved/degenerate faces are rejected, never silently dropped.
    Arbitrary input need not yield Sri Yantra rings; ``ring_cycle`` verifies them.
    """
    if not math.isfinite(tolerance) or not 0 < tolerance <= 1e-6:
        raise ValueError("tolerance must be finite and in (0, 1e-6]")
    if triangles is None:
        triangles = tuple(item.vertices for item in HUET_PLANAR_SOLUTION.triangles)
    if len(triangles) != 9 or any(len(t) != 3 for t in triangles):
        raise ValueError("expected nine triangles with three vertices each")
    points = tuple(p for t in triangles for p in t)
    if any(len(p) != 2 or not all(math.isfinite(v) for v in p) for p in points):
        raise ValueError("vertices must be finite planar points")
    origin = tuple(min(p[axis] for p in points) for axis in (0, 1))
    scale = max(max(p[axis] for p in points) - origin[axis] for axis in (0, 1))
    if scale <= 0 or not math.isfinite(scale):
        raise ValueError("triangle extent must be finite and positive")
    normalized = tuple(
        tuple(((x - origin[0]) / scale, (y - origin[1]) / scale) for x, y in t) for t in triangles
    )
    if any(abs(_area(t)) <= tolerance for t in normalized):
        raise ValueError("degenerate or unresolved generator triangle")
    segments = tuple((a, b) for t in normalized for a, b in zip(t, t[1:] + t[:1], strict=False))
    vertices: list[Point] = []

    def vertex_id(p: Point) -> int:
        for i, existing in enumerate(vertices):
            if math.dist(p, existing) <= tolerance:
                return i
        vertices.append(p)
        return len(vertices) - 1

    splits = [{vertex_id(a), vertex_id(b)} for a, b in segments]
    for i, (a, b) in enumerate(segments):
        u = _subtract(b, a)
        for j, (c, d) in enumerate(segments[:i]):
            v = _subtract(d, c)
            determinant = _cross(u, v)
            if abs(determinant) <= 1e-14 * math.hypot(*u) * math.hypot(*v):
                if abs(_cross(_subtract(c, a), u)) <= tolerance * math.hypot(*u):
                    raise ValueError("collinear generator edges are unsupported")
                continue
            t = _cross(_subtract(c, a), v) / determinant
            s = _cross(_subtract(c, a), u) / determinant
            if -tolerance / math.hypot(*u) <= t <= 1 + tolerance / math.hypot(
                *u
            ) and -tolerance / math.hypot(*v) <= s <= 1 + tolerance / math.hypot(*v):
                k = vertex_id((a[0] + t * u[0], a[1] + t * u[1]))
                splits[i].add(k)
                splits[j].add(k)

    edge_set: set[Edge] = set()
    for (a, _), ids in zip(segments, splits, strict=False):
        ordered = sorted(ids, key=lambda i: math.dist(a, vertices[i]))
        edge_set.update(tuple(sorted(edge)) for edge in zip(ordered, ordered[1:], strict=False))
    edges = tuple(sorted(edge_set))
    neighbors: dict[int, list[int]] = {i: [] for i in range(len(vertices))}
    for a, b in edges:
        neighbors[a].append(b)
        neighbors[b].append(a)
    for a, items in neighbors.items():
        items.sort(key=lambda b: math.atan2(*_subtract(vertices[b], vertices[a])[::-1]))

    # Keep the traversed face on the left of each directed atomic edge.
    left_face: dict[Edge, int] = {}
    boundaries: list[tuple[int, ...]] = []
    for edge in edges:
        for start in (edge, edge[::-1]):
            if start in left_face:
                continue
            boundary = []
            a, b = start
            while (a, b) not in left_face:
                left_face[a, b] = len(boundaries)
                boundary.append(a)
                items = neighbors[b]
                a, b = b, items[(items.index(a) - 1) % len(items)]
            if (a, b) != start:
                raise ValueError("face traversal did not close")
            boundaries.append(tuple(boundary))
    areas = [_area(tuple(vertices[i] for i in f)) for f in boundaries]
    exterior = [i for i, area in enumerate(areas) if area < 0]
    if len(exterior) != 1 or len(vertices) - len(edges) + len(boundaries) != 2:
        raise ValueError("expected one connected planar arrangement")
    outside = exterior[0]
    if any(abs(area) <= tolerance**2 for area in areas):
        raise ValueError("unresolved face at the requested tolerance")
    dual = {i: set() for i in range(len(boundaries))}
    for a, b in edges:
        first, second = left_face[a, b], left_face[b, a]
        dual[first].add(second)
        dual[second].add(first)
    depths = {outside: 0}
    queue = deque([outside])
    while queue:
        current = queue.popleft()
        for other in dual[current]:
            if other not in depths:
                depths[other] = depths[current] + 1
                queue.append(other)

    faces = []
    remap = {outside: -1}
    for i, boundary in enumerate(boundaries):
        if i == outside:
            continue
        corners = tuple(
            b
            for a, b, c in zip(
                boundary[-1:] + boundary[:-1], boundary, boundary[1:] + boundary[:1], strict=False
            )
            if abs(_cross(_subtract(vertices[b], vertices[a]), _subtract(vertices[c], vertices[a])))
            > tolerance * math.dist(vertices[a], vertices[c])
        )
        if len(corners) < 3:
            raise ValueError("face has fewer than three resolved corners")
        sample = _interior_sample(boundary, vertices, edges, tolerance)
        covering = []
        for index, triangle in enumerate(normalized, 1):
            distances = tuple(
                _cross(_subtract(b, a), _subtract(sample, a)) / math.dist(a, b)
                for a, b in zip(triangle, triangle[1:] + triangle[:1], strict=False)
            )
            if (
                all(value >= -tolerance for value in distances)
                or all(value <= tolerance for value in distances)
            ) and any(abs(value) <= tolerance for value in distances):
                raise ValueError("face sample lies on an unresolved generator boundary")
            if all(value > 0 for value in distances) or all(value < 0 for value in distances):
                covering.append(index)
        remap[i] = len(faces)
        faces.append(PlanarFace(boundary, corners, areas[i] * scale**2, depths[i], tuple(covering)))
    adjacency = tuple(sorted({tuple(sorted((remap[i], remap[j]))) for i in dual for j in dual[i]}))
    return ChamberComplex(
        tuple((x * scale + origin[0], y * scale + origin[1]) for x, y in vertices),
        edges,
        tuple(faces),
        boundaries[outside],
        adjacency,
        tolerance,
    )


if __name__ == "__main__":
    result = extract_chambers()
    print(f"Vertices: {len(result.vertices)}; atomic edges: {len(result.edges)}")
    print(f"Bounded regions: {len(result.faces)}; chambers: {len(result.chamber_ids)}")
    print(
        "Outer-to-inner circuit sizes:",
        tuple(len(result.ring_cycle(ring)) for ring in result.rings),
    )
