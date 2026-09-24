"""Exact mod-9 quotient and 12-phase interface decomposition of Z_108.

The canonical core has 108 states and interface operator E=T_9.  Because
108=9*12, reduction modulo nine labels the nine E-orbits and the quotient
inside each fiber carries a twelve-step interface phase.

This module also records the multiplication-by-two automorphism of Z_9.  Its
orbit structure is the exact arithmetic pattern

    (0), (3, 6), (1, 2, 4, 8, 7, 5).

That quotient automorphism is mathematically valid but is not promoted to a
canonical Universal Matrix transition law.
"""

from __future__ import annotations

from . import canonical_kernel as ck

MOD9_SIZE = 9
INTERFACE_PHASE_SIZE = 12


def mod9_fiber(n: int) -> int:
    """Return the canonical Z_9 quotient label of a Z_108 core state."""
    return (n % ck.N_CORE) % MOD9_SIZE


def interface_phase(n: int) -> int:
    """Return the unique phase k in n = r + 9k with r in 0..8 and k in 0..11."""
    core = n % ck.N_CORE
    return (core - core % MOD9_SIZE) // MOD9_SIZE


def fiber_phase(n: int) -> tuple[int, int]:
    """Return the exact set coordinates (mod-9 fiber, interface phase)."""
    return mod9_fiber(n), interface_phase(n)


def encode_fiber_phase(fiber: int, phase: int) -> int:
    """Invert :func:`fiber_phase` on the canonical representative range."""
    if fiber not in range(MOD9_SIZE):
        raise ValueError("fiber must lie in 0..8")
    if phase not in range(INTERFACE_PHASE_SIZE):
        raise ValueError("phase must lie in 0..11")
    return fiber + MOD9_SIZE * phase


def projected_translation_step(step: int) -> int:
    """Project a canonical additive translation step to Z_9."""
    return step % MOD9_SIZE


def interface_coordinate_action(n: int) -> tuple[int, int]:
    """Return the fiber/phase coordinates after one canonical E=T_9 step."""
    return fiber_phase(ck.interface(n))


def polarity_coordinate_action(n: int) -> tuple[int, int]:
    """Return the fiber/phase coordinates after P=T_54."""
    return fiber_phase(ck.polarity(n))


def reflection_coordinate_action(n: int) -> tuple[int, int]:
    """Return the fiber/phase coordinates after F(n)=107-n."""
    return fiber_phase(ck.reflect(n))


def routing_coordinate_action(n: int) -> tuple[int, int]:
    """Return the fiber/phase coordinates after the canonical T=T_21 route."""
    return fiber_phase(ck.route(n))


def expected_interface_action(fiber: int, phase: int) -> tuple[int, int]:
    """Exact coordinate law for E: (r,k)->(r,k+1)."""
    return fiber, (phase + 1) % INTERFACE_PHASE_SIZE


def expected_polarity_action(fiber: int, phase: int) -> tuple[int, int]:
    """Exact coordinate law for P: (r,k)->(r,k+6)."""
    return fiber, (phase + 6) % INTERFACE_PHASE_SIZE


def expected_reflection_action(fiber: int, phase: int) -> tuple[int, int]:
    """Exact coordinate law for F: (r,k)->(8-r,11-k)."""
    return 8 - fiber, 11 - phase


def expected_routing_action(fiber: int, phase: int) -> tuple[int, int]:
    """Exact coordinate law for T_21, including the mod-9 carry."""
    carry = 1 if fiber >= 6 else 0
    return (fiber + 3) % MOD9_SIZE, (phase + 2 + carry) % INTERFACE_PHASE_SIZE


def interface_fiber(fiber: int) -> tuple[int, ...]:
    """Return the twelve canonical states in one E-orbit/fiber."""
    if fiber not in range(MOD9_SIZE):
        raise ValueError("fiber must lie in 0..8")
    return tuple(encode_fiber_phase(fiber, phase) for phase in range(INTERFACE_PHASE_SIZE))


def doubling_mod9(residue: int) -> int:
    """Return multiplication by two in Z_9."""
    if residue not in range(MOD9_SIZE):
        raise ValueError("residue must lie in 0..8")
    return (2 * residue) % MOD9_SIZE


def doubling_orbit(start: int) -> tuple[int, ...]:
    """Return one complete orbit of the multiplication-by-two automorphism."""
    if start not in range(MOD9_SIZE):
        raise ValueError("start must lie in 0..8")
    orbit: list[int] = []
    current = start
    while current not in orbit:
        orbit.append(current)
        current = doubling_mod9(current)
    if current != start:
        raise RuntimeError("doubling orbit did not close at its start")
    return tuple(orbit)


def doubling_orbit_partition() -> tuple[tuple[int, ...], ...]:
    """Return the three disjoint Z_9 doubling orbits in canonical order."""
    return (
        doubling_orbit(0),
        doubling_orbit(3),
        doubling_orbit(1),
    )


def doubling_is_translation() -> bool:
    """Return whether multiplication by two equals one additive Z_9 translation."""
    return any(
        all(doubling_mod9(r) == (r + step) % MOD9_SIZE for r in range(MOD9_SIZE))
        for step in range(MOD9_SIZE)
    )


def verify_mod9_interface_audit() -> bool:
    """Run inexpensive exact checks for the quotient/decomposition contract."""
    seen = {fiber_phase(n) for n in range(ck.N_CORE)}
    if len(seen) != ck.N_CORE:
        return False
    if doubling_orbit_partition() != ((0,), (3, 6), (1, 2, 4, 8, 7, 5)):
        return False
    if doubling_is_translation():
        return False

    for n in range(ck.N_CORE):
        fiber, phase = fiber_phase(n)
        if encode_fiber_phase(fiber, phase) != n:
            return False
        if interface_coordinate_action(n) != expected_interface_action(fiber, phase):
            return False
        if polarity_coordinate_action(n) != expected_polarity_action(fiber, phase):
            return False
        if reflection_coordinate_action(n) != expected_reflection_action(fiber, phase):
            return False
        if routing_coordinate_action(n) != expected_routing_action(fiber, phase):
            return False
    return True


if verify_mod9_interface_audit() is not True:
    raise RuntimeError("canonical mod-9/interface decomposition audit failed")
