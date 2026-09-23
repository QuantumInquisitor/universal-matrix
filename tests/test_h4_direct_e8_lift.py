from __future__ import annotations

from fractions import Fraction

from src.h4_direct_e8_lift import (
    DIRECT_E8_ROOTS,
    H4_ROOTS,
    PHI_H4_ROOTS,
    coefficient_lift_8d,
    coefficient_rank_8d,
    direct_e8_antipodal_pair_count,
    direct_e8_inner_product_spectrum,
    direct_e8_neighbor_counts,
    direct_e8_reflect,
    rational_dot_8d,
    reduced_inner_product,
)


def test_direct_lift_is_exactly_two_disjoint_h4_copies():
    assert len(H4_ROOTS) == 120
    assert len(PHI_H4_ROOTS) == 120
    assert len(DIRECT_E8_ROOTS) == 240
    assert set(H4_ROOTS).isdisjoint(PHI_H4_ROOTS)


def test_reduced_metric_is_ordinary_euclidean_metric_on_coefficient_lift():
    for left in DIRECT_E8_ROOTS:
        lifted_left = coefficient_lift_8d(left)
        for right in DIRECT_E8_ROOTS:
            lifted_right = coefficient_lift_8d(right)
            assert rational_dot_8d(lifted_left, lifted_right) == reduced_inner_product(left, right)


def test_direct_e8_roots_have_rank_eight_and_unit_norm():
    assert coefficient_rank_8d() == 8
    assert {reduced_inner_product(root, root) for root in DIRECT_E8_ROOTS} == {Fraction(1)}


def test_direct_e8_has_the_simply_laced_root_inner_product_spectrum():
    assert direct_e8_inner_product_spectrum() == (
        Fraction(-1),
        Fraction(-1, 2),
        Fraction(0),
        Fraction(1, 2),
        Fraction(1),
    )


def test_direct_e8_closes_under_every_root_reflection():
    root_set = set(DIRECT_E8_ROOTS)
    for vector in DIRECT_E8_ROOTS:
        for root in DIRECT_E8_ROOTS:
            assert direct_e8_reflect(vector, root) in root_set


def test_direct_e8_has_120_antipodal_pairs():
    assert direct_e8_antipodal_pair_count() == 120


def test_direct_e8_root_polytope_has_56_nearest_neighbors_per_root():
    assert set(direct_e8_neighbor_counts()) == {56}
