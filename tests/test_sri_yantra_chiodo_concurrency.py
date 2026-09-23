from __future__ import annotations

from src.sri_yantra_chiodo_concurrency import (
    APEX_BASE_INCIDENCES,
    COMMON_CIRCUMCIRCLE_PAIR,
    HUET_BASE_PARAMETERS,
    THREE_LINE_CONCURRENCIES,
    TRIANGLES,
    TriangleOrientation,
    constraint_degree,
    constraint_edges,
    every_triangle_participates,
)


def test_chiodo_orientation_inventory_matches_five_down_four_up():
    assert len(TRIANGLES) == 9
    assert sum(item.orientation is TriangleOrientation.DOWNWARD for item in TRIANGLES) == 5
    assert sum(item.orientation is TriangleOrientation.UPWARD for item in TRIANGLES) == 4


def test_common_circumcircle_is_t3_t7():
    assert tuple(item.index for item in COMMON_CIRCUMCIRCLE_PAIR) == (3, 7)


def test_seven_apex_base_incidences_are_encoded_exactly():
    assert tuple(
        (relation.apex_triangle.index, relation.base_triangle.index)
        for relation in APEX_BASE_INCIDENCES
    ) == (
        (8, 1),
        (6, 2),
        (9, 3),
        (1, 6),
        (5, 7),
        (4, 8),
        (2, 9),
    )


def test_twelve_three_line_concurrency_conditions_are_encoded_exactly():
    assert tuple(
        (
            relation.downward_leg.index,
            relation.base_triangle.index,
            relation.upward_leg.index,
        )
        for relation in THREE_LINE_CONCURRENCIES
    ) == (
        (1, 2, 7),
        (2, 3, 7),
        (1, 3, 8),
        (1, 4, 6),
        (1, 5, 9),
        (4, 6, 9),
        (2, 7, 9),
        (3, 7, 8),
        (3, 8, 9),
        (4, 4, 8),
        (5, 5, 6),
        (2, 6, 6),
    )


def test_huet_base_parameters_are_ordered_on_unit_diameter():
    assert 0 < HUET_BASE_PARAMETERS.p < HUET_BASE_PARAMETERS.q
    assert HUET_BASE_PARAMETERS.q < HUET_BASE_PARAMETERS.r
    assert HUET_BASE_PARAMETERS.r < HUET_BASE_PARAMETERS.s < 1
    assert HUET_BASE_PARAMETERS.triangle_base_points == {
        "t3": HUET_BASE_PARAMETERS.p,
        "t6": HUET_BASE_PARAMETERS.q,
        "t7": HUET_BASE_PARAMETERS.r,
        "t9": HUET_BASE_PARAMETERS.s,
    }


def test_sourced_constraint_graph_covers_all_nine_triangles():
    assert every_triangle_participates()
    assert len(constraint_edges()) > 8
    assert all(constraint_degree(index) > 0 for index in range(1, 10))
