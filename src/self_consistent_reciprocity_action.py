"""Self-consistent reciprocity-geometry + complex-matter action.

Natural units c_*=1 are used in this module.

Effective metric:
    g_{mu nu}(psi)
      = diag(-exp(-2 psi), exp(2 psi), exp(2 psi), exp(2 psi))

so
    sqrt(-g) = exp(2 psi).

Geometry-scalar action density:
    L_psi
      = -(1/(2 kappa)) sqrt(-g) g^{mu nu}
          partial_mu psi partial_nu psi

which reduces exactly to
    L_psi
      = exp(4 psi) psi_t^2/(2 kappa)
        - |grad psi|^2/(2 kappa).

Complex scalar matter:
    L_m
      = -sqrt(-g) [
          g^{mu nu} partial_mu Phi^* partial_nu Phi
          + U(|Phi|^2)
        ]

which reduces to
    L_m
      = exp(4 psi) |Phi_t|^2
        - |grad Phi|^2
        - exp(2 psi) U(|Phi|^2).

The psi variation of the matter action is
    d L_m / d psi
      = 4 exp(4 psi) |Phi_t|^2
        - 2 exp(2 psi) U.

This equals
    sqrt(-g) * (rho + p_x + p_y + p_z)
for the complex scalar stress tensor.

Thus the source is derived from stress-energy rather than an assigned
amplitude-density charge.

Canonical momenta:
    P_psi = exp(4 psi) psi_t / kappa
    Pi    = exp(4 psi) Phi_t

Hamiltonian density:
    H =
      (kappa/2) exp(-4 psi) P_psi^2
      + |grad psi|^2/(2 kappa)
      + exp(-4 psi) |Pi|^2
      + |grad Phi|^2
      + exp(2 psi) U.

This module implements the periodic-lattice Hamiltonian and RK4 evolution for
research tests. It is an experimental scalar-geometry theory, not established
gravity.
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


def gradient_energy(field: np.ndarray) -> float:
    a = np.asarray(field)
    total = 0.0
    for axis in AXES:
        d = np.roll(a, -1, axis=axis) - a
        total += float(np.sum(np.abs(d) ** 2))
    return total


def matter_potential_density(
    phi: np.ndarray,
    potential: MatterPotential,
) -> np.ndarray:
    rho = np.abs(np.asarray(phi, dtype=complex)) ** 2
    return (
        potential.mass2 * rho
        + potential.lambda4 * rho**2
        + potential.lambda6 * rho**3
    )


def matter_potential_derivative(
    phi: np.ndarray,
    potential: MatterPotential,
) -> np.ndarray:
    rho = np.abs(np.asarray(phi, dtype=complex)) ** 2
    return (
        potential.mass2
        + 2.0 * potential.lambda4 * rho
        + 3.0 * potential.lambda6 * rho**2
    )


def effective_metric_diagonal(psi: np.ndarray | float) -> np.ndarray:
    value = np.asarray(psi, dtype=float)
    return np.stack(
        [
            -np.exp(-2.0 * value),
            np.exp(2.0 * value),
            np.exp(2.0 * value),
            np.exp(2.0 * value),
        ],
        axis=0,
    )


def sqrt_minus_g(psi: np.ndarray | float) -> np.ndarray:
    return np.exp(2.0 * np.asarray(psi, dtype=float))


def active_source_density_velocity_form(
    phi: np.ndarray,
    phi_velocity: np.ndarray,
    psi: np.ndarray,
    potential: MatterPotential,
) -> np.ndarray:
    """sqrt(-g)*(rho + p_x+p_y+p_z) from direct action variation."""
    phi = np.asarray(phi, dtype=complex)
    phi_velocity = np.asarray(phi_velocity, dtype=complex)
    psi = np.asarray(psi, dtype=float)
    return (
        4.0 * np.exp(4.0 * psi) * np.abs(phi_velocity) ** 2
        - 2.0 * np.exp(2.0 * psi)
        * matter_potential_density(phi, potential)
    )


def active_source_density_canonical(
    phi: np.ndarray,
    momentum: np.ndarray,
    psi: np.ndarray,
    potential: MatterPotential,
) -> np.ndarray:
    """Same source written using Pi=exp(4 psi) Phi_t."""
    phi = np.asarray(phi, dtype=complex)
    momentum = np.asarray(momentum, dtype=complex)
    psi = np.asarray(psi, dtype=float)
    return (
        4.0 * np.exp(-4.0 * psi) * np.abs(momentum) ** 2
        - 2.0 * np.exp(2.0 * psi)
        * matter_potential_density(phi, potential)
    )


def local_matter_energy_density(
    phi: np.ndarray,
    phi_velocity: np.ndarray,
    psi: np.ndarray,
    potential: MatterPotential,
    spatial_gradient_squared: np.ndarray | float = 0.0,
) -> np.ndarray:
    """Coordinate Hamiltonian density in velocity variables."""
    return (
        np.exp(4.0 * psi) * np.abs(phi_velocity) ** 2
        + np.asarray(spatial_gradient_squared, dtype=float)
        + np.exp(2.0 * psi) * matter_potential_density(phi, potential)
    )


def rest_harmonic_source_energy_identity(
    amplitude: float,
    mass: float,
) -> tuple[float, float]:
    """Return (active_source, rest_energy_density) at psi=0 for Phi=A exp(-imt)."""
    if amplitude < 0 or mass <= 0:
        raise ValueError("amplitude must be non-negative and mass positive")
    rho = amplitude * amplitude
    kinetic = mass * mass * rho
    potential = mass * mass * rho
    source = 4.0 * kinetic - 2.0 * potential
    energy = kinetic + potential
    return source, energy


def null_coordinate_speed(psi: float) -> float:
    """Coordinate light speed from the effective metric in c_*=1 units."""
    return math.exp(-2.0 * psi)


def scalar_characteristic_speed(psi: float) -> float:
    """Principal-part speed of the psi equation."""
    return math.exp(-2.0 * psi)


@dataclass(frozen=True)
class ReciprocityActionParameters:
    kappa: float = 1.0
    matter: MatterPotential = MatterPotential()

    def __post_init__(self) -> None:
        if self.kappa <= 0:
            raise ValueError("kappa must be positive")


def hamiltonian(
    phi: np.ndarray,
    momentum: np.ndarray,
    psi: np.ndarray,
    psi_momentum: np.ndarray,
    params: ReciprocityActionParameters,
) -> float:
    phi = np.asarray(phi, dtype=complex)
    momentum = np.asarray(momentum, dtype=complex)
    psi = np.asarray(psi, dtype=float)
    psi_momentum = np.asarray(psi_momentum, dtype=float)

    if not (
        phi.shape
        == momentum.shape
        == psi.shape
        == psi_momentum.shape
    ):
        raise ValueError("all fields must have the same 3D shape")

    exp_m4 = np.exp(-4.0 * psi)
    exp_p2 = np.exp(2.0 * psi)

    total = 0.5 * params.kappa * float(
        np.sum(exp_m4 * psi_momentum**2)
    )
    total += gradient_energy(psi) / (2.0 * params.kappa)
    total += float(np.sum(exp_m4 * np.abs(momentum) ** 2))
    total += gradient_energy(phi)
    total += float(
        np.sum(
            exp_p2
            * matter_potential_density(phi, params.matter)
        )
    )
    return total


def rhs(
    phi: np.ndarray,
    momentum: np.ndarray,
    psi: np.ndarray,
    psi_momentum: np.ndarray,
    params: ReciprocityActionParameters,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Hamilton equations for (Phi,Pi,psi,P_psi)."""
    phi = np.asarray(phi, dtype=complex)
    momentum = np.asarray(momentum, dtype=complex)
    psi = np.asarray(psi, dtype=float)
    psi_momentum = np.asarray(psi_momentum, dtype=float)

    exp_m4 = np.exp(-4.0 * psi)
    exp_p2 = np.exp(2.0 * psi)

    phi_dot = exp_m4 * momentum

    momentum_dot = (
        periodic_laplacian(phi)
        - exp_p2
        * matter_potential_derivative(phi, params.matter)
        * phi
    )

    psi_dot = params.kappa * exp_m4 * psi_momentum

    psi_momentum_dot = (
        periodic_laplacian(psi) / params.kappa
        + 2.0 * params.kappa * exp_m4 * psi_momentum**2
        + 4.0 * exp_m4 * np.abs(momentum) ** 2
        - 2.0 * exp_p2
        * matter_potential_density(phi, params.matter)
    )

    return phi_dot, momentum_dot, psi_dot, psi_momentum_dot


