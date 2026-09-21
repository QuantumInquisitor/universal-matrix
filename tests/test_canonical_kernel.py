import math

from src.canonical_kernel import (
    BOUNDARY_GATES,
    M_TOTAL,
    N_CORE,
    REGISTER_SIZE,
    decode,
    encode,
    interface,
    polarity,
    projection_delta,
    projection_delta_theorem,
    reflect,
    register_address,
    register_collision_pairs,
    route,
    routing_channel,
    routing_orbit,
    verify_kernel,
    synchronized_routing_steps,
    routing_lift_properties,
    KERNEL_VERSION,
)


def test_kernel_version():
    assert KERNEL_VERSION == "0.4"


def test_architecture_cardinalities():
    assert N_CORE == 108
    assert M_TOTAL == 114
    assert REGISTER_SIZE == 64
    assert set(BOUNDARY_GATES.values()) == set(range(108, 114))


def test_mixed_radix_bijection():
    seen = set()
    for r in range(3):
        for q in range(3):
            for s in range(3):
                for u in range(4):
                    n = encode(r, q, s, u)
                    assert decode(n) == (r, q, s, u)
                    seen.add(n)
    assert seen == set(range(108))


def test_interface_order_12():
    assert all(interface(n, 12) == n for n in range(108))
    assert any(interface(n, 6) != n for n in range(108))


def test_synchronized_routing_lifts_and_minimal_convention():
    assert synchronized_routing_steps() == (21, 57, 93)
    for step in synchronized_routing_steps():
        assert math.gcd(step, 108) == 3
        assert (3 * step) % 108 == 63
    assert min(synchronized_routing_steps()) == 21


def test_exact_routing_lift_carry_counts():
    expected = {
        21: (7, 29, 21, 87, 19, 31),
        57: (19, 17, 57, 51, 15, 27),
        93: (31, 5, 93, 15, 11, 23),
    }
    for step, values in expected.items():
        p = routing_lift_properties(step)
        got = (
            p["wraps_per_orbit"], p["nonwraps_per_orbit"],
            p["wraps_total"], p["nonwraps_total"],
            p["nonwrap_register_delta"], p["wrap_register_delta"],
        )
        assert got == values
        # Each 36-state orbit closes after an integer number of 64-address turns.
        assert (p["nonwraps_per_orbit"] * p["nonwrap_register_delta"] +
                p["wraps_per_orbit"] * p["wrap_register_delta"]) % 64 == 0


def test_routing_three_cycles_of_36():
    orbits = [routing_orbit(r) for r in range(3)]
    assert [len(o) for o in orbits] == [36, 36, 36]
    assert set().union(*map(set, orbits)) == set(range(108))
    assert all(all(routing_channel(n) == r for n in orbit) for r, orbit in enumerate(orbits))


def test_synchronization_and_polarity():
    for n in range(108):
        assert route(n, 3) == interface(n, 7)
        assert route(n, 18) == interface(n, 6) == polarity(n)
        assert route(n, 36) == n
        assert polarity(polarity(n)) == n


def test_reflection_relations():
    for n in range(108):
        assert reflect(reflect(n)) == n
        assert reflect(route(reflect(n))) == route(n, -1)
        assert reflect(interface(reflect(n))) == interface(n, -1)
        assert reflect(polarity(n)) == polarity(reflect(n))


def test_projection_carry_theorem_exhaustive():
    for n in range(108):
        for d in range(108):
            assert projection_delta(n, d) == projection_delta_theorem(n, d)


def test_register_collision_topology():
    pairs = register_collision_pairs()
    assert len(pairs) == 44
    assert all(register_address(a) == register_address(b) for a, b in pairs)

    multiplicity = {a: 0 for a in range(64)}
    for n in range(108):
        multiplicity[register_address(n)] += 1

    assert sum(v == 2 for v in multiplicity.values()) == 44
    assert sum(v == 1 for v in multiplicity.values()) == 20
    assert max(multiplicity.values()) == 2


def test_scalar_identities():
    assert math.gcd(21, 108) == 3
    assert 7 * 9 == 3 * 21 == 63
    assert 63 == 64 - 1


def test_kernel_self_check():
    assert verify_kernel()
