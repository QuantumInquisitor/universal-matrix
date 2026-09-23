from __future__ import annotations

from src.e8_radial_degree_audit import (
    E8RadialFit,
    e8_radial_degree_audit,
    existing_quantity_can_supply_e8_radius,
)


def test_no_existing_quantity_survives_the_e8_radial_no_duplication_audit():
    assert not existing_quantity_can_supply_e8_radius()


def test_all_existing_candidates_are_already_committed():
    ledger = e8_radial_degree_audit()
    existing = [entry for entry in ledger if entry.quantity != "new_e8_radial_amplitude"]
    assert existing
    assert all(entry.fit is E8RadialFit.NO_FIT_ALREADY_COMMITTED for entry in existing)


def test_distinct_e8_radial_dynamics_requires_a_new_degree():
    ledger = {entry.quantity: entry for entry in e8_radial_degree_audit()}
    assert (
        ledger["new_e8_radial_amplitude"].fit
        is E8RadialFit.OPEN_NEW_DEGREE_REQUIRED
    )
