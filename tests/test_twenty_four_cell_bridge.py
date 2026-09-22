from collections import Counter
from itertools import combinations

import pytest

from src.canonical_kernel import BOUNDARY_GATES
from src.four_dimensional_polytope_bridge import (
    TESSERACT_VERTICES,
    central_mirror_4d,
    tesseract_parity,
)
from src.stella_octangula_register_bridge import STELLA_VERTICES, gate_coordinate
from src.twenty_four_cell_bridge import (
    RADIUS_MATCHED_16_CELL_VERTICES,
    TETRAHEDRAL_EDGE_ROOTS,
    TWENTY_FOUR_CELL_FACET_NORMALS,
    TWENTY_FOUR_CELL_VERTICES,
    dot,
    edge_root_spinor_product,
    projected_xyz_multiplicities,
    squared_distance,
    tetrahedral_edge_roots,
    triality_transform,
    twenty_four_cell_edges,
    twenty_four_cell_facets,
    twenty_four_cell_symmetry_permutations,
    twenty_four_cell_triangular_faces,
    twenty_four_cell_vertices_from_tetrahedron,
)


def test_common_radius_union_is_exactly_tesseract_plus_16_cell():
    tesseract = set(TESSERACT_VERTICES)
    cross_polytope = set(RADIUS_MATCHED_16_CELL_VERTICES)

    assert tesseract.isdisjoint(cross_polytope)
    assert tesseract | cross_polytope == set(TWENTY_FOUR_CELL_VERTICES)
    assert len(TWENTY_FOUR_CELL_VERTICES) == 24
    assert {dot(vertex, vertex) for vertex in TWENTY_FOUR_CELL_VERTICES} == {4}


def test_both_stella_tetrahedra_have_the_same_twelve_a3_edge_roots():
    positive = set(tetrahedral_edge_roots(1))
    negative = set(tetrahedral_edge_roots(-1))

    assert positive == negative == set(TETRAHEDRAL_EDGE_ROOTS)
    assert len(positive) == 12
    assert {dot(root, root) for root in positive} == {2}
    assert all(sum(component == 0 for component in root) == 1 for root in positive)


@pytest.mark.parametrize("parity", (-1, 1))
def test_either_tetrahedron_generates_all_24_vertices_bottom_up(parity):
    assert set(twenty_four_cell_vertices_from_tetrahedron(parity)) == set(TWENTY_FOUR_CELL_VERTICES)


def test_edge_root_products_split_into_tesseract_and_scaled_16_cell_parts():
    products = {
        edge_root_spinor_product(left, right)
        for left in TETRAHEDRAL_EDGE_ROOTS
        for right in TETRAHEDRAL_EDGE_ROOTS
    }

    assert products & set(TESSERACT_VERTICES) == set(TESSERACT_VERTICES)
    assert products & set(RADIUS_MATCHED_16_CELL_VERTICES) == set(RADIUS_MATCHED_16_CELL_VERTICES)


def test_24_cell_has_the_exact_regular_edge_graph():
    edges = twenty_four_cell_edges()
    degree = Counter(vertex for edge in edges for vertex in edge)

    assert len(edges) == 96
    assert set(degree) == set(TWENTY_FOUR_CELL_VERTICES)
    assert set(degree.values()) == {8}
    assert {squared_distance(left, right) for left, right in edges} == {4}


def test_24_cell_has_96_triangular_faces():
    faces = twenty_four_cell_triangular_faces()

    assert len(faces) == 96
    assert all(
        squared_distance(left, right) == 4
        for face in faces
        for left, right in combinations(face, 2)
    )


