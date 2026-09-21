"""Real-time classical complex matter dynamics with fixed compact U(1) links.

Temporal gauge is used for this first dynamical matter layer:

    A_0 = 0.

State:
    Phi(x,t) complex matter field
    Pi(x,t)  = d_t Phi
    A_i(x)   fixed spatial compact U(1) links

Equation:
    d_t Phi = Pi

    d_t Pi
      = Delta_A Phi
        - [m2 + 2 lambda4 |Phi|^2 + 3 lambda6 |Phi|^4] Phi.

The gauge-covariant lattice Laplacian is

    Delta_A Phi(x)
      = sum_i [
          exp(i A_i(x)) Phi(x+i)
          + exp(-i A_i(x-i)) Phi(x-i)
          - 2 Phi(x)
        ].

Energy:
    E = sum_x [
        |Pi|^2
        + sum_i |D_i^+ Phi|^2
        + U(|Phi|^2)
    ].

Charge convention:
    Q = 2 Im sum_x Phi^* Pi

chosen to match the positive Q=2 omega int f^2 convention used by the
time-harmonic radial matter modules.

Time integration uses velocity Verlet / kick-drift-kick.

This is a classical field evolution, not quantum mechanics.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

try:
    from .localized_matter_variational import MatterPotential
except ImportError:
    from localized_matter_variational import MatterPotential


AXES = (0, 1, 2)


def _forward(a: np.ndarray, axis: int) -> np.ndarray:
    return np.roll(a, -1, axis=axis)


def _backward(a: np.ndarray, axis: int) -> np.ndarray:
    return np.roll(a, 1, axis=axis)


def gauge_covariant_laplacian(
    phi: np.ndarray,
    links: np.ndarray,
) -> np.ndarray:
    phi = np.asarray(phi, dtype=complex)
    links = np.asarray(links, dtype=float)
    if phi.ndim != 3:
        raise ValueError("phi must be 3D")
    if links.shape != (3,) + phi.shape:
        raise ValueError("links shape mismatch")

    out = np.zeros_like(phi, dtype=complex)
    for axis in AXES:
        forward_term = np.exp(1j * links[axis]) * _forward(phi, axis)
        backward_link = _backward(links[axis], axis)
        backward_term = np.exp(-1j * backward_link) * _backward(phi, axis)
        out += forward_term + backward_term - 2.0 * phi
    return out


def matter_force(
    phi: np.ndarray,
    links: np.ndarray,
    potential: MatterPotential,
) -> np.ndarray:
    rho = np.abs(phi) ** 2
    nonlinear = (
        potential.mass2
        + 2.0 * potential.lambda4 * rho
        + 3.0 * potential.lambda6 * rho**2
    )
    return gauge_covariant_laplacian(phi, links) - nonlinear * phi


def matter_charge(phi: np.ndarray, momentum: np.ndarray) -> float:
    phi = np.asarray(phi, dtype=complex)
    momentum = np.asarray(momentum, dtype=complex)
    if phi.shape != momentum.shape:
        raise ValueError("phi and momentum shapes must match")
    return float(2.0 * np.imag(np.vdot(phi, momentum)))


def matter_energy(
    phi: np.ndarray,
    momentum: np.ndarray,
    links: np.ndarray,
    potential: MatterPotential,
) -> float:
    phi = np.asarray(phi, dtype=complex)
    momentum = np.asarray(momentum, dtype=complex)
    links = np.asarray(links, dtype=float)

    if phi.shape != momentum.shape:
        raise ValueError("phi and momentum shapes must match")
    if links.shape != (3,) + phi.shape:
        raise ValueError("links shape mismatch")

    total = float(np.sum(np.abs(momentum) ** 2))
    for axis in AXES:
        d = np.exp(1j * links[axis]) * _forward(phi, axis) - phi
        total += float(np.sum(np.abs(d) ** 2))

    rho = np.abs(phi) ** 2
    total += float(
        np.sum(
            potential.mass2 * rho
            + potential.lambda4 * rho**2
            + potential.lambda6 * rho**3
        )
    )
    return total


@dataclass
class ClassicalMatterDynamics:
    phi: np.ndarray
    momentum: np.ndarray
    links: np.ndarray
    potential: MatterPotential = MatterPotential()
    time: float = 0.0

    def __post_init__(self) -> None:
        self.phi = np.asarray(self.phi, dtype=complex).copy()
        self.momentum = np.asarray(self.momentum, dtype=complex).copy()
        self.links = np.asarray(self.links, dtype=float).copy()

        if self.phi.ndim != 3:
            raise ValueError("phi must be 3D")
        if self.momentum.shape != self.phi.shape:
            raise ValueError("momentum shape mismatch")
        if self.links.shape != (3,) + self.phi.shape:
            raise ValueError("links shape mismatch")

    @property
    def charge(self) -> float:
        return matter_charge(self.phi, self.momentum)

    @property
    def energy(self) -> float:
        return matter_energy(
            self.phi,
            self.momentum,
            self.links,
            self.potential,
        )

    def step(self, dt: float) -> None:
        if dt <= 0:
            raise ValueError("dt must be positive")

        self.momentum += 0.5 * dt * matter_force(
            self.phi,
            self.links,
            self.potential,
        )
        self.phi += dt * self.momentum
        self.momentum += 0.5 * dt * matter_force(
            self.phi,
            self.links,
            self.potential,
        )
        self.time += dt

    def snapshot(self) -> dict[str, float | str]:
        return {
            "time": self.time,
            "energy": self.energy,
            "charge": self.charge,
            "max_amplitude": float(np.max(np.abs(self.phi))),
            "model_status": "classical_gauge_covariant_matter_dynamics",
        }
