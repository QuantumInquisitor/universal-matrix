"""Spatially weighted SU(3) reciprocity-geometry dynamics.

This is the SU(3) counterpart of the existing dynamic SU(2) reciprocity engine.

Combined Hamiltonian:

    H = H_psi + H_SU3[psi]

with

    H_psi
      = sum_x [
          (kappa/2) exp(-4 psi) P_psi^2
          + |grad psi|^2/(2 kappa)
        ]

and

    H_SU3
      = 1/2 sum_links w_l E_l^a E_l^a
        + beta sum_p w_p [
            1 - (1/3) ReTr U_p
          ].

The scalar weights are

    w_l = exp[-2 mean_link(psi)]
    w_p = exp[-2 mean_plaquette(psi)].

The geometry source is
    S_psi = -dH_SU3/dpsi

using the exact local deposition implemented in
reciprocity_nonabelian_spatial_geometry.py.

The SU(3) magnetic force is derived from the weighted staple and verified
against a slow group finite-difference oracle.

This is a classical lattice model and the endpoint/corner averaging of psi is
a discretization convention.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

try:
    from .reciprocity_dynamic_su2_geometry import (
        periodic_laplacian,
        geometry_gradient_energy,
        geometry_kinetic_energy,
    )
    from .reciprocity_nonabelian_spatial_geometry import (
        link_weight,
        plaquette_weight,
        local_geometry_source,
        weighted_su3_energy,
    )
    from .su3_hamiltonian import (
        GENERATORS,
        su3_exp,
    )
except ImportError:
    from reciprocity_dynamic_su2_geometry import (
        periodic_laplacian,
        geometry_gradient_energy,
        geometry_kinetic_energy,
    )
    from reciprocity_nonabelian_spatial_geometry import (
        link_weight,
        plaquette_weight,
        local_geometry_source,
        weighted_su3_energy,
    )
    from su3_hamiltonian import GENERATORS, su3_exp


AXES = (0, 1, 2)


def shift_index(idx, axis, step, shape):
    out = list(idx)
    out[axis] = (out[axis] + step) % shape[axis]
    return tuple(out)


def total_energy(
    psi: np.ndarray,
    psi_momentum: np.ndarray,
    links: np.ndarray,
    electric: np.ndarray,
    kappa: float,
    beta: float,
) -> float:
    return (
        geometry_kinetic_energy(psi, psi_momentum, kappa)
        + geometry_gradient_energy(psi, kappa)
        + weighted_su3_energy(
            links,
            electric,
            psi,
            beta,
        )
    )


def geometry_rhs(
    psi: np.ndarray,
    psi_momentum: np.ndarray,
    links: np.ndarray,
    electric: np.ndarray,
    kappa: float,
    beta: float,
) -> tuple[np.ndarray, np.ndarray]:
    p = np.asarray(psi, dtype=float)
    mom = np.asarray(psi_momentum, dtype=float)

    psi_dot = kappa * np.exp(-4.0 * p) * mom
    source = local_geometry_source(
        links,
        electric,
        p,
        beta,
        group_dimension=3,
    )
    momentum_dot = (
        periodic_laplacian(p) / kappa
        + 2.0 * kappa * np.exp(-4.0 * p) * mom**2
        + source
    )
    return psi_dot, momentum_dot


def weighted_staple_sum(
    links: np.ndarray,
    psi: np.ndarray,
    axis: int,
    idx: tuple[int, int, int],
) -> np.ndarray:
    p = np.asarray(psi, dtype=float)
    shape = p.shape
    total = np.zeros((3, 3), dtype=complex)
    x_plus_mu = shift_index(idx, axis, 1, shape)

    for nu in AXES:
        if nu == axis:
            continue

        x_plus_nu = shift_index(idx, nu, 1, shape)
        x_minus_nu = shift_index(idx, nu, -1, shape)
        x_plus_mu_minus_nu = shift_index(
            x_minus_nu,
            axis,
            1,
            shape,
        )

        forward = (
            links[(nu,) + x_plus_mu]
            @ links[(axis,) + x_plus_nu].conj().T
            @ links[(nu,) + idx].conj().T
        )
        backward = (
            links[(nu,) + x_plus_mu_minus_nu].conj().T
            @ links[(axis,) + x_minus_nu].conj().T
            @ links[(nu,) + x_minus_nu]
        )

        wf = plaquette_weight(p, axis, nu)[idx]
        wb = plaquette_weight(p, axis, nu)[x_minus_nu]
        total += wf * forward + wb * backward

    return total


def analytic_weighted_force(
    links: np.ndarray,
    psi: np.ndarray,
    beta: float,
) -> np.ndarray:
    if beta < 0:
        raise ValueError("beta must be non-negative")

    shape = np.asarray(psi).shape
    force = np.zeros(
        (3,) + shape + (8,),
        dtype=float,
    )

    for axis in AXES:
        for idx in np.ndindex(shape):
            product = (
                links[(axis,) + idx]
                @ weighted_staple_sum(
                    links,
                    psi,
                    axis,
                    idx,
                )
            )
            for a, generator in enumerate(GENERATORS):
                force[(axis,) + idx + (a,)] = (
                    -(beta / 3.0)
                    * float(
                        np.trace(
                            generator @ product
                        ).imag
                    )
                )

    return force


def weighted_magnetic_energy(
    links: np.ndarray,
    psi: np.ndarray,
    beta: float,
) -> float:
    shape = np.asarray(psi).shape
    zero_electric = np.zeros(
        (3,) + shape + (8,),
        dtype=float,
    )
    return weighted_su3_energy(
        links,
        zero_electric,
        psi,
        beta,
    )


def weighted_group_force_reference(
    links: np.ndarray,
    psi: np.ndarray,
    beta: float,
    epsilon: float = 1e-6,
) -> np.ndarray:
    """Slow -dH_mag/dq_a group finite-difference oracle."""
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")

    shape = np.asarray(psi).shape
    force = np.zeros(
        (3,) + shape + (8,),
        dtype=float,
    )

    for axis in AXES:
        for idx in np.ndindex(shape):
            original = links[(axis,) + idx].copy()
            for a in range(8):
                direction = np.zeros(8)
                direction[a] = epsilon

                plus = links.copy()
                minus = links.copy()
                plus[(axis,) + idx] = (
                    su3_exp(direction) @ original
                )
                minus[(axis,) + idx] = (
                    su3_exp(-direction) @ original
                )

                derivative = (
                    weighted_magnetic_energy(
                        plus,
                        psi,
                        beta,
                    )
                    - weighted_magnetic_energy(
                        minus,
                        psi,
                        beta,
                    )
                ) / (2.0 * epsilon)

                force[(axis,) + idx + (a,)] = -derivative

    return force


def drift_links_weighted(
    links: np.ndarray,
    electric: np.ndarray,
    psi: np.ndarray,
    dt: float,
) -> np.ndarray:
    if dt <= 0:
        raise ValueError("dt must be positive")

    shape = np.asarray(psi).shape
    if electric.shape != (3,) + shape + (8,):
        raise ValueError("electric shape mismatch")

    out = np.empty_like(links)
    for axis in AXES:
        weight = link_weight(psi, axis)
        for idx in np.ndindex(shape):
            out[(axis,) + idx] = (
                su3_exp(
                    dt
                    * weight[idx]
                    * electric[(axis,) + idx]
                )
                @ links[(axis,) + idx]
            )
    return out


@dataclass
class SU3DynamicReciprocity:
    psi: np.ndarray
    psi_momentum: np.ndarray
    links: np.ndarray
    electric: np.ndarray
    kappa: float = 1.0
    beta: float = 1.0
    time: float = 0.0

    def __post_init__(self) -> None:
        self.psi = np.asarray(self.psi, dtype=float).copy()
        self.psi_momentum = np.asarray(
            self.psi_momentum,
            dtype=float,
        ).copy()
        self.links = np.asarray(
            self.links,
            dtype=complex,
        ).copy()
        self.electric = np.asarray(
            self.electric,
            dtype=float,
        ).copy()

        shape = self.psi.shape
        if self.psi.ndim != 3:
            raise ValueError("psi must be 3D")
        if self.psi_momentum.shape != shape:
            raise ValueError("psi_momentum shape mismatch")
        if self.links.shape != (3,) + shape + (3, 3):
            raise ValueError("link shape mismatch")
        if self.electric.shape != (3,) + shape + (8,):
            raise ValueError("electric shape mismatch")
        if self.kappa <= 0 or self.beta < 0:
            raise ValueError("invalid coupling")

    @property
    def energy(self) -> float:
        return total_energy(
            self.psi,
            self.psi_momentum,
            self.links,
            self.electric,
            self.kappa,
            self.beta,
        )

    def step(self, dt: float) -> None:
        if dt <= 0:
            raise ValueError("dt must be positive")

        _, p_dot = geometry_rhs(
            self.psi,
            self.psi_momentum,
            self.links,
            self.electric,
            self.kappa,
            self.beta,
        )
        self.psi_momentum += 0.5 * dt * p_dot

        force = analytic_weighted_force(
            self.links,
            self.psi,
            self.beta,
        )
        self.electric += 0.5 * dt * force

        psi_dot = (
            self.kappa
            * np.exp(-4.0 * self.psi)
            * self.psi_momentum
        )
        self.psi += dt * psi_dot

        self.links = drift_links_weighted(
            self.links,
            self.electric,
            self.psi,
            dt,
        )

        force = analytic_weighted_force(
            self.links,
            self.psi,
            self.beta,
        )
        self.electric += 0.5 * dt * force

        _, p_dot = geometry_rhs(
            self.psi,
            self.psi_momentum,
            self.links,
            self.electric,
            self.kappa,
            self.beta,
        )
        self.psi_momentum += 0.5 * dt * p_dot

        self.time += dt
