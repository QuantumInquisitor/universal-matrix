"""Reference SU(2) Hamiltonian lattice gauge dynamics.

Canonical variables:
    U_i(x) in SU(2)
    E_i^a(x) in R^3

Generators:
    T_a = sigma_a/2

Hamiltonian:
    H =
      1/2 sum_{links,a} (E_i^a)^2
      + beta sum_p [
          1 - 1/2 Re Tr U_p
        ].

Left-electric convention:
    U_dot = i E^a T_a U.

For the reference implementation, the Wilson force is evaluated by symmetric
finite differences along exact SU(2) group directions:

    U -> exp(+i eps T_a) U
    U -> exp(-i eps T_a) U.

This is intentionally a correctness reference. A later optimized engine can
replace the finite-difference force with an analytic staple expression and be
tested against this module.

Non-Abelian Gauss matrix at site x:

    G(x)
      = sum_i [
          E_i(x)
          - U_i^dagger(x-i) E_i(x-i) U_i(x-i)
        ].

For source-free physical initial data, G=0 should remain conserved under the
exact Hamiltonian flow. The finite-difference reference preserves it up to
numerical force/integration error.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

try:
    from .su2_lattice_gauge import (
        AXES,
        IDENTITY2,
        is_su2,
        wilson_action,
    )
except ImportError:
    from su2_lattice_gauge import (
        AXES,
        IDENTITY2,
        is_su2,
        wilson_action,
    )


SIGMA = (
    np.array([[0, 1], [1, 0]], dtype=complex),
    np.array([[0, -1j], [1j, 0]], dtype=complex),
    np.array([[1, 0], [0, -1]], dtype=complex),
)
GENERATORS = tuple(0.5*s for s in SIGMA)


def su2_exp(algebra_vector: np.ndarray) -> np.ndarray:
    """exp(i v^a sigma_a/2) in closed form."""
    v = np.asarray(algebra_vector, dtype=float)
    if v.shape != (3,):
        raise ValueError("algebra_vector must have shape (3,)")

    magnitude = float(np.linalg.norm(v))
    if magnitude == 0.0:
        return IDENTITY2.copy()

    direction_matrix = sum(
        (v[a]/magnitude)*SIGMA[a]
        for a in range(3)
    )
    half = 0.5*magnitude
    return (
        math.cos(half)*IDENTITY2
        + 1j*math.sin(half)*direction_matrix
    )


def electric_matrix(components: np.ndarray) -> np.ndarray:
    e = np.asarray(components, dtype=float)
    if e.shape != (3,):
        raise ValueError("electric components must have shape (3,)")
    return sum(e[a]*GENERATORS[a] for a in range(3))


def algebra_components(matrix: np.ndarray) -> np.ndarray:
    """Components v^a for Hermitian traceless matrix v^a T_a."""
    m = np.asarray(matrix, dtype=complex)
    return np.array(
        [
            2.0*float(np.trace(GENERATORS[a] @ m).real)
            for a in range(3)
        ],
        dtype=float,
    )


def identity_links(shape: tuple[int,int,int]) -> np.ndarray:
    out = np.empty((3,) + shape + (2,2), dtype=complex)
    out[...] = IDENTITY2
    return out


def zero_electric(shape: tuple[int,int,int]) -> np.ndarray:
    return np.zeros((3,) + shape + (3,), dtype=float)


def kinetic_energy(electric: np.ndarray) -> float:
    return 0.5*float(np.sum(np.asarray(electric, dtype=float)**2))


def total_energy(
    links: np.ndarray,
    electric: np.ndarray,
    beta: float,
) -> float:
    return kinetic_energy(electric) + wilson_action(links, beta)


def drift_links(
    links: np.ndarray,
    electric: np.ndarray,
    dt: float,
) -> np.ndarray:
    if dt <= 0:
        raise ValueError("dt must be positive")
    shape = links.shape[1:4]
    if electric.shape != (3,) + shape + (3,):
        raise ValueError("electric shape mismatch")

    out = np.empty_like(links)
    for axis in AXES:
        for idx in np.ndindex(shape):
            rotation = su2_exp(
                dt*electric[(axis,) + idx]
            )
            out[(axis,) + idx] = (
                rotation @ links[(axis,) + idx]
            )
    return out


def wilson_force_reference(
    links: np.ndarray,
    beta: float,
    epsilon: float = 1e-6,
) -> np.ndarray:
    """Return -dV/dq_a for left multiplication exp(i q_a T_a)."""
    if beta < 0:
        raise ValueError("beta must be non-negative")
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")

    shape = links.shape[1:4]
    force = np.zeros((3,) + shape + (3,), dtype=float)

    for axis in AXES:
        for idx in np.ndindex(shape):
            original = links[(axis,) + idx].copy()
            for a in range(3):
                direction = np.zeros(3)
                direction[a] = epsilon

                plus = links.copy()
                minus = links.copy()

                plus[(axis,) + idx] = (
                    su2_exp(direction) @ original
                )
                minus[(axis,) + idx] = (
                    su2_exp(-direction) @ original
                )

                derivative = (
                    wilson_action(plus, beta)
                    - wilson_action(minus, beta)
                ) / (2.0*epsilon)

                force[(axis,) + idx + (a,)] = -derivative

    return force


def backward_index(
    idx: tuple[int,int,int],
    axis: int,
    shape: tuple[int,int,int],
) -> tuple[int,int,int]:
    out = list(idx)
    out[axis] = (out[axis]-1) % shape[axis]
    return tuple(out)


def gauss_matrices(
    links: np.ndarray,
    electric: np.ndarray,
) -> np.ndarray:
    shape = links.shape[1:4]
    if electric.shape != (3,) + shape + (3,):
        raise ValueError("electric shape mismatch")

    out = np.zeros(shape + (2,2), dtype=complex)

    for idx in np.ndindex(shape):
        total = np.zeros((2,2), dtype=complex)
        for axis in AXES:
            outgoing = electric_matrix(
                electric[(axis,) + idx]
            )
            xm = backward_index(idx, axis, shape)
            u_in = links[(axis,) + xm]
            incoming_source = electric_matrix(
                electric[(axis,) + xm]
            )
            incoming_at_site = (
                u_in.conj().T
                @ incoming_source
                @ u_in
            )
            total += outgoing - incoming_at_site
        out[idx] = total
    return out


def gauss_components(
    links: np.ndarray,
    electric: np.ndarray,
) -> np.ndarray:
    matrices = gauss_matrices(links, electric)
    shape = matrices.shape[:3]
    out = np.zeros(shape + (3,), dtype=float)
    for idx in np.ndindex(shape):
        out[idx] = algebra_components(matrices[idx])
    return out


def max_gauss_residual(
    links: np.ndarray,
    electric: np.ndarray,
) -> float:
    return float(
        np.max(
            np.abs(
                gauss_components(links, electric)
            )
        )
    )


@dataclass
class SU2HamiltonianReference:
    links: np.ndarray
    electric: np.ndarray
    beta: float = 1.0
    force_epsilon: float = 1e-6
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
        if self.force_epsilon <= 0:
            raise ValueError("force_epsilon must be positive")

    @classmethod
    def zeros(
        cls,
        shape: tuple[int,int,int] = (2,2,2),
        beta: float = 1.0,
    ) -> "SU2HamiltonianReference":
        return cls(
            links=identity_links(shape),
            electric=zero_electric(shape),
            beta=beta,
        )

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

        force = wilson_force_reference(
            self.links,
            self.beta,
            self.force_epsilon,
        )
        self.electric += 0.5*dt*force

        self.links = drift_links(
            self.links,
            self.electric,
            dt,
        )

        force = wilson_force_reference(
            self.links,
            self.beta,
            self.force_epsilon,
        )
        self.electric += 0.5*dt*force
        self.time += dt
