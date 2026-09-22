from collections import Counter
from math import hypot

import pytest

from src.canonical_kernel import BOUNDARY_GATES, N_CORE, REGISTER_SIZE, register_address
from src.seed_matrix_bridge import gate_assignments
from src.stella_octangula_register_bridge import (
    CENTRAL_MIRROR_FRAME,
    STELLA_VERTICES,
    body_diagonal_projection,
    central_mirror_coordinate,
    central_mirror_gate,
    central_mirror_register_address,
    central_mirror_vertex,
    central_octahedron_vertices,
    core_state_vertex_pair,
    gate_coordinate,
    pair_hamming_distance,
    register_distance_shell_counts,
    register_frame_permutation,
    register_vertex_pair,
    relative_signature,
    seed_shadow_centers,
    tetrahedron_edges,
    tetrahedron_parity,
    tetrahedron_vertices,
    transform_coordinate,
    transform_vertex,
    vertex_from_index,
    vertex_index,
    vertex_pair_address,
)


def squared_distance(left, right):
    return sum((a - b) ** 2 for a, b in zip(left, right, strict=True))


def test_eight_cube_vertices_round_trip_through_three_bit_indices():
    assert len(STELLA_VERTICES) == 8
    assert len(set(STELLA_VERTICES)) == 8
    assert tuple(vertex_index(vertex) for vertex in STELLA_VERTICES) == tuple(range(8))
    assert tuple(vertex_from_index(index) for index in range(8)) == STELLA_VERTICES


@pytest.mark.parametrize("parity", (-1, 1))
def test_each_parity_class_is_a_regular_tetrahedron(parity):
    vertices = tetrahedron_vertices(parity)
    edges = tetrahedron_edges(parity)

    assert len(vertices) == 4
    assert len(edges) == 6
    assert all(tetrahedron_parity(vertex) == parity for vertex in vertices)
    assert {squared_distance(left, right) for left, right in edges} == {8}


def test_two_tetrahedra_partition_all_eight_outer_vertices():
    negative = set(tetrahedron_vertices(-1))
    positive = set(tetrahedron_vertices(1))

    assert negative.isdisjoint(positive)
    assert negative | positive == set(STELLA_VERTICES)


@pytest.mark.parametrize("parity", (-1, 1))
def test_each_tetrahedron_has_the_same_six_octahedral_edge_midpoints(parity):
    expected = {gate_coordinate(label) for label in BOUNDARY_GATES}

    assert set(central_octahedron_vertices(parity)) == expected


def test_all_64_register_addresses_are_ordered_eight_by_eight_vertex_pairs():
    pairs = [register_vertex_pair(address) for address in range(REGISTER_SIZE)]

    assert len(pairs) == 64
    assert len(set(pairs)) == 64
    assert {vertex_pair_address(first, second) for first, second in pairs} == set(
        range(REGISTER_SIZE)
    )


def test_relative_signatures_partition_the_register_into_eight_equal_classes():
    signature_counts = Counter(relative_signature(address) for address in range(64))

    assert set(signature_counts) == set(STELLA_VERTICES)
    assert set(signature_counts.values()) == {8}


def test_hamming_distance_shells_are_exactly_8_24_24_8():
    assert register_distance_shell_counts() == (8, 24, 24, 8)
    assert sum(register_distance_shell_counts()) == REGISTER_SIZE


def test_six_gate_coordinates_transform_equivariantly_in_every_frame():
    local_labels = ("X_POS", "Y_POS", "Z_POS", "X_NEG", "Y_NEG", "Z_NEG")

    for assignment in gate_assignments():
        for position, local_label in enumerate(local_labels):
            assert transform_coordinate(
                gate_coordinate(local_label), assignment
            ) == gate_coordinate(assignment[position])


def test_all_48_signed_frames_induce_distinct_64_address_permutations():
    permutations = [register_frame_permutation(frame) for frame in gate_assignments()]

    assert len(permutations) == 48
    assert len(set(permutations)) == 48
    assert all(set(permutation) == set(range(64)) for permutation in permutations)


def test_signed_frame_action_preserves_pair_distance():
    for frame in gate_assignments():
        permutation = register_frame_permutation(frame)
        for address, transformed_address in enumerate(permutation):
            assert pair_hamming_distance(transformed_address) == pair_hamming_distance(address)


