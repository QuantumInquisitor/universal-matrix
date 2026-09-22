"""Canonical polarity / phase reduction bridge.

This module connects three existing descriptions without promoting a new
canonical law:

1. Exact canonical polarity branch:
       p in {0, 1}, with P=T_54 toggling p.

2. Independent local phase:
       phi.

3. Polarity-sensitive matter currents / fixed-amplitude complex matter.

If the local phase is independent of canonical polarity, the exact branch can
be encoded as a pi phase offset:

    phi_eff = phi + pi * p

because

    exp(i phi_eff) = (-1)^p exp(i phi).

Then a polarity-weighted sine factor is exactly equivalent to an ordinary
gauge-covariant sine of effective phases.

This gives a strict bookkeeping rule:
- use the branch offset when phase is independent of canonical polarity;
- do NOT add the same branch offset again when phase already represents the
  canonical polarity clock.

Otherwise the same polarity reversal is double counted.

The module also proves the fixed-amplitude reduction of the existing complex
matter link energy to the minimal rotor interaction:

    |exp(i theta) Phi_y - Phi_x|^2
      = 2 R^2 [1 - cos(delta_eff)]

for |Phi_x|=|Phi_y|=R.
"""

from __future__ import annotations

import math

from .matrix_ontology import CanonicalCoreAddress


TAU = 2.0 * math.pi


def principal_angle(angle: float) -> float:
    return (float(angle) + math.pi) % TAU - math.pi


def canonical_polarity_sign(address: CanonicalCoreAddress) -> int:
    """Return +1 for lower branch and -1 for upper branch."""
    return 1 if address.polarity_bit == 0 else -1


def phase_with_canonical_polarity(
    phase: float,
    address: CanonicalCoreAddress,
) -> float:
    """Encode the exact branch as a pi offset of an independent local phase."""
    if not math.isfinite(phase):
        raise ValueError("phase must be finite")
    return principal_angle(phase + math.pi * address.polarity_bit)


def gauge_covariant_difference(
    source_phase: float,
    target_phase: float,
    link_phase: float,
) -> float:
    if not all(math.isfinite(v) for v in (source_phase, target_phase, link_phase)):
        raise ValueError("phases must be finite")
    return principal_angle(target_phase - source_phase + link_phase)


def polarity_weighted_sine(
    source_phase: float,
    target_phase: float,
    link_phase: float,
    source_address: CanonicalCoreAddress,
    target_address: CanonicalCoreAddress,
) -> float:
    """Explicit sign representation used by polarity-sensitive current models."""
    delta = gauge_covariant_difference(
        source_phase,
        target_phase,
        link_phase,
    )
    return (
        canonical_polarity_sign(source_address)
        * canonical_polarity_sign(target_address)
        * math.sin(delta)
    )


def effective_phase_sine(
    source_phase: float,
    target_phase: float,
    link_phase: float,
    source_address: CanonicalCoreAddress,
    target_address: CanonicalCoreAddress,
) -> float:
    """Same current factor using branch-offset effective phases only."""
    source_eff = phase_with_canonical_polarity(
        source_phase,
        source_address,
    )
    target_eff = phase_with_canonical_polarity(
        target_phase,
        target_address,
    )
    delta_eff = gauge_covariant_difference(
        source_eff,
        target_eff,
        link_phase,
    )
    return math.sin(delta_eff)


def polarity_current_equivalence_error(
    source_phase: float,
    target_phase: float,
    link_phase: float,
    source_address: CanonicalCoreAddress,
    target_address: CanonicalCoreAddress,
) -> float:
    """Numerical difference between the two exactly equivalent representations."""
    return effective_phase_sine(
        source_phase,
        target_phase,
        link_phase,
        source_address,
        target_address,
    ) - polarity_weighted_sine(
        source_phase,
        target_phase,
        link_phase,
        source_address,
        target_address,
    )


def fixed_amplitude_complex_link_energy(
    amplitude: float,
    source_phase: float,
    target_phase: float,
    link_phase: float,
    source_address: CanonicalCoreAddress | None = None,
    target_address: CanonicalCoreAddress | None = None,
) -> float:
    """Complex-scalar nearest-neighbor gradient energy at equal amplitude.

    Computes |exp(i theta) Phi_target - Phi_source|^2 with both fields
    having magnitude amplitude. If addresses are supplied, their canonical
    branch is encoded as a pi phase offset.
    """
    if not math.isfinite(amplitude) or amplitude < 0:
        raise ValueError("amplitude must be finite and non-negative")

    sp = source_phase
    tp = target_phase

    if (source_address is None) != (target_address is None):
        raise ValueError("supply both addresses or neither")
    if source_address is not None and target_address is not None:
        sp = phase_with_canonical_polarity(sp, source_address)
        tp = phase_with_canonical_polarity(tp, target_address)

    delta = gauge_covariant_difference(sp, tp, link_phase)
    return 2.0 * amplitude * amplitude * (1.0 - math.cos(delta))


def equivalent_rotor_coupling(amplitude: float) -> float:
    """Coupling K such that K(1-cos delta) equals fixed-amplitude link energy."""
    if not math.isfinite(amplitude) or amplitude < 0:
        raise ValueError("amplitude must be finite and non-negative")
    return 2.0 * amplitude * amplitude


def rotor_link_energy(
    coupling: float,
    source_phase: float,
    target_phase: float,
    link_phase: float,
) -> float:
    if not math.isfinite(coupling) or coupling < 0:
        raise ValueError("coupling must be finite and non-negative")
    delta = gauge_covariant_difference(
        source_phase,
        target_phase,
        link_phase,
    )
    return coupling * (1.0 - math.cos(delta))


def canonical_half_cycle_consistency(
    phase_before: float,
    address_before: CanonicalCoreAddress,
) -> dict[str, float | int | bool]:
    """Show the representation choice across one exact P=T54 half-cycle.

    The exact half-cycle does two mathematically related things:
    - the canonical address branch flips;
    - the canonical polarity-clock phase advances by pi.

    If phase_before already denotes the canonical clock phase, applying both
    the pi clock advance and a branch-offset pi to the same physical polarity
    effect produces an additional 2*pi total offset and therefore no net sign
    change. That is the double-counting warning encoded here.
    """
    if not math.isfinite(phase_before):
        raise ValueError("phase_before must be finite")

    after = address_before.flipped()

    branch_only_before = phase_with_canonical_polarity(
        phase_before,
        address_before,
    )
    branch_only_after = phase_with_canonical_polarity(
        phase_before,
        after,
    )

    clock_only_after = principal_angle(phase_before + math.pi)

    clock_plus_branch_after = phase_with_canonical_polarity(
        phase_before + math.pi,
        after,
    )

    branch_sign_flipped = math.isclose(
        math.cos(branch_only_after),
        -math.cos(branch_only_before),
        abs_tol=1e-12,
    )
    clock_sign_flipped = math.isclose(
        math.cos(clock_only_after),
        -math.cos(principal_angle(phase_before)),
        abs_tol=1e-12,
    )
    double_count_returns_original_sign = math.isclose(
        math.cos(clock_plus_branch_after),
        math.cos(branch_only_before),
        abs_tol=1e-12,
    )

    return {
        "before_branch": address_before.polarity_bit,
        "after_branch": after.polarity_bit,
        "branch_sign_flipped": branch_sign_flipped,
        "clock_sign_flipped": clock_sign_flipped,
        "double_count_returns_original_sign": double_count_returns_original_sign,
    }
