"""Integrated nested oscillatory hierarchy for the experimental Matrix extension.

Each layer carries:
- a canonical base node;
- a physical polarity phase phi_P;
- a separate U(1) gauge phase phi_G;
- a signed scale amplitude a;
- an intrinsic polarity angular rate omega.

The physical polarity phase controls:
    polarity carrier = cos(phi_P)
    scale-transfer carrier = sin(phi_P)

The gauge phase participates only through gauge-covariant link combinations.

Adjacent scale amplitudes undergo orthogonal neutral-crossing rotations, so the
global quadratic content sum(a_l^2) is conserved up to floating arithmetic.

This is an experimental integration layer, not part of the canonical v0.4
kernel and not an established physical law.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from collections.abc import Sequence

try:
    from . import canonical_kernel as ck
    from .phase_roles import (
        PhaseState,
        gauge_coupling_energy,
    )
    from .polarity_oscillator import canonical_polarity_state
    from .scale_transfer import quadratic_content, transfer_chain
    from .canonical_polarity_clock import POLARITY_PHASE_PER_ROUTING_TICK
    from .content_clock import effective_tick_duration, clock_rate_ratio
except ImportError:
    import canonical_kernel as ck
    from phase_roles import PhaseState, gauge_coupling_energy
    from polarity_oscillator import canonical_polarity_state
    from scale_transfer import quadratic_content, transfer_chain
    from canonical_polarity_clock import POLARITY_PHASE_PER_ROUTING_TICK
    from content_clock import effective_tick_duration, clock_rate_ratio


@dataclass
class NestedOscillatorLayer:
    layer_id: int
    base_node: int
    phases: PhaseState
    amplitude: float
    angular_rate: float = 1.0
    initial_polarity: int = 1
    physical_elapsed_time: float = 0.0

    def __post_init__(self) -> None:
        self.base_node %= ck.N_CORE
        if self.angular_rate < 0:
            raise ValueError("angular_rate must be non-negative")
        if self.initial_polarity not in (-1, 1):
            raise ValueError("initial_polarity must be -1 or +1")
        if self.physical_elapsed_time < 0:
            raise ValueError("physical_elapsed_time must be non-negative")

    @property
    def canonical_node(self) -> int:
        return canonical_polarity_state(
            self.base_node,
            self.phases.polarity_phase,
            self.initial_polarity,
        )[0]

    @property
    def polarity(self) -> int:
        return canonical_polarity_state(
            self.base_node,
            self.phases.polarity_phase,
            self.initial_polarity,
        )[1]

    @property
    def polarity_carrier(self) -> float:
        return self.phases.polarity_carrier

    @property
    def transfer_carrier(self) -> float:
        return self.phases.transfer_carrier

    @property
    def local_content(self) -> float:
        return self.amplitude * self.amplitude


class OscillatoryScaleHierarchy:
    """Nested micro-to-macro oscillator chain with separated phase roles."""

    def __init__(
        self,
        layers: Sequence[NestedOscillatorLayer],
        transfer_coupling: float = 0.05,
        gauge_coupling: float = 0.05,
        link_phases: Sequence[float] | None = None,
    ):
        self.layers = list(layers)
        if not self.layers:
            raise ValueError("at least one layer is required")
        if transfer_coupling < 0 or gauge_coupling < 0:
            raise ValueError("couplings must be non-negative")

        self.transfer_coupling = float(transfer_coupling)
        self.gauge_coupling = float(gauge_coupling)
        if link_phases is None:
            link_phases = [0.0] * (len(self.layers) - 1)
        self.link_phases = [float(v) for v in link_phases]
        if len(self.link_phases) != len(self.layers) - 1:
            raise ValueError("link_phases must have len(layers)-1 entries")

        self.time = 0.0
        self._initial_quadratic_content = self.total_quadratic_content()

    def total_quadratic_content(self) -> float:
        return quadratic_content([layer.amplitude for layer in self.layers])

    def total_gauge_link_energy(self) -> float:
        return math.fsum(
            gauge_coupling_energy(
                self.layers[i].phases,
                self.layers[i + 1].phases,
                self.link_phases[i],
                coupling=self.gauge_coupling,
            )
            for i in range(len(self.link_phases))
        )

    def _edge_transfer_phases(self) -> list[float]:
        """Use the lower layer's physical transition clock on each scale edge."""
        return [
            self.layers[i].phases.polarity_phase
            for i in range(len(self.layers) - 1)
        ]

    def step(self, dt: float) -> list[dict]:
        if dt < 0:
            raise ValueError("dt must be non-negative")

        # 1. Advance physical polarity clocks only by intrinsic rates.
        for layer in self.layers:
            layer.phases.polarity_phase += layer.angular_rate * dt

        # 2. Apply reversible neutral-crossing scale transfer.
        amplitudes = [layer.amplitude for layer in self.layers]
        amplitudes = transfer_chain(
            amplitudes,
            self._edge_transfer_phases(),
            coupling=self.transfer_coupling,
            dt=dt,
        )
        for layer, amplitude in zip(self.layers, amplitudes):
            layer.amplitude = amplitude

        self.time += dt

        return [
            {
                "layer_id": layer.layer_id,
                "canonical_node": layer.canonical_node,
                "polarity": layer.polarity,
                "polarity_phase": layer.phases.polarity_phase,
                "gauge_phase": layer.phases.gauge_phase,
                "polarity_carrier": layer.polarity_carrier,
                "transfer_carrier": layer.transfer_carrier,
                "amplitude": layer.amplitude,
                "local_quadratic_content": layer.local_content,
                "time": self.time,
                "model_status": "experimental_nested_oscillatory_hierarchy",
            }
            for layer in self.layers
        ]

    def step_routing_tick(
        self,
        reference_tick_duration: float,
        content_clock_coupling: float,
        reference_content: float = 0.0,
    ) -> list[dict]:
        """Advance exactly one canonical routing/polarity tick.

        Every layer advances by the same canonical phase increment pi/18.
        Physical elapsed time is layer dependent:

            d tau_l = tau0 * exp(g * (C_l - C_ref)).

        Scale transfer is evaluated over one dimensionless routing tick after
        the canonical phase advance. This keeps the state-transition algebra
        exact while making physical clock accumulation content dependent.
        """
        if reference_tick_duration <= 0:
            raise ValueError("reference_tick_duration must be positive")
        if content_clock_coupling < 0:
            raise ValueError("content_clock_coupling must be non-negative")
        if reference_content < 0:
            raise ValueError("reference_content must be non-negative")

        pre_transfer_content = [layer.local_content for layer in self.layers]

        # 1. Exact canonical polarity-clock advance.
        for layer, content in zip(self.layers, pre_transfer_content):
            layer.phases.polarity_phase += POLARITY_PHASE_PER_ROUTING_TICK
            layer.physical_elapsed_time += effective_tick_duration(
                reference_tick_duration,
                content,
                content_clock_coupling,
                reference_content,
            )

        # 2. Conservative inter-scale exchange over one routing tick.
        amplitudes = transfer_chain(
            [layer.amplitude for layer in self.layers],
            self._edge_transfer_phases(),
            coupling=self.transfer_coupling,
            dt=1.0,
        )
        for layer, amplitude in zip(self.layers, amplitudes):
            layer.amplitude = amplitude

        self.time += 1.0

        telemetry = []
        for layer, old_content in zip(self.layers, pre_transfer_content):
            telemetry.append(
                {
                    "layer_id": layer.layer_id,
                    "canonical_node": layer.canonical_node,
                    "polarity": layer.polarity,
                    "polarity_phase": layer.phases.polarity_phase,
                    "gauge_phase": layer.phases.gauge_phase,
                    "polarity_carrier": layer.polarity_carrier,
                    "transfer_carrier": layer.transfer_carrier,
                    "amplitude": layer.amplitude,
                    "local_quadratic_content": layer.local_content,
                    "pre_transfer_content": old_content,
                    "physical_elapsed_time": layer.physical_elapsed_time,
                    "clock_rate_ratio": clock_rate_ratio(
                        old_content,
                        content_clock_coupling,
                        reference_content,
                    ),
                    "routing_tick": self.time,
                    "model_status": "experimental_content_clock_hierarchy",
                }
            )
        return telemetry

    def verify_quadratic_conservation(self, tolerance: float = 1e-12) -> bool:
        return abs(
            self.total_quadratic_content()
            - self._initial_quadratic_content
        ) <= tolerance
