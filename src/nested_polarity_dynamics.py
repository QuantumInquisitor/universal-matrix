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
    """Russell-inspired inter-layer exchange ansatz.

    Positive values transfer amplitude source -> target.
    Negative values transfer amplitude target -> source.

    This is an explicit exploratory postulate:
        J = k * sqrt(A_s A_t) * (-sigma_s sigma_t) * cos(delta_phi)

    Opposite polarities with aligned phase therefore yield positive transfer,
    while like polarities reverse the sign. The sign convention is a model
    choice and must not be presented as a law of electromagnetism.
    """
    if coupling < 0:
        raise ValueError("coupling must be non-negative")
    magnitude = coupling * math.sqrt(source.amplitude * target.amplitude)
    return magnitude * (-relative_polarity(source, target)) * phase_coupling(source, target)


def bounded_transfer(
    source: ToroidalLayerState,
    target: ToroidalLayerState,
    requested_flux: float,
) -> float:
    """Limit exchange so neither layer acquires negative amplitude."""
    if requested_flux >= 0:
        return min(requested_flux, source.amplitude)
    return -min(-requested_flux, target.amplitude)


def transition_rate(state: ToroidalLayerState, coupling_load: float = 0.0) -> float:
    """Exploratory dimensionless update-rate law.

    The rate remains positive and varies with layer amplitude and net coupling.
    It is deliberately dimensionless. Mapping it to a physical clock frequency
    would require an additional independently justified observable map.
    """
    load = max(-0.95, coupling_load)
    return state.base_rate * (1.0 + state.amplitude) * (1.0 + load)


class NestedPolarityDynamics:
    """Coupled micro-to-macro layer hierarchy."""

    def __init__(
        self,
        layers: Iterable[ToroidalLayerState],
        coupling: float = 0.05,
        phase_step: float = math.pi / 18.0,
        flip_period: int = 18,
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

        # Polarity-directed core routing and phase progression.
        updated: list[ToroidalLayerState] = []
        for layer in self.layers:
            updated.append(
                ToroidalLayerState(
                    layer_id=layer.layer_id,
                    node=signed_route(layer),
                    polarity=layer.polarity,
                    phase=(layer.phase + self.phase_step * layer.polarity) % (2.0 * math.pi),
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
                    "dimensionless_transition_rate": transition_rate(
                        layer, coupling_load=incoming - outgoing
                    ),
                }
            )
        return telemetry

    def verify_conservation(self, tolerance: float = 1e-12) -> bool:
        """Check conservation of the modeled exchange amplitude."""
        return abs(self.total_amplitude() - self._initial_total_amplitude) <= tolerance
