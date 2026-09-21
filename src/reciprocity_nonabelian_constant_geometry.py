"""Constant reciprocity-background coupling for SU(2)/SU(3) Hamiltonians.

For classical Yang-Mills theory on a uniform reciprocity background

    ds^2 = -exp(-2 psi) dt^2 + exp(2 psi) d x^2,

the Hamiltonian density is

    H_YM(psi)
      = exp(-2 psi) H_YM(0)

when the canonical electric displacement is used.

Therefore the full lattice Hamiltonian scales by

    w(psi) = exp(-2 psi).

Hamilton equations become

    U_dot = w * (flat U_dot)
    E_dot = w * (flat E_dot).

A geometry-background step of duration dt is therefore exactly equivalent to a
flat-background Hamiltonian step of duration

    dt_eff = w dt

for constant psi.

The geometry source obtained from the Hamiltonian dependence is

    -dH/dpsi = 2 H,

matching the continuum active Yang-Mills source rho + sum_i p_i = 2 rho for a
free traceless gauge field.

This module supports both the optimized SU(2) and SU(3) Hamiltonian engines.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

try:
    from .su2_hamiltonian import (
        SU2Hamiltonian,
        analytic_wilson_force as su2_force,
        drift_links as su2_drift,
        total_energy as su2_flat_energy,
    )
    from .su3_hamiltonian import (
        SU3Hamiltonian,
        analytic_wilson_force as su3_force,
        drift_links as su3_drift,
        total_energy as su3_flat_energy,
    )
except ImportError:
    from su2_hamiltonian import (
        SU2Hamiltonian,
        analytic_wilson_force as su2_force,
        drift_links as su2_drift,
        total_energy as su2_flat_energy,
    )
    from su3_hamiltonian import (
        SU3Hamiltonian,
        analytic_wilson_force as su3_force,
        drift_links as su3_drift,
        total_energy as su3_flat_energy,
    )


def geometry_weight(psi: float) -> float:
    return math.exp(-2.0*psi)


def metric_null_coordinate_speed(psi: float) -> float:
    return math.exp(-2.0*psi)


def yang_mills_characteristic_speed(psi: float) -> float:
    return geometry_weight(psi)


def geometry_scaled_energy(
    flat_energy: float,
    psi: float,
) -> float:
    return geometry_weight(psi)*flat_energy


def geometry_active_source_from_energy(
    geometry_energy: float,
) -> float:
    """-dH/dpsi for H=e^-2psi H0."""
    return 2.0*geometry_energy


@dataclass
class SU2ReciprocityBackground:
    links: np.ndarray
    electric: np.ndarray
    beta: float = 1.0
    psi: float = 0.0
    time: float = 0.0

    @property
    def energy(self) -> float:
        return geometry_scaled_energy(
            su2_flat_energy(
                self.links,
                self.electric,
                self.beta,
            ),
            self.psi,
        )

    @property
    def active_source(self) -> float:
        return geometry_active_source_from_energy(
            self.energy
        )

    def step(self, dt: float) -> None:
        if dt <= 0:
            raise ValueError("dt must be positive")
        w = geometry_weight(self.psi)

        force = su2_force(
            self.links,
            self.beta,
        )
        self.electric += 0.5*dt*w*force

        self.links = su2_drift(
            self.links,
            self.electric,
            dt*w,
        )

        force = su2_force(
            self.links,
            self.beta,
        )
        self.electric += 0.5*dt*w*force
        self.time += dt


@dataclass
class SU3ReciprocityBackground:
    links: np.ndarray
    electric: np.ndarray
    beta: float = 1.0
    psi: float = 0.0
    time: float = 0.0

    @property
    def energy(self) -> float:
        return geometry_scaled_energy(
            su3_flat_energy(
                self.links,
                self.electric,
                self.beta,
            ),
            self.psi,
        )

    @property
    def active_source(self) -> float:
        return geometry_active_source_from_energy(
            self.energy
        )

    def step(self, dt: float) -> None:
        if dt <= 0:
            raise ValueError("dt must be positive")
        w = geometry_weight(self.psi)

        force = su3_force(
            self.links,
            self.beta,
        )
        self.electric += 0.5*dt*w*force

        self.links = su3_drift(
            self.links,
            self.electric,
            dt*w,
        )

        force = su3_force(
            self.links,
            self.beta,
        )
        self.electric += 0.5*dt*w*force
        self.time += dt
