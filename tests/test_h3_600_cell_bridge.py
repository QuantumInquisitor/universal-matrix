from collections import Counter
from itertools import combinations

import pytest

from src.h3_600_cell_bridge import (
    H3_ROOTS,
    HURWITZ_24_CELL_VERTICES,
    SIX_HUNDRED_CELL_EDGE_SQUARED,
    SIX_HUNDRED_CELL_VERTICES,
    SNUB_24_CELL_VERTICES,
    central_mirror_4d,
    dot4,
    h3_reflect,
    h3_spinor_product,
    pure_h3_spinors,
    quaternion_product,
    six_hundred_cell_edges,
    six_hundred_cell_tetrahedral_cells,
    six_hundred_cell_triangular_faces,
    squared_distance4,
    vertex_cell_incidence_counts,
)
from src.platonic_solid_bridge import ONE, PHI, ZERO, PhiNumber, dot, solid_edges


def test_q_phi_general_division_is_exact():
    assert ONE / PHI == PHI - 1
    assert PHI / PHI == ONE
    assert PhiNumber(3, 2) / PhiNumber(3, 2) == ONE
    with pytest.raises(ZeroDivisionError):
        _ = ONE / ZERO


def test_icosahedron_edges_generate_exactly_thirty_unit_h3_roots():
    assert len(H3_ROOTS) == 30
    assert len(solid_edges("icosahedron")) == 30
    assert {dot(root, root) for root in H3_ROOTS} == {ONE}
    assert {tuple(-component for component in root) for root in H3_ROOTS} == set(H3_ROOTS)


def test_h3_root_set_is_closed_under_all_root_reflections():
    assert {h3_reflect(vector, root) for vector in H3_ROOTS for root in H3_ROOTS} == set(H3_ROOTS)


def test_h3_products_generate_120_unit_spinors_without_count_padding():
    products = {h3_spinor_product(left, right) for left in H3_ROOTS for right in H3_ROOTS}

    assert products == set(SIX_HUNDRED_CELL_VERTICES)
    assert len(products) == 120
    assert {dot4(vertex, vertex) for vertex in products} == {ONE}


def test_binary_icosahedral_spinors_are_closed_under_quaternion_multiplication():
    vertices = set(SIX_HUNDRED_CELL_VERTICES)

    assert {
        quaternion_product(left, right)
        for left in SIX_HUNDRED_CELL_VERTICES
        for right in SIX_HUNDRED_CELL_VERTICES
    } == vertices


def test_pure_spinors_recover_the_original_h3_root_system():
    pure = pure_h3_spinors()

    assert len(pure) == 30
    assert {vertex[:3] for vertex in pure} == set(H3_ROOTS)
    assert {vertex[3] for vertex in pure} == {ZERO}


def test_existing_24_cell_is_an_exact_subgroup_and_leaves_96_vertices():
    full = set(SIX_HUNDRED_CELL_VERTICES)
    hurwitz = set(HURWITZ_24_CELL_VERTICES)
    residue = set(SNUB_24_CELL_VERTICES)

    assert len(hurwitz) == 24
    assert len(residue) == 96
    assert hurwitz.isdisjoint(residue)
    assert hurwitz | residue == full
    assert {
        quaternion_product(left, right)
        for left in HURWITZ_24_CELL_VERTICES
        for right in HURWITZ_24_CELL_VERTICES
    } == hurwitz


def test_coordinate_shells_are_8_plus_16_plus_96():
    zero_counts = Counter(
        sum(component == ZERO for component in vertex) for vertex in SIX_HUNDRED_CELL_VERTICES
    )

    assert zero_counts == {3: 8, 0: 16, 1: 96}


def test_600_cell_has_720_regular_edges_and_degree_twelve():
    edges = six_hundred_cell_edges()
    degrees = Counter(vertex for edge in edges for vertex in edge)

    assert SIX_HUNDRED_CELL_EDGE_SQUARED == 2 - PHI
    assert len(edges) == 720
    assert set(degrees) == set(SIX_HUNDRED_CELL_VERTICES)
    assert set(degrees.values()) == {12}
    assert {squared_distance4(left, right) for left, right in edges} == {
        SIX_HUNDRED_CELL_EDGE_SQUARED
    }


def test_600_cell_has_1200_equilateral_triangular_faces():
    edge_sets = {frozenset(edge) for edge in six_hundred_cell_edges()}
    faces = six_hundred_cell_triangular_faces()

    assert len(faces) == 1200
    assert all(frozenset(edge) in edge_sets for face in faces for edge in combinations(face, 2))


def test_600_cell_has_600_regular_tetrahedral_cells():
    edge_sets = {frozenset(edge) for edge in six_hundred_cell_edges()}
    face_sets = {frozenset(face) for face in six_hundred_cell_triangular_faces()}
    cells = six_hundred_cell_tetrahedral_cells()

    assert len(cells) == 600
    for cell in cells:
        assert len(cell) == 4
        assert all(frozenset(edge) in edge_sets for edge in combinations(cell, 2))
        assert all(frozenset(face) in face_sets for face in combinations(cell, 3))


def test_boundary_incidence_and_euler_relation_are_exact():
    vertices = SIX_HUNDRED_CELL_VERTICES
    edges = six_hundred_cell_edges()
    faces = six_hundred_cell_triangular_faces()
    cells = six_hundred_cell_tetrahedral_cells()
    face_incidence = Counter(frozenset(face) for cell in cells for face in combinations(cell, 3))
    edge_cell_incidence = Counter(
        frozenset(edge) for cell in cells for edge in combinations(cell, 2)
    )

    assert len(vertices) - len(edges) + len(faces) - len(cells) == 0
    assert set(vertex_cell_incidence_counts()) == {20}
    assert set(face_incidence.values()) == {2}
    assert set(edge_cell_incidence.values()) == {5}


def test_central_mirror_preserves_vertices_edges_faces_and_cells():
    vertices = set(SIX_HUNDRED_CELL_VERTICES)
    edges = {frozenset(edge) for edge in six_hundred_cell_edges()}
    faces = {frozenset(face) for face in six_hundred_cell_triangular_faces()}
    cells = {frozenset(cell) for cell in six_hundred_cell_tetrahedral_cells()}

    assert {central_mirror_4d(vertex) for vertex in vertices} == vertices
    assert {frozenset(central_mirror_4d(vertex) for vertex in edge) for edge in edges} == edges
    assert {frozenset(central_mirror_4d(vertex) for vertex in face) for face in faces} == faces
    assert {frozenset(central_mirror_4d(vertex) for vertex in cell) for cell in cells} == cells


def test_spinor_mirror_law_distinguishes_one_and_two_input_inversion():
    root_set = set(H3_ROOTS)
    for left in H3_ROOTS:
        mirrored_left = tuple(-component for component in left)
        assert mirrored_left in root_set
        for right in H3_ROOTS:
            product = h3_spinor_product(left, right)
            assert h3_spinor_product(mirrored_left, right) == central_mirror_4d(product)
            mirrored_right = tuple(-component for component in right)
            assert h3_spinor_product(mirrored_left, mirrored_right) == product


def test_non_h3_inputs_and_non_spinors_are_rejected():
    invalid_root = (ZERO, ZERO, ZERO)
    invalid_spinor = (ZERO, ZERO, ZERO, ZERO)

    with pytest.raises(ValueError):
        h3_reflect(invalid_root, H3_ROOTS[0])
    with pytest.raises(ValueError):
        h3_spinor_product(invalid_root, H3_ROOTS[0])
    with pytest.raises(ValueError):
        quaternion_product(invalid_spinor, SIX_HUNDRED_CELL_VERTICES[0])
