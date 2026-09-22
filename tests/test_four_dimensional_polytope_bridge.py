from collections import Counter

import pytest

from src.canonical_kernel import BOUNDARY_GATES, REGISTER_SIZE
from src.four_dimensional_polytope_bridge import (
    CROSS_POLYTOPE_VERTICES,
    HYPER_REGISTER_SIZE,
    TESSERACT_VERTICES,
    W_LAYERS,
    central_mirror_4d,
    central_mirror_hyper_address,
    cross_polytope_to_demitesseract,
    demitesseract_to_cross_polytope,
    demitesseract_vertices,
    drop_w,
    embed_register_address,
    embed_spatial_frame,
    embed_stella_vertex,
    fixed_w_slice,
    frame_orientation_4d,
    gate_spinor_product,
    hyper_address_components,
    hyper_pair_hamming_distance,
    hyper_register_distance_shell_counts,
    hyper_register_vertex_pair,
    hyper_relative_signature,
    hyper_vertex_pair_address,
    seed_projection_centers_4d,
    signed_frames_4d,
    sixteen_cell_vertices_from_gates,
    tesseract_parity,
    tesseract_vertex_from_index,
    tesseract_vertex_index,
    tesseract_vertices_from_gates,
    transform_coordinate_4d,
)
from src.seed_matrix_bridge import gate_assignments
from src.stella_octangula_register_bridge import (
    STELLA_VERTICES,
    central_mirror_coordinate,
    gate_coordinate,
    seed_shadow_centers,
    transform_vertex,
)


def squared_distance(left, right):
    return sum((a - b) ** 2 for a, b in zip(left, right, strict=True))


def rounded_points(points):
    return {tuple(round(component, 12) for component in point) for point in points}


def test_sixteen_tesseract_vertices_round_trip_through_four_bit_indices():
    assert len(TESSERACT_VERTICES) == 16
    assert len(set(TESSERACT_VERTICES)) == 16
    assert tuple(tesseract_vertex_index(v) for v in TESSERACT_VERTICES) == tuple(range(16))
    assert tuple(tesseract_vertex_from_index(i) for i in range(16)) == TESSERACT_VERTICES


def test_product_parity_partitions_the_tesseract_into_two_equal_halves():
    negative = set(demitesseract_vertices(-1))
    positive = set(demitesseract_vertices(1))

    assert len(negative) == len(positive) == 8
    assert negative.isdisjoint(positive)
    assert negative | positive == set(TESSERACT_VERTICES)


@pytest.mark.parametrize("parity", W_LAYERS)
def test_each_demitesseract_is_a_uniformly_scaled_regular_16_cell(parity):
    vertices = demitesseract_vertices(parity)
    mapped = {demitesseract_to_cross_polytope(vertex) for vertex in vertices}

    assert mapped == set(CROSS_POLYTOPE_VERTICES)
    for left in vertices:
        for right in vertices:
            assert squared_distance(left, right) == 4 * squared_distance(
                demitesseract_to_cross_polytope(left),
                demitesseract_to_cross_polytope(right),
            )


@pytest.mark.parametrize("parity", W_LAYERS)
def test_hadamard_demitesseract_map_round_trips(parity):
    for vertex in demitesseract_vertices(parity):
        cross_vertex = demitesseract_to_cross_polytope(vertex)

        assert cross_polytope_to_demitesseract(cross_vertex, parity) == vertex


@pytest.mark.parametrize("w_layer", W_LAYERS)
def test_fixed_w_tesseract_cells_recover_the_existing_stella_cube(w_layer):
    cell = fixed_w_slice(w_layer)

    assert len(cell) == 8
    assert {drop_w(vertex) for vertex in cell} == set(STELLA_VERTICES)
    assert all(vertex[3] == w_layer for vertex in cell)


def test_tesseract_parity_restricts_to_stella_parity_with_w_sign():
    for w_layer in W_LAYERS:
        for vertex in STELLA_VERTICES:
            embedded = embed_stella_vertex(vertex, w_layer)
            assert tesseract_parity(embedded) == w_layer * vertex[0] * vertex[1] * vertex[2]


def test_16_cell_projects_to_six_gates_and_a_twice_occupied_center():
    projected = [drop_w(vertex) for vertex in CROSS_POLYTOPE_VERTICES]
    counts = Counter(projected)

    assert counts[(0, 0, 0)] == 2
    assert set(counts) == {(0, 0, 0), *(gate_coordinate(label) for label in BOUNDARY_GATES)}
    assert all(counts[gate_coordinate(label)] == 1 for label in BOUNDARY_GATES)


def test_six_local_gates_generate_all_eight_16_cell_vertices():
    generated = {
        gate_spinor_product(left, right) for left in BOUNDARY_GATES for right in BOUNDARY_GATES
    }

    assert generated == set(CROSS_POLYTOPE_VERTICES)
    assert set(sixteen_cell_vertices_from_gates()) == set(CROSS_POLYTOPE_VERTICES)