def test_each_of_24_facets_is_a_six_vertex_octahedron():
    facets = twenty_four_cell_facets()
    edge_sets = {frozenset(edge) for edge in twenty_four_cell_edges()}
    face_sets = {frozenset(face) for face in twenty_four_cell_triangular_faces()}

    assert len(TWENTY_FOUR_CELL_FACET_NORMALS) == 24
    assert len(facets) == 24
    assert len(set(facets)) == 24
    for normal, facet in zip(TWENTY_FOUR_CELL_FACET_NORMALS, facets, strict=True):
        induced_edges = {
            frozenset(edge) for edge in combinations(facet, 2) if frozenset(edge) in edge_sets
        }
        induced_faces = {
            frozenset(face) for face in combinations(facet, 3) if frozenset(face) in face_sets
        }

        assert len(facet) == 6
        assert max(dot(normal, vertex) for vertex in TWENTY_FOUR_CELL_VERTICES) == 2
        assert all(dot(normal, vertex) == 2 for vertex in facet)
        assert len(induced_edges) == 12
        assert len(induced_faces) == 8
        assert set(Counter(vertex for edge in induced_edges for vertex in edge).values()) == {4}


def test_boundary_counts_satisfy_the_four_polytope_euler_relation():
    vertices = len(TWENTY_FOUR_CELL_VERTICES)
    edges = len(twenty_four_cell_edges())
    faces = len(twenty_four_cell_triangular_faces())
    cells = len(twenty_four_cell_facets())

    assert (vertices, edges, faces, cells) == (24, 96, 96, 24)
    assert vertices - edges + faces - cells == 0


def test_each_vertex_belongs_to_six_octahedral_cells():
    incidence = Counter(vertex for facet in twenty_four_cell_facets() for vertex in facet)

    assert set(incidence) == set(TWENTY_FOUR_CELL_VERTICES)
    assert set(incidence.values()) == {6}


def test_central_mirror_preserves_vertices_edges_and_opposite_facets():
    vertices = set(TWENTY_FOUR_CELL_VERTICES)
    edges = {frozenset(edge) for edge in twenty_four_cell_edges()}
    normal_to_facet = dict(
        zip(TWENTY_FOUR_CELL_FACET_NORMALS, twenty_four_cell_facets(), strict=True)
    )

    assert {central_mirror_4d(vertex) for vertex in vertices} == vertices
    assert {frozenset(central_mirror_4d(vertex) for vertex in edge) for edge in edges} == edges
    for normal, facet in normal_to_facet.items():
        opposite_normal = central_mirror_4d(normal)
        assert {central_mirror_4d(vertex) for vertex in facet} == set(
            normal_to_facet[opposite_normal]
        )


def test_xyz_projection_contains_stella_gates_and_doubled_center():
    counts = dict(projected_xyz_multiplicities())

    assert len(counts) == 15
    assert counts[(0, 0, 0)] == 2
    assert all(counts[vertex] == 2 for vertex in STELLA_VERTICES)
    assert all(
        counts[tuple(2 * component for component in gate_coordinate(label))] == 1
        for label in BOUNDARY_GATES
    )


def test_triality_exchanges_one_demitesseract_with_the_scaled_16_cell():
    cross_polytope = set(RADIUS_MATCHED_16_CELL_VERTICES)
    positive = {vertex for vertex in TESSERACT_VERTICES if tesseract_parity(vertex) == 1}
    negative = {vertex for vertex in TESSERACT_VERTICES if tesseract_parity(vertex) == -1}

    assert {triality_transform(vertex) for vertex in cross_polytope} == positive
    assert {triality_transform(vertex) for vertex in positive} == cross_polytope
    assert {triality_transform(vertex) for vertex in negative} == negative
    assert all(
        triality_transform(triality_transform(vertex)) == vertex
        for vertex in TWENTY_FOUR_CELL_VERTICES
    )


def test_triality_extends_384_signed_frames_to_1152_symmetries():
    permutations = twenty_four_cell_symmetry_permutations()

    assert len(permutations) == 1152
    assert len(set(permutations)) == 1152
    assert all(set(permutation) == set(range(24)) for permutation in permutations)


def test_non_edge_root_and_non_vertex_are_rejected():
    with pytest.raises(ValueError):
        edge_root_spinor_product((1, 0, 0), TETRAHEDRAL_EDGE_ROOTS[0])
    with pytest.raises(ValueError):
        triality_transform((0, 0, 0, 0))
