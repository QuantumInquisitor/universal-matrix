"""Minimal local transition kernel for neighboring Matrix cells.

This experimental bridge combines four constraints already present elsewhere in
the repository:

1. locality: only one oriented edge and its two endpoint cells participate;
2. reversibility: the local map is an orthogonal two-state rotation;
3. conservation: endpoint quadratic content is preserved exactly up to floating
   arithmetic;
4. gauge covariance: phase coupling depends only on the invariant combination

       Delta = phi_target - phi_source + theta_source_target.

A second channel is sensitive to the signed polarity difference between the
two cells. This preserves the user's micro-to-macro alternating-polarity design
idea without claiming it is established electromagnetism.

The model is an explicit ansatz, not a unique theorem of the canonical kernel.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from .matrix_ontology import CanonicalCoreAddress


def branch_sign(address: CanonicalCoreAddress) -> int:
    """Return +1 for the lower branch and -1 for the upper branch."""
    return 1 if address.polarity_bit == 0 else -1


def oriented_polarity(
    address: CanonicalCoreAddress,
    scale_level: int = 0,
) -> int:
    """Combine canonical branch with alternating nested-scale orientation."""
    if scale_level < 0:
        raise ValueError("scale_level must be non-negative")
    scale_sign = 1 if scale_level % 2 == 0 else -1
    return branch_sign(address) * scale_sign


def gauge_covariant_phase_difference(
    source_phase: float,
    target_phase: float,
    link_phase: float,
) -> float:
    """Gauge-invariant oriented phase difference."""
    for value in (source_phase, target_phase, link_phase):
        if not math.isfinite(value):
            raise ValueError("phases must be finite")
    return target_phase - source_phase + link_phase


def phase_exchange_carrier(delta: float) -> float:
    """Odd first-harmonic exchange carrier."""
    return math.sin(delta)


def polarity_exchange_carrier(
    source_polarity: int,
    target_polarity: int,
    delta: float,
) -> float:
    """Oriented opposite-polarity carrier.

    The polarity gradient is zero for like polarity and +/-1 for opposite
    polarity. Multiplication by cos(delta) keeps this channel maximal for
    phase-aligned opposite polarities and preserves orientation reversal.
    """
    if source_polarity not in (-1, 1) or target_polarity not in (-1, 1):
        raise ValueError("polarities must be -1 or +1")
    return (
        0.5
        * (source_polarity - target_polarity)
        * math.cos(delta)
    )


@dataclass(frozen=True)
class EdgeTransitionParameters:
    """Dimensionless local edge couplings.

    The numerical values remain physical-model inputs. They are not derived
    from the canonical finite kernel in v0.1.
    """

    phase_coupling: float = 0.0
    polarity_coupling: float = 0.0

    def __post_init__(self) -> None:
        for name, value in (
            ("phase_coupling", self.phase_coupling),
            ("polarity_coupling", self.polarity_coupling),
        ):
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and non-negative")


def local_edge_generator(
    source_phase: float,
    target_phase: float,
    link_phase: float,
    source_polarity: int,
    target_polarity: int,
    parameters: EdgeTransitionParameters,
) -> float:
    """Return the signed dimensionless generator for one oriented edge."""
    delta = gauge_covariant_phase_difference(
        source_phase,
        target_phase,
        link_phase,
    )
    return (
        parameters.phase_coupling
        * phase_exchange_carrier(delta)
        + parameters.polarity_coupling
        * polarity_exchange_carrier(
            source_polarity,
            target_polarity,
            delta,
        )
    )


def local_edge_generator_from_addresses(
    source_address: CanonicalCoreAddress,
    target_address: CanonicalCoreAddress,
    source_phase: float,
    target_phase: float,
    link_phase: float,
    parameters: EdgeTransitionParameters,
    source_scale_level: int = 0,
    target_scale_level: int = 0,
) -> float:
    """Evaluate the edge generator using ontology-aware polarity signs."""
    return local_edge_generator(
        source_phase,
        target_phase,
        link_phase,
        oriented_polarity(source_address, source_scale_level),
        oriented_polarity(target_address, target_scale_level),
        parameters,
    )


def conservative_exchange(
    source_content: float,
    target_content: float,
    generator: float,
    step: float,
) -> tuple[float, float]:
    """Apply the local orthogonal exchange map.

    The map is

        [a']   [ cos(d) -sin(d) ] [a]
        [b'] = [ sin(d)  cos(d) ] [b]

    with d = generator * step.

    Signed step is allowed so time reversal can be tested directly.
    """
    for name, value in (
        ("source_content", source_content),
        ("target_content", target_content),
        ("generator", generator),
        ("step", step),
    ):
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")

    angle = generator * step
    c = math.cos(angle)
    s = math.sin(angle)
    return (
        c * source_content - s * target_content,
        s * source_content + c * target_content,
    )


def transition_edge(
    source_content: float,
    target_content: float,
    source_address: CanonicalCoreAddress,
    target_address: CanonicalCoreAddress,
    source_phase: float,
    target_phase: float,
    link_phase: float,
    parameters: EdgeTransitionParameters,
    step: float,
    source_scale_level: int = 0,
    target_scale_level: int = 0,
) -> tuple[float, float]:
    """Evaluate and apply one ontology-aware local edge transition."""
    generator = local_edge_generator_from_addresses(
        source_address,
        target_address,
        source_phase,
        target_phase,
        link_phase,
        parameters,
        source_scale_level,
        target_scale_level,
    )
    return conservative_exchange(
        source_content,
        target_content,
        generator,
        step,
    )


def quadratic_content(
    source_content: float,
    target_content: float,
) -> float:
    return (
        source_content * source_content
        + target_content * target_content
    )


def gauge_transform_edge(
    source_phase: float,
    target_phase: float,
    link_phase: float,
    source_gauge_phase: float,
    target_gauge_phase: float,
) -> tuple[float, float, float]:
    """Apply the local U(1) convention used by the repository.

    phi_i -> phi_i + alpha_i
    theta_ij -> theta_ij + alpha_i - alpha_j
    """
    return (
        source_phase + source_gauge_phase,
        target_phase + target_gauge_phase,
        link_phase
        + source_gauge_phase
        - target_gauge_phase,
    )


def reverse_oriented_edge(
    source_phase: float,
    target_phase: float,
    link_phase: float,
    source_polarity: int,
    target_polarity: int,
) -> tuple[float, float, float, int, int]:
    """Return data for the same physical edge with opposite orientation."""
    return (
        target_phase,
        source_phase,
        -link_phase,
        target_polarity,
        source_polarity,
    )
