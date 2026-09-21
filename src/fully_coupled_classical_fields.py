"""Fully coupled classical matter + content scalar + weak U(1) gauge dynamics.

This module extends the common variational system so all three sectors
backreact dynamically on a periodic cubic lattice.

Coordinates:
    Phi(x)       complex matter field
    chi(x)       real content scalar
    A_i(x)       real weak-field U(1) link coordinate

Canonical velocities/momenta:
    Pi(x)
    v_chi(x)
    E_i(x)

Hamiltonian/energy:
    H =
      |Pi|^2
      + sum_i |D_i Phi|^2
      + U(|Phi|^2)
      - g_chi chi |Phi|^2
      + v_chi^2/(2 kappa_chi c_chi^2)
      + |grad chi|^2/(2 kappa_chi)
      + 1/2 sum_i E_i^2
      + beta/2 sum_{i<j} F_ij^2.

Matter-link derivative:
    dH_matter/dA_i(x)
      = 2 Im[
          Phi*(x) exp(i A_i(x)) Phi(x+i)
        ].

Gauge equation:
    A_dot = E
    E_dot = -dH/dA.

With the positive global charge convention
    rho_U1 = 2 Im(Phi* Pi),
the conserved lattice Gauss generator for these canonical signs is
    G = div(E) + rho_U1.

This sign convention is explicit and should not be confused with the alternate
physical-charge convention -rho_U1.

The system uses a kick-drift-kick integrator. It is classical and weak-gauge;
the compact Wilson nonlinearity is not yet used in this fully coupled layer.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

try:
    from .localized_matter_variational import MatterPotential
except ImportError:
    from localized_matter_variational import MatterPotential


AXES = (0, 1, 2)
PLANES = ((0, 1), (1, 2), (2, 0))


def forward(a: np.ndarray, axis: int) -> np.ndarray:
    return np.roll(a, -1, axis=axis)


def backward(a: np.ndarray, axis: int) -> np.ndarray:
    return np.roll(a, 1, axis=axis)


def plaquette(links: np.ndarray, i: int, j: int) -> np.ndarray:
    return (
        links[i]
        + forward(links[j], i)
        - forward(links[i], j)
        - links[j]
    )


def gauge_magnetic_energy(links: np.ndarray, beta: float) -> float:
    if beta < 0:
        raise ValueError("beta must be non-negative")
    return 0.5 * beta * sum(
        float(np.sum(plaquette(links, i, j) ** 2))
        for i, j in PLANES
    )


def gauge_weak_force(links: np.ndarray, beta: float) -> np.ndarray:
    """Return -dV_gauge/dA for quadratic plaquette energy."""
    if beta < 0:
        raise ValueError("beta must be non-negative")
    force = np.zeros_like(links, dtype=float)

    for axis in AXES:
        total = np.zeros_like(links[axis], dtype=float)
        for other in AXES:
            if other == axis:
                continue
            if (axis, other) in PLANES:
                f = plaquette(links, axis, other)
                oriented = f
            else:
                f = plaquette(links, other, axis)
                oriented = -f
            total += oriented - backward(oriented, other)
        force[axis] = -beta * total
    return force


def matter_link_energy(phi: np.ndarray, links: np.ndarray) -> float:
    total = 0.0
    for axis in AXES:
        d = np.exp(1j * links[axis]) * forward(phi, axis) - phi
        total += float(np.sum(np.abs(d) ** 2))
    return total


def matter_link_gradient(phi: np.ndarray, links: np.ndarray) -> np.ndarray:
    """Return dH_matter/dA_i for every oriented link."""
    grad = np.zeros_like(links, dtype=float)
    for axis in AXES:
        transported = np.exp(1j * links[axis]) * forward(phi, axis)
        grad[axis] = 2.0 * np.imag(np.conj(phi) * transported)
    return grad


def gauge_covariant_laplacian(phi: np.ndarray, links: np.ndarray) -> np.ndarray:
    out = np.zeros_like(phi, dtype=complex)
    for axis in AXES:
        out += (
            np.exp(1j * links[axis]) * forward(phi, axis)
            + np.exp(-1j * backward(links[axis], axis))
            * backward(phi, axis)
            - 2.0 * phi
        )
    return out


def periodic_laplacian(a: np.ndarray) -> np.ndarray:
    out = np.zeros_like(a)
    for axis in AXES:
        out += forward(a, axis) + backward(a, axis) - 2.0 * a
    return out


def divergence(links: np.ndarray) -> np.ndarray:
    out = np.zeros_like(links[0], dtype=float)
    for axis in AXES:
        out += links[axis] - backward(links[axis], axis)
    return out


def u1_charge_density(phi: np.ndarray, momentum: np.ndarray) -> np.ndarray:
    return 2.0 * np.imag(np.conj(phi) * momentum)


def u1_charge(phi: np.ndarray, momentum: np.ndarray) -> float:
    return float(np.sum(u1_charge_density(phi, momentum)))


@dataclass(frozen=True)
class FullyCoupledParameters:
    matter: MatterPotential = MatterPotential()
    beta: float = 1.0
    scalar_field_kappa: float = 1.0
    matter_content_coupling: float = 0.1
    content_wave_speed: float = 1.0

    def __post_init__(self) -> None:
        if self.beta < 0:
            raise ValueError("beta must be non-negative")
        if self.scalar_field_kappa <= 0:
            raise ValueError("scalar_field_kappa must be positive")
        if self.matter_content_coupling < 0:
            raise ValueError("matter_content_coupling must be non-negative")
        if self.content_wave_speed <= 0:
            raise ValueError("content_wave_speed must be positive")


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
        gauge_weak_force(links, params.beta)
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
    total += gauge_magnetic_energy(links, params.beta)
    return total


@dataclass
class FullyCoupledClassicalFields:
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
        self.links = np.asarray(self.links, dtype=float).copy()
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
        """Canonical Gauss generator div(E)+rho_U1 for this sign convention."""
        return divergence(self.electric) + u1_charge_density(
            self.phi,
            self.momentum,
        )

    def max_abs_gauss_residual(self) -> float:
        return float(np.max(np.abs(self.gauss_residual())))

    def step(self, dt: float) -> None:
        if dt <= 0:
            raise ValueError("dt must be positive")

        self.momentum += 0.5 * dt * matter_force(
            self.phi, self.chi, self.links, self.params
        )
        self.chi_velocity += 0.5 * dt * content_force(
            self.phi, self.chi, self.params
        )
        self.electric += 0.5 * dt * electric_force(
            self.phi, self.links, self.params
        )

        self.phi += dt * self.momentum
        self.chi += dt * self.chi_velocity
        self.links += dt * self.electric

        self.momentum += 0.5 * dt * matter_force(
            self.phi, self.chi, self.links, self.params
        )
        self.chi_velocity += 0.5 * dt * content_force(
            self.phi, self.chi, self.params
        )
        self.electric += 0.5 * dt * electric_force(
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
            "model_status": "experimental_fully_coupled_classical_fields",
        }
