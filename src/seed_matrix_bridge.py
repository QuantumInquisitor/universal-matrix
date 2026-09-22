"""Candidate bridge from Sevenfold Seed geometry to the 108:6 Matrix.

The Consciousness/Ether center is associated with the complete 108-state local
processor. The six ring positions are associated bijectively with the six
boundary gates. No elemental interpretation is used to select a preferred
spatial orientation.
"""

from __future__ import annotations

from itertools import permutations, product

from .canonical_kernel import BOUNDARY_GATES, N_CORE
from .sevenfold_seed_contract import RING_POSITIONS, SeedModel, reciprocal_pairs

SPATIAL_AXES = ("X", "Y", "Z")


def center_core_states() -> tuple[int, ...]:
    """Return the entire canonical processor associated with the Seed center."""
    return tuple(range(N_CORE))


def gate_assignments() -> tuple[tuple[str, ...], ...]:
    """Enumerate all opposite-preserving ring-to-gate assignments.

    A returned tuple is ordered by Seed ring positions 1 through 6. The three
    opposite Seed axes may permute over X, Y, and Z, and either end of each axis
    may carry its positive orientation. This leaves orientation open rather
    than choosing one from symbolism alone.
    """
    assignments = []
    for axes in permutations(SPATIAL_AXES):
        for signs in product((1, -1), repeat=3):
            mapping = [""] * len(RING_POSITIONS)
            for pair_index, (axis, sign) in enumerate(zip(axes, signs, strict=True)):
                positive = f"{axis}_POS"
                negative = f"{axis}_NEG"
                near, far = pair_index, pair_index + 3
                mapping[near], mapping[far] = (
                    (positive, negative) if sign == 1 else (negative, positive)
                )
            assignments.append(tuple(mapping))
    return tuple(assignments)


def assignment_gate_ids(assignment: tuple[str, ...]) -> tuple[int, ...]:
    """Translate a valid six-position assignment to canonical gate node IDs."""
    if len(assignment) != len(RING_POSITIONS):
        raise ValueError("assignment must contain six gate labels")
    if set(assignment) != set(BOUNDARY_GATES):
        raise ValueError("assignment must be a bijection over all boundary gates")
    return tuple(BOUNDARY_GATES[label] for label in assignment)


def elemental_gate_pairs(
    model: SeedModel,
    assignment: tuple[str, ...],
) -> tuple[tuple[str, str, str, str], ...]:
    """Report elemental and gate labels for the three reciprocal axes."""
    assignment_gate_ids(assignment)
    return tuple(
        (
            left.name,
            assignment[left.position - 1],
            right.name,
            assignment[right.position - 1],
        )
        for left, right in reciprocal_pairs(model)
    )
