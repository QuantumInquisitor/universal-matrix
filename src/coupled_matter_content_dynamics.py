"""Self-consistent classical matter-content dynamics on a periodic lattice.

This is the first dynamical system in the repository where the classical matter
field both sources and responds to the content scalar through the SAME coupling.

Flat-background Lagrangian density:

    L =
        |D_t Phi|^2
        - sum_i |D_i Phi|^2
        - U(|Phi|^2)
        + g_chi chi |Phi|^2
        + chi_t^2/(2 kappa_chi c_chi^2)
        - |grad chi|^2/(2 kappa_chi).

Temporal gauge A_0=0 is used and the spatial U(1) links are held fixed in this
first coupled matter-content implementation.

Equations:

    Phi_tt
      = Delta_A Phi
        - U'(rho) Phi
        + g_chi chi Phi

    chi_tt
      = c_chi^2 [
          laplacian chi
          + kappa_chi g_chi rho
        ]

where rho=|Phi|^2.

Total energy:

    E =
      |Pi|^2
      + |D Phi|^2
      + U(rho)
      - g_chi chi rho
      + v_chi^2/(2 kappa_chi c_chi^2)
      + |grad chi|^2/(2 kappa_chi).

The coupling is therefore reciprocal at the action level.

This is a classical experimental field system, not quantum gravity or an
established matter theory.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

try:
    from .classical_matter_dynamics import (
        gauge_covariant_laplacian,
        matter_charge,
    )
    from .localized_matter_variational import MatterPotential
except ImportError:
    from classical_matter_dynamics import gauge_covariant_laplacian, matter_charge
    from localized_matter_variational import MatterPotential


AXES = (0, 1, 2)


def periodic_laplacian(field: np.ndarray) -> np.ndarray:
    a = np.asarray(field)
    if a.ndim != 3:
        raise ValueError("field must be 3D")

    out = np.zeros_like(a)
    for axis in AXES:
        out += (
            np.roll(a, -1, axis=axis)
            + np.roll(a, 1, axis=axis)
            - 2.0 * a
        )
    return out


def matter_acceleration(
    phi: np.ndarray,
    chi: np.ndarray,
    links: np.ndarray,
    potential: MatterPotential,
    matter_content_coupling: float,
) -> np.ndarray:
    if matter_content_coupling < 0:
        raise ValueError("matter_content_coupling must be non-negative")
    rho = np.abs(phi) ** 2
    potential_derivative = (
        potential.mass2
        + 2.0 * potential.lambda4 * rho
        + 3.0 * potential.lambda6 * rho**2
    )
    return (
        gauge_covariant_laplacian(phi, links)
        - potential_derivative * phi
        + matter_content_coupling * chi * phi
    )


def content_acceleration(
    phi: np.ndarray,
    chi: np.ndarray,
    scalar_field_kappa: float,
    matter_content_coupling: float,
    content_wave_speed: float,
) -> np.ndarray:
    if scalar_field_kappa <= 0:
        raise ValueError("scalar_field_kappa must be positive")
    if matter_content_coupling < 0:
        raise ValueError("matter_content_coupling must be non-negative")
    if content_wave_speed <= 0:
        raise ValueError("content_wave_speed must be positive")

    rho = np.abs(phi) ** 2
    return content_wave_speed**2 * (
        periodic_laplacian(chi)
        + scalar_field_kappa * matter_content_coupling * rho
    )


def coupled_total_energy(
    phi: np.ndarray,
    momentum: np.ndarray,
    chi: np.ndarray,
    chi_velocity: np.ndarray,
    links: np.ndarray,
    potential: MatterPotential,
    scalar_field_kappa: float,
    matter_content_coupling: float,
    content_wave_speed: float,
) -> float:
    if scalar_field_kappa <= 0:
        raise ValueError("scalar_field_kappa must be positive")
    if content_wave_speed <= 0:
        raise ValueError("content_wave_speed must be positive")

    phi = np.asarray(phi, dtype=complex)
    momentum = np.asarray(momentum, dtype=complex)
    chi = np.asarray(chi, dtype=float)
    chi_velocity = np.asarray(chi_velocity, dtype=float)
    links = np.asarray(links, dtype=float)

    if phi.shape != momentum.shape or phi.shape != chi.shape:
        raise ValueError("matter and scalar shapes must match")
    if chi_velocity.shape != chi.shape:
        raise ValueError("chi velocity shape mismatch")
    if links.shape != (3,) + phi.shape:
        raise ValueError("links shape mismatch")

    rho = np.abs(phi) ** 2

    total = float(np.sum(np.abs(momentum) ** 2))

    for axis in AXES:
        dphi = (
            np.exp(1j * links[axis])
            * np.roll(phi, -1, axis=axis)
            - phi
        )
        total += float(np.sum(np.abs(dphi) ** 2))

    total += float(
        np.sum(
            potential.mass2 * rho
            + potential.lambda4 * rho**2
            + potential.lambda6 * rho**3
            - matter_content_coupling * chi * rho
        )
    )

    total += float(
        np.sum(chi_velocity**2)
        / (2.0 * scalar_field_kappa * content_wave_speed**2)
    )

    scalar_gradient = 0.0
    for axis in AXES:
        dchi = np.roll(chi, -1, axis=axis) - chi
        scalar_gradient += float(np.sum(dchi * dchi))
    total += scalar_gradient / (2.0 * scalar_field_kappa)

    return total


@dataclass
class CoupledMatterContentDynamics:
    phi: np.ndarray
    momentum: np.ndarray
    chi: np.ndarray
    chi_velocity: np.ndarray
    links: np.ndarray
    potential: MatterPotential = MatterPotential()
    scalar_field_kappa: float = 1.0
    matter_content_coupling: float = 0.1
    content_wave_speed: float = 1.0
    time: float = 0.0

    def __post_init__(self) -> None:
        self.phi = np.asarray(self.phi, dtype=complex).copy()
        self.momentum = np.asarray(self.momentum, dtype=complex).copy()
        self.chi = np.asarray(self.chi, dtype=float).copy()
        self.chi_velocity = np.asarray(self.chi_velocity, dtype=float).copy()
        self.links = np.asarray(self.links, dtype=float).copy()

        if self.phi.ndim != 3:
            raise ValueError("phi must be 3D")
        if self.momentum.shape != self.phi.shape:
            raise ValueError("momentum shape mismatch")
        if self.chi.shape != self.phi.shape:
            raise ValueError("chi shape mismatch")
        if self.chi_velocity.shape != self.chi.shape:
            raise ValueError("chi_velocity shape mismatch")
        if self.links.shape != (3,) + self.phi.shape:
            raise ValueError("links shape mismatch")
        if self.scalar_field_kappa <= 0:
            raise ValueError("scalar_field_kappa must be positive")
        if self.matter_content_coupling < 0:
            raise ValueError("matter_content_coupling must be non-negative")
        if self.content_wave_speed <= 0:
            raise ValueError("content_wave_speed must be positive")

    @property
    def charge(self) -> float:
        return matter_charge(self.phi, self.momentum)

    @property
    def energy(self) -> float:
        return coupled_total_energy(
            self.phi,
            self.momentum,
            self.chi,
            self.chi_velocity,
            self.links,
            self.potential,
            self.scalar_field_kappa,
            self.matter_content_coupling,
            self.content_wave_speed,
        )

    def step(self, dt: float) -> None:
        if dt <= 0:
            raise ValueError("dt must be positive")

        self.momentum += 0.5 * dt * matter_acceleration(
            self.phi,
            self.chi,
            self.links,
            self.potential,
            self.matter_content_coupling,
        )
        self.chi_velocity += 0.5 * dt * content_acceleration(
            self.phi,
            self.chi,
            self.scalar_field_kappa,
            self.matter_content_coupling,
            self.content_wave_speed,
        )

        self.phi += dt * self.momentum
        self.chi += dt * self.chi_velocity

        self.momentum += 0.5 * dt * matter_acceleration(
            self.phi,
            self.chi,
            self.links,
            self.potential,
            self.matter_content_coupling,
        )
        self.chi_velocity += 0.5 * dt * content_acceleration(
            self.phi,
            self.chi,
            self.scalar_field_kappa,
            self.matter_content_coupling,
            self.content_wave_speed,
        )

        self.time += dt

    def snapshot(self) -> dict[str, float | str]:
        return {
            "time": self.time,
            "energy": self.energy,
            "matter_charge": self.charge,
            "max_matter_amplitude": float(np.max(np.abs(self.phi))),
            "max_content_potential": float(np.max(self.chi)),
            "model_status": "experimental_reciprocal_matter_content_dynamics",
        }
