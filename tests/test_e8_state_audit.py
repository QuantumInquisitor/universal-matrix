from __future__ import annotations

from fractions import Fraction

from src.e8_state_audit import (
    E8CartanState,
    E8StateFit,
    e8_state_audit,
    root_reflection_matches_geometry,
    standard_root_state,
)
from src.higher_dimensional_geometry import e8_roots_scaled


def test_existing_matrix_states_do_not_claim_a_full_e8_representation():
    ledger = e8_state_audit()
    assert ledger
    assert all(entry.fit is not E8StateFit.FULL_E8_REPRESENTATION for entry in ledger)


def test_su3_eight_component_field_is_explicitly_not_relabelled_e8():
    entry = next(item for item in e8_state_audit() if item.name == "su3_electric_components")
    assert entry.component_count == 8
    assert entry.fit is E8StateFit.NO_FIT


def test_h4_derived_eight_coordinates_are_only_weyl_space_candidate():
    entry = next(
        item for item in e8_state_audit()
        if item.name == "h4_e8_coefficient_coordinates"
    )
    assert entry.component_count == 8
    assert entry.fit is E8StateFit.WEYL_SPACE_ONLY


def test_cartan_state_preserves_norm_under_every_root_reflection_for_roots():
    roots = e8_roots_scaled()
    for vector in roots:
        state = standard_root_state(vector)
        for root in roots:
            reflected = state.reflect_in_standard_root(root)
            assert reflected.squared_norm == state.squared_norm


def test_cartan_state_reflection_matches_existing_geometry_action():
    roots = e8_roots_scaled()
    for vector in roots:
        for root in roots:
            assert root_reflection_matches_geometry(vector, root)


def test_cartan_state_central_mirror_is_involutive():
    state = E8CartanState(
        (
            Fraction(1),
            Fraction(2),
            Fraction(3),
            Fraction(4),
            Fraction(5),
            Fraction(6),
            Fraction(7),
            Fraction(8),
        )
    )
    assert state.central_mirror().central_mirror() == state
