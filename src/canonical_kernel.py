"""Canonical mathematical kernel for the Universal Matrix.

This module implements only the finite discrete architecture. It intentionally
contains no claims about gravity, quantum mechanics, consciousness, or other
physical interpretations.
"""

N_CORE = 108
BOUNDARY_COUNT = 6
M_TOTAL = N_CORE + BOUNDARY_COUNT
REGISTER_SIZE = 64

INTERFACE_STEP = 9
SYNCHRONIZED_ROUTING_STEPS = (21, 57, 93)
# T^3 = E^7 permits all three lifts above. 21 is the canonical minimal-positive
# lift (reduced step 7 rather than 19 or 31), not a uniqueness theorem.
ROUTING_STEP = SYNCHRONIZED_ROUTING_STEPS[0]
POLARITY_STEP = 54
REGISTER_MULTIPLIER = 7

BOUNDARY_GATES = {
    "X_POS": 108,
    "X_NEG": 109,
    "Y_POS": 110,
    "Y_NEG": 111,
    "Z_POS": 112,
    "Z_NEG": 113,
}


def _core(n: int) -> int:
    """Return the canonical representative in Z_108."""
    return n % N_CORE


def translate(n: int, step: int) -> int:
    """Translate a core state in Z_108."""
    return (n + step) % N_CORE


def interface(n: int, power: int = 1) -> int:
    """E^power, where E = T_9."""
    return translate(n, INTERFACE_STEP * power)


def route(n: int, power: int = 1) -> int:
    """T^power, where T = T_21."""
    return translate(n, ROUTING_STEP * power)


def polarity(n: int) -> int:
    """P = T_54, the order-two core translation."""
    return translate(n, POLARITY_STEP)


def reflect(n: int) -> int:
    """F(n) = 107 - n on canonical core representatives."""
    return (N_CORE - 1 - _core(n)) % N_CORE


def register_address(n: int) -> int:
    """pi(n) = 7n mod 64 for the canonical representative of n."""
    return (REGISTER_MULTIPLIER * _core(n)) % REGISTER_SIZE


def routing_channel(n: int) -> int:
    """rho(n) = n mod 3."""
    return _core(n) % 3


def encode(r: int, q: int, s: int, u: int) -> int:
    """Encode mixed-radix coordinates n = r + 3q + 9s + 27u."""
    if r not in range(3) or q not in range(3) or s not in range(3) or u not in range(4):
        raise ValueError("expected r,q,s in 0..2 and u in 0..3")
    return r + 3 * q + 9 * s + 27 * u


def decode(n: int) -> tuple[int, int, int, int]:
    """Decode a canonical core state into (r,q,s,u)."""
    n = _core(n)
    r = n % 3
    q = (n // 3) % 3
    s = (n // 9) % 3
    u = n // 27
    return r, q, s, u


def projection_delta(n: int, step: int) -> int:
    """Actual register-address delta for a core translation."""
    return (register_address(translate(n, step)) - register_address(n)) % REGISTER_SIZE


def projection_delta_theorem(n: int, step: int) -> int:
    """Carry-aware formula: Delta pi = 7d + 12w (mod 64), 0 <= d < 108."""
    d = step % N_CORE
    n = _core(n)
    wrap = 1 if d and n >= N_CORE - d else 0
    return (REGISTER_MULTIPLIER * d + 12 * wrap) % REGISTER_SIZE


def synchronized_routing_steps() -> tuple[int, ...]:
    """Return all positive routing lifts satisfying the current synchronization constraints."""
    return SYNCHRONIZED_ROUTING_STEPS


def routing_orbit(start: int) -> tuple[int, ...]:
    """Return one complete T_21 orbit."""
    start = _core(start)
    out = []
    n = start
    while not out or n != start:
        out.append(n)
        n = route(n)
    return tuple(out)


def register_collision_pairs() -> tuple[tuple[int, int], ...]:
    """All distinct pairs of core states sharing a 64-address register location."""
    return tuple((n, n + REGISTER_SIZE) for n in range(N_CORE - REGISTER_SIZE))


def verify_kernel() -> bool:
    """Run inexpensive canonical identity checks."""
    if M_TOTAL != 114 or len(BOUNDARY_GATES) != 6:
        return False
    if set(BOUNDARY_GATES.values()) != set(range(108, 114)):
        return False
    for n in range(N_CORE):
        if interface(n, 12) != n:
            return False
        if route(n, 36) != n:
            return False
        if polarity(polarity(n)) != n:
            return False
        if route(n, 3) != interface(n, 7):
            return False
        if route(n, 18) != interface(n, 6) or route(n, 18) != polarity(n):
            return False
        if reflect(reflect(n)) != n:
            return False
        if reflect(route(reflect(n))) != route(n, -1):
            return False
        if reflect(interface(reflect(n))) != interface(n, -1):
            return False
        if reflect(polarity(n)) != polarity(reflect(n)):
            return False
        for d in (0, 1, 9, 18, 21, 54, 87, 107):
            if projection_delta(n, d) != projection_delta_theorem(n, d):
                return False
    return True
