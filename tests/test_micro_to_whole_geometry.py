from math import isclose

import pytest

from src.four_dimensional_polytope_bridge import (
    CROSS_POLYTOPE_VERTICES,
    TESSERACT_VERTICES,
    body_diagonal_projection,
    central_mirror_4d,
    cross_polytope_to_demitesseract,
    drop_w,
    gate_spinor_product,
)
from src.micro_to_whole_geometry import (
    CONSTRUCTION_ROUTES,
    boundary_gate_coordinates,
    central_mirror,
    centrally_symmetric_layer_names,
    downward_xyz_multiplicities,
    layer_by_name,
    micro_to_whole_layers,
    stella_vertices_from_gates,
)
from src.stella_octangula_register_bridge import (
    STELLA_VERTICES,
    central_mirror_gate,
)
from src.twenty_four_cell_bridge import (
    RADIUS_MATCHED_16_CELL_VERTICES,
    TETRAHEDRAL_EDGE_ROOTS,
    TWENTY_FOUR_CELL_VERTICES,
    edge_root_spinor_product,
)


def test_micro_to_whole_layers_have_exact_dimensions_and_counts():
    layers = micro_to_whole_layers()

    assert [(layer.name, layer.ambient_dimension, len(layer.coordinates)) for layer in layers] == [
        ("port_center", 2, 1),
        ("boundary_gates", 3, 6),
        ("seed_centers", 2, 7),
        ("stella_octangula", 3, 8),
        ("sixteen_cell", 4, 8),
        ("tesseract", 4, 16),
        ("twenty_four_cell", 4, 24),
    ]
    assert all(
        len(coordinate) == layer.ambient_dimension
        for layer in layers
        for coordinate in layer.coordinates
    )


def test_every_construction_route_references_a_real_layer():
    names = {layer.name for layer in micro_to_whole_layers()}

    assert {route.target for route in CONSTRUCTION_ROUTES} <= names
    assert {source for route in CONSTRUCTION_ROUTES for source in route.sources} <= names
    assert len(CONSTRUCTION_ROUTES) == 6


def test_six_gates_generate_the_stella_and_sixteen_cell_exactly():
    assert set(stella_vertices_from_gates()) == set(STELLA_VERTICES)
    assert set(layer_by_name("sixteen_cell").coordinates) == set(CROSS_POLYTOPE_VERTICES)
    assert {
        gate_spinor_product(left, right)
        for left in ("X_POS", "X_NEG", "Y_POS", "Y_NEG", "Z_POS", "Z_NEG")
        for right in ("X_POS", "X_NEG", "Y_POS", "Y_NEG", "Z_POS", "Z_NEG")
    } == set(CROSS_POLYTOPE_VERTICES)


def test_sixteen_cell_lifts_to_both_halves_of_the_tesseract():
    lifted = {
        cross_polytope_to_demitesseract(vertex, parity)
        for vertex in CROSS_POLYTOPE_VERTICES
        for parity in (-1, 1)
    }

    assert lifted == set(TESSERACT_VERTICES)
    assert lifted == set(layer_by_name("tesseract").coordinates)


def test_common_radius_union_is_the_twenty_four_cell():
    common_radius_union = set(TESSERACT_VERTICES) | set(RADIUS_MATCHED_16_CELL_VERTICES)

    assert common_radius_union == set(TWENTY_FOUR_CELL_VERTICES)
    assert common_radius_union == set(layer_by_name("twenty_four_cell").coordinates)


def test_downward_xyz_shadows_recover_smaller_layers_with_multiplicity():
    shadows = dict(downward_xyz_multiplicities())
    sixteen = dict(shadows["sixteen_cell"])
    tesseract = dict(shadows["tesseract"])
    twenty_four = dict(shadows["twenty_four_cell"])

    assert sixteen[(0, 0, 0)] == 2
    assert all(sixteen[gate] == 1 for gate in boundary_gate_coordinates())
    assert tesseract == {vertex: 2 for vertex in STELLA_VERTICES}
    assert twenty_four[(0, 0, 0)] == 2
    assert all(twenty_four[vertex] == 2 for vertex in STELLA_VERTICES)
    assert all(
        twenty_four[tuple(2 * component for component in gate)] == 1
        for gate in boundary_gate_coordinates()
    )


def test_seed_projection_is_one_center_plus_a_unit_hexagonal_ring():
    centers = layer_by_name("seed_centers").coordinates
    center, ring = centers[0], centers[1:]

    assert center == (0.0, 0.0)
    assert len(set(ring)) == 6
    assert all(isclose(x * x + y * y, 1.0) for x, y in ring)
    assert all(
        any(
            all(
                isclose(component, candidate_component)
                for component, candidate_component in zip(
                    central_mirror(point), candidate, strict=True
                )
            )
            for candidate in centers
        )
        for point in centers
    )


def test_every_layer_is_closed_under_the_same_central_mirror():
    layers = micro_to_whole_layers()

    assert set(centrally_symmetric_layer_names()) == {layer.name for layer in layers}
    for layer in layers:
        assert {central_mirror(point) for point in layer.coordinates} == set(layer.coordinates)


def test_linear_downward_projection_commutes_with_the_mirror():
    for vertex in (*CROSS_POLYTOPE_VERTICES, *TESSERACT_VERTICES, *TWENTY_FOUR_CELL_VERTICES):
        projected = body_diagonal_projection(drop_w(vertex))
        mirrored_projection = body_diagonal_projection(drop_w(central_mirror_4d(vertex)))

        assert mirrored_projection == pytest.approx(tuple(-component for component in projected))


def test_bilinear_generators_mirror_output_when_one_input_is_mirrored():
    labels = ("X_POS", "X_NEG", "Y_POS", "Y_NEG", "Z_POS", "Z_NEG")
    for left in labels:
        for right in labels:
            product = gate_spinor_product(left, right)
            mirrored = gate_spinor_product(central_mirror_gate(left), right)
            assert mirrored == central_mirror_4d(product)

    for left in TETRAHEDRAL_EDGE_ROOTS:
        for right in TETRAHEDRAL_EDGE_ROOTS:
            product = edge_root_spinor_product(left, right)
            mirrored = edge_root_spinor_product(tuple(-component for component in left), right)
            assert mirrored == central_mirror_4d(product)


def test_invalid_layer_name_is_rejected():
    with pytest.raises(ValueError, match="unknown geometry layer"):
        layer_by_name("literal_omniverse")