@dataclass
class SelfConsistentReciprocityDynamics:
    phi: np.ndarray
    momentum: np.ndarray
    psi: np.ndarray
    psi_momentum: np.ndarray
    params: ReciprocityActionParameters = ReciprocityActionParameters()
    time: float = 0.0

    def __post_init__(self) -> None:
        self.phi = np.asarray(self.phi, dtype=complex).copy()
        self.momentum = np.asarray(self.momentum, dtype=complex).copy()
        self.psi = np.asarray(self.psi, dtype=float).copy()
        self.psi_momentum = np.asarray(self.psi_momentum, dtype=float).copy()

        shape = self.phi.shape
        if self.phi.ndim != 3:
            raise ValueError("fields must be 3D")
        if not (
            self.momentum.shape
            == self.psi.shape
            == self.psi_momentum.shape
            == shape
        ):
            raise ValueError("field shape mismatch")

    @property
    def energy(self) -> float:
        return hamiltonian(
            self.phi,
            self.momentum,
            self.psi,
            self.psi_momentum,
            self.params,
        )

    @property
    def charge(self) -> float:
        return float(
            2.0
            * np.imag(
                np.vdot(self.phi, self.momentum)
            )
        )

    def _state_add(
        self,
        base,
        deriv,
        scale: float,
    ):
        return tuple(
            b + scale*d
            for b, d in zip(base, deriv)
        )

    def step_rk4(self, dt: float) -> None:
        if dt <= 0:
            raise ValueError("dt must be positive")

        y0 = (
            self.phi,
            self.momentum,
            self.psi,
            self.psi_momentum,
        )

        k1 = rhs(*y0, self.params)
        k2 = rhs(
            *self._state_add(y0, k1, 0.5*dt),
            self.params,
        )
        k3 = rhs(
            *self._state_add(y0, k2, 0.5*dt),
            self.params,
        )
        k4 = rhs(
            *self._state_add(y0, k3, dt),
            self.params,
        )

        updated = []
        for base, d1, d2, d3, d4 in zip(
            y0, k1, k2, k3, k4
        ):
            updated.append(
                base
                + (dt/6.0)
                * (d1 + 2*d2 + 2*d3 + d4)
            )

        (
            self.phi,
            self.momentum,
            self.psi,
            self.psi_momentum,
        ) = updated
        self.time += dt

    def snapshot(self) -> dict[str, float | str]:
        return {
            "time": self.time,
            "energy": self.energy,
            "u1_charge": self.charge,
            "max_abs_psi": float(np.max(np.abs(self.psi))),
            "max_matter_amplitude": float(np.max(np.abs(self.phi))),
            "model_status": "experimental_self_consistent_reciprocity_action",
        }
