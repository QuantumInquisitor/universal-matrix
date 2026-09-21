import math

from src import canonical_kernel as ck
from src.canonical_polarity_clock import (
    POLARITY_PHASE_PER_ROUTING_TICK,
    clock_node,
    clock_sector,
    polarity_carrier_from_tick,
    polarity_phase_from_tick,
    transfer_carrier_from_tick,
    verify_clock_identities,
)


def test_phase_increment_is_exactly_pi_over_18():
    assert math.isclose(
        POLARITY_PHASE_PER_ROUTING_TICK,
        math.pi / 18.0,
        rel_tol=0,
        abs_tol=0,
    )


def test_quarter_half_full_cycle_nodes():
    base = 7
    assert clock_node(base, 9) == ck.translate(base, 81)
    assert clock_node(base, 18) == ck.polarity(base)
    assert clock_node(base, 36) == base


def test_four_cardinal_clock_states():
    assert clock_sector(0) == "outward-extremum"
    assert clock_sector(9) == "neutral-up"
    assert clock_sector(18) == "inward-extremum"
    assert clock_sector(27) == "neutral-down"
    assert clock_sector(36) == "outward-extremum"


def test_carriers_match_quarter_cycle():
    assert math.isclose(polarity_carrier_from_tick(0), 1.0, abs_tol=1e-15)
    assert abs(polarity_carrier_from_tick(9)) < 1e-15
    assert math.isclose(polarity_carrier_from_tick(18), -1.0, abs_tol=1e-15)
    assert math.isclose(transfer_carrier_from_tick(9), 1.0, abs_tol=1e-15)
    assert math.isclose(transfer_carrier_from_tick(27), -1.0, abs_tol=1e-15)


def test_tick_phase_has_period_36():
    for k in range(72):
        assert math.isclose(
            polarity_phase_from_tick(k),
            polarity_phase_from_tick(k + 36),
            abs_tol=1e-15,
        )


def test_clock_identities_hold_for_all_core_nodes():
    assert all(verify_clock_identities(n) for n in range(ck.N_CORE))
