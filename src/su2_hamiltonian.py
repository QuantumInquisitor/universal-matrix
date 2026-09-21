"""Optimized SU(2) Hamiltonian lattice gauge dynamics.

This module replaces the finite-difference Wilson force in
su2_hamiltonian_reference.py with the analytic staple force.

For a link U_mu(x), define the staple sum K_mu(x) over every nu != mu:

forward staple:
    U_nu(x+mu)
    U_mu^dagger(x+nu)
    U_nu^dagger(x)

backward staple:
    U_nu^dagger(x+mu-nu)
    U_mu^dagger(x-nu)
    U_nu(x-nu)

The Wilson terms containing the link can be written

    V_link
      = const
        - (beta/2) Re Tr[U_mu(x) K_mu(x)].

Under left variation
    U -> exp(i eps T_a) U,

the canonical force is

    F_mu^a
      = -dV/d eps
      = -(beta/2) Im Tr[T_a U_mu K_mu].

The implementation is tested pointwise against the slower group finite-
difference reference force.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

try:
    from .su2_lattice_gauge import AXES, wilson_action
    from .su2_hamiltonian_reference import (
        GENERATORS,
        drift_links,
        gauss_components,
        max_gauss_residual,
    )
except ImportError:
    from su2_lattice_gauge import AXES, wilson_action
    from su2_hamiltonian_reference import (
        GENERATORS,
        drift_links,
        gauss_components,
        max_gauss_residual,
    )


def shift_index(
    idx: tuple[int,int,int],
    axis: int,
    step: int,
    shape: tuple[int,int,int],
) -> tuple[int,int,int]:
    out = list(idx)
    out[axis] = (out[axis] + step) % shape[axis]
    return tuple(out)


def staple_sum(
    links: np.ndarray,
    axis: int,
    idx: tuple[int,int,int],
) -> np.ndarray:
    shape = links.shape[1:4]
    if axis not in AXES:
        raise ValueError("axis must be 0,1,2")

    total = np.zeros((2,2), dtype=complex)

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

        total += forward + backward

    return total


def analytic_wilson_force(
    links: np.ndarray,
    beta: float,
) -> np.ndarray:
    if beta < 0:
        raise ValueError("beta must be non-negative")

    shape = links.shape[1:4]
    force = np.zeros(
        (3,) + shape + (3,),
        dtype=float,
    )

    for axis in AXES:
        for idx in np.ndindex(shape):
            u = links[(axis,) + idx]
            staple = staple_sum(
                links,
                axis,
                idx,
            )
            product = u @ staple

            for a, generator in enumerate(GENERATORS):
                force[(axis,) + idx + (a,)] = (
                    -0.5
                    * beta
                    * float(
                        np.trace(
                            generator @ product
                        ).imag
                    )
                )

    return force


def kinetic_energy(electric: np.ndarray) -> float:
    return 0.5*float(
        np.sum(
            np.asarray(electric, dtype=float)**2
        )
    )


def total_energy(
    links: np.ndarray,
    electric: np.ndarray,
    beta: float,
) -> float:
    return kinetic_energy(electric) + wilson_action(
        links,
        beta,
    )


def force_gauss_residual(
    links: np.ndarray,
    beta: float,
) -> float:
    """Covariant divergence of the analytic gauge force."""
    force = analytic_wilson_force(links, beta)
    return max_gauss_residual(links, force)


@dataclass
class SU2Hamiltonian:
    links: np.ndarray
    electric: np.ndarray
    beta: float = 1.0
    time: float = 0.0

    def __post_init__(self) -> None:
        self.links = np.asarray(
            self.links,
            dtype=complex,
        ).copy()
        self.electric = np.asarray(
            self.electric,
            dtype=float,
        ).copy()

        shape = self.links.shape[1:4]
        if self.links.shape != (3,) + shape + (2,2):
            raise ValueError("link shape mismatch")
        if self.electric.shape != (3,) + shape + (3,):
            raise ValueError("electric shape mismatch")
        if self.beta < 0:
            raise ValueError("beta must be non-negative")

    @property
    def energy(self) -> float:
        return total_energy(
            self.links,
            self.electric,
            self.beta,
        )

    @property
    def max_gauss(self) -> float:
        return max_gauss_residual(
            self.links,
            self.electric,
        )

    def step(self, dt: float) -> None:
        if dt <= 0:
            raise ValueError("dt must be positive")

        force = analytic_wilson_force(
            self.links,
            self.beta,
        )
        self.electric += 0.5*dt*force

        self.links = drift_links(
            self.links,
            self.electric,
            dt,
        )

        force = analytic_wilson_force(
            self.links,
            self.beta,
        )
        self.electric += 0.5*dt*force

        self.time += dt
