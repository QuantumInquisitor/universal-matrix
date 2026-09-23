from __future__ import annotations

from src.e8_equivalence_map import (
    DIRECT_COEFFICIENT_ROOTS,
    STANDARD_E8_ROOTS,
    direct_simple_roots,
    expected_similarity_gram,
    h4_to_standard_e8_matrix,
    map_direct_root_to_standard,
    map_is_bijection,
    mirror_commutes,
    reflection_commutes,
    similarity_gram,
    standard_simple_roots,
)


def test_each_realization_yields_an_e8_simple_root_basis():
    assert len(direct_simple_roots()) == 8
    assert len(standard_simple_roots()) == 8


def test_equivalence_matrix_is_exact_scaled_orthogonal():
    matrix = h4_to_standard_e8_matrix()
    assert len(matrix) == 8
    assert all(len(row) == 8 for row in matrix)
    assert similarity_gram() == expected_similarity_gram()


def test_equivalence_maps_all_240_roots_bijectively():
    assert len(DIRECT_COEFFICIENT_ROOTS) == 240
    assert len(STANDARD_E8_ROOTS) == 240
    assert map_is_bijection()
    assert {
        map_direct_root_to_standard(root) for root in DIRECT_COEFFICIENT_ROOTS
    } == set(STANDARD_E8_ROOTS)


def test_central_mirror_commutes_for_every_root():
    assert all(mirror_commutes(root) for root in DIRECT_COEFFICIENT_ROOTS)


def test_root_reflections_commute_for_all_240_squared_pairs():
    for vector_index in range(240):
        for root_index in range(240):
            assert reflection_commutes(vector_index, root_index)