def test_every_signed_frame_preserves_the_star_compound_as_a_whole():
    for frame in gate_assignments():
        assert {transform_vertex(vertex, frame) for vertex in STELLA_VERTICES} == set(
            STELLA_VERTICES
        )


def test_central_mirror_is_an_involution_and_swaps_the_two_tetrahedra():
    for vertex in STELLA_VERTICES:
        mirrored = central_mirror_vertex(vertex)

        assert central_mirror_vertex(mirrored) == vertex
        assert tetrahedron_parity(mirrored) == -tetrahedron_parity(vertex)


def test_central_mirror_exchanges_all_six_opposite_gates():
    for label in BOUNDARY_GATES:
        opposite = central_mirror_gate(label)

        assert central_mirror_gate(opposite) == label
        assert gate_coordinate(opposite) == central_mirror_coordinate(gate_coordinate(label))


def test_register_mirror_is_exactly_address_complement_and_an_involution():
    for address in range(REGISTER_SIZE):
        mirrored = central_mirror_register_address(address)

        assert mirrored == REGISTER_SIZE - 1 - address
        assert central_mirror_register_address(mirrored) == address
        assert relative_signature(mirrored) == relative_signature(address)
        assert pair_hamming_distance(mirrored) == pair_hamming_distance(address)


def test_reflected_frame_action_equals_the_explicit_register_mirror():
    assert CENTRAL_MIRROR_FRAME in gate_assignments()
    assert register_frame_permutation(CENTRAL_MIRROR_FRAME) == tuple(
        central_mirror_register_address(address) for address in range(REGISTER_SIZE)
    )


def test_body_diagonal_projection_of_eight_tips_has_seven_unique_points():
    projected = [body_diagonal_projection(vertex) for vertex in STELLA_VERTICES]
    rounded = {(round(x, 12), round(y, 12)) for x, y in projected}

    assert len(rounded) == 7
    assert sum(point == pytest.approx((0.0, 0.0)) for point in projected) == 2


def test_stella_projection_is_a_normalized_seed_center_pattern():
    center, *ring = seed_shadow_centers()

    assert center == (0.0, 0.0)
    assert len(ring) == 6
    assert all(hypot(*point) == pytest.approx(1.0) for point in ring)
    assert all(
        squared_distance(ring[index], ring[(index + 1) % len(ring)]) == pytest.approx(1.0)
        for index in range(len(ring))
    )


def test_inner_octahedron_and_outer_stella_project_as_aligned_scaled_hexagons():
    outer_ring = {
        tuple(round(component, 12) for component in body_diagonal_projection(vertex))
        for vertex in STELLA_VERTICES
        if len(set(vertex)) > 1
    }
    doubled_inner_ring = {
        tuple(
            round(2 * component, 12)
            for component in body_diagonal_projection(gate_coordinate(label))
        )
        for label in BOUNDARY_GATES
    }

    assert outer_ring == doubled_inner_ring


def test_projection_commutes_with_the_central_mirror():
    coordinates = (*STELLA_VERTICES, *((0, 0, 0),), *(gate_coordinate(g) for g in BOUNDARY_GATES))

    for coordinate in coordinates:
        projected = body_diagonal_projection(coordinate)
        mirrored_projection = body_diagonal_projection(central_mirror_coordinate(coordinate))

        assert mirrored_projection == pytest.approx(tuple(-component for component in projected))


def test_108_core_projection_covers_64_pairs_with_the_canonical_collision_pattern():
    projected = [core_state_vertex_pair(state) for state in range(N_CORE)]
    multiplicities = Counter(projected)

    assert len(multiplicities) == REGISTER_SIZE
    assert sum(count == 2 for count in multiplicities.values()) == 44
    assert sum(count == 1 for count in multiplicities.values()) == 20
    assert all(
        vertex_pair_address(*projected[state]) == register_address(state) for state in range(N_CORE)
    )


@pytest.mark.parametrize("index", (-1, 8))
def test_unknown_vertex_index_is_rejected(index):
    with pytest.raises(ValueError):
        vertex_from_index(index)


def test_non_stella_vertex_is_rejected():
    with pytest.raises(ValueError):
        vertex_index((1, 0, -1))


def test_unknown_register_address_is_rejected():
    with pytest.raises(ValueError):
        register_vertex_pair(64)
