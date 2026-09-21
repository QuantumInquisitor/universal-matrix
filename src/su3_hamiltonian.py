"""Hamiltonian SU(3) lattice gauge dynamics.

Canonical variables:
    U_i(x) in SU(3)
    E_i^a(x), a=1..8

Generators:
    T_a = lambda_a/2
with
    Tr(T_a T_b) = delta_ab/2.

Hamiltonian:
    H =
      1/2 sum E_i^a E_i^a
      + beta sum_p [
          1 - (1/3) Re Tr U_p
        ].

Left-electric link equation:
    U_dot = i E U,
    E = E^a T_a.

Exact drift:
    U -> exp(i dt E) U.

Analytic Wilson force:
    F_i^a
      = -(beta/3)
        Im Tr[T_a U_i K_i],

where K_i is the forward+backward staple sum.

Non-Abelian Gauss matrix:
    G(x)
      = sum_i [
          E_i(x)
          - U_i^dagger(x-i)
            E_i(x-i)
            U_i(x-i)
        ].

The test suite compares the analytic force against direct group-direction
finite differences on a small SU(3) lattice.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from scipy.linalg import expm

try:
    from .su3_lattice_gauge import (
        AXES,
        IDENTITY3,
        is_su3,
        wilson_action,
    )
except ImportError:
    from su3_lattice_gauge import (
        AXES,
        IDENTITY3,
        is_su3,
        wilson_action,
    )


SQRT3 = np.sqrt(3.0)

GELL_MANN = (
    np.array([[0,1,0],[1,0,0],[0,0,0]], dtype=complex),
    np.array([[0,-1j,0],[1j,0,0],[0,0,0]], dtype=complex),
    np.array([[1,0,0],[0,-1,0],[0,0,0]], dtype=complex),
    np.array([[0,0,1],[0,0,0],[1,0,0]], dtype=complex),
    np.array([[0,0,-1j],[0,0,0],[1j,0,0]], dtype=complex),
    np.array([[0,0,0],[0,0,1],[0,1,0]], dtype=complex),
    np.array([[0,0,0],[0,0,-1j],[0,1j,0]], dtype=complex),
    np.array([
        [1/SQRT3,0,0],
        [0,1/SQRT3,0],
        [0,0,-2/SQRT3],
    ], dtype=complex),
)
GENERATORS = tuple(0.5*matrix for matrix in GELL_MANN)


def algebra_matrix(components: np.ndarray) -> np.ndarray:
    e = np.asarray(components, dtype=float)
    if e.shape != (8,):
        raise ValueError("components must have shape (8,)")
    return sum(e[a]*GENERATORS[a] for a in range(8))


def algebra_components(matrix: np.ndarray) -> np.ndarray:
    m = np.asarray(matrix, dtype=complex)
    if m.shape != (3,3):
        raise ValueError("matrix must be 3x3")
    return np.array(
        [
            2.0*float(np.trace(GENERATORS[a] @ m).real)
            for a in range(8)
        ],
        dtype=float,
    )


def su3_exp(components: np.ndarray) -> np.ndarray:
    """exp(i E^a T_a)."""
    m = algebra_matrix(components)
    return expm(1j*m)


def shift_index(
    idx: tuple[int,int,int],
    axis: int,
    step: int,
    shape: tuple[int,int,int],
) -> tuple[int,int,int]:
    out = list(idx)
    out[axis] = (out[axis]+step) % shape[axis]
    return tuple(out)


def staple_sum(
    links: np.ndarray,
    axis: int,
    idx: tuple[int,int,int],
) -> np.ndarray:
    shape = links.shape[1:4]
    total = np.zeros((3,3), dtype=complex)
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
        (3,) + shape + (8,),
        dtype=float,
    )

    for axis in AXES:
        for idx in np.ndindex(shape):
            product = (
                links[(axis,) + idx]
                @ staple_sum(links, axis, idx)
            )
            for a, generator in enumerate(GENERATORS):
                force[(axis,) + idx + (a,)] = (
                    -(beta/3.0)
                    * float(
                        np.trace(
                            generator @ product
                        ).imag
                    )
                )

    return force


def reference_force(
    links: np.ndarray,
    beta: float,
    epsilon: float = 1e-6,
) -> np.ndarray:
    """Slow group-direction finite-difference force oracle."""
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")

    shape = links.shape[1:4]
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
                    wilson_action(plus, beta)
                    - wilson_action(minus, beta)
                ) / (2.0*epsilon)
                force[(axis,) + idx + (a,)] = -derivative

    return force


def drift_links(
    links: np.ndarray,
    electric: np.ndarray,
    dt: float,
) -> np.ndarray:
    if dt <= 0:
        raise ValueError("dt must be positive")

    shape = links.shape[1:4]
    if electric.shape != (3,) + shape + (8,):
        raise ValueError("electric shape mismatch")

    out = np.empty_like(links)
    for axis in AXES:
        for idx in np.ndindex(shape):
            out[(axis,) + idx] = (
                su3_exp(
                    dt*electric[(axis,) + idx]
                )
                @ links[(axis,) + idx]
            )
    return out


def backward_index(
    idx: tuple[int,int,int],
    axis: int,
    shape: tuple[int,int,int],
) -> tuple[int,int,int]:
    return shift_index(idx, axis, -1, shape)


def gauss_matrices(
    links: np.ndarray,
    electric: np.ndarray,
) -> np.ndarray:
    shape = links.shape[1:4]
    if electric.shape != (3,) + shape + (8,):
        raise ValueError("electric shape mismatch")

    out = np.zeros(shape + (3,3), dtype=complex)

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
        out[idx] = total

    return out


def gauss_components(
    links: np.ndarray,
    electric: np.ndarray,
) -> np.ndarray:
    matrices = gauss_matrices(links, electric)
    shape = matrices.shape[:3]
    out = np.zeros(shape + (8,), dtype=float)
    for idx in np.ndindex(shape):
        out[idx] = algebra_components(
            matrices[idx]
        )
    return out


def max_gauss_residual(
    links: np.ndarray,
    electric: np.ndarray,
) -> float:
    return float(
        np.max(
            np.abs(
                gauss_components(
                    links,
                    electric,
                )
            )
        )
    )


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


@dataclass
class SU3Hamiltonian:
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
        if self.links.shape != (3,) + shape + (3,3):
            raise ValueError("link shape mismatch")
        if self.electric.shape != (3,) + shape + (8,):
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