def test_gate_products_separate_parallel_w_tips_from_orthogonal_xyz_tips():
    parallel_products = set()
    orthogonal_products = set()

    for left in BOUNDARY_GATES:
        for right in BOUNDARY_GATES:
            left_coordinate = gate_coordinate(left)
            right_coordinate = gate_coordinate(right)
            dot = sum(a * b for a, b in zip(left_coordinate, right_coordinate, strict=True))
            target = parallel_products if dot else orthogonal_products
            target.add(gate_spinor_product(left, right))

    assert parallel_products == {(0, 0, 0, -1), (0, 0, 0, 1)}
    assert orthogonal_products == {(*gate_coordinate(label), 0) for label in BOUNDARY_GATES}


def test_gate_generated_16_cell_lifts_to_the_whole_tesseract():
    assert set(tesseract_vertices_from_gates()) == set(TESSERACT_VERTICES)


def test_4d_16_cell_and_3d_stella_give_the_same_normalized_seed_shadow():
    assert rounded_points(seed_projection_centers_4d()) == rounded_points(seed_shadow_centers())


def test_hyper_register_is_four_exact_64_address_w_sheets():
    addresses = {
        embed_register_address(address, first_w, second_w)
        for address in range(REGISTER_SIZE)
        for first_w in W_LAYERS
        for second_w in W_LAYERS
    }

    assert addresses == set(range(HYPER_REGISTER_SIZE))
    for address in range(HYPER_REGISTER_SIZE):
        base_address, first_w, second_w = hyper_address_components(address)
        assert embed_register_address(base_address, first_w, second_w) == address


def test_all_256_hyper_addresses_are_ordered_tesseract_vertex_pairs():
    pairs = [hyper_register_vertex_pair(address) for address in range(HYPER_REGISTER_SIZE)]

    assert len(set(pairs)) == HYPER_REGISTER_SIZE
    assert {hyper_vertex_pair_address(first, second) for first, second in pairs} == set(
        range(HYPER_REGISTER_SIZE)
    )


def test_four_bit_distance_shells_extend_the_existing_pascal_pattern():
    assert hyper_register_distance_shell_counts() == (16, 64, 96, 64, 16)
    assert sum(hyper_register_distance_shell_counts()) == HYPER_REGISTER_SIZE


def test_4d_central_mirror_is_involutive_and_preserves_demitesseract_parity():
    for vertex in TESSERACT_VERTICES:
        mirrored = central_mirror_4d(vertex)

        assert central_mirror_4d(mirrored) == vertex
        assert tesseract_parity(mirrored) == tesseract_parity(vertex)


def test_4d_mirror_exchanges_w_slices_and_reduces_to_the_3d_mirror():
    for w_layer in W_LAYERS:
        for vertex in STELLA_VERTICES:
            mirrored = central_mirror_4d(embed_stella_vertex(vertex, w_layer))

            assert mirrored == embed_stella_vertex(central_mirror_coordinate(vertex), -w_layer)


def test_hyper_register_mirror_is_address_complement_and_preserves_distance():
    for address in range(HYPER_REGISTER_SIZE):
        mirrored = central_mirror_hyper_address(address)

        assert mirrored == HYPER_REGISTER_SIZE - 1 - address
        assert central_mirror_hyper_address(mirrored) == address
        assert hyper_relative_signature(mirrored) == hyper_relative_signature(address)
        assert hyper_pair_hamming_distance(mirrored) == hyper_pair_hamming_distance(address)


def test_four_dimensional_signed_frame_group_has_384_balanced_frames():
    frames = signed_frames_4d()
    orientations = Counter(frame_orientation_4d(frame) for frame in frames)

    assert len(frames) == 384
    assert len(set(frames)) == 384
    assert orientations == {-1: 192, 1: 192}


def test_existing_48_spatial_frames_embed_exactly_while_fixing_w():
    embedded_frames = {embed_spatial_frame(frame) for frame in gate_assignments()}

    assert len(embedded_frames) == 48
    assert embedded_frames <= set(signed_frames_4d())
    for frame in gate_assignments():
        embedded_frame = embed_spatial_frame(frame)
        for vertex in STELLA_VERTICES:
            for w_layer in W_LAYERS:
                assert transform_coordinate_4d(
                    embed_stella_vertex(vertex, w_layer), embedded_frame
                ) == embed_stella_vertex(transform_vertex(vertex, frame), w_layer)


def test_central_inversion_is_proper_in_4d_even_though_it_is_reflected_in_3d():
    central_inversion = (-1, -2, -3, -4)

    assert central_inversion in signed_frames_4d()
    assert frame_orientation_4d(central_inversion) == 1
    assert all(
        transform_coordinate_4d(vertex, central_inversion) == central_mirror_4d(vertex)
        for vertex in TESSERACT_VERTICES
    )


@pytest.mark.parametrize("index", (-1, 16))
def test_unknown_tesseract_index_is_rejected(index):
    with pytest.raises(ValueError):
        tesseract_vertex_from_index(index)


def test_invalid_four_dimensional_inputs_are_rejected():
    with pytest.raises(ValueError):
        tesseract_vertex_index((1, 1, 1, 0))
    with pytest.raises(ValueError):
        embed_stella_vertex(STELLA_VERTICES[0], 0)
    with pytest.raises(ValueError):
        hyper_register_vertex_pair(HYPER_REGISTER_SIZE)
    with pytest.raises(ValueError):
        frame_orientation_4d((1, 2, 3, 3))
