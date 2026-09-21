"""Experimental content-dependent physical clock law.

The canonical routing algebra fixes the dimensionless polarity phase advance

    dphi = pi/18

per routing tick.

This module does NOT change that discrete clock. It introduces a separate
physical tick duration tau_eff that may depend on local conserved quadratic
content relative to a reference/vacuum level.

Assumptions used to select the lapse family
--------------------------------------------
Let x be dimensionless excess content and L(x) > 0 the factor multiplying a
reference physical tick duration tau0.

We impose:
    L(0) = 1
    L(x+y) = L(x)L(y)
    continuity

The unique positive continuous family is

    L(x) = exp(g*x)

for a dimensionless coupling g.

Therefore

    tau_eff = tau0 * exp(g*x)
    clock_rate / reference_rate = exp(-g*x)

and, if one fixed physical link length is crossed per local tick,

    propagation_speed / reference_speed = exp(-g*x).

For weak content,
    L(x) = 1 + g*x + O(x^2).

This is an experimental bridge law. The composition assumption and coupling g
are not consequences of the canonical kernel and require independent physical
validation.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

try:
    from .canonical_polarity_clock import POLARITY_PHASE_PER_ROUTING_TICK
except ImportError:
    from canonical_polarity_clock import POLARITY_PHASE_PER_ROUTING_TICK


def excess_content(local_content: float, reference_content: float = 0.0) -> float:
    if local_content < 0 or reference_content < 0:
        raise ValueError("content values must be non-negative")
    return local_content - reference_content


def lapse_factor(
    local_content: float,
    coupling: float,
    reference_content: float = 0.0,
) -> float:
    """Positive multiplicative physical tick-duration factor."""
    if coupling < 0:
        raise ValueError("coupling must be non-negative")
    x = excess_content(local_content, reference_content)
    return math.exp(coupling * x)


def clock_rate_ratio(
    local_content: float,
    coupling: float,
    reference_content: float = 0.0,
) -> float:
    """Local physical clock rate divided by the reference clock rate."""
    return 1.0 / lapse_factor(local_content, coupling, reference_content)


def effective_tick_duration(
    reference_tick_duration: float,
    local_content: float,
    coupling: float,
    reference_content: float = 0.0,
) -> float:
    if reference_tick_duration <= 0:
        raise ValueError("reference_tick_duration must be positive")
    return reference_tick_duration * lapse_factor(
        local_content,
        coupling,
        reference_content,
    )


def physical_polarity_angular_frequency(
    reference_tick_duration: float,
    local_content: float,
    coupling: float,
    reference_content: float = 0.0,
) -> float:
    """Physical angular rate while preserving pi/18 phase per routing tick."""
    tau = effective_tick_duration(
        reference_tick_duration,
        local_content,
        coupling,
        reference_content,
    )
    return POLARITY_PHASE_PER_ROUTING_TICK / tau


def propagation_speed_ratio(
    local_content: float,
    coupling: float,
    reference_content: float = 0.0,
) -> float:
    """Speed ratio for the hypothesis 'one fixed link per local tick'."""
    return clock_rate_ratio(local_content, coupling, reference_content)


def effective_refractive_index(
    local_content: float,
    coupling: float,
    reference_content: float = 0.0,
) -> float:
    """Equivalent travel-time index n=c_ref/c_eff under the link-per-tick map."""
    return lapse_factor(local_content, coupling, reference_content)


@dataclass(frozen=True)
class ContentClockState:
    local_content: float
    coupling: float
    reference_content: float = 0.0
    reference_tick_duration: float = 1.0

    @property
    def lapse(self) -> float:
        return lapse_factor(
            self.local_content,
            self.coupling,
            self.reference_content,
        )

    @property
    def tick_duration(self) -> float:
        return effective_tick_duration(
            self.reference_tick_duration,
            self.local_content,
            self.coupling,
            self.reference_content,
        )

    @property
    def rate_ratio(self) -> float:
        return 1.0 / self.lapse

    @property
    def polarity_angular_frequency(self) -> float:
        return POLARITY_PHASE_PER_ROUTING_TICK / self.tick_duration

    @property
    def refractive_index(self) -> float:
        return self.lapse

    def snapshot(self) -> dict[str, float | str]:
        return {
            "local_content": self.local_content,
            "reference_content": self.reference_content,
            "coupling": self.coupling,
            "lapse_factor": self.lapse,
            "physical_tick_duration": self.tick_duration,
            "clock_rate_ratio": self.rate_ratio,
            "polarity_angular_frequency": self.polarity_angular_frequency,
            "effective_refractive_index": self.refractive_index,
            "model_status": "experimental_content_clock_not_gravity_law",
        }
