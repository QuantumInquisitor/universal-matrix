"""Homogeneous time-dependent Dirac field on reciprocity geometry.

Metric:
    ds^2 = -N(t)^2 dt^2 + a(t)^2 d x^2

with reciprocity factors
    N = exp(-psi)
    a = exp(+psi).

For a spatial Fourier mode p, define the original curved-space spinor Psi and
the volume-rescaled spinor

    chi = a^(3/2) Psi = exp(3 psi/2) Psi.

The rescaled spinor obeys the Hermitian coordinate-time equation

    i d_t chi = H_chi chi

with

    H_chi
      = exp(-2 psi) alpha.p
        + exp(-psi) beta m.

The unrescaled spinor therefore obeys

    i d_t Psi
      = [
          H_chi
          - (3 i / 2) psi_dot I
        ] Psi.

The apparently anti-Hermitian dilution term is exactly what preserves the
curved spatial norm

    a^3 Psi^dagger Psi.

This module is exact for spatially homogeneous psi(t). It does not yet combine
time and spatial gradients of psi in one general spin-connection operator.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable
import math
import numpy as np

try:
    from .wilson_dirac_reference import ALPHA, BETA
except ImportError:
    from wilson_dirac_reference import ALPHA, BETA


I4 = np.eye(4, dtype=complex)


def lapse(psi: float) -> float:
    return math.exp(-psi)


def scale_factor(psi: float) -> float:
    return math.exp(psi)


def spinor_rescaling(psi: float) -> float:
    return math.exp(1.5 * psi)


def rescaled_hamiltonian(
    momentum: tuple[float, float, float] | np.ndarray,
    mass: float,
    psi: float,
) -> np.ndarray:
    p = np.asarray(momentum, dtype=float)
    if p.shape != (3,):
        raise ValueError("momentum must have three components")
    if mass < 0:
        raise ValueError("mass must be non-negative")

    h = math.exp(-psi) * mass * BETA
    kinetic = math.exp(-2.0 * psi)
    for axis in range(3):
        h = h + kinetic * p[axis] * ALPHA[axis]
    return h


def unrescaled_generator(
    momentum: tuple[float, float, float] | np.ndarray,
    mass: float,
    psi: float,
    psi_dot: float,
) -> np.ndarray:
    """Return H_eff in i Psi_dot = H_eff Psi."""
    return (
        rescaled_hamiltonian(momentum, mass, psi)
        - 1.5j * psi_dot * I4
    )


def rescaled_rhs(
    chi: np.ndarray,
    momentum: tuple[float, float, float] | np.ndarray,
    mass: float,
    psi: float,
) -> np.ndarray:
    state = np.asarray(chi, dtype=complex)
    if state.shape != (4,):
        raise ValueError("chi must be a four-component spinor")
    return -1j * rescaled_hamiltonian(
        momentum,
        mass,
        psi,
    ) @ state


def unrescaled_rhs(
    spinor: np.ndarray,
    momentum: tuple[float, float, float] | np.ndarray,
    mass: float,
    psi: float,
    psi_dot: float,
) -> np.ndarray:
    state = np.asarray(spinor, dtype=complex)
    if state.shape != (4,):
        raise ValueError("spinor must be a four-component spinor")
    return -1j * unrescaled_generator(
        momentum,
        mass,
        psi,
        psi_dot,
    ) @ state


def curved_norm(spinor: np.ndarray, psi: float) -> float:
    state = np.asarray(spinor, dtype=complex)
    if state.shape != (4,):
        raise ValueError("spinor must be a four-component spinor")
    return (
        math.exp(3.0 * psi)
        * float(np.vdot(state, state).real)
    )


def flat_rescaled_norm(chi: np.ndarray) -> float:
    state = np.asarray(chi, dtype=complex)
    if state.shape != (4,):
        raise ValueError("chi must be a four-component spinor")
    return float(np.vdot(state, state).real)


def to_rescaled(spinor: np.ndarray, psi: float) -> np.ndarray:
    return spinor_rescaling(psi) * np.asarray(spinor, dtype=complex)


def from_rescaled(chi: np.ndarray, psi: float) -> np.ndarray:
    return np.asarray(chi, dtype=complex) / spinor_rescaling(psi)


def instantaneous_positive_energy(
    momentum: tuple[float, float, float] | np.ndarray,
    mass: float,
    psi: float,
) -> float:
    p = np.asarray(momentum, dtype=float)
    if p.shape != (3,):
        raise ValueError("momentum must have three components")
    return math.sqrt(
        math.exp(-4.0 * psi) * float(np.dot(p, p))
        + math.exp(-2.0 * psi) * mass**2
    )


def massless_coordinate_speed(psi: float) -> float:
    return math.exp(-2.0 * psi)


def metric_null_coordinate_speed(psi: float) -> float:
    return math.exp(-2.0 * psi)


def _rk4_vector_step(
    state: np.ndarray,
    time: float,
    dt: float,
    rhs: Callable[[float, np.ndarray], np.ndarray],
) -> np.ndarray:
    k1 = rhs(time, state)
    k2 = rhs(time + 0.5*dt, state + 0.5*dt*k1)
    k3 = rhs(time + 0.5*dt, state + 0.5*dt*k2)
    k4 = rhs(time + dt, state + dt*k3)
    return state + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)


@dataclass
class HomogeneousReciprocityDiracMode:
    momentum: tuple[float, float, float]
    mass: float
    chi: np.ndarray
    psi_function: Callable[[float], float]
    time: float = 0.0

    def __post_init__(self) -> None:
        self.chi = np.asarray(self.chi, dtype=complex).copy()
        if self.chi.shape != (4,):
            raise ValueError("chi must be a four-component spinor")
        if self.mass < 0:
            raise ValueError("mass must be non-negative")

    @property
    def norm(self) -> float:
        return flat_rescaled_norm(self.chi)

    def step(self, dt: float) -> None:
        if dt <= 0:
            raise ValueError("dt must be positive")

        def f(t, state):
            return rescaled_rhs(
                state,
                self.momentum,
                self.mass,
                self.psi_function(t),
            )

        self.chi = _rk4_vector_step(
            self.chi,
            self.time,
            dt,
            f,
        )
        self.time += dt
