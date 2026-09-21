"""Experimental nested polarity dynamics for the Universal Matrix.

This module is intentionally outside the canonical v0.4 kernel. It explores a
micro-to-macro hierarchy of coupled layers with polarity reversal and
inter-layer exchange. The equations are modeling assumptions, not established
electromagnetic or gravitational laws.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, List

try:
    from . import canonical_kernel as ck
except ImportError:
    import canonical_kernel as ck


@dataclass
class ToroidalLayerState:
    """State of one nested layer in the exploratory dynamics."""

    layer_id: int
    node: int
    polarity: int
    phase: float
    amplitude: float
    base_rate: float = 1.0

    def __post_init__(self) -> None:
        self.node %= ck.N_CORE
        if self.polarity not in (-1, 1):
            raise ValueError("polarity must be -1 or +1")
        if self.amplitude < 0:
            raise ValueError("amplitude must be non-negative")
        if self.base_rate <= 0:
            raise ValueError("base_rate must be positive")


def polarity_flip(state: ToroidalLayerState) -> ToroidalLayerState:
    """Apply Q(n,sigma)=(n+54,-sigma), so Q^2=I."""
    return ToroidalLayerState(
        layer_id=state.layer_id,
        node=ck.polarity(state.node),
        polarity=-state.polarity,
        phase=state.phase,
        amplitude=state.amplitude,
        base_rate=state.base_rate,
    )


def signed_route(state: ToroidalLayerState, steps: int = 1) -> int:
    """Route forward for + polarity and backward for - polarity."""
    signed_step = state.polarity * ck.ROUTING_STEP * steps
    return ck.translate(state.node, signed_step)


def relative_polarity(a: ToroidalLayerState, b: ToroidalLayerState) -> int:
    """Return +1 for like polarity and -1 for opposite polarity."""
    return a.polarity * b.polarity


def phase_coupling(a: ToroidalLayerState, b: ToroidalLayerState) -> float:
    """Bounded phase relation in [-1,1]."""
    return math.cos(a.phase - b.phase)


def injection_flux(
    source: ToroidalLayerState,
    target: ToroidalLayerState,
    coupling: float,
) -> float:
    """Directed Russell-inspired inter-layer exchange ansatz.

    Positive values mean source -> target and negative values mean the reverse.

    The minimal form used here is constrained to:
      * be local to a neighboring pair,
      * reverse sign when source and target are exchanged,
      * vanish for equal polarities,
      * reverse under a global polarity reversal,
      * be maximal for phase-aligned opposite polarities.

    J(a,b) = k * sqrt(A_a A_b) * ((sigma_a-sigma_b)/2)
             * cos(phi_a-phi_b)

    These symmetry requirements constrain the form but do not make it a law
    of electromagnetism. It remains an explicit physical-extension ansatz.
    """
    if coupling < 0:
        raise ValueError("coupling must be non-negative")
    magnitude = coupling * math.sqrt(source.amplitude * target.amplitude)
    polarity_gradient = 0.5 * (source.polarity - target.polarity)
    return magnitude * polarity_gradient * phase_coupling(source, target)


def self_similar_scale(
    layer_id: int,
    scale_ratio: float,
    reference_scale: float = 1.0,
) -> float:
    """Geometric micro-to-macro scale hierarchy R_l = R_0 * lambda^l.

    This follows from the self-similarity postulate that every adjacent pair
    has the same scale ratio. The numerical value of lambda is not supplied by
    the v0.4 kernel and must be independently justified.
    """
    if scale_ratio <= 0:
        raise ValueError("scale_ratio must be positive")
    if reference_scale <= 0:
        raise ValueError("reference_scale must be positive")
    return reference_scale * (scale_ratio ** layer_id)


def self_similar_rate(
    layer_id: int,
    scale_ratio: float,
    dynamic_exponent: float = 1.0,
    reference_rate: float = 1.0,
) -> float:
    """Dimensionless intrinsic rate omega_l = omega_0 * lambda^(-z l).

    z=1 corresponds to a constant characteristic propagation speed across
    geometrically scaled layers. That value is a physical postulate, not a
    theorem of the canonical kernel.
    """
    if scale_ratio <= 0:
        raise ValueError("scale_ratio must be positive")
    if reference_rate <= 0:
        raise ValueError("reference_rate must be positive")
    return reference_rate * (scale_ratio ** (-dynamic_exponent * layer_id))


def neighbor_phase_shift(
    state: ToroidalLayerState,
    neighbor: ToroidalLayerState,
    coupling: float,
) -> float:
    """Dimensionless phase-rate correction from one neighboring layer.

    The correction is polarity-sensitive and reverses with the state polarity:
        dphi = sigma_i * k * (-sigma_i sigma_j)
               * sqrt(A_j/A_i) * cos(phi_i-phi_j)

    It is a minimal coupled-mode ansatz used to make the dynamical clock
    variable an actual phase velocity rather than an arbitrary telemetry label.
    """
    if coupling < 0:
        raise ValueError("coupling must be non-negative")
    if state.amplitude <= 0 or neighbor.amplitude <= 0:
        return 0.0
    relative = -relative_polarity(state, neighbor)
    amplitude_ratio = math.sqrt(neighbor.amplitude / state.amplitude)
    return (
        state.polarity
        * coupling
        * relative
        * amplitude_ratio
        * phase_coupling(state, neighbor)
    )


def fractional_rate_shift(rate_a: float, rate_b: float) -> float:
    """Dimensionless differential rate (rate_b-rate_a)/rate_a."""
    if rate_a == 0:
        raise ValueError("reference rate must be nonzero")
    return (rate_b - rate_a) / rate_a


def bounded_transfer(
    source: ToroidalLayerState,
    target: ToroidalLayerState,
    requested_flux: float,
) -> float:
    """Limit exchange so neither layer acquires negative amplitude."""
    if requested_flux >= 0:
        return min(requested_flux, source.amplitude)
    return -min(-requested_flux, target.amplitude)


def transition_rate(
    state: ToroidalLayerState,
    neighbors: Iterable[ToroidalLayerState] = (),
    coupling: float = 0.0,
) -> float:
    """Actual dimensionless phase velocity used by the extension.

    The intrinsic term follows the layer polarity. Neighbor corrections are
    generated by the same phase/polarity variables that drive inter-layer
    dynamics. A physical clock interpretation remains an additional hypothesis.
    """
    rate = state.polarity * state.base_rate
    for neighbor in neighbors:
        rate += neighbor_phase_shift(state, neighbor, coupling)
    return rate


class NestedPolarityDynamics:
    """Coupled micro-to-macro layer hierarchy."""

    def __init__(
        self,
        layers: Iterable[ToroidalLayerState],
        coupling: float = 0.05,
        phase_step: float = math.pi / 18.0,
        flip_period: int = 18,
        scale_ratio: float | None = None,
        dynamic_exponent: float = 1.0,
    ):
        self.layers: List[ToroidalLayerState] = list(layers)
        if not self.layers:
            raise ValueError("at least one layer is required")
        if coupling < 0:
            raise ValueError("coupling must be non-negative")
        if flip_period <= 0:
            raise ValueError("flip_period must be positive")
        self.coupling = coupling
        self.phase_step = phase_step
        self.flip_period = flip_period
        self.scale_ratio = scale_ratio
        self.dynamic_exponent = dynamic_exponent
        if scale_ratio is not None:
            if scale_ratio <= 0:
                raise ValueError("scale_ratio must be positive")
            for layer in self.layers:
                layer.base_rate = self.phase_step * self_similar_rate(
                    layer.layer_id,
                    scale_ratio,
                    dynamic_exponent=dynamic_exponent,
                    reference_rate=1.0,
                )
        else:
            # No scale law assumed: all layers share the canonical phase step.
            for layer in self.layers:
                layer.base_rate = self.phase_step
        self.tick = 0
        self._initial_total_amplitude = self.total_amplitude()

    def total_amplitude(self) -> float:
        return sum(layer.amplitude for layer in self.layers)

    def _neighbor_fluxes(self) -> list[float]:
        return [
            injection_flux(self.layers[i], self.layers[i + 1], self.coupling)
            for i in range(len(self.layers) - 1)
        ]

    def step(self) -> list[dict]:
        """Advance one discrete tick and return layer telemetry."""
        fluxes = self._neighbor_fluxes()

        # Conservative nearest-neighbor exchange.
        for i, requested in enumerate(fluxes):
            source = self.layers[i]
            target = self.layers[i + 1]
            actual = bounded_transfer(source, target, requested)
            source.amplitude -= actual
            target.amplitude += actual

        # Polarity-directed core routing and coupled phase progression.
        updated: list[ToroidalLayerState] = []
        effective_rates: list[float] = []
        for i, layer in enumerate(self.layers):
            neighbors = []
            if i > 0:
                neighbors.append(self.layers[i - 1])
            if i + 1 < len(self.layers):
                neighbors.append(self.layers[i + 1])

            rate = transition_rate(layer, neighbors, self.coupling)
            effective_rates.append(rate)
            updated.append(
                ToroidalLayerState(
                    layer_id=layer.layer_id,
                    node=signed_route(layer),
                    polarity=layer.polarity,
                    phase=(layer.phase + rate) % (2.0 * math.pi),
                    amplitude=layer.amplitude,
                    base_rate=layer.base_rate,
                )
            )
        self.layers = updated
        self.tick += 1

        # Half-cycle reversal aligned with T^18=P in the canonical routing.
        if self.tick % self.flip_period == 0:
            self.layers = [polarity_flip(layer) for layer in self.layers]

        telemetry = []
        for i, layer in enumerate(self.layers):
            incoming = fluxes[i - 1] if i > 0 else 0.0
            outgoing = fluxes[i] if i < len(fluxes) else 0.0
            telemetry.append(
                {
                    "layer_id": layer.layer_id,
                    "node": layer.node,
                    "polarity": layer.polarity,
                    "phase": layer.phase,
                    "amplitude": layer.amplitude,
                    "net_neighbor_flux": incoming - outgoing,
                    "dimensionless_transition_rate": effective_rates[i],
                    "scale": (
                        self_similar_scale(layer.layer_id, self.scale_ratio)
                        if self.scale_ratio is not None
                        else None
                    ),
                }
            )
        return telemetry

    def verify_conservation(self, tolerance: float = 1e-12) -> bool:
        """Check conservation of the modeled exchange amplitude."""
        return abs(self.total_amplitude() - self._initial_total_amplitude) <= tolerance
