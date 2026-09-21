"""Fully coupled classical SU(3) fundamental matter + gauge dynamics.

Matter:
    Psi(x) in C^3
    Pi(x)  in C^3

Gauge:
    U_i(x) in SU(3)
    E_i^a(x), a=1..8

Hamiltonian:
    H =
      sum |Pi|^2
      + sum |U_i Psi(x+i)-Psi(x)|^2
      + sum [m2 rho + lambda4 rho^2]
      + 1/2 sum E^2
      + beta sum_p [1 - (1/3) ReTr U_p].

Matter current:
    J_i^a
      = 2 Im[
          Psi^dagger T_a U_i Psi(x+i)
        ].

Matter charge:
    rho_a
      = 2 Im[
          Psi^dagger T_a Pi
        ].

Coupled Gauss generator:
    G_a = (D_i E_i)_a + rho_a.

This is a classical SU(3) triplet gauge theory, not a QCD claim.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

try:
    from .su3_hamiltonian import (
        GENERATORS,
        algebra_components,
        algebra_matrix,
        analytic_wilson_force,
        backward_index,
        drift_links,
    )
    from .su3_lattice_gauge import AXES, wilson_action
except ImportError:
    from su3_hamiltonian import (
        GENERATORS,
        algebra_components,
        algebra_matrix,
        analytic_wilson_force,
        backward_index,
        drift_links,
    )
    from su3_lattice_gauge import AXES, wilson_action


@dataclass(frozen=True)
class SU3ScalarMatterParameters:
    mass2: float = 1.0
    lambda4: float = 0.0

    def __post_init__(self) -> None:
        if self.lambda4 < 0:
            raise ValueError(
                "lambda4 must be non-negative in this bounded prototype"
            )


def matter_density(psi: np.ndarray) -> np.ndarray:
    field = np.asarray(psi, dtype=complex)
    if field.ndim != 4 or field.shape[-1] != 3:
        raise ValueError("psi must have shape (nx,ny,nz,3)")
    return np.sum(np.abs(field)**2, axis=-1)


def forward_index(
    idx: tuple[int,int,int],
    axis: int,
    shape: tuple[int,int,int],
) -> tuple[int,int,int]:
    out = list(idx)
    out[axis] = (out[axis]+1) % shape[axis]
    return tuple(out)


def covariant_laplacian(
    psi: np.ndarray,
    links: np.ndarray,
) -> np.ndarray:
    field = np.asarray(psi, dtype=complex)
    shape = field.shape[:3]
    out = np.zeros_like(field)

    for idx in np.ndindex(shape):
        total = np.zeros(3, dtype=complex)
        for axis in AXES:
            xp = forward_index(idx, axis, shape)
            xm = backward_index(idx, axis, shape)

            total += (
                links[(axis,) + idx] @ field[xp]
                + links[(axis,) + xm].conj().T @ field[xm]
                - 2.0*field[idx]
            )
        out[idx] = total

    return out


def matter_force(
    psi: np.ndarray,
    links: np.ndarray,
    params: SU3ScalarMatterParameters,
) -> np.ndarray:
    rho = matter_density(psi)
    return (
        covariant_laplacian(psi, links)
        - (
            params.mass2
            + 2.0*params.lambda4*rho
        )[...,None]*psi
    )


def matter_hopping_energy(
    psi: np.ndarray,
    links: np.ndarray,
) -> float:
    field = np.asarray(psi, dtype=complex)
    shape = field.shape[:3]
    total = 0.0

    for idx in np.ndindex(shape):
        for axis in AXES:
            xp = forward_index(idx, axis, shape)
            d = (
                links[(axis,) + idx] @ field[xp]
                - field[idx]
            )
            total += float(np.vdot(d,d).real)

    return total


def matter_potential_energy(
    psi: np.ndarray,
    params: SU3ScalarMatterParameters,
) -> float:
    rho = matter_density(psi)
    return float(
        np.sum(
            params.mass2*rho
            + params.lambda4*rho**2
        )
    )


def matter_link_current(
    psi: np.ndarray,
    links: np.ndarray,
) -> np.ndarray:
    field = np.asarray(psi, dtype=complex)
    shape = field.shape[:3]
    out = np.zeros(
        (3,) + shape + (8,),
        dtype=float,
    )

    for idx in np.ndindex(shape):
        for axis in AXES:
            xp = forward_index(idx, axis, shape)
            transported = (
                links[(axis,) + idx] @ field[xp]
            )
            for a, generator in enumerate(GENERATORS):
                out[(axis,) + idx + (a,)] = (
                    2.0
                    * float(
                        np.vdot(
                            field[idx],
                            generator @ transported,
                        ).imag
                    )
                )
    return out


def matter_charge_density(
    psi: np.ndarray,
    momentum: np.ndarray,
) -> np.ndarray:
    field = np.asarray(psi, dtype=complex)
    pi = np.asarray(momentum, dtype=complex)
    if field.shape != pi.shape:
        raise ValueError("psi and momentum shapes must match")

    shape = field.shape[:3]
    out = np.zeros(shape + (8,), dtype=float)

    for idx in np.ndindex(shape):
        for a, generator in enumerate(GENERATORS):
            out[idx + (a,)] = (
                2.0
                * float(
                    np.vdot(
                        field[idx],
                        generator @ pi[idx],
                    ).imag
                )
            )
    return out


def pure_gauge_gauss_components(
    links: np.ndarray,
    electric: np.ndarray,
) -> np.ndarray:
    shape = links.shape[1:4]
    out = np.zeros(shape + (8,), dtype=float)

    for idx in np.ndindex(shape):
        total = np.zeros((3,3), dtype=complex)
        for axis in AXES:
            outgoing = algebra_matrix(
                electric[(axis,) + idx]
            )
            xm = backward_index(idx, axis, shape)
            u_in = links[(axis,) + xm]
            incoming = algebra_matrix(
                electric[(axis,) + xm]
            )
            total += (
                outgoing
                - u_in.conj().T @ incoming @ u_in
            )
        out[idx] = algebra_components(total)

    return out


def coupled_gauss_components(
    psi: np.ndarray,
    momentum: np.ndarray,
    links: np.ndarray,
    electric: np.ndarray,
) -> np.ndarray:
    return (
        pure_gauge_gauss_components(links, electric)
        + matter_charge_density(psi, momentum)
    )


def total_energy(
    psi: np.ndarray,
    momentum: np.ndarray,
    links: np.ndarray,
    electric: np.ndarray,
    beta: float,
    params: SU3ScalarMatterParameters,
) -> float:
    return (
        float(np.sum(np.abs(momentum)**2))
        + matter_hopping_energy(psi, links)
        + matter_potential_energy(psi, params)
        + 0.5*float(np.sum(electric**2))
        + wilson_action(links, beta)
    )


def gauge_transform_state(
    psi: np.ndarray,
    momentum: np.ndarray,
    links: np.ndarray,
    electric: np.ndarray,
    site_transform: np.ndarray,
) -> tuple[np.ndarray,np.ndarray,np.ndarray,np.ndarray]:
    field = np.asarray(psi, dtype=complex)
    pi = np.asarray(momentum, dtype=complex)
    shape = field.shape[:3]

    psi_out = np.empty_like(field)
    pi_out = np.empty_like(pi)
    links_out = np.empty_like(links)
    electric_out = np.empty_like(electric)

    for idx in np.ndindex(shape):
        g = site_transform[idx]
        psi_out[idx] = g @ field[idx]
        pi_out[idx] = g @ pi[idx]

    for axis in AXES:
        for idx in np.ndindex(shape):
            xp = forward_index(idx, axis, shape)
            g = site_transform[idx]

            links_out[(axis,) + idx] = (
                g
                @ links[(axis,) + idx]
                @ site_transform[xp].conj().T
            )

            e_matrix = algebra_matrix(
                electric[(axis,) + idx]
            )
            electric_out[(axis,) + idx] = (
                algebra_components(
                    g @ e_matrix @ g.conj().T
                )
            )

    return psi_out,pi_out,links_out,electric_out


@dataclass
class SU3MatterGaugeDynamics:
    psi: np.ndarray
    momentum: np.ndarray
    links: np.ndarray
    electric: np.ndarray
    beta: float = 1.0
    matter_params: SU3ScalarMatterParameters = SU3ScalarMatterParameters()
    time: float = 0.0

    def __post_init__(self) -> None:
        self.psi = np.asarray(self.psi, dtype=complex).copy()
        self.momentum = np.asarray(
            self.momentum,
            dtype=complex,
        ).copy()
        self.links = np.asarray(self.links, dtype=complex).copy()
        self.electric = np.asarray(
            self.electric,
            dtype=float,
        ).copy()

        shape = self.psi.shape[:3]
        if self.psi.shape != shape + (3,):
            raise ValueError("psi shape mismatch")
        if self.momentum.shape != self.psi.shape:
            raise ValueError("momentum shape mismatch")
        if self.links.shape != (3,) + shape + (3,3):
            raise ValueError("links shape mismatch")
        if self.electric.shape != (3,) + shape + (8,):
            raise ValueError("electric shape mismatch")

    @property
    def energy(self) -> float:
        return total_energy(
            self.psi,
            self.momentum,
            self.links,
            self.electric,
            self.beta,
            self.matter_params,
        )

    @property
    def max_gauss(self) -> float:
        return float(
            np.max(
                np.abs(
                    coupled_gauss_components(
                        self.psi,
                        self.momentum,
                        self.links,
                        self.electric,
                    )
                )
            )
        )

    def step(self, dt: float) -> None:
        if dt <= 0:
            raise ValueError("dt must be positive")

        self.momentum += 0.5*dt*matter_force(
            self.psi,
            self.links,
            self.matter_params,
        )
        self.electric += 0.5*dt*(
            analytic_wilson_force(
                self.links,
                self.beta,
            )
            - matter_link_current(
                self.psi,
                self.links,
            )
        )

        self.psi += dt*self.momentum
        self.links = drift_links(
            self.links,
            self.electric,
            dt,
        )

        self.momentum += 0.5*dt*matter_force(
            self.psi,
            self.links,
            self.matter_params,
        )
        self.electric += 0.5*dt*(
            analytic_wilson_force(
                self.links,
                self.beta,
            )
            - matter_link_current(
                self.psi,
                self.links,
            )
        )

        self.time += dt
