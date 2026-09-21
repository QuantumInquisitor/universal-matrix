"""Time- and space-dependent Dirac evolution on prescribed reciprocity geometry.

Metric:
    ds^2 = -exp(-2 psi(t,x)) dt^2
           + exp(2 psi(t,x)) d x^2.

Use the locally volume-rescaled spinor
    chi(t,x) = exp(3 psi(t,x)/2) Psi(t,x).

For the diagonal isotropic zero-shift tetrad, the rescaled coordinate-time
Hamiltonian is the instantaneous Hermitian operator

    H(t)
      = beta m exp(-psi)
        + 1/2 { alpha.p, exp(-2 psi) }.

The anticommutator contains the spatial spin-connection/geometry-gradient term.
The local exp(3 psi/2) rescaling removes the temporal volume-dilution term from
the chi equation.

Thus
    i d_t chi = H(t) chi

with ordinary flat lattice inner product.

The original unrescaled spinor is reconstructed as
    Psi = exp(-3 psi/2) chi

and its curved norm
    int exp(3 psi) Psi^dagger Psi d^3x
equals the flat chi norm.

This module evolves a prescribed external psi(t,x). It does not yet feed the
spinor stress-energy back into psi.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable
import numpy as np

try:
    from .reciprocity_dirac_static_background import (
        apply_static_reciprocity_dirac,
        inner_product,
    )
except ImportError:
    from reciprocity_dirac_static_background import (
        apply_static_reciprocity_dirac,
        inner_product,
    )


GeometryFunction = Callable[[float], np.ndarray]


def to_rescaled(
    spinor: np.ndarray,
    psi: np.ndarray,
) -> np.ndarray:
    field = np.asarray(spinor, dtype=complex)
    geometry = np.asarray(psi, dtype=float)
    if field.shape[:3] != geometry.shape or field.shape[-1] != 4:
        raise ValueError("spinor/geometry shape mismatch")
    return np.exp(1.5 * geometry)[..., None] * field


def from_rescaled(
    chi: np.ndarray,
    psi: np.ndarray,
) -> np.ndarray:
    field = np.asarray(chi, dtype=complex)
    geometry = np.asarray(psi, dtype=float)
    if field.shape[:3] != geometry.shape or field.shape[-1] != 4:
        raise ValueError("chi/geometry shape mismatch")
    return np.exp(-1.5 * geometry)[..., None] * field


def curved_norm(
    spinor: np.ndarray,
    psi: np.ndarray,
) -> float:
    field = np.asarray(spinor, dtype=complex)
    geometry = np.asarray(psi, dtype=float)
    if field.shape[:3] != geometry.shape or field.shape[-1] != 4:
        raise ValueError("spinor/geometry shape mismatch")
    density = (
        np.exp(3.0 * geometry)
        * np.sum(np.abs(field) ** 2, axis=-1)
    )
    return float(np.sum(density))


def flat_norm(chi: np.ndarray) -> float:
    field = np.asarray(chi, dtype=complex)
    if field.ndim != 4 or field.shape[-1] != 4:
        raise ValueError("chi must have shape (nx,ny,nz,4)")
    return float(np.vdot(field, field).real)


def apply_hamiltonian(
    chi: np.ndarray,
    psi: np.ndarray,
    mass: float,
    spacing: float = 1.0,
) -> np.ndarray:
    return apply_static_reciprocity_dirac(
        chi,
        psi,
        mass,
        spacing,
    )


def rhs(
    chi: np.ndarray,
    psi: np.ndarray,
    mass: float,
    spacing: float = 1.0,
) -> np.ndarray:
    return -1j * apply_hamiltonian(
        chi,
        psi,
        mass,
        spacing,
    )


def hermiticity_residual(
    a: np.ndarray,
    b: np.ndarray,
    psi: np.ndarray,
    mass: float,
    spacing: float = 1.0,
) -> complex:
    ha = apply_hamiltonian(a, psi, mass, spacing)
    hb = apply_hamiltonian(b, psi, mass, spacing)
    return inner_product(a, hb) - inner_product(ha, b)


def _rk4_step(
    state: np.ndarray,
    time: float,
    dt: float,
    geometry_function: GeometryFunction,
    mass: float,
    spacing: float,
) -> np.ndarray:
    def f(t, y):
        return rhs(
            y,
            geometry_function(t),
            mass,
            spacing,
        )

    k1 = f(time, state)
    k2 = f(time + 0.5*dt, state + 0.5*dt*k1)
    k3 = f(time + 0.5*dt, state + 0.5*dt*k2)
    k4 = f(time + dt, state + dt*k3)
    return state + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)


@dataclass
class SpacetimeReciprocityDirac:
    chi: np.ndarray
    geometry_function: GeometryFunction
    mass: float
    spacing: float = 1.0
    time: float = 0.0

    def __post_init__(self) -> None:
        self.chi = np.asarray(self.chi, dtype=complex).copy()
        if self.chi.ndim != 4 or self.chi.shape[-1] != 4:
            raise ValueError("chi must have shape (nx,ny,nz,4)")
        if self.mass < 0:
            raise ValueError("mass must be non-negative")
        if self.spacing <= 0:
            raise ValueError("spacing must be positive")

        geometry = np.asarray(
            self.geometry_function(self.time),
            dtype=float,
        )
        if geometry.shape != self.chi.shape[:3]:
            raise ValueError("geometry shape mismatch")

    @property
    def norm(self) -> float:
        return flat_norm(self.chi)

    @property
    def unrescaled_spinor(self) -> np.ndarray:
        return from_rescaled(
            self.chi,
            self.geometry_function(self.time),
        )

    @property
    def curved_norm(self) -> float:
        return curved_norm(
            self.unrescaled_spinor,
            self.geometry_function(self.time),
        )

    def step(self, dt: float) -> None:
        if dt <= 0:
            raise ValueError("dt must be positive")
        self.chi = _rk4_step(
            self.chi,
            self.time,
            dt,
            self.geometry_function,
            self.mass,
            self.spacing,
        )
        self.time += dt
