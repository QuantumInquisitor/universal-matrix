"""Canonical 36-tick polarity clock derived from the T21 routing cycle.

The routing operator T has order 36 and satisfies

    T^18 = P
    T^36 = I

where P=T54 is the canonical polarity involution.

Define the dimensionless polarity clock phase after k routing ticks by

    phi_P(k) = 2*pi*k/36 = pi*k/18.

Then:
    k=0   -> phi=0       -> outward extremum
    k=9   -> phi=pi/2    -> first neutral crossing
    k=18  -> phi=pi      -> inward extremum and P
    k=27  -> phi=3pi/2   -> second neutral crossing
    k=36  -> phi=2pi     -> full return

The quarter-cycle operator is

    C = T^9 = T81,

with
    C^2 = P
    C^4 = I.

This supplies a dimensionless polarity clock directly from canonical routing.
It does not determine the physical duration of one tick.
"""

from __future__ import annotations

import math

try:
    from . import canonical_kernel as ck
except ImportError:
    import canonical_kernel as ck


ROUTING_TICKS_PER_CYCLE = 36
ROUTING_TICKS_PER_HALF_CYCLE = 18
ROUTING_TICKS_PER_QUARTER_CYCLE = 9
POLARITY_PHASE_PER_ROUTING_TICK = math.pi / 18.0


def polarity_phase_from_tick(tick: int) -> float:
    return (tick % ROUTING_TICKS_PER_CYCLE) * POLARITY_PHASE_PER_ROUTING_TICK


def clock_node(base_node: int, tick: int) -> int:
    return ck.route(base_node, tick)


def polarity_carrier_from_tick(tick: int) -> float:
    return math.cos(polarity_phase_from_tick(tick))


def transfer_carrier_from_tick(tick: int) -> float:
    return math.sin(polarity_phase_from_tick(tick))


def clock_sector(tick: int, tolerance: float = 1e-12) -> str:
    p = polarity_carrier_from_tick(tick)
    s = transfer_carrier_from_tick(tick)
    if abs(s) <= tolerance:
        return "outward-extremum" if p > 0 else "inward-extremum"
    if abs(p) <= tolerance:
        return "neutral-up" if s > 0 else "neutral-down"
    return "transition"


def verify_clock_identities(base_node: int = 0) -> bool:
    base_node %= ck.N_CORE
    quarter = ck.route(base_node, 9)
    half = ck.route(base_node, 18)
    full = ck.route(base_node, 36)

    return (
        quarter == ck.translate(base_node, 81)
        and half == ck.polarity(base_node)
        and full == base_node
        and ck.route(quarter, 9) == half
        and ck.route(half, 18) == base_node
    )
