import math

from .canonical_kernel import (
    BOUNDARY_COUNT,
    BOUNDARY_GATES,
    M_TOTAL as CANONICAL_M_TOTAL,
    N_CORE,
    REGISTER_MULTIPLIER,
    REGISTER_SIZE,
    ROUTING_STEP,
    verify_kernel,
)

# Canonical architecture
M_TOTAL = CANONICAL_M_TOTAL
TOTAL_NODES = M_TOTAL
INTERNAL_CORE_NODES = N_CORE
EXTERNAL_GATE_NODES = BOUNDARY_COUNT

# Legacy aliases retained for compatibility with existing modules.
ELECTRIC_INWARD_NODES = 54
ELECTROMAGNETIC_OUTWARD_NODES = 54
ALPHA_GEOMETRIC = 1.0 / (54.0 * (math.pi ** 2))
GOLDEN_RATIO_RESONANCE = 1.618033988749895

# Legacy classification masks. These are not canonical transition operators.
TESLA_CONTROL_3_MASK = 0x2492492492492492
TESLA_CONTROL_6_MASK = 0x4924924924924924
TESLA_CONTROL_9_MASK = 0x9249249249249249
TESLA_TRIAD_MASK = TESLA_CONTROL_3_MASK | TESLA_CONTROL_6_MASK | TESLA_CONTROL_9_MASK

# Legacy name retained for API compatibility. Geometrically these are the six
# oriented external boundary gates, indexed outside the Z_108 routing core.
HYPERCUBE_FACE_GATES = {
    "FACE_X_POS": BOUNDARY_GATES["X_POS"],
    "FACE_X_NEG": BOUNDARY_GATES["X_NEG"],
    "FACE_Y_POS": BOUNDARY_GATES["Y_POS"],
    "FACE_Y_NEG": BOUNDARY_GATES["Y_NEG"],
    "FACE_Z_POS": BOUNDARY_GATES["Z_POS"],
    "FACE_Z_NEG": BOUNDARY_GATES["Z_NEG"],
}

# Explicit register/routing aliases for modules that have not yet migrated.
BIT_SHIFT_MULTIPLIER = REGISTER_MULTIPLIER
REGISTER_ADDRESS_COUNT = REGISTER_SIZE
INFINITY_STEP = ROUTING_STEP


def verify_structural_integrity():
    """Verify that this compatibility layer agrees with the canonical kernel."""
    return (
        verify_kernel()
        and M_TOTAL == 114
        and INTERNAL_CORE_NODES == 108
        and EXTERNAL_GATE_NODES == 6
        and set(HYPERCUBE_FACE_GATES.values()) == set(range(108, 114))
    )
