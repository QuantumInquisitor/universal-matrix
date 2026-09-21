"""Experimental U(1) gauge dynamics on a Matrix routing-by-scale lattice.

The lattice is a cylinder:
  * routing coordinate k is periodic with 36 sites,
  * scale coordinate l runs over nested micro-to-macro layers.

This is a mathematical gauge-field adapter, not a claim that the coordinates
are physical spacetime. It implements the compact U(1) Wilson plaquette action,
its exact gauge symmetry, Euler-Lagrange residuals, and weak-field quadratic
limit.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

try:
    from . import canonical_kernel as ck
except ImportError:
    import canonical_kernel as ck


TAU = 2.0 * math.pi
ROUTING_PERIOD = 36


def wrap_angle(angle: float) -> float:
    """Return an angle in (-pi, pi]."""
    wrapped = (angle + math.pi) % TAU - math.pi
    if wrapped <= -math.pi:
        return math.pi
    return wrapped


def gauge_covariant_phase_difference(
    source_phase: float,
    target_phase: float,
    link_phase: float,
) -> float:
    """Gauge-invariant phase difference phi_t - phi_s + theta_st.

    Convention:
      phi_i -> phi_i + alpha_i
      theta_ij -> theta_ij + alpha_i - alpha_j
    """
    return wrap_angle(target_phase - source_phase + link_phase)


@dataclass
class U1CylinderField:
    """Compact U(1) connection on nested layers x a 36-state routing cycle."""

    routing_links: list[list[float]]
    scale_links: list[list[float]]
    beta: float = 1.0

    def __post_init__(self) -> None:
        if self.beta <= 0:
            raise ValueError("beta must be positive")
        if len(self.routing_links) < 1:
            raise ValueError("at least one layer is required")
        width = len(self.routing_links[0])
        if width != ROUTING_PERIOD:
            raise ValueError(f"routing width must be {ROUTING_PERIOD}")
        if any(len(row) != width for row in self.routing_links):
            raise ValueError("all routing-link rows must have equal width")
        if len(self.scale_links) != len(self.routing_links) - 1:
            raise ValueError("scale links must have layer_count-1 rows")
        if any(len(row) != width for row in self.scale_links):
            raise ValueError("all scale-link rows must match routing width")

    @classmethod
    def zeros(cls, layer_count: int, beta: float = 1.0) -> "U1CylinderField":
        if layer_count <= 0:
            raise ValueError("layer_count must be positive")
        routing = [[0.0] * ROUTING_PERIOD for _ in range(layer_count)]
        scale = [[0.0] * ROUTING_PERIOD for _ in range(layer_count - 1)]
        return cls(routing, scale, beta=beta)

    @property
    def layer_count(self) -> int:
        return len(self.routing_links)

    def raw_plaquette_angle(self, layer: int, k: int) -> float:
        """Unwrapped oriented curvature for the weak linearized theory."""
        if not 0 <= layer < self.layer_count - 1:
            raise IndexError("plaquette layer out of range")
        k %= ROUTING_PERIOD
        kp = (k + 1) % ROUTING_PERIOD
        return (
            self.routing_links[layer][k]
            + self.scale_links[layer][kp]
            - self.routing_links[layer + 1][k]
            - self.scale_links[layer][k]
        )

    def plaquette_angle(self, layer: int, k: int) -> float:
        """Principal compact U(1) plaquette angle."""
        return wrap_angle(self.raw_plaquette_angle(layer, k))

    def raw_plaquettes(self) -> list[list[float]]:
        return [
            [self.raw_plaquette_angle(l, k) for k in range(ROUTING_PERIOD)]
            for l in range(self.layer_count - 1)
        ]

    def plaquettes(self) -> list[list[float]]:
        return [
            [self.plaquette_angle(l, k) for k in range(ROUTING_PERIOD)]
            for l in range(self.layer_count - 1)
        ]

    def wilson_action(self) -> float:
        """Compact U(1) Wilson action beta*sum(1-cos(F_p))."""
        return self.beta * sum(
            2.0 * math.sin(0.5 * angle) ** 2
            for row in self.plaquettes()
            for angle in row
        )

    def weak_field_action(self) -> float:
        """Quadratic small-angle action beta/2 * sum(F_p^2)."""
        return 0.5 * self.beta * sum(
            angle * angle
            for row in self.raw_plaquettes()
            for angle in row
        )

    def gauge_transform(
        self,
        site_phases: Sequence[Sequence[float]],
    ) -> "U1CylinderField":
        """Apply a local U(1) transformation at every lattice site."""
        if len(site_phases) != self.layer_count:
            raise ValueError("site phase layer count mismatch")
        if any(len(row) != ROUTING_PERIOD for row in site_phases):
            raise ValueError("site phase width mismatch")

        routing = []
        for l in range(self.layer_count):
            row = []
            for k in range(ROUTING_PERIOD):
                kp = (k + 1) % ROUTING_PERIOD
                row.append(
                    wrap_angle(
                        self.routing_links[l][k]
                        + site_phases[l][k]
                        - site_phases[l][kp]
                    )
                )
            routing.append(row)

        scale = []
        for l in range(self.layer_count - 1):
            row = []
            for k in range(ROUTING_PERIOD):
                row.append(
                    wrap_angle(
                        self.scale_links[l][k]
                        + site_phases[l][k]
                        - site_phases[l + 1][k]
                    )
                )
            scale.append(row)

        return U1CylinderField(routing, scale, beta=self.beta)

    def euler_lagrange_residuals(
        self,
    ) -> tuple[list[list[float]], list[list[float]]]:
        """Exact derivatives of the Wilson action with respect to link angles."""
        p = self.plaquettes()

        routing_grad = [
            [0.0] * ROUTING_PERIOD for _ in range(self.layer_count)
        ]
        for l in range(self.layer_count):
            for k in range(ROUTING_PERIOD):
                value = 0.0
                if l < self.layer_count - 1:
                    value += math.sin(p[l][k])
                if l > 0:
                    value -= math.sin(p[l - 1][k])
                routing_grad[l][k] = self.beta * value

        scale_grad = [
            [0.0] * ROUTING_PERIOD for _ in range(self.layer_count - 1)
        ]
        for l in range(self.layer_count - 1):
            for k in range(ROUTING_PERIOD):
                km = (k - 1) % ROUTING_PERIOD
                scale_grad[l][k] = self.beta * (
                    math.sin(p[l][km]) - math.sin(p[l][k])
                )

        return routing_grad, scale_grad

    def linearized_euler_lagrange_residuals(
        self,
    ) -> tuple[list[list[float]], list[list[float]]]:
        """Derivatives of the quadratic weak-field action.

        This is the exact linear operator used by the analytic dispersion
        relation. It replaces sin(F) by F and must not be confused with the
        nonlinear compact Wilson equations.
        """
        p = self.raw_plaquettes()

        routing_grad = [
            [0.0] * ROUTING_PERIOD for _ in range(self.layer_count)
        ]
        for l in range(self.layer_count):
            for k in range(ROUTING_PERIOD):
                value = 0.0
                if l < self.layer_count - 1:
                    value += p[l][k]
                if l > 0:
                    value -= p[l - 1][k]
                routing_grad[l][k] = self.beta * value

        scale_grad = [
            [0.0] * ROUTING_PERIOD for _ in range(self.layer_count - 1)
        ]
        for l in range(self.layer_count - 1):
            for k in range(ROUTING_PERIOD):
                km = (k - 1) % ROUTING_PERIOD
                scale_grad[l][k] = self.beta * (
                    p[l][km] - p[l][k]
                )

        return routing_grad, scale_grad

    def max_abs_residual(self) -> float:
        routing, scale = self.euler_lagrange_residuals()
        values = [abs(v) for row in routing for v in row]
        values.extend(abs(v) for row in scale for v in row)
        return max(values, default=0.0)

    def routing_holonomy(self, layer: int) -> complex:
        """Wilson loop around the complete periodic routing cycle."""
        if not 0 <= layer < self.layer_count:
            raise IndexError("layer out of range")
        angle = sum(self.routing_links[layer])
        return complex(math.cos(angle), math.sin(angle))


def pure_gauge_field(site_phases: Sequence[Sequence[float]], beta: float = 1.0) -> U1CylinderField:
    """Build theta_ij = phi_i - phi_j; all plaquette curvature is zero."""
    layer_count = len(site_phases)
    if layer_count <= 0:
        raise ValueError("at least one layer is required")
    if any(len(row) != ROUTING_PERIOD for row in site_phases):
        raise ValueError("site phase width mismatch")

    routing = []
    for l in range(layer_count):
        row = []
        for k in range(ROUTING_PERIOD):
            kp = (k + 1) % ROUTING_PERIOD
            row.append(wrap_angle(site_phases[l][k] - site_phases[l][kp]))
        routing.append(row)

    scale = []
    for l in range(layer_count - 1):
        row = []
        for k in range(ROUTING_PERIOD):
            row.append(wrap_angle(site_phases[l][k] - site_phases[l + 1][k]))
        scale.append(row)

    return U1CylinderField(routing, scale, beta=beta)


def routing_index_to_core_state(channel: int, k: int) -> int:
    """Map cylinder routing index k to the canonical T21 orbit in channel r."""
    if channel not in (0, 1, 2):
        raise ValueError("channel must be 0, 1, or 2")
    return ck.route(channel, k)


def weak_field_relative_error(field: U1CylinderField) -> float:
    """Relative action error between compact and quadratic actions."""
    exact = field.wilson_action()
    approx = field.weak_field_action()
    if exact == 0.0:
        return 0.0 if approx == 0.0 else math.inf
    return abs(approx - exact) / abs(exact)
