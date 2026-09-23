from __future__ import annotations

from src.sri_yantra_incidence_topology_audit import (
    IncidenceKnowledge,
    all_locations,
    cyclic_edge_count,
    cyclic_neighbors,
    enclosure_interfaces,
    incidence_audit,
    spherical_chart_is_injective,
    spiral_cone_chart_is_injective,
    topology_change_detected_in_valid_candidate_charts,
    total_location_count,
)


def test_total_abstract_location_inventory_is_72():
    assert total_location_count() == 72
    assert len(all_locations()) == 72


def test_nine_enclosures_form_eight_declared_shell_interfaces():
    interfaces = enclosure_interfaces()
    assert len(interfaces) == 8
    assert len(set(interfaces)) == 8


def test_declared_cyclic_member_graph_has_expected_local_degrees():
    for location in all_locations():
        neighbors = cyclic_neighbors(location)
        if location.member_count == 1:
            assert neighbors == ()
        elif location.member_count == 2:
            assert len(neighbors) == 1
        else:
            assert len(neighbors) == 2
            assert len(set(neighbors)) == 2


def test_cyclic_edge_count_is_70():
    assert cyclic_edge_count() == 70


def test_missing_historical_incidence_is_explicitly_unknown():
    ledger = {entry.relation: entry for entry in incidence_audit()}
    assert (
        ledger["complete_43_triangle_intersection_graph"].status
        is IncidenceKnowledge.UNKNOWN_NOT_ENCODED
    )
    assert (
        ledger["generator_pair_intersection_multiplicities"].status
        is IncidenceKnowledge.UNKNOWN_NOT_ENCODED
    )
    assert (
        ledger["historical_plane_spherical_meru_topological_equivalence"].status
        is IncidenceKnowledge.UNKNOWN_NOT_ENCODED
    )


def test_spherical_candidate_chart_preserves_every_location():
    assert spherical_chart_is_injective()


def test_spiral_cone_candidate_chart_preserves_every_location():
    assert spiral_cone_chart_is_injective()


def test_no_topology_change_occurs_in_current_valid_candidate_charts():
    assert not topology_change_detected_in_valid_candidate_charts()
