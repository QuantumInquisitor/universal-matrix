"""Derive the traditional 43 Sri Yantra chambers from the Huet planar geometry.

This module does not store a list of 43 chamber coordinates.

It starts from the 27 finite edges of the nine reconstructed maximal triangles,
builds their snapped planar intersection arrangement, enumerates every triangle
whose three sides are supported by the original maximal-triangle segments, and
then applies the traditional concentric-ring contract.

Chiodo records the central triangle as t1 intersect t5 and the surrounding
rows as 8, 10, 10, and 14 triangles.  In the rotated Huet coordinate system
the symmetry axis is horizontal.  The arrangement contains nine atomic
axis-symmetric triangular anchors: the central triangle plus two anchors for
each surrounding ring.

For each ring the extractor:
1. pairs the two axis anchors by inward-to-outward order;
2. searches the upper half for a chain of the required number of chambers,
   with consecutive chambers meeting at exactly one arrangement vertex;
3. mirrors that chain into the lower half;
4. rejects any full ring whose chambers overlap in area or share positive
   edge length;
5. combines the four rings with the central chamber and requires the complete
   43-chamber system to be globally conflict-free.

For the Huet reference geometry there is exactly one global solution.

The result is a finite geometric derivation.  The traditional ring counts are
the sourced contract being reconstructed; the individual chamber coordinates
and their incidence are outputs of the geometry rather than stored metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import atan2, hypot

from .sri_yantra_huet_planar import (
    HUET_PLANAR_SOLUTION,
    HuetPlanarSolution,
)

Point2D = tuple[float, float]

_NODE_TOLERANCE = 1e-9
_GEOMETRY_TOLERANCE = 1e-10


@dataclass(frozen=True)
class ParentSegment:
    """One finite edge belonging to one maximal Huet triangle."""

    triangle_index: int
    edge_name: str
    start: Point2D
    end: Point2D


@dataclass(frozen=True)
class ChamberCandidate:
    """One triangular circuit supported by the maximal-triangle linework."""

    vertex_ids: tuple[int, int, int]
    support_triangle_ids: tuple[int, ...]


@dataclass(frozen=True)
class ChamberRing:
    """One traditional concentric chamber ring."""

    name: str
    expected_count: int
    candidate_ids: tuple[int, ...]


@dataclass(frozen=True)
class ChamberSystem:
    """Complete 43-chamber reconstruction over one planar Huet solution."""

    nodes: tuple[Point2D, ...]
    segments: tuple[ParentSegment, ...]
    candidates: tuple[ChamberCandidate, ...]
    central_candidate_id: int
    rings: tuple[ChamberRing, ...]

    @property
    def selected_candidate_ids(self) -> tuple[int, ...]:
        selected = {self.central_candidate_id}
        for ring in self.rings:
            selected.update(ring.candidate_ids)
        return tuple(sorted(selected))

    @property
    def chamber_count(self) -> int:
        return len(self.selected_candidate_ids)

    @property
    def ring_counts(self) -> tuple[int, int, int, int, int]:
        return (1, *(len(ring.candidate_ids) for ring in self.rings))

    @property
    def ring_vertex_counts(self) -> tuple[int, int, int, int, int]:
        central = len(self.candidates[self.central_candidate_id].vertex_ids)
        counts = [central]
        for ring in self.rings:
            vertices = {
                vertex_id
                for candidate_id in ring.candidate_ids
                for vertex_id in self.candidates[candidate_id].vertex_ids
            }
            counts.append(len(vertices))
        return tuple(counts)

    @property
    def chamber_edge_count(self) -> int:
        edges = set()
        for candidate_id in self.selected_candidate_ids:
            vertices = self.candidates[candidate_id].vertex_ids
            for left, right in _candidate_edge_pairs(vertices):
                edges.add(tuple(sorted((left, right))))
        return len(edges)


def _cross_vectors(left: Point2D, right: Point2D) -> float:
    return left[0] * right[1] - left[1] * right[0]


def _subtract(left: Point2D, right: Point2D) -> Point2D:
    return left[0] - right[0], left[1] - right[1]


def _triangle_area_twice(first: Point2D, second: Point2D, third: Point2D) -> float:
    return abs(_cross_vectors(_subtract(second, first), _subtract(third, first)))


def _centroid(points: tuple[Point2D, Point2D, Point2D]) -> Point2D:
    return (
        sum(point[0] for point in points) / 3.0,
        sum(point[1] for point in points) / 3.0,
    )


def _point_distance(left: Point2D, right: Point2D) -> float:
    return hypot(left[0] - right[0], left[1] - right[1])


def _point_on_segment(
    point: Point2D,
    start: Point2D,
    end: Point2D,
    tolerance: float = _NODE_TOLERANCE,
) -> bool:
    direction = _subtract(end, start)
    offset = _subtract(point, start)
    length = hypot(*direction)
    if length <= tolerance:
        return _point_distance(point, start) <= tolerance

    if abs(_cross_vectors(direction, offset)) > tolerance * max(1.0, length):
        return False

    dot = offset[0] * direction[0] + offset[1] * direction[1]
    squared_length = direction[0] ** 2 + direction[1] ** 2
    return -tolerance <= dot <= squared_length + tolerance


def _segment_intersection_points(
    first_start: Point2D,
    first_end: Point2D,
    second_start: Point2D,
    second_end: Point2D,
    tolerance: float = _NODE_TOLERANCE,
) -> tuple[Point2D, ...]:
    first_direction = _subtract(first_end, first_start)
    second_direction = _subtract(second_end, second_start)
    denominator = _cross_vectors(first_direction, second_direction)
    displacement = _subtract(second_start, first_start)

    if abs(denominator) > tolerance:
        first_parameter = _cross_vectors(displacement, second_direction) / denominator
        second_parameter = _cross_vectors(displacement, first_direction) / denominator
        if (
            -tolerance <= first_parameter <= 1.0 + tolerance
            and -tolerance <= second_parameter <= 1.0 + tolerance
        ):
            point = (
                first_start[0] + first_parameter * first_direction[0],
                first_start[1] + first_parameter * first_direction[1],
            )
            return (point,)
        return ()

    if abs(_cross_vectors(displacement, first_direction)) > tolerance:
        return ()

    common = []
    for point in (first_start, first_end, second_start, second_end):
        if _point_on_segment(point, first_start, first_end, tolerance) and _point_on_segment(
            point,
            second_start,
            second_end,
            tolerance,
        ):
            if not any(_point_distance(point, existing) <= tolerance for existing in common):
                common.append(point)
    return tuple(common)


def _snap_point(nodes: list[Point2D], point: Point2D) -> int:
    for index, existing in enumerate(nodes):
        if _point_distance(existing, point) <= _NODE_TOLERANCE:
            return index
    nodes.append((float(point[0]), float(point[1])))
    return len(nodes) - 1


def _parent_segments(solution: HuetPlanarSolution) -> tuple[ParentSegment, ...]:
    segments = []
    for triangle in solution.triangles:
        apex, upper, lower = triangle.vertices
        segments.extend(
            (
                ParentSegment(triangle.index, "upper_leg", apex, upper),
                ParentSegment(triangle.index, "lower_leg", apex, lower),
                ParentSegment(triangle.index, "base", upper, lower),
            )
        )
    return tuple(segments)


def _arrangement_nodes(segments: tuple[ParentSegment, ...]) -> tuple[Point2D, ...]:
    nodes: list[Point2D] = []

    for segment in segments:
        _snap_point(nodes, segment.start)
        _snap_point(nodes, segment.end)

    for first, second in combinations(segments, 2):
        intersections = _segment_intersection_points(
            first.start,
            first.end,
            second.start,
            second.end,
        )
        for point in intersections:
            _snap_point(nodes, point)

    return tuple(nodes)


def _pair_support(
    nodes: tuple[Point2D, ...],
    segments: tuple[ParentSegment, ...],
) -> dict[tuple[int, int], tuple[int, ...]]:
    support: dict[tuple[int, int], tuple[int, ...]] = {}
    for left_id, right_id in combinations(range(len(nodes)), 2):
        segment_ids = tuple(
            segment_id
            for segment_id, segment in enumerate(segments)
            if _point_on_segment(nodes[left_id], segment.start, segment.end)
            and _point_on_segment(nodes[right_id], segment.start, segment.end)
        )
        if segment_ids:
            support[(left_id, right_id)] = segment_ids
    return support


def _candidate_edge_pairs(
    vertex_ids: tuple[int, int, int],
) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
    first, second, third = vertex_ids
    return (
        tuple(sorted((first, second))),
        tuple(sorted((second, third))),
        tuple(sorted((third, first))),
    )


def _enumerate_candidates(
    nodes: tuple[Point2D, ...],
    segments: tuple[ParentSegment, ...],
) -> tuple[ChamberCandidate, ...]:
    support = _pair_support(nodes, segments)
    candidates = []

    for vertex_ids in combinations(range(len(nodes)), 3):
        edge_pairs = _candidate_edge_pairs(vertex_ids)
        if any(edge not in support for edge in edge_pairs):
            continue

        points = tuple(nodes[vertex_id] for vertex_id in vertex_ids)
        if _triangle_area_twice(*points) <= _GEOMETRY_TOLERANCE:
            continue

        support_triangles = {
            segments[segment_id].triangle_index
            for edge in edge_pairs
            for segment_id in support[edge]
        }
        candidates.append(
            ChamberCandidate(
                vertex_ids=vertex_ids,
                support_triangle_ids=tuple(sorted(support_triangles)),
            )
        )

    return tuple(candidates)


def _candidate_points(
    candidate: ChamberCandidate,
    nodes: tuple[Point2D, ...],
) -> tuple[Point2D, Point2D, Point2D]:
    points = tuple(nodes[index] for index in candidate.vertex_ids)
    center = _centroid(points)
    return tuple(
        sorted(
            points,
            key=lambda point: atan2(point[1] - center[1], point[0] - center[0]),
        )
    )


def _candidate_centroid(
    candidate: ChamberCandidate,
    nodes: tuple[Point2D, ...],
) -> Point2D:
    return _centroid(_candidate_points(candidate, nodes))


def _mirror_node_map(nodes: tuple[Point2D, ...]) -> tuple[int, ...]:
    result = []
    for point in nodes:
        target = (point[0], -point[1])
        matches = [
            index
            for index, candidate in enumerate(nodes)
            if _point_distance(target, candidate) <= _NODE_TOLERANCE
        ]
        if len(matches) != 1:
            raise RuntimeError("every arrangement node must have one reflected partner")
        result.append(matches[0])
    return tuple(result)


def _mirror_candidate_map(
    candidates: tuple[ChamberCandidate, ...],
    node_mirror: tuple[int, ...],
) -> tuple[int, ...]:
    by_vertices = {
        tuple(sorted(candidate.vertex_ids)): index
        for index, candidate in enumerate(candidates)
    }
    result = []
    for candidate in candidates:
        mirrored_vertices = tuple(
            sorted(node_mirror[vertex_id] for vertex_id in candidate.vertex_ids)
        )
        try:
            result.append(by_vertices[mirrored_vertices])
        except KeyError as error:
            raise RuntimeError("every chamber candidate must have one reflected partner") from error
    return tuple(result)


def _point_in_triangle_strict(
    point: Point2D,
    triangle: tuple[Point2D, Point2D, Point2D],
) -> bool:
    signs = []
    for index in range(3):
        first = triangle[index]
        second = triangle[(index + 1) % 3]
        signs.append(_cross_vectors(_subtract(second, first), _subtract(point, first)))

    positive = all(value > _GEOMETRY_TOLERANCE for value in signs)
    negative = all(value < -_GEOMETRY_TOLERANCE for value in signs)
    return positive or negative


def _segment_parameter(point: Point2D, start: Point2D, end: Point2D) -> float:
    direction = _subtract(end, start)
    denominator = direction[0] ** 2 + direction[1] ** 2
    if denominator <= _GEOMETRY_TOLERANCE:
        return 0.0
    offset = _subtract(point, start)
    return (offset[0] * direction[0] + offset[1] * direction[1]) / denominator


def _segment_enters_triangle_interior(
    segment: ParentSegment,
    triangle: tuple[Point2D, Point2D, Point2D],
) -> bool:
    if _point_in_triangle_strict(segment.start, triangle) or _point_in_triangle_strict(
        segment.end,
        triangle,
    ):
        return True

    parameters = [0.0, 1.0]
    for index in range(3):
        edge_start = triangle[index]
        edge_end = triangle[(index + 1) % 3]
        for point in _segment_intersection_points(
            segment.start,
            segment.end,
            edge_start,
            edge_end,
        ):
            parameter = _segment_parameter(point, segment.start, segment.end)
            if -_NODE_TOLERANCE <= parameter <= 1.0 + _NODE_TOLERANCE:
                parameters.append(max(0.0, min(1.0, parameter)))

    parameters = sorted(parameters)
    unique_parameters = []
    for value in parameters:
        if not unique_parameters or abs(value - unique_parameters[-1]) > _NODE_TOLERANCE:
            unique_parameters.append(value)

    for left, right in zip(unique_parameters, unique_parameters[1:], strict=False):
        if right - left <= _NODE_TOLERANCE:
            continue
        parameter = 0.5 * (left + right)
        sample = (
            segment.start[0] + parameter * (segment.end[0] - segment.start[0]),
            segment.start[1] + parameter * (segment.end[1] - segment.start[1]),
        )
        if _point_in_triangle_strict(sample, triangle):
            return True

    return False


def _atomic_axis_candidates(
    nodes: tuple[Point2D, ...],
    segments: tuple[ParentSegment, ...],
    candidates: tuple[ChamberCandidate, ...],
    mirror_map: tuple[int, ...],
) -> tuple[int, ...]:
    atomic = []

    for candidate_id, candidate in enumerate(candidates):
        if mirror_map[candidate_id] != candidate_id:
            continue

        triangle = _candidate_points(candidate, nodes)
        vertex_set = set(candidate.vertex_ids)
        if any(
            node_id not in vertex_set and _point_in_triangle_strict(point, triangle)
            for node_id, point in enumerate(nodes)
        ):
            continue

        if any(_segment_enters_triangle_interior(segment, triangle) for segment in segments):
            continue

        atomic.append(candidate_id)

    return tuple(atomic)


def _projection_interval(
    points: tuple[Point2D, Point2D, Point2D],
    axis: Point2D,
) -> tuple[float, float]:
    values = [point[0] * axis[0] + point[1] * axis[1] for point in points]
    return min(values), max(values)


def _positive_edge_overlap(
    first_start: Point2D,
    first_end: Point2D,
    second_start: Point2D,
    second_end: Point2D,
) -> bool:
    first_direction = _subtract(first_end, first_start)
    second_direction = _subtract(second_end, second_start)

    if abs(_cross_vectors(first_direction, second_direction)) > _NODE_TOLERANCE:
        return False
    if abs(_cross_vectors(_subtract(second_start, first_start), first_direction)) > _NODE_TOLERANCE:
        return False

    axis = 0 if abs(first_direction[0]) >= abs(first_direction[1]) else 1
    first_interval = sorted((first_start[axis], first_end[axis]))
    second_interval = sorted((second_start[axis], second_end[axis]))
    overlap = min(first_interval[1], second_interval[1]) - max(
        first_interval[0],
        second_interval[0],
    )
    return overlap > _NODE_TOLERANCE


def _triangle_interiors_overlap(
    first: tuple[Point2D, Point2D, Point2D],
    second: tuple[Point2D, Point2D, Point2D],
) -> bool:
    for triangle in (first, second):
        for index in range(3):
            start = triangle[index]
            end = triangle[(index + 1) % 3]
            edge = _subtract(end, start)
            axis = (-edge[1], edge[0])
            first_interval = _projection_interval(first, axis)
            second_interval = _projection_interval(second, axis)
            overlap = min(first_interval[1], second_interval[1]) - max(
                first_interval[0],
                second_interval[0],
            )
            if overlap <= _GEOMETRY_TOLERANCE:
                return False
    return True


def _candidates_conflict(
    first: ChamberCandidate,
    second: ChamberCandidate,
    nodes: tuple[Point2D, ...],
) -> bool:
    first_points = _candidate_points(first, nodes)
    second_points = _candidate_points(second, nodes)

    if _triangle_interiors_overlap(first_points, second_points):
        return True

    for first_index in range(3):
        first_start = first_points[first_index]
        first_end = first_points[(first_index + 1) % 3]
        for second_index in range(3):
            second_start = second_points[second_index]
            second_end = second_points[(second_index + 1) % 3]
            if _positive_edge_overlap(
                first_start,
                first_end,
                second_start,
                second_end,
            ):
                return True

    return False


def _conflict_lookup(
    candidates: tuple[ChamberCandidate, ...],
    nodes: tuple[Point2D, ...],
) -> frozenset[tuple[int, int]]:
    conflicts = set()
    for first_id, second_id in combinations(range(len(candidates)), 2):
        if _candidates_conflict(candidates[first_id], candidates[second_id], nodes):
            conflicts.add((first_id, second_id))
    return frozenset(conflicts)


def _is_conflict(
    first_id: int,
    second_id: int,
    conflicts: frozenset[tuple[int, int]],
) -> bool:
    return tuple(sorted((first_id, second_id))) in conflicts


def _upper_candidate_ids(
    candidates: tuple[ChamberCandidate, ...],
    nodes: tuple[Point2D, ...],
) -> frozenset[int]:
    result = set()
    for candidate_id, candidate in enumerate(candidates):
        values = [nodes[vertex_id][1] for vertex_id in candidate.vertex_ids]
        if min(values) >= -_NODE_TOLERANCE and max(values) > _NODE_TOLERANCE:
            result.add(candidate_id)
    return frozenset(result)


def _touch_graph(
    candidates: tuple[ChamberCandidate, ...],
    conflicts: frozenset[tuple[int, int]],
) -> tuple[frozenset[int], ...]:
    adjacency = [set() for _ in candidates]
    for first_id, second_id in combinations(range(len(candidates)), 2):
        if _is_conflict(first_id, second_id, conflicts):
            continue
        shared = set(candidates[first_id].vertex_ids) & set(candidates[second_id].vertex_ids)
        if len(shared) == 1:
            adjacency[first_id].add(second_id)
            adjacency[second_id].add(first_id)
    return tuple(frozenset(neighbors) for neighbors in adjacency)


def _simple_paths(
    start: int,
    end: int,
    intermediate_count: int,
    adjacency: tuple[frozenset[int], ...],
    allowed: frozenset[int],
) -> tuple[tuple[int, ...], ...]:
    target_edges = intermediate_count + 1
    paths = []

    def search(path: list[int]) -> None:
        current = path[-1]
        edge_count = len(path) - 1
        if edge_count > target_edges:
            return
        if current == end:
            if edge_count == target_edges:
                paths.append(tuple(path))
            return

        for neighbor in sorted(adjacency[current]):
            if neighbor not in allowed or neighbor in path:
                continue
            search([*path, neighbor])

    search([start])
    return tuple(paths)


def _ring_options(
    start_anchor: int,
    end_anchor: int,
    expected_count: int,
    candidates: tuple[ChamberCandidate, ...],
    mirror_map: tuple[int, ...],
    conflicts: frozenset[tuple[int, int]],
    adjacency: tuple[frozenset[int], ...],
    upper_candidates: frozenset[int],
) -> tuple[tuple[int, ...], ...]:
    intermediate_count = (expected_count - 2) // 2
    allowed = frozenset({*upper_candidates, start_anchor, end_anchor})
    options = []

    for path in _simple_paths(
        start_anchor,
        end_anchor,
        intermediate_count,
        adjacency,
        allowed,
    ):
        full = {
            candidate_id
            for candidate_id in path
        }
        full.update(mirror_map[candidate_id] for candidate_id in path)

        if len(full) != expected_count:
            continue

        ordered = tuple(sorted(full))
        if any(
            _is_conflict(first_id, second_id, conflicts)
            for first_id, second_id in combinations(ordered, 2)
        ):
            continue

        options.append(ordered)

    return tuple(options)


def _candidate_centroid_x(
    candidate_id: int,
    candidates: tuple[ChamberCandidate, ...],
    nodes: tuple[Point2D, ...],
) -> float:
    return _candidate_centroid(candidates[candidate_id], nodes)[0]


def derive_huet_chambers(
    solution: HuetPlanarSolution = HUET_PLANAR_SOLUTION,
) -> ChamberSystem:
    """Derive the unique traditional 43-chamber system from Huet geometry."""
    segments = _parent_segments(solution)
    nodes = _arrangement_nodes(segments)
    candidates = _enumerate_candidates(nodes, segments)

    node_mirror = _mirror_node_map(nodes)
    mirror_map = _mirror_candidate_map(candidates, node_mirror)
    atomic_axis = _atomic_axis_candidates(
        nodes,
        segments,
        candidates,
        mirror_map,
    )

    if len(atomic_axis) != 9:
        raise RuntimeError(
            f"expected nine atomic symmetry-axis chambers, found {len(atomic_axis)}"
        )

    central_matches = [
        candidate_id
        for candidate_id in atomic_axis
        if candidates[candidate_id].support_triangle_ids == (1, 5)
    ]
    if len(central_matches) != 1:
        raise RuntimeError("the central t1-intersect-t5 chamber must be unique")
    central_id = central_matches[0]
    central_x = _candidate_centroid_x(central_id, candidates, nodes)

    left_anchors = sorted(
        (
            candidate_id
            for candidate_id in atomic_axis
            if _candidate_centroid_x(candidate_id, candidates, nodes) < central_x
        ),
        key=lambda candidate_id: central_x
        - _candidate_centroid_x(candidate_id, candidates, nodes),
    )
    right_anchors = sorted(
        (
            candidate_id
            for candidate_id in atomic_axis
            if _candidate_centroid_x(candidate_id, candidates, nodes) > central_x
        ),
        key=lambda candidate_id: _candidate_centroid_x(candidate_id, candidates, nodes)
        - central_x,
    )

    if len(left_anchors) != 4 or len(right_anchors) != 4:
        raise RuntimeError("the central chamber must have four nested anchor pairs")

    conflicts = _conflict_lookup(candidates, nodes)
    adjacency = _touch_graph(candidates, conflicts)
    upper_candidates = _upper_candidate_ids(candidates, nodes)

    ring_specs = (
        ("eight", 8),
        ("inner_ten", 10),
        ("outer_ten", 10),
        ("fourteen", 14),
    )

    option_sets = []
    for index, (name, expected_count) in enumerate(ring_specs):
        options = _ring_options(
            left_anchors[index],
            right_anchors[index],
            expected_count,
            candidates,
            mirror_map,
            conflicts,
            adjacency,
            upper_candidates,
        )
        if not options:
            raise RuntimeError(f"no admissible chamber chain found for ring {name}")
        option_sets.append((name, expected_count, options))

    global_solutions: list[tuple[ChamberRing, ...]] = []

    def combine(
        ring_index: int,
        selected: set[int],
        chosen: list[ChamberRing],
    ) -> None:
        if ring_index == len(option_sets):
            if len(selected) == 43:
                global_solutions.append(tuple(chosen))
            return

        name, expected_count, options = option_sets[ring_index]
        for option in options:
            option_set = set(option)
            if selected & option_set:
                continue
            if any(
                _is_conflict(existing, candidate_id, conflicts)
                for existing in selected
                for candidate_id in option_set
            ):
                continue

            combine(
                ring_index + 1,
                selected | option_set,
                [
                    *chosen,
                    ChamberRing(
                        name=name,
                        expected_count=expected_count,
                        candidate_ids=option,
                    ),
                ],
            )

    combine(0, {central_id}, [])

    if len(global_solutions) != 1:
        raise RuntimeError(
            "Huet chamber extraction must have one global solution; "
            f"found {len(global_solutions)}"
        )

    system = ChamberSystem(
        nodes=nodes,
        segments=segments,
        candidates=candidates,
        central_candidate_id=central_id,
        rings=global_solutions[0],
    )

    if system.chamber_count != 43:
        raise RuntimeError("the reconstructed Sri Yantra must contain 43 chambers")
    if system.ring_counts != (1, 8, 10, 10, 14):
        raise RuntimeError("the reconstructed chamber rings have the wrong counts")
    if system.ring_vertex_counts != (3, 16, 20, 20, 28):
        raise RuntimeError("the concentric chamber circuits have the wrong vertex counts")
    if system.chamber_edge_count != 129:
        raise RuntimeError("the 43 chambers must contribute 129 distinct chamber edges")

    return system


def selected_chambers_are_conflict_free(system: ChamberSystem) -> bool:
    """Return whether selected chambers have disjoint interiors and edge lengths."""
    selected = system.selected_candidate_ids
    return not any(
        _candidates_conflict(
            system.candidates[first_id],
            system.candidates[second_id],
            system.nodes,
        )
        for first_id, second_id in combinations(selected, 2)
    )


def ring_is_vertex_cycle(system: ChamberSystem, ring: ChamberRing) -> bool:
    """Return whether every chamber in a ring touches exactly two ring neighbors."""
    ring_ids = set(ring.candidate_ids)
    for candidate_id in ring.candidate_ids:
        neighbors = 0
        vertices = set(system.candidates[candidate_id].vertex_ids)
        for other_id in ring_ids - {candidate_id}:
            other_vertices = set(system.candidates[other_id].vertex_ids)
            if len(vertices & other_vertices) == 1:
                neighbors += 1
        if neighbors != 2:
            return False
    return True


def rings_are_mirror_closed(system: ChamberSystem) -> bool:
    """Return whether each concentric ring is closed under axis reflection."""
    node_mirror = _mirror_node_map(system.nodes)
    candidate_mirror = _mirror_candidate_map(system.candidates, node_mirror)
    return all(
        {
            candidate_mirror[candidate_id]
            for candidate_id in ring.candidate_ids
        }
        == set(ring.candidate_ids)
        for ring in system.rings
    )


def all_rings_are_vertex_cycles(system: ChamberSystem) -> bool:
    """Return whether all four noncentral rings are vertex-touching cycles."""
    return all(ring_is_vertex_cycle(system, ring) for ring in system.rings)


HUET_CHAMBER_SYSTEM = derive_huet_chambers()
