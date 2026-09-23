from __future__ import annotations

from src.sri_yantra_huet_chambers import (
    HUET_CHAMBER_SYSTEM,
    all_rings_are_vertex_cycles,
    rings_are_mirror_closed,
    selected_chambers_are_conflict_free,
)


def test_huet_arrangement_derives_candidates_from_the_27_parent_edges():
    system = HUET_CHAMBER_SYSTEM

    assert len(system.segments) == 27
    assert len(system.nodes) == 69
    assert len(system.candidates) == 122


def test_huet_chamber_extractor_recovers_the_traditional_43():
    system = HUET_CHAMBER_SYSTEM

    assert system.chamber_count == 43
    assert system.ring_counts == (1, 8, 10, 10, 14)
    assert tuple(ring.expected_count for ring in system.rings) == (8, 10, 10, 14)


def test_central_chamber_is_the_unique_t1_t5_triangle():
    system = HUET_CHAMBER_SYSTEM
    central = system.candidates[system.central_candidate_id]

    assert central.support_triangle_ids == (1, 5)
    assert len(central.vertex_ids) == 3


def test_each_noncentral_enclosure_is_a_vertex_touching_cycle():
    system = HUET_CHAMBER_SYSTEM

    assert all_rings_are_vertex_cycles(system)
    assert system.ring_vertex_counts == (3, 16, 20, 20, 28)


def test_every_chamber_ring_is_closed_under_the_planar_mirror():
    assert rings_are_mirror_closed(HUET_CHAMBER_SYSTEM)


def test_selected_chambers_do_not_overlap_or_share_positive_edge_length():
    system = HUET_CHAMBER_SYSTEM

    assert selected_chambers_are_conflict_free(system)
    assert system.chamber_edge_count == 129


def test_all_43_selected_chambers_are_distinct_candidates():
    system = HUET_CHAMBER_SYSTEM

    assert len(system.selected_candidate_ids) == 43
    assert len(set(system.selected_candidate_ids)) == 43
