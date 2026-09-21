"""Separate physical polarity clock phase from U(1) gauge phase.

A single angle cannot simultaneously be:
1. an absolute observable through cos(phi), and
2. a local U(1) gauge coordinate whose absolute value is redundant.

This module separates those roles.

polarity_phase:
    physical experimental clock/transition phase used by the polarity
    oscillator and neutral-crossing scale transfer.

gauge_phase:
    local U(1) matter phase. Only gauge-covariant combinations involving link
    phases are observable in the gauge adapter.

This separation is experimental architecture, but it prevents a direct
gauge-invariance contradiction.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


TAU = 2.0 * math.pi


def principal(angle: float) -> float:
    return (angle + math.pi) % TAU - math.pi


@dataclass
class PhaseState:
    polarity_phase: float = 0.0
    gauge_phase: float = 0.0

    @property
    def polarity_carrier(self) -> float:
        return math.cos(self.polarity_phase)

    @property
    def transfer_carrier(self) -> float:
        return math.sin(self.polarity_phase)

    def gauge_transform(self, alpha: float) -> "PhaseState":
        """Local U(1) transformation leaves physical polarity phase unchanged."""
        return PhaseState(
            polarity_phase=self.polarity_phase,
            gauge_phase=principal(self.gauge_phase + alpha),
        )


def gauge_covariant_difference(
    source: PhaseState,
    target: PhaseState,
    link_phase: float,
) -> float:
    """Return phi_g,target - phi_g,source + theta_source,target."""
    return principal(
        target.gauge_phase - source.gauge_phase + link_phase
    )


def transform_link_phase(
    link_phase: float,
    source_alpha: float,
    target_alpha: float,
) -> float:
    """theta_ij -> theta_ij + alpha_i - alpha_j."""
    return principal(link_phase + source_alpha - target_alpha)


def gauge_coupling_energy(
    source: PhaseState,
    target: PhaseState,
    link_phase: float,
    coupling: float = 1.0,
) -> float:
    if coupling < 0:
        raise ValueError("coupling must be non-negative")
    delta = gauge_covariant_difference(source, target, link_phase)
    return -coupling * math.cos(delta)
