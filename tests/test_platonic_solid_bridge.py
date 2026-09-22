from collections import Counter
from itertools import combinations

import pytest

from src.platonic_solid_bridge import (
    CUBE_VERTICES,
    DODECAHEDRON_VERTICES,
    DUAL_SOLID_NAMES,
    ICOSAHEDRON_VERTICES,
    MIRROR_TETRAHEDRON_VERTICES,
    OCTAHEDRON_VERTICES,
    PHI,
    PLATONIC_SOLIDS,
    TETRAHEDRON_VERTICES,
    ZERO,
    PhiNumber,
    central_mirror,
    cross,
    dot,
    dual_face_center_matches,
    dual_vertices,
    face_center,
    platonic_solid,
    solid_edges,
    solid_faces,
    solid_signature,
    squared_distance,
)

EXPECTED_SIGNATURES = {
    "tetrahedron": (4, 6, 4),
    "cube": (8, 12, 6),
    "octahedron": (6, 12, 8),
    "dodecahedron": (20, 30, 12),
    "icosahedron": (12, 30, 20),
}


def test_phi_number_arithmetic_is_exact():
    assert PHI * PHI == PHI + 1
    assert (PHI - 1) * PHI == PhiNumber(1)
    assert PhiNumber(8, -4) == 4 * (PHI - 1) * (PHI - 1)


def test_all_five_platonic_signatures_are_derived_from_incidence():
    assert {solid.name for solid in PLATONIC_SOLIDS} == set(EXPECTED_SIGNATURES)
    assert {name: solid_signature(name) for name in EXPECTED_SIGNATURES} == EXPECTED_SIGNATURES


@pytest.mark.parametrize("name", EXPECTED_SIGNATURES)
def test_each_solid_is_centered_circumscribed_and_edge_regular(name):
    solid = platonic_solid(name)
    coordinate_sum = tuple(
        sum((vertex[axis] for vertex in solid.vertices), ZERO) for axis in range(3)
    )

    assert coordinate_sum == (ZERO, ZERO, ZERO)
    assert len({dot(vertex, vertex) for vertex in solid.vertices}) == 1
    assert {squared_distance(*edge) for edge in solid_edges(name)} == {solid.edge_squared}


@pytest.mark.parametrize("name", EXPECTED_SIGNATURES)
def test_every_vertex_has_uniform_edge_degree(name):
    solid = platonic_solid(name)
    degree = Counter(vertex for edge in solid_edges(name) for vertex in edge)

    assert set(degree) == set(solid.vertices)
    assert len(set(degree.values())) == 1


@pytest.mark.parametrize("name", EXPECTED_SIGNATURES)
def test_derived_faces_are_regular_cycles_and_satisfy_euler(name):
    solid = platonic_solid(name)
    edges = {frozenset(edge) for edge in solid_edges(name)}
    faces = solid_faces(name)

    assert len(solid.vertices) - len(edges) + len(faces) == 2
    for face in faces:
        induced_edges = [edge for edge in combinations(face, 2) if frozenset(edge) in edges]
        degree = Counter(vertex for edge in induced_edges for vertex in edge)
        assert len(face) == solid.face_size
        assert len(induced_edges) == solid.face_size
        assert set(degree.values()) == {2}


@pytest.mark.parametrize("name", EXPECTED_SIGNATURES)
def test_every_face_is_planar_with_one_exact_diagonal_length(name):
    edges = {frozenset(edge) for edge in solid_edges(name)}
    for face in solid_faces(name):
        origin = face[0]
        first = tuple(component - base for component, base in zip(face[1], origin, strict=True))
        second = tuple(component - base for component, base in zip(face[2], origin, strict=True))
        normal = cross(first, second)
        offsets = (
            tuple(component - base for component, base in zip(vertex, origin, strict=True))
            for vertex in face
        )
        diagonals = {
            squared_distance(left, right)
            for left, right in combinations(face, 2)
            if frozenset((left, right)) not in edges
        }

        assert normal != (ZERO, ZERO, ZERO)
        assert all(dot(normal, offset) == ZERO for offset in offsets)
        assert len(diagonals) <= 1


def test_existing_stella_geometry_supplies_the_first_three_solids():
    assert len(TETRAHEDRON_VERTICES) == 4
    assert len(CUBE_VERTICES) == 8
    assert len(OCTAHEDRON_VERTICES) == 6
    assert set(TETRAHEDRON_VERTICES).isdisjoint(MIRROR_TETRAHEDRON_VERTICES)
    assert set(TETRAHEDRON_VERTICES) | set(MIRROR_TETRAHEDRON_VERTICES) == set(CUBE_VERTICES)


def test_golden_ratio_coordinates_supply_the_missing_dual_pair():
    assert len(ICOSAHEDRON_VERTICES) == 12
    assert len(DODECAHEDRON_VERTICES) == 20
    assert {dot(vertex, vertex) for vertex in ICOSAHEDRON_VERTICES} == {PHI + 2}
    assert {dot(vertex, vertex) for vertex in DODECAHEDRON_VERTICES} == {PhiNumber(3)}


@pytest.mark.parametrize("name", EXPECTED_SIGNATURES)
def test_every_face_center_has_exactly_one_outward_dual_vertex(name):
    matches = dual_face_center_matches(name)

    assert len(matches) == len(solid_faces(name))
    assert {dual for _, dual in matches} == set(dual_vertices(name))


def test_duality_pairs_exchange_vertex_and_face_counts():
    for name, dual_name in DUAL_SOLID_NAMES.items():
        vertices, edges, faces = solid_signature(name)
        dual_vertices_count, dual_edges, dual_faces = solid_signature(dual_name)

        assert vertices == dual_faces
        assert edges == dual_edges
        assert faces == dual_vertices_count


def test_mirror_law_distinguishes_tetrahedron_from_the_other_four_solids():
    assert {central_mirror(vertex) for vertex in TETRAHEDRON_VERTICES} == set(
        MIRROR_TETRAHEDRON_VERTICES
    )
    assert set(TETRAHEDRON_VERTICES).isdisjoint(MIRROR_TETRAHEDRON_VERTICES)

    for name in ("cube", "octahedron", "dodecahedron", "icosahedron"):
        vertices = set(platonic_solid(name).vertices)
        assert {central_mirror(vertex) for vertex in vertices} == vertices


def test_tetrahedral_face_centers_point_to_the_mirrored_companion():
    centers = {face_center(face) for face in solid_faces("tetrahedron")}
    assert {tuple(component * 3 for component in center) for center in centers} == set(
        MIRROR_TETRAHEDRON_VERTICES
    )


def test_unknown_solid_is_rejected():
    with pytest.raises(ValueError, match="unknown Platonic solid"):
        platonic_solid("sphere")
