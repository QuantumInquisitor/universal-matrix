import math
from collections import Counter
from dataclasses import replace

import pytest

from src.sri_yantra_chambers import extract_chambers
from src.sri_yantra_huet_planar import HUET_PLANAR_SOLUTION

TRIANGLES = tuple(t.vertices for t in HUET_PLANAR_SOLUTION.triangles)


@pytest.fixture(scope="module")
def geometry():
    return extract_chambers()


def area(points):
    a, b, c = points
    return abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])) / 2


def test_euler_identity_and_face_inventory(geometry):
    assert (len(geometry.vertices), len(geometry.edges), len(geometry.faces)) == (69, 142, 74)
    assert len(geometry.vertices) - len(geometry.edges) + len(geometry.faces) + 1 == 2
    # Some triangular faces have a fourth collinear incidence vertex.
    assert Counter(len(f.corners) for f in geometry.faces) == {3: 53, 4: 21}
    assert len(geometry.chamber_ids) == 43
    assert all(len(geometry.faces[i].corners) == 3 for i in geometry.chamber_ids)


def test_independent_generator_coverage_matches_dual_distance(geometry):
    assert all(len(face.generators) == face.depth for face in geometry.faces)
    assert tuple(len(ring) for ring in geometry.rings) == (14, 10, 10, 8, 1)
    assert tuple(geometry.faces[ring[0]].depth for ring in geometry.rings) == (1, 3, 5, 7, 9)
    for i, j in geometry.face_adjacency:
        first = set() if i == -1 else set(geometry.faces[i].generators)
        second = set() if j == -1 else set(geometry.faces[j].generators)
        assert len(first ^ second) == 1


def test_area_partition_recovers_each_original_generator(geometry):
    # Independent area conservation checks every extracted face assignment.
    for index, triangle in enumerate(TRIANGLES, 1):
        recovered = sum(f.area for f in geometry.faces if index in f.generators)
        assert recovered == pytest.approx(area(triangle), abs=2e-12)
    for face in geometry.faces:
        if face.is_chamber:
            assert face.area == pytest.approx(
                area(tuple(geometry.vertices[i] for i in face.corners)), abs=2e-12
            )


def test_rings_are_connected_vertex_contact_cycles(geometry):
    for ring in geometry.rings:
        cycle = geometry.ring_cycle(ring)
        assert set(cycle) == set(ring)
        if len(cycle) > 1:
            for i, j in zip(cycle, cycle[1:] + cycle[:1], strict=True):
                shared = set(geometry.faces[i].boundary) & set(geometry.faces[j].boundary)
                assert len(shared) == 1
    assert len(geometry.chamber_contacts) == 91
    # Neighboring selected chambers touch at points, never along an edge.
    selected = set(geometry.chamber_ids)
    assert not any(i in selected and j in selected for i, j in geometry.face_adjacency)
    for i, j in geometry.chamber_contacts:
        assert len(set(geometry.faces[i].boundary) & set(geometry.faces[j].boundary)) == 1
    with pytest.raises(ValueError, match="cycle"):
        geometry.ring_cycle(geometry.rings[0][:-1])


def test_reflection_is_an_involution_preserving_faces_and_depth(geometry):
    mirror = {}
    for i, (x, y) in enumerate(geometry.vertices):
        candidates = [j for j, p in enumerate(geometry.vertices) if math.dist(p, (x, -y)) < 1e-10]
        assert len(candidates) == 1
        mirror[i] = candidates[0]
    assert all(mirror[mirror[i]] == i for i in mirror)
    faces = {frozenset(f.boundary): f for f in geometry.faces}
    for face in geometry.faces:
        reflected = faces[frozenset(mirror[i] for i in face.boundary)]
        assert reflected.depth == face.depth
        assert reflected.generators == face.generators
        assert reflected.area == pytest.approx(face.area, abs=2e-12)


def test_independent_ring_constraint_solver_selects_identical_chambers(geometry):
    from src.sri_yantra_huet_chambers import HUET_CHAMBER_SYSTEM

    reference = HUET_CHAMBER_SYSTEM
    node_map = {}
    for i, point in enumerate(reference.nodes):
        matches = [
            j for j, other in enumerate(geometry.vertices) if math.dist(point, other) < 1e-10
        ]
        assert len(matches) == 1
        node_map[i] = matches[0]
    reference_rings = ((reference.central_candidate_id,),) + tuple(
        ring.candidate_ids for ring in reference.rings
    )
    for reference_ring, computed_ring in zip(reference_rings, geometry.rings[::-1], strict=True):
        expected = {
            frozenset(node_map[v] for v in reference.candidates[i].vertex_ids)
            for i in reference_ring
        }
        actual = {frozenset(geometry.faces[i].corners) for i in computed_ring}
        assert actual == expected


@pytest.mark.parametrize("tolerance", [1e-11, 1e-9, 1e-7])
def test_tolerance_sweep(tolerance, geometry):
    actual = extract_chambers(tolerance=tolerance)
    assert actual.edges == geometry.edges
    assert tuple(f.boundary for f in actual.faces) == tuple(f.boundary for f in geometry.faces)
    assert actual.chamber_contacts == geometry.chamber_contacts


@pytest.mark.parametrize("scale", [1e-5, 1.0, 1e5])
def test_rotation_translation_scale_and_reversed_input_order(scale, geometry):
    angle = 0.371
    co, si = math.cos(angle), math.sin(angle)
    triangles = tuple(
        tuple((scale * (co * x - si * y + 2), scale * (si * x + co * y - 3)) for x, y in t[::-1])
        for t in TRIANGLES[::-1]
    )
    actual = extract_chambers(triangles)
    assert tuple(len(actual.ring_cycle(ring)) for ring in actual.rings) == (14, 10, 10, 8, 1)
    assert len(actual.vertices) == len(geometry.vertices)
    assert sorted(f.area / scale**2 for f in actual.faces) == pytest.approx(
        sorted(f.area for f in geometry.faces), abs=2e-12
    )


def test_broken_concurrency_is_not_forced_to_expected_counts():
    changed = replace(HUET_PLANAR_SOLUTION.triangle(1), upper_slope=-1.2)
    actual = extract_chambers((changed.vertices,) + TRIANGLES[1:])
    assert tuple(len(ring) for ring in actual.rings) != (14, 10, 10, 8, 1)


@pytest.mark.parametrize("tolerance", [0, -1, 1e-3, math.nan, math.inf])
def test_invalid_tolerance_is_rejected(tolerance):
    with pytest.raises(ValueError, match="tolerance"):
        extract_chambers(tolerance=tolerance)


def test_invalid_geometry_is_rejected():
    with pytest.raises(ValueError, match="nine triangles"):
        extract_chambers(TRIANGLES[:8])
    with pytest.raises(ValueError, match="finite"):
        extract_chambers((((math.nan, 0), *TRIANGLES[0][1:]),) + TRIANGLES[1:])
    with pytest.raises(ValueError, match="degenerate"):
        extract_chambers((((0, 0), (0, 0), (1, 1)),) + TRIANGLES[1:])
    with pytest.raises(ValueError, match="collinear"):
        extract_chambers((TRIANGLES[1],) + TRIANGLES[1:])
