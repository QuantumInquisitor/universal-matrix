"""Semiclassical Dirac + reciprocity-geometry backreaction dynamics.

This module closes the prescribed-background loop at the one-particle /
semiclassical level.

State:
    chi(x)       rescaled four-component Dirac spinor
    psi(x)       reciprocity geometry scalar
    P_psi(x)     canonical momentum conjugate to psi

Hamiltonian:
    H_total
      = H_geometry[psi,P_psi]
        + Re <chi | H_D[psi] | chi>

with
    H_geometry
      = sum_x [
          (kappa/2) exp(-4 psi) P_psi^2
          + |grad psi|^2/(2 kappa)
        ]

and
    H_D[psi]
      = beta m exp(-psi)
        + 1/2 {alpha.p, exp(-2 psi)}.

Equations:
    i d_t chi = H_D[psi] chi

    d_t psi
      = kappa exp(-4 psi) P_psi

    d_t P_psi
      = laplacian(psi)/kappa
        + 2 kappa exp(-4 psi) P_psi^2
        + S_D,

where
    S_D(x)
      = - partial <H_D>/partial psi(x)

is the analytic source implemented in reciprocity_dirac_geometry_source.py.

Because the same Hamiltonian generates both directions of coupling, this is an
Ehrenfest-type Hamiltonian backreaction model. It is not second-quantized QFT
and not quantum gravity.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

try:
    from .reciprocity_dirac_spacetime_background import (
        apply_hamiltonian,
        flat_norm,
    )
    from .reciprocity_dirac_geometry_source import (
        analytic_geometry_source,
        dirac_energy,
    )
    from .self_consistent_reciprocity_action import (
        periodic_laplacian,
        gradient_energy,
    )
except ImportError:
    from reciprocity_dirac_spacetime_background import (
        apply_hamiltonian,
        flat_norm,
    )
    from reciprocity_dirac_geometry_source import (
        analytic_geometry_source,
        dirac_energy,
    )
    from self_consistent_reciprocity_action import (
        periodic_laplacian,
        gradient_energy,
    )


def geometry_energy(
    psi: np.ndarray,
    psi_momentum: np.ndarray,
    kappa: float,
) -> float:
    if kappa <= 0:
        raise ValueError("kappa must be positive")

    g = np.asarray(psi, dtype=float)
    pg = np.asarray(psi_momentum, dtype=float)
    if g.shape != pg.shape or g.ndim != 3:
        raise ValueError("geometry fields must be matching 3D arrays")

    kinetic = 0.5 * kappa * float(
        np.sum(np.exp(-4.0 * g) * pg**2)
    )
    gradient = gradient_energy(g) / (2.0 * kappa)
    return kinetic + gradient


def total_energy(
    chi: np.ndarray,
    psi: np.ndarray,
    psi_momentum: np.ndarray,
    mass: float,
    kappa: float,
    spacing: float = 1.0,
) -> float:
    return (
        geometry_energy(
            psi,
            psi_momentum,
            kappa,
        )
        + dirac_energy(
            chi,
            psi,
            mass,
            spacing,
        )
    )


def rhs(
    chi: np.ndarray,
    psi: np.ndarray,
    psi_momentum: np.ndarray,
    mass: float,
    kappa: float,
    spacing: float = 1.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if kappa <= 0:
        raise ValueError("kappa must be positive")
    if mass < 0:
        raise ValueError("mass must be non-negative")
    if spacing <= 0:
        raise ValueError("spacing must be positive")

    state = np.asarray(chi, dtype=complex)
    g = np.asarray(psi, dtype=float)
    pg = np.asarray(psi_momentum, dtype=float)

    if state.ndim != 4 or state.shape[-1] != 4:
        raise ValueError("chi must have shape (nx,ny,nz,4)")
    if g.shape != state.shape[:3] or pg.shape != g.shape:
        raise ValueError("geometry shape mismatch")

    chi_dot = -1j * apply_hamiltonian(
        state,
        g,
        mass,
        spacing,
    )

    psi_dot = (
        kappa
        * np.exp(-4.0 * g)
        * pg
    )

    source = analytic_geometry_source(
        state,
        g,
        mass,
        spacing,
    )

    psi_momentum_dot = (
        periodic_laplacian(g) / kappa
        + 2.0
        * kappa
        * np.exp(-4.0 * g)
        * pg**2
        + source
    )

    return chi_dot, psi_dot, psi_momentum_dot


@dataclass
class DiracReciprocityBackreaction:
    chi: np.ndarray
    psi: np.ndarray
    psi_momentum: np.ndarray
    mass: float
    kappa: float = 1.0
    spacing: float = 1.0
    time: float = 0.0

    def __post_init__(self) -> None:
        self.chi = np.asarray(
            self.chi,
            dtype=complex,
        ).copy()
        self.psi = np.asarray(
            self.psi,
            dtype=float,
        ).copy()
        self.psi_momentum = np.asarray(
            self.psi_momentum,
            dtype=float,
        ).copy()

        if self.chi.ndim != 4 or self.chi.shape[-1] != 4:
            raise ValueError("chi must have shape (nx,ny,nz,4)")
        if self.psi.shape != self.chi.shape[:3]:
            raise ValueError("psi shape mismatch")
        if self.psi_momentum.shape != self.psi.shape:
            raise ValueError("psi_momentum shape mismatch")
        if self.mass < 0:
            raise ValueError("mass must be non-negative")
        if self.kappa <= 0:
            raise ValueError("kappa must be positive")
        if self.spacing <= 0:
            raise ValueError("spacing must be positive")

    @property
    def norm(self) -> float:
        return flat_norm(self.chi)

    @property
    def energy(self) -> float:
        return total_energy(
            self.chi,
            self.psi,
            self.psi_momentum,
            self.mass,
            self.kappa,
            self.spacing,
        )

    def _add_state(
        self,
        base,
        deriv,
        scale: float,
    ):
        return tuple(
            b + scale * d
            for b, d in zip(base, deriv)
        )

    def step_rk4(self, dt: float) -> None:
        """Advance the coupled semiclassical system with fourth-order RK."""
        if dt <= 0:
            raise ValueError("dt must be positive")

        y0 = (
            self.chi,
            self.psi,
            self.psi_momentum,
        )

        def f(state):
            return rhs(
                *state,
                self.mass,
                self.kappa,
                self.spacing,
            )

        k1 = f(y0)
        k2 = f(self._add_state(y0, k1, 0.5 * dt))
        k3 = f(self._add_state(y0, k2, 0.5 * dt))
        k4 = f(self._add_state(y0, k3, dt))

        updated = []
        for base, d1, d2, d3, d4 in zip(
            y0,
            k1,
            k2,
            k3,
            k4,
        ):
            updated.append(
                base
                + (dt / 6.0)
                * (d1 + 2.0 * d2 + 2.0 * d3 + d4)
            )

        self.chi, self.psi, self.psi_momentum = updated
        self.time += dt

    def snapshot(self) -> dict[str, float | str]:
        return {
            "time": self.time,
            "energy": self.energy,
            "spinor_norm": self.norm,
            "max_abs_psi": float(
                np.max(np.abs(self.psi))
            ),
            "model_status": (
                "experimental_semiclassical_dirac_geometry_backreaction"
            ),
        }
