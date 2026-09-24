from __future__ import annotations

import pytest

from src import canonical_kernel as ck
from src.canonical_mod9_interface_audit import (
    doubling_is_translation,
    doubling_mod9,
    doubling_orbit,
    doubling_orbit_partition,
    encode_fiber_phase,
    expected_interface_action,
    expected_polarity_action,
    expected_reflection_action,
    expected_routing_action,
    fiber_phase,
    interface_coordinate_action,
    interface_fiber,
    mod9_fiber,
    polarity_coordinate_action,
    projected_translation_step,
    reflection_coordinate_action,
    routing_coordinate_action,
    verify_mod9_interface_audit,
)


def test_fiber_phase_coordinates_are_a_bijection_of_all_108_states():
    coordinates = {fiber_phase(n) for n in range(ck.N_CORE)}
    assert len(coordinates) == 108
    assert coordinates == {
        (fiber, phase)
        for fiber in range(9)
        for phase in range(12)
    }
    for n in range(ck.N_CORE):
        assert encode_fiber_phase(*fiber_phase(n)) == n


def test_interface_fibers_are_exactly_nine_twelve_state_e_orbits():
    fibers = tuple(interface_fiber(fiber) for fiber in range(9))
    assert len(fibers) == 9
    assert all(len(states) == 12 for states in fibers)
    assert set().union(*(set(states) for states in fibers)) == set(range(108))

    for fiber, states in enumerate(fibers):
        assert all(mod9_fiber(n) == fiber for n in states)
        assert tuple(ck.interface(n) for n in states) == states[1:] + states[:1]


def test_canonical_operators_have_exact_fiber_phase_actions():
    for n in range(108):
        fiber, phase = fiber_phase(n)
        assert interface_coordinate_action(n) == expected_interface_action(fiber, phase)
        assert polarity_coordinate_action(n) == expected_polarity_action(fiber, phase)
        assert reflection_coordinate_action(n) == expected_reflection_action(fiber, phase)
        assert routing_coordinate_action(n) == expected_routing_action(fiber, phase)


def test_interface_and_polarity_are_identity_on_the_mod9_quotient():
    assert projected_translation_step(ck.INTERFACE_STEP) == 0
    assert projected_translation_step(ck.POLARITY_STEP) == 0
    assert all(mod9_fiber(ck.interface(n)) == mod9_fiber(n) for n in range(108))
    assert all(mod9_fiber(ck.polarity(n)) == mod9_fiber(n) for n in range(108))


def test_canonical_route_projects_to_add_three_mod9():
    assert projected_translation_step(ck.ROUTING_STEP) == 3
    assert all(
        mod9_fiber(ck.route(n)) == (mod9_fiber(n) + 3) % 9
        for n in range(108)
    )


def test_doubling_mod9_has_exact_three_orbit_partition():
    assert doubling_orbit_partition() == (
        (0,),
        (3, 6),
        (1, 2, 4, 8, 7, 5),
    )
    assert doubling_orbit(9 % 9) == (0,)


def test_doubling_is_an_order_six_automorphism_but_not_a_translation():
    assert sorted(doubling_mod9(r) for r in range(9)) == list(range(9))
    for residue in range(9):
        value = residue
        for _ in range(6):
            value = doubling_mod9(value)
        assert value == residue
    assert doubling_is_translation() is False


def test_doubling_conjugates_plus_three_to_plus_six_on_quotient():
    for r in range(9):
        assert doubling_mod9((r + 3) % 9) == (doubling_mod9(r) + 6) % 9


@pytest.mark.parametrize(
    ("fiber", "phase"),
    [
        (-1, 0),
        (9, 0),
        (0, -1),
        (0, 12),
    ],
)
def test_invalid_fiber_phase_coordinates_are_rejected(fiber, phase):
    with pytest.raises(ValueError):
        encode_fiber_phase(fiber, phase)


def test_audit_verifier_passes():
    assert verify_mod9_interface_audit()
