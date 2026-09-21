"""Hamiltonian evolution for the experimental U(1) Matrix gauge field.

This module adds an explicit time coordinate to the routing-by-scale gauge
lattice. Link angles are generalized coordinates and real-valued link momenta
are their conjugate electric-like variables.

Hamiltonian:
    H = 1/2 sum_links E^2 + beta sum_plaquettes (1-cos F)

Equations:
    theta_dot = E
    E_dot = - dV/dtheta

The Gauss quantity is the lattice divergence of E. In source-free evolution,
the exact Hamiltonian equations preserve it because the potential is gauge
invariant. Numerical leapfrog evolution preserves it up to floating-point
error.

This is an experimental gauge dynamics layer, not yet a claim of physical
electromagnetism or physical spacetime.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

try:
    from .gauge_dynamics import ROUTING_PERIOD, U1CylinderField, wrap_angle
except ImportError:
    from gauge_dynamics import ROUTING_PERIOD, U1CylinderField, wrap_angle


def _zeros(rows: int) -> list[list[float]]:
    return [[0.0] * ROUTING_PERIOD for _ in range(rows)]


@dataclass
class U1HamiltonianState:
    """Gauge connection plus its conjugate link momenta."""

    field: U1CylinderField
    routing_momenta: list[list[float]]
    scale_momenta: list[list[float]]
    time: float = 0.0

    def __post_init__(self) -> None:
        layers = self.field.layer_count
        if len(self.routing_momenta) != layers:
            raise ValueError("routing momentum layer count mismatch")
        if any(len(row) != ROUTING_PERIOD for row in self.routing_momenta):
            raise ValueError("routing momentum width mismatch")
        if len(self.scale_momenta) != layers - 1:
            raise ValueError("scale momentum layer count mismatch")
        if any(len(row) != ROUTING_PERIOD for row in self.scale_momenta):
            raise ValueError("scale momentum width mismatch")

    @classmethod
    def zeros(
        cls,
        layer_count: int,
        beta: float = 1.0,
    ) -> "U1HamiltonianState":
        field = U1CylinderField.zeros(layer_count, beta=beta)
        return cls(
            field=field,
            routing_momenta=_zeros(layer_count),
            scale_momenta=_zeros(layer_count - 1),
            time=0.0,
        )

    def kinetic_energy(self) -> float:
        return 0.5 * (
            sum(v * v for row in self.routing_momenta for v in row)
            + sum(v * v for row in self.scale_momenta for v in row)
        )

    def potential_energy(self) -> float:
        return self.field.wilson_action()

    def total_energy(self) -> float:
        return self.kinetic_energy() + self.potential_energy()

    def gauss_divergence(self) -> list[list[float]]:
        """Discrete divergence of conjugate link momenta at each site.

        Positive link orientation is:
          routing: (l,k) -> (l,k+1)
          scale:   (l,k) -> (l+1,k)

        G(l,k) = E_r(l,k)-E_r(l,k-1)
               + E_s(l,k) [if outgoing]
               - E_s(l-1,k) [if incoming]
        """
        layers = self.field.layer_count
        result = _zeros(layers)
        for l in range(layers):
            for k in range(ROUTING_PERIOD):
                km = (k - 1) % ROUTING_PERIOD
                div = self.routing_momenta[l][k] - self.routing_momenta[l][km]
                if l < layers - 1:
                    div += self.scale_momenta[l][k]
                if l > 0:
                    div -= self.scale_momenta[l - 1][k]
                result[l][k] = div
        return result

    def gauss_residual(
        self,
        charge_density: Sequence[Sequence[float]] | None = None,
    ) -> list[list[float]]:
        """Return div(E)-rho at each lattice site."""
        divergence = self.gauss_divergence()
        if charge_density is None:
            return divergence
        if len(charge_density) != self.field.layer_count:
            raise ValueError("charge layer count mismatch")
        if any(len(row) != ROUTING_PERIOD for row in charge_density):
            raise ValueError("charge width mismatch")
        return [
            [
                divergence[l][k] - charge_density[l][k]
                for k in range(ROUTING_PERIOD)
            ]
            for l in range(self.field.layer_count)
        ]

    def max_abs_gauss_residual(
        self,
        charge_density: Sequence[Sequence[float]] | None = None,
    ) -> float:
        residual = self.gauss_residual(charge_density)
        return max(abs(v) for row in residual for v in row)

    def magnetic_like_curvature(self) -> list[list[float]]:
        """Gauge-invariant plaquette curvature F."""
        return self.field.plaquettes()

    def electric_like_links(
        self,
    ) -> tuple[list[list[float]], list[list[float]]]:
        """Return the conjugate link momenta."""
        return self.routing_momenta, self.scale_momenta

    def _kick(self, dt: float) -> None:
        """E <- E - dt*dV/dtheta."""
        routing_grad, scale_grad = self.field.euler_lagrange_residuals()
        for l in range(self.field.layer_count):
            for k in range(ROUTING_PERIOD):
                self.routing_momenta[l][k] -= dt * routing_grad[l][k]
        for l in range(self.field.layer_count - 1):
            for k in range(ROUTING_PERIOD):
                self.scale_momenta[l][k] -= dt * scale_grad[l][k]

    def _drift(self, dt: float) -> None:
        """theta <- theta + dt*E."""
        for l in range(self.field.layer_count):
            for k in range(ROUTING_PERIOD):
                self.field.routing_links[l][k] = wrap_angle(
                    self.field.routing_links[l][k]
                    + dt * self.routing_momenta[l][k]
                )
        for l in range(self.field.layer_count - 1):
            for k in range(ROUTING_PERIOD):
                self.field.scale_links[l][k] = wrap_angle(
                    self.field.scale_links[l][k]
                    + dt * self.scale_momenta[l][k]
                )

    def leapfrog_step(self, dt: float) -> None:
        """Second-order symplectic velocity-Verlet/leapfrog update."""
        if dt <= 0:
            raise ValueError("dt must be positive")
        self._kick(0.5 * dt)
        self._drift(dt)
        self._kick(0.5 * dt)
        self.time += dt

    def evolve(self, dt: float, steps: int) -> None:
        if steps < 0:
            raise ValueError("steps must be non-negative")
        for _ in range(steps):
            self.leapfrog_step(dt)


def gauss_sum(divergence: Sequence[Sequence[float]]) -> float:
    """Total discrete divergence; zero for a closed/open-link lattice inventory."""
    return sum(v for row in divergence for v in row)


def weak_field_hamiltonian(state: U1HamiltonianState) -> float:
    """Quadratic weak-field Hamiltonian."""
    return state.kinetic_energy() + state.field.weak_field_action()


def energy_relative_drift(
    initial_energy: float,
    final_energy: float,
) -> float:
    if initial_energy == 0.0:
        return 0.0 if final_energy == 0.0 else math.inf
    return abs(final_energy - initial_energy) / abs(initial_energy)
