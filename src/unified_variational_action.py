"""Unified experimental variational energy for scalar content, U(1) gauge, and matter.

This module is the first common action/energy layer tying together:
- a neutral scalar content field chi;
- a classical complex matter amplitude Phi;
- compact U(1) link phases A_i.

It is deliberately classical. Phi is not declared to be a quantum wavefunction.

For a periodic cubic lattice, define the static energy

    E = E_chi + E_matter + E_gauge + E_coupling

with

    E_chi
      = sum_x [ |grad chi|^2 / (2*kappa_chi) ]

    E_matter
      = sum_x [ sum_i |D_i Phi|^2
                + m2 |Phi|^2
                + lambda4 |Phi|^4
                + lambda6 |Phi|^6 ]

    E_coupling
      = -g_chi sum_x chi |Phi|^2

    E_gauge
      = beta sum_plaquettes [1 - cos(F_ij)].

Gauge-covariant forward difference:

    D_i Phi(x)
      = exp(i A_i(x)) Phi(x+i) - Phi(x).

Local gauge transformation:

    Phi(x) -> exp(i alpha(x)) Phi(x)
    A_i(x) -> A_i(x) + alpha(x) - alpha(x+i)

leaves the full energy invariant.

Variation with respect to chi gives the discrete scalar source equation

    -(1/kappa_chi) laplacian(chi) - g_chi |Phi|^2 = 0

for the sign convention used here.

This is an experimental variational model, not an established fundamental
action and not a quantum field theory.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np


AXES = (0, 1, 2)


def _roll(a: np.ndarray, axis: int, step: int) -> np.ndarray:
    return np.roll(a, shift=-step, axis=axis)


def _validate_shape(phi: np.ndarray, chi: np.ndarray, links: np.ndarray) -> tuple[int, int, int]:
    if phi.ndim != 3 or chi.ndim != 3:
        raise ValueError("phi and chi must be 3D")
    if phi.shape != chi.shape:
        raise ValueError("phi and chi shapes must match")
    if links.shape != (3,) + phi.shape:
        raise ValueError("links must have shape (3, nx, ny, nz)")
    return phi.shape


def matter_density(phi: np.ndarray) -> np.ndarray:
    phi = np.asarray(phi, dtype=complex)
    return np.abs(phi) ** 2


def covariant_forward_difference(
    phi: np.ndarray,
    links: np.ndarray,
    axis: int,
) -> np.ndarray:
    phi = np.asarray(phi, dtype=complex)
    links = np.asarray(links, dtype=float)
    if axis not in AXES:
        raise ValueError("axis must be 0, 1, or 2")
    return np.exp(1j * links[axis]) * _roll(phi, axis, 1) - phi


def plaquette_angle(
    links: np.ndarray,
    axis_i: int,
    axis_j: int,
) -> np.ndarray:
    """Unwrapped oriented lattice curl F_ij."""
    if axis_i == axis_j or axis_i not in AXES or axis_j not in AXES:
        raise ValueError("axes must be distinct members of {0,1,2}")
    ai = links[axis_i]
    aj = links[axis_j]
    return (
        ai
        + _roll(aj, axis_i, 1)
        - _roll(ai, axis_j, 1)
        - aj
    )


def gauge_transform(
    phi: np.ndarray,
    links: np.ndarray,
    alpha: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    phi = np.asarray(phi, dtype=complex)
    links = np.asarray(links, dtype=float)
    alpha = np.asarray(alpha, dtype=float)
    if alpha.shape != phi.shape:
        raise ValueError("alpha shape must match phi")
    if links.shape != (3,) + phi.shape:
        raise ValueError("links shape mismatch")

    transformed_phi = np.exp(1j * alpha) * phi
    transformed_links = np.empty_like(links)
    for axis in AXES:
        transformed_links[axis] = (
            links[axis]
            + alpha
            - _roll(alpha, axis, 1)
        )
    return transformed_phi, transformed_links


def scalar_gradient_energy(chi: np.ndarray, kappa_chi: float) -> float:
    if kappa_chi <= 0:
        raise ValueError("kappa_chi must be positive")
    chi = np.asarray(chi, dtype=float)
    total = 0.0
    for axis in AXES:
        d = _roll(chi, axis, 1) - chi
        total += float(np.sum(d * d))
    return total / (2.0 * kappa_chi)


def matter_gradient_energy(phi: np.ndarray, links: np.ndarray) -> float:
    total = 0.0
    for axis in AXES:
        d = covariant_forward_difference(phi, links, axis)
        total += float(np.sum(np.abs(d) ** 2))
    return total


def matter_potential_energy(
    phi: np.ndarray,
    mass2: float,
    lambda4: float,
    lambda6: float,
) -> float:
    rho = matter_density(phi)
    return float(
        np.sum(
            mass2 * rho
            + lambda4 * rho**2
            + lambda6 * rho**3
        )
    )


def scalar_matter_coupling_energy(
    phi: np.ndarray,
    chi: np.ndarray,
    g_chi: float,
) -> float:
    if g_chi < 0:
        raise ValueError("g_chi must be non-negative")
    return -g_chi * float(np.sum(np.asarray(chi, dtype=float) * matter_density(phi)))


def gauge_wilson_energy(links: np.ndarray, beta: float) -> float:
    if beta < 0:
        raise ValueError("beta must be non-negative")
    total = 0.0
    for i, j in ((0, 1), (1, 2), (2, 0)):
        f = plaquette_angle(links, i, j)
        total += float(np.sum(1.0 - np.cos(f)))
    return beta * total


@dataclass(frozen=True)
class UnifiedActionParameters:
    kappa_chi: float = 1.0
    g_chi: float = 0.1
    beta: float = 1.0
    mass2: float = 1.0
    lambda4: float = 0.0
    lambda6: float = 0.0

    def __post_init__(self) -> None:
        if self.kappa_chi <= 0:
            raise ValueError("kappa_chi must be positive")
        if self.g_chi < 0 or self.beta < 0:
            raise ValueError("g_chi and beta must be non-negative")
        if self.lambda6 < 0:
            raise ValueError("lambda6 must be non-negative for bounded large-field energy")


def total_static_energy(
    phi: np.ndarray,
    chi: np.ndarray,
    links: np.ndarray,
    params: UnifiedActionParameters,
) -> dict[str, float]:
    phi = np.asarray(phi, dtype=complex)
    chi = np.asarray(chi, dtype=float)
    links = np.asarray(links, dtype=float)
    _validate_shape(phi, chi, links)

    e_chi = scalar_gradient_energy(chi, params.kappa_chi)
    e_grad = matter_gradient_energy(phi, links)
    e_pot = matter_potential_energy(
        phi,
        params.mass2,
        params.lambda4,
        params.lambda6,
    )
    e_coupling = scalar_matter_coupling_energy(phi, chi, params.g_chi)
    e_gauge = gauge_wilson_energy(links, params.beta)

    total = e_chi + e_grad + e_pot + e_coupling + e_gauge
    return {
        "total": total,
        "scalar_gradient": e_chi,
        "matter_gradient": e_grad,
        "matter_potential": e_pot,
        "scalar_matter_coupling": e_coupling,
        "gauge_wilson": e_gauge,
        "model_status": "experimental_classical_unified_variational_energy",
    }


def chi_euler_lagrange_residual(
    phi: np.ndarray,
    chi: np.ndarray,
    params: UnifiedActionParameters,
) -> np.ndarray:
    """Derivative of the static energy with respect to chi."""
    phi = np.asarray(phi, dtype=complex)
    chi = np.asarray(chi, dtype=float)
    lap = np.zeros_like(chi)
    for axis in AXES:
        lap += _roll(chi, axis, 1) + _roll(chi, axis, -1) - 2.0 * chi

    return (
        -(1.0 / params.kappa_chi) * lap
        - params.g_chi * matter_density(phi)
    )


def global_u1_charge(phi: np.ndarray) -> float:
    """Classical amplitude norm, conserved only in a dynamical U(1) theory."""
    return float(np.sum(matter_density(phi)))
