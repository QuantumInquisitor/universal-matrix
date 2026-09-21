"""Reference dynamics for reciprocity geometry backreacting with SU(2).

Combined Hamiltonian:

    H =
      H_psi
      + H_SU2[psi]

with geometry scalar sector

    H_psi
      = sum_x [
          (kappa/2) exp(-4 psi) P_psi^2
          + |grad psi|^2/(2 kappa)
        ]

and spatially weighted SU(2) sector

    H_SU2
      = 1/2 sum_links w_l E_l^a E_l^a
        + beta sum_p w_p [
            1 - 1/2 ReTr U_p
          ].

Weights are defined by
reciprocity_nonabelian_spatial_geometry.py.

Hamilton equations:

    psi_dot
      = kappa exp(-4 psi) P_psi

    P_psi_dot
      = laplacian(psi)/kappa
        + 2 kappa exp(-4 psi) P_psi^2
        + S_SU2(x)

where
    S_SU2(x) = -dH_SU2/dpsi(x).

For the gauge coordinates, the left-electric drift is

    U_dot
      = i w_l E U.

The electric force is
    E_dot = -dH_mag/dq

under exact left group variation U -> exp(i q^a T_a) U.

The reference force is evaluated by symmetric group finite differences. This
is intentionally slow and intended as a correctness oracle for a future
analytic weighted-staple force.

Integration uses RK4 on psi/P_psi and a symmetric kick-drift-kick update for
the group sector inside a Strang-like composition. The tests focus on the
Hamiltonian derivatives and small-step energy behavior rather than claiming a
globally high-order geometric integrator.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

try:
    from .reciprocity_nonabelian_spatial_geometry import (
        link_weight,
        local_geometry_source,
        weighted_su2_energy,
    )
    from .su2_hamiltonian_reference import (
        su2_exp,
    )
except ImportError:
    from reciprocity_nonabelian_spatial_geometry import (
        link_weight,
        local_geometry_source,
        weighted_su2_energy,
    )
    from su2_hamiltonian_reference import su2_exp


AXES = (0, 1, 2)


def periodic_laplacian(field: np.ndarray) -> np.ndarray:
    a = np.asarray(field, dtype=float)
    out = np.zeros_like(a)
    for axis in AXES:
        out += (
            np.roll(a, -1, axis=axis)
            + np.roll(a, 1, axis=axis)
            - 2.0*a
        )
    return out


def geometry_gradient_energy(
    psi: np.ndarray,
    kappa: float,
) -> float:
    if kappa <= 0:
        raise ValueError("kappa must be positive")
    total = 0.0
    p = np.asarray(psi, dtype=float)
    for axis in AXES:
        d = np.roll(p, -1, axis=axis) - p
        total += float(np.sum(d*d))
    return total/(2.0*kappa)


def geometry_kinetic_energy(
    psi: np.ndarray,
    momentum: np.ndarray,
    kappa: float,
) -> float:
    if kappa <= 0:
        raise ValueError("kappa must be positive")
    return 0.5*kappa*float(
        np.sum(
            np.exp(-4.0*np.asarray(psi, dtype=float))
            * np.asarray(momentum, dtype=float)**2
        )
    )


def total_energy(
    psi: np.ndarray,
    psi_momentum: np.ndarray,
    links: np.ndarray,
    electric: np.ndarray,
    kappa: float,
    beta: float,
) -> float:
    return (
        geometry_kinetic_energy(
            psi,
            psi_momentum,
            kappa,
        )
        + geometry_gradient_energy(
            psi,
            kappa,
        )
        + weighted_su2_energy(
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
) -> tuple[np.ndarray,np.ndarray]:
    p = np.asarray(psi, dtype=float)
    mom = np.asarray(psi_momentum, dtype=float)

    psi_dot = (
        kappa
        * np.exp(-4.0*p)
        * mom
    )

    source = local_geometry_source(
        links,
        electric,
        p,
        beta,
        group_dimension=2,
    )

    momentum_dot = (
        periodic_laplacian(p)/kappa
        + 2.0*kappa
        * np.exp(-4.0*p)
        * mom**2
        + source
    )

    return psi_dot,momentum_dot


def weighted_magnetic_energy(
    links: np.ndarray,
    psi: np.ndarray,
    beta: float,
) -> float:
    shape = np.asarray(psi).shape
    zero_electric = np.zeros(
        (3,) + shape + (3,),
        dtype=float,
    )
    return weighted_su2_energy(
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
    """Return -dH_mag/dq_a under left SU(2) variation."""
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")

    shape = np.asarray(psi).shape
    force = np.zeros(
        (3,) + shape + (3,),
        dtype=float,
    )

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
                )/(2.0*epsilon)

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
    out = np.empty_like(links)

    for axis in AXES:
        weight = link_weight(psi, axis)
        for idx in np.ndindex(shape):
            out[(axis,) + idx] = (
                su2_exp(
                    dt
                    * weight[idx]
                    * electric[(axis,) + idx]
                )
                @ links[(axis,) + idx]
            )

    return out


@dataclass
class SU2DynamicReciprocityReference:
    psi: np.ndarray
    psi_momentum: np.ndarray
    links: np.ndarray
    electric: np.ndarray
    kappa: float = 1.0
    beta: float = 1.0
    force_epsilon: float = 1e-6
    time: float = 0.0

    def __post_init__(self) -> None:
        self.psi = np.asarray(
            self.psi,
            dtype=float,
        ).copy()
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
        if self.links.shape != (3,) + shape + (2,2):
            raise ValueError("links shape mismatch")
        if self.electric.shape != (3,) + shape + (3,):
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
        """Symmetric reference step with midpoint-like geometry updates."""
        if dt <= 0:
            raise ValueError("dt must be positive")

        # Half update geometry momenta.
        _, p_dot = geometry_rhs(
            self.psi,
            self.psi_momentum,
            self.links,
            self.electric,
            self.kappa,
            self.beta,
        )
        self.psi_momentum += 0.5*dt*p_dot

        # Half update electric momenta.
        force = weighted_group_force_reference(
            self.links,
            self.psi,
            self.beta,
            self.force_epsilon,
        )
        self.electric += 0.5*dt*force

        # Drift scalar coordinate.
        psi_dot = (
            self.kappa
            * np.exp(-4.0*self.psi)
            * self.psi_momentum
        )
        self.psi += dt*psi_dot

        # Drift group coordinate with geometry-weighted kinetic coefficient.
        self.links = drift_links_weighted(
            self.links,
            self.electric,
            self.psi,
            dt,
        )

        # Second electric half kick.
        force = weighted_group_force_reference(
            self.links,
            self.psi,
            self.beta,
            self.force_epsilon,
        )
        self.electric += 0.5*dt*force

        # Second geometry half kick.
        _, p_dot = geometry_rhs(
            self.psi,
            self.psi_momentum,
            self.links,
            self.electric,
            self.kappa,
            self.beta,
        )
        self.psi_momentum += 0.5*dt*p_dot

        self.time += dt
