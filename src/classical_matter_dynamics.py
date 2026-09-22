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

For cubic lattice spacing h, the gauge-covariant lattice Laplacian is

    Delta_A Phi(x)
      = (1/h^2) sum_i [
          exp(i A_i(x)) Phi(x+i)
          + exp(-i A_i(x-i)) Phi(x-i)
          - 2 Phi(x)
        ].

Energy and charge use the lattice cell volume h^3.  The default h=1 preserves
the historical repository normalization exactly.

Time integration uses velocity Verlet / kick-drift-kick.

This is a classical field evolution, not quantum mechanics.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

try:
    from .localized_matter_variational import MatterPotential
except ImportError:
    from localized_matter_variational import MatterPotential


AXES = (0, 1, 2)


def _validate_spacing(spacing: float) -> float:
    spacing = float(spacing)
    if not math.isfinite(spacing) or spacing <= 0:
        raise ValueError("spacing must be finite and positive")
    return spacing


def _forward(a: np.ndarray, axis: int) -> np.ndarray:
    return np.roll(a, -1, axis=axis)


def _backward(a: np.ndarray, axis: int) -> np.ndarray:
    return np.roll(a, 1, axis=axis)


def gauge_covariant_laplacian(
    phi: np.ndarray,
    links: np.ndarray,
    spacing: float = 1.0,
) -> np.ndarray:
    phi = np.asarray(phi, dtype=complex)
    links = np.asarray(links, dtype=float)
    spacing = _validate_spacing(spacing)

    if phi.ndim != 3:
        raise ValueError("phi must be 3D")
    if links.shape != (3,) + phi.shape:
        raise ValueError("links shape mismatch")

    out = np.zeros_like(phi, dtype=complex)
    inv_h2 = 1.0 / (spacing * spacing)
    for axis in AXES:
        forward_term = np.exp(1j * links[axis]) * _forward(phi, axis)
        backward_link = _backward(links[axis], axis)
        backward_term = np.exp(-1j * backward_link) * _backward(phi, axis)
        out += (forward_term + backward_term - 2.0 * phi) * inv_h2
    return out


def matter_force(
    phi: np.ndarray,
    links: np.ndarray,
    potential: MatterPotential,
    spacing: float = 1.0,
) -> np.ndarray:
    rho = np.abs(phi) ** 2
    nonlinear = (
        potential.mass2
        + 2.0 * potential.lambda4 * rho
        + 3.0 * potential.lambda6 * rho**2
    )
    return (
        gauge_covariant_laplacian(phi, links, spacing=spacing)
        - nonlinear * phi
    )


def matter_charge(
    phi: np.ndarray,
    momentum: np.ndarray,
    spacing: float = 1.0,
) -> float:
    phi = np.asarray(phi, dtype=complex)
    momentum = np.asarray(momentum, dtype=complex)
    spacing = _validate_spacing(spacing)

    if phi.shape != momentum.shape:
        raise ValueError("phi and momentum shapes must match")

    cell_volume = spacing**3
    return float(
        2.0
        * np.imag(np.vdot(phi, momentum))
        * cell_volume
    )


def matter_energy(
    phi: np.ndarray,
    momentum: np.ndarray,
    links: np.ndarray,
    potential: MatterPotential,
    spacing: float = 1.0,
) -> float:
    phi = np.asarray(phi, dtype=complex)
    momentum = np.asarray(momentum, dtype=complex)
    links = np.asarray(links, dtype=float)
    spacing = _validate_spacing(spacing)

    if phi.shape != momentum.shape:
        raise ValueError("phi and momentum shapes must match")
    if links.shape != (3,) + phi.shape:
        raise ValueError("links shape mismatch")

    cell_volume = spacing**3
    inverse_spacing_squared = 1.0 / (spacing * spacing)

    total_density_sum = float(np.sum(np.abs(momentum) ** 2))
    for axis in AXES:
        d = np.exp(1j * links[axis]) * _forward(phi, axis) - phi
        total_density_sum += float(
            np.sum(np.abs(d) ** 2)
            * inverse_spacing_squared
        )

    rho = np.abs(phi) ** 2
    total_density_sum += float(
        np.sum(
            potential.mass2 * rho
            + potential.lambda4 * rho**2
            + potential.lambda6 * rho**3
        )
    )
    return total_density_sum * cell_volume


@dataclass
class ClassicalMatterDynamics:
    phi: np.ndarray
    momentum: np.ndarray
    links: np.ndarray
    potential: MatterPotential = MatterPotential()
    time: float = 0.0
    lattice_spacing: float = 1.0

    def __post_init__(self) -> None:
        self.phi = np.asarray(self.phi, dtype=complex).copy()
        self.momentum = np.asarray(self.momentum, dtype=complex).copy()
        self.links = np.asarray(self.links, dtype=float).copy()
        self.lattice_spacing = _validate_spacing(self.lattice_spacing)

        if self.phi.ndim != 3:
            raise ValueError("phi must be 3D")
        if self.momentum.shape != self.phi.shape:
            raise ValueError("momentum shape mismatch")
        if self.links.shape != (3,) + self.phi.shape:
            raise ValueError("links shape mismatch")

    @property
    def charge(self) -> float:
        return matter_charge(
            self.phi,
            self.momentum,
            spacing=self.lattice_spacing,
        )

    @property
    def energy(self) -> float:
        return matter_energy(
            self.phi,
            self.momentum,
            self.links,
            self.potential,
            spacing=self.lattice_spacing,
        )

    def step(self, dt: float) -> None:
        if not math.isfinite(dt) or dt <= 0:
            raise ValueError("dt must be finite and positive")

        self.momentum += 0.5 * dt * matter_force(
            self.phi,
            self.links,
            self.potential,
            spacing=self.lattice_spacing,
        )
        self.phi += dt * self.momentum
        self.momentum += 0.5 * dt * matter_force(
            self.phi,
            self.links,
            self.potential,
            spacing=self.lattice_spacing,
        )
        self.time += dt

    def snapshot(self) -> dict[str, float | str]:
        return {
            "time": self.time,
            "energy": self.energy,
            "charge": self.charge,
            "max_amplitude": float(np.max(np.abs(self.phi))),
            "lattice_spacing": self.lattice_spacing,
            "model_status": "classical_gauge_covariant_matter_dynamics",
        }
