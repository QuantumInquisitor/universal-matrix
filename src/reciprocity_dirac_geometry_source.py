"""Dirac backreaction source for the reciprocity geometry scalar.

For the prescribed-background Hermitian Dirac operator

    H_D[psi]
      = beta m exp(-psi)
        + 1/2 {alpha.p, exp(-2 psi)},

define the one-particle energy functional

    E_D[psi,chi]
      = Re <chi | H_D[psi] | chi>.

The geometry source is the Hamiltonian derivative

    S_psi(x)
      = - partial E_D / partial psi(x).

This module evaluates that local source with symmetric finite differences. The
finite-difference implementation is intentionally a correctness oracle for
small lattices. An optimized analytic source can be derived later.

The source is gauge/representation independent at this level because this
module uses the neutral prescribed-background Dirac operator. Coupled U(1) or
non-Abelian spinor backreaction requires replacing H_D with the corresponding
gauge-covariant curved operator.

This is a single-particle / semiclassical backreaction prototype, not a
second-quantized quantum-gravity theory.
"""

from __future__ import annotations

import numpy as np

try:
    from .reciprocity_dirac_static_background import (
        apply_static_reciprocity_dirac,
    )
except ImportError:
    from reciprocity_dirac_static_background import (
        apply_static_reciprocity_dirac,
    )


def dirac_energy(
    spinor: np.ndarray,
    psi: np.ndarray,
    mass: float,
    spacing: float = 1.0,
) -> float:
    state = np.asarray(spinor, dtype=complex)
    geometry = np.asarray(psi, dtype=float)
    h_state = apply_static_reciprocity_dirac(
        state,
        geometry,
        mass,
        spacing,
    )
    return float(np.vdot(state, h_state).real)


def local_geometry_source_reference(
    spinor: np.ndarray,
    psi: np.ndarray,
    mass: float,
    spacing: float = 1.0,
    epsilon: float = 1e-6,
) -> np.ndarray:
    """Return -d <H_D>/d psi(x) by symmetric finite differences."""
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")

    geometry = np.asarray(psi, dtype=float)
    source = np.zeros_like(geometry)

    for idx in np.ndindex(geometry.shape):
        plus = geometry.copy()
        minus = geometry.copy()
        plus[idx] += epsilon
        minus[idx] -= epsilon

        derivative = (
            dirac_energy(
                spinor,
                plus,
                mass,
                spacing,
            )
            - dirac_energy(
                spinor,
                minus,
                mass,
                spacing,
            )
        ) / (2.0*epsilon)
        source[idx] = -derivative

    return source


def uniform_geometry_source_sum(
    spinor: np.ndarray,
    psi_value: float,
    mass: float,
    spacing: float = 1.0,
    epsilon: float = 1e-6,
) -> float:
    """Derivative under a uniform psi displacement."""
    state = np.asarray(spinor, dtype=complex)
    shape = state.shape[:3]
    plus = np.full(shape, psi_value + epsilon)
    minus = np.full(shape, psi_value - epsilon)

    derivative = (
        dirac_energy(state, plus, mass, spacing)
        - dirac_energy(state, minus, mass, spacing)
    ) / (2.0*epsilon)
    return -derivative


def source_sum_residual(
    spinor: np.ndarray,
    psi: np.ndarray,
    mass: float,
    spacing: float = 1.0,
    epsilon: float = 1e-6,
) -> float:
    local = local_geometry_source_reference(
        spinor,
        psi,
        mass,
        spacing,
        epsilon,
    )

    # A uniform shift changes all psi sites together. Its derivative must equal
    # the sum of local partial derivatives.
    geometry = np.asarray(psi, dtype=float)
    plus = geometry + epsilon
    minus = geometry - epsilon
    uniform_source = -(
        dirac_energy(spinor, plus, mass, spacing)
        - dirac_energy(spinor, minus, mass, spacing)
    ) / (2.0*epsilon)

    return float(np.sum(local) - uniform_source)


def rest_mode_source_energy(
    amplitude: complex,
    mass: float,
    psi: float = 0.0,
) -> tuple[float, float]:
    """Uniform zero-momentum positive beta eigenstate diagnostic.

    For a rest spinor with beta eigenvalue +1:
        E = m exp(-psi) |A|^2
    and
        S = -dE/dpsi = E.

    Returns (source, energy).
    """
    if mass < 0:
        raise ValueError("mass must be non-negative")
    density = abs(amplitude)**2
    energy = mass*np.exp(-psi)*density
    return energy, energy
