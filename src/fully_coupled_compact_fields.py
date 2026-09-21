"""Fully coupled classical matter + content scalar + compact U(1) gauge dynamics.

This module upgrades the weak-gauge coupled Hamiltonian to the compact Wilson
gauge action while preserving the same matter and content couplings.

Gauge potential:
    V_gauge = beta * sum_p [1 - cos(F_p)]

Gauge force:
    E_dot = -dH/dA

with sin(F) entering the plaquette derivative.

Matter remains minimally coupled through compact link transport
    exp(i A_i).

Link coordinates are wrapped to the principal interval after drift.

This is still a classical field theory. It is not quantum electrodynamics.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

try:
    from .fully_coupled_classical_fields import (
        AXES,
        PLANES,
        FullyCoupledParameters,
        forward,
        backward,
        plaquette,
        matter_link_energy,
        matter_link_gradient,
        gauge_covariant_laplacian,
        periodic_laplacian,
        divergence,
        u1_charge,
        u1_charge_density,
    )
except ImportError:
    from fully_coupled_classical_fields import (
        AXES,
        PLANES,
        FullyCoupledParameters,
        forward,
        backward,
        plaquette,
        matter_link_energy,
        matter_link_gradient,
        gauge_covariant_laplacian,
        periodic_laplacian,
        divergence,
        u1_charge,
        u1_charge_density,
    )


TAU = 2.0 * math.pi


def principal_angle(a: np.ndarray) -> np.ndarray:
    return (a + math.pi) % TAU - math.pi


def compact_gauge_energy(links: np.ndarray, beta: float) -> float:
    if beta < 0:
        raise ValueError("beta must be non-negative")
    return beta * sum(
        float(np.sum(1.0 - np.cos(plaquette(links, i, j))))
        for i, j in PLANES
    )


def compact_gauge_force(links: np.ndarray, beta: float) -> np.ndarray:
    """Return -dV_Wilson/dA."""
    if beta < 0:
        raise ValueError("beta must be non-negative")
    force = np.zeros_like(links, dtype=float)

    for axis in AXES:
        total = np.zeros_like(links[axis], dtype=float)
        for other in AXES:
            if other == axis:
                f = plaquette(links, axis, other)
                oriented_sin = np.sin(f)
            else:
                f = plaquette(links, other, axis)
                oriented_sin = -np.sin(f)
            total += oriented_sin - backward(oriented_sin, other)
        force[axis] = -beta * total
    return force


def matter_force(
    phi: np.ndarray,
    chi: np.ndarray,
    links: np.ndarray,
    params: FullyCoupledParameters,
) -> np.ndarray:
    rho = np.abs(phi) ** 2
    p = params.matter
    derivative = p.mass2 + 2.0*p.lambda4*rho + 3.0*p.lambda6*rho**2
    return (
        gauge_covariant_laplacian(phi, links)
        - derivative * phi
        + params.matter_content_coupling * chi * phi
    )


def content_force(
    phi: np.ndarray,
    chi: np.ndarray,
    params: FullyCoupledParameters,
) -> np.ndarray:
    return params.content_wave_speed**2 * (
        periodic_laplacian(chi)
        + params.scalar_field_kappa
        * params.matter_content_coupling
        * np.abs(phi) ** 2
    )


def electric_force(
    phi: np.ndarray,
    links: np.ndarray,
    params: FullyCoupledParameters,
) -> np.ndarray:
    return (
        compact_gauge_force(links, params.beta)
        - matter_link_gradient(phi, links)
    )


def total_energy(
    phi: np.ndarray,
    momentum: np.ndarray,
    chi: np.ndarray,
    chi_velocity: np.ndarray,
    links: np.ndarray,
    electric: np.ndarray,
    params: FullyCoupledParameters,
) -> float:
    rho = np.abs(phi) ** 2
    p = params.matter

    total = float(np.sum(np.abs(momentum) ** 2))
    total += matter_link_energy(phi, links)
    total += float(
        np.sum(
            p.mass2*rho
            + p.lambda4*rho**2
            + p.lambda6*rho**3
            - params.matter_content_coupling * chi * rho
        )
    )

    total += float(
        np.sum(chi_velocity**2)
        / (
            2.0
            * params.scalar_field_kappa
            * params.content_wave_speed**2
        )
    )

    for axis in AXES:
        dchi = forward(chi, axis) - chi
        total += float(np.sum(dchi*dchi)) / (2.0*params.scalar_field_kappa)

    total += 0.5 * float(np.sum(electric**2))
    total += compact_gauge_energy(links, params.beta)
    return total


@dataclass
class FullyCoupledCompactFields:
    phi: np.ndarray
    momentum: np.ndarray
    chi: np.ndarray
    chi_velocity: np.ndarray
    links: np.ndarray
    electric: np.ndarray
    params: FullyCoupledParameters = FullyCoupledParameters()
    time: float = 0.0

    def __post_init__(self) -> None:
        self.phi = np.asarray(self.phi, dtype=complex).copy()
        self.momentum = np.asarray(self.momentum, dtype=complex).copy()
        self.chi = np.asarray(self.chi, dtype=float).copy()
        self.chi_velocity = np.asarray(self.chi_velocity, dtype=float).copy()
        self.links = principal_angle(np.asarray(self.links, dtype=float).copy())
        self.electric = np.asarray(self.electric, dtype=float).copy()

        shape = self.phi.shape
        if self.phi.ndim != 3:
            raise ValueError("phi must be 3D")
        if self.momentum.shape != shape:
            raise ValueError("momentum shape mismatch")
        if self.chi.shape != shape or self.chi_velocity.shape != shape:
            raise ValueError("content field shape mismatch")
        if self.links.shape != (3,) + shape:
            raise ValueError("link shape mismatch")
        if self.electric.shape != (3,) + shape:
            raise ValueError("electric shape mismatch")

    @property
    def energy(self) -> float:
        return total_energy(
            self.phi,
            self.momentum,
            self.chi,
            self.chi_velocity,
            self.links,
            self.electric,
            self.params,
        )

    @property
    def charge(self) -> float:
        return u1_charge(self.phi, self.momentum)

    def gauss_residual(self) -> np.ndarray:
        return divergence(self.electric) + u1_charge_density(
            self.phi,
            self.momentum,
        )

    def max_abs_gauss_residual(self) -> float:
        return float(np.max(np.abs(self.gauss_residual())))

    def step(self, dt: float) -> None:
        if dt <= 0:
            raise ValueError("dt must be positive")

        self.momentum += 0.5*dt*matter_force(
            self.phi, self.chi, self.links, self.params
        )
        self.chi_velocity += 0.5*dt*content_force(
            self.phi, self.chi, self.params
        )
        self.electric += 0.5*dt*electric_force(
            self.phi, self.links, self.params
        )

        self.phi += dt*self.momentum
        self.chi += dt*self.chi_velocity
        self.links = principal_angle(self.links + dt*self.electric)

        self.momentum += 0.5*dt*matter_force(
            self.phi, self.chi, self.links, self.params
        )
        self.chi_velocity += 0.5*dt*content_force(
            self.phi, self.chi, self.params
        )
        self.electric += 0.5*dt*electric_force(
            self.phi, self.links, self.params
        )

        self.time += dt

    def snapshot(self) -> dict[str, float | str]:
        return {
            "time": self.time,
            "energy": self.energy,
            "u1_charge": self.charge,
            "max_gauss_residual": self.max_abs_gauss_residual(),
            "max_matter_amplitude": float(np.max(np.abs(self.phi))),
            "max_content_potential": float(np.max(self.chi)),
            "model_status": "experimental_fully_coupled_compact_fields",
        }
