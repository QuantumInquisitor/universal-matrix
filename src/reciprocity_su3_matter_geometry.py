"""Fully coupled SU(3) scalar matter + Yang-Mills + reciprocity geometry.

Fields:
    Psi(x)       in C^3
    Pi(x)        in C^3
    psi(x)       real reciprocity geometry scalar
    P_psi(x)     canonical geometry momentum
    U_i(x)       in SU(3)
    E_i^a(x)     eight-component left electric field

Hamiltonian:

    H = H_geometry + H_matter[psi] + H_SU3[psi]

Geometry:
    H_geometry =
      sum_x [
        (kappa/2) exp(-4 psi) P_psi^2
        + |grad psi|^2/(2 kappa)
      ].

Matter:
    H_matter =
      sum_x [
        exp(-4 psi) |Pi|^2
        + exp(2 psi) V(Psi^dagger Psi)
      ]
      + sum_links |U_i Psi(x+i)-Psi(x)|^2.

The spatial hopping term is unweighted for the reciprocity metric because
sqrt(-g) g^ij = delta^ij.

Gauge:
    H_SU3 =
      1/2 sum_links w_l E_l^a E_l^a
      + beta sum_p w_p [1 - (1/3) ReTr U_p].

The geometry source is exactly

    S_psi =
      -d(H_matter + H_SU3)/d psi

with matter contribution
    4 exp(-4 psi)|Pi|^2
    - 2 exp(2 psi)V

and gauge contribution supplied by the weighted Yang-Mills source.

This is a classical lattice Hamiltonian prototype, not QCD or established
gravity.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

try:
    from .reciprocity_dynamic_su2_geometry import (
        periodic_laplacian,
        geometry_gradient_energy,
        geometry_kinetic_energy,
    )
    from .reciprocity_dynamic_su3_geometry import (
        analytic_weighted_force,
        drift_links_weighted,
    )
    from .reciprocity_nonabelian_spatial_geometry import (
        local_geometry_source,
        weighted_su3_energy,
    )
    from .su3_matter_gauge_dynamics import (
        SU3ScalarMatterParameters,
        coupled_gauss_components,
        gauge_transform_state,
        matter_density,
        matter_hopping_energy,
        matter_link_current,
        covariant_laplacian,
    )
except ImportError:
    from reciprocity_dynamic_su2_geometry import (
        periodic_laplacian,
        geometry_gradient_energy,
        geometry_kinetic_energy,
    )
    from reciprocity_dynamic_su3_geometry import (
        analytic_weighted_force,
        drift_links_weighted,
    )
    from reciprocity_nonabelian_spatial_geometry import (
        local_geometry_source,
        weighted_su3_energy,
    )
    from su3_matter_gauge_dynamics import (
        SU3ScalarMatterParameters,
        coupled_gauss_components,
        gauge_transform_state,
        matter_density,
        matter_hopping_energy,
        matter_link_current,
        covariant_laplacian,
    )


def matter_potential_density(
    matter: np.ndarray,
    params: SU3ScalarMatterParameters,
) -> np.ndarray:
    rho = matter_density(matter)
    return params.mass2 * rho + params.lambda4 * rho**2


def matter_energy(
    matter: np.ndarray,
    momentum: np.ndarray,
    links: np.ndarray,
    geometry: np.ndarray,
    params: SU3ScalarMatterParameters,
) -> float:
    g = np.asarray(geometry, dtype=float)
    pi = np.asarray(momentum, dtype=complex)
    return (
        float(np.sum(np.exp(-4.0*g)[..., None] * np.abs(pi)**2))
        + matter_hopping_energy(matter, links)
        + float(
            np.sum(
                np.exp(2.0*g)
                * matter_potential_density(matter, params)
            )
        )
    )


def matter_geometry_source(
    matter: np.ndarray,
    momentum: np.ndarray,
    geometry: np.ndarray,
    params: SU3ScalarMatterParameters,
) -> np.ndarray:
    g = np.asarray(geometry, dtype=float)
    pi2 = np.sum(np.abs(np.asarray(momentum, dtype=complex))**2, axis=-1)
    return (
        4.0 * np.exp(-4.0*g) * pi2
        - 2.0 * np.exp(2.0*g)
        * matter_potential_density(matter, params)
    )


def matter_coordinate_velocity(
    momentum: np.ndarray,
    geometry: np.ndarray,
) -> np.ndarray:
    return (
        np.exp(-4.0*np.asarray(geometry, dtype=float))[..., None]
        * np.asarray(momentum, dtype=complex)
    )


def matter_momentum_force(
    matter: np.ndarray,
    links: np.ndarray,
    geometry: np.ndarray,
    params: SU3ScalarMatterParameters,
) -> np.ndarray:
    rho = matter_density(matter)
    potential_derivative = (
        params.mass2 + 2.0*params.lambda4*rho
    )
    return (
        covariant_laplacian(matter, links)
        - (
            np.exp(2.0*np.asarray(geometry, dtype=float))
            * potential_derivative
        )[..., None]
        * matter
    )


def geometry_rhs(
    geometry: np.ndarray,
    geometry_momentum: np.ndarray,
    matter: np.ndarray,
    matter_momentum: np.ndarray,
    links: np.ndarray,
    electric: np.ndarray,
    kappa: float,
    beta: float,
    matter_params: SU3ScalarMatterParameters,
) -> tuple[np.ndarray, np.ndarray]:
    if kappa <= 0:
        raise ValueError("kappa must be positive")

    g = np.asarray(geometry, dtype=float)
    pg = np.asarray(geometry_momentum, dtype=float)

    g_dot = kappa * np.exp(-4.0*g) * pg

    gauge_source = local_geometry_source(
        links,
        electric,
        g,
        beta,
        group_dimension=3,
    )
    matter_source = matter_geometry_source(
        matter,
        matter_momentum,
        g,
        matter_params,
    )

    pg_dot = (
        periodic_laplacian(g)/kappa
        + 2.0*kappa*np.exp(-4.0*g)*pg**2
        + matter_source
        + gauge_source
    )
    return g_dot, pg_dot


def total_energy(
    geometry: np.ndarray,
    geometry_momentum: np.ndarray,
    matter: np.ndarray,
    matter_momentum: np.ndarray,
    links: np.ndarray,
    electric: np.ndarray,
    kappa: float,
    beta: float,
    matter_params: SU3ScalarMatterParameters,
) -> float:
    return (
        geometry_kinetic_energy(
            geometry,
            geometry_momentum,
            kappa,
        )
        + geometry_gradient_energy(
            geometry,
            kappa,
        )
        + matter_energy(
            matter,
            matter_momentum,
            links,
            geometry,
            matter_params,
        )
        + weighted_su3_energy(
            links,
            electric,
            geometry,
            beta,
        )
    )


def non_geometry_energy(
    geometry: np.ndarray,
    matter: np.ndarray,
    matter_momentum: np.ndarray,
    links: np.ndarray,
    electric: np.ndarray,
    beta: float,
    matter_params: SU3ScalarMatterParameters,
) -> float:
    return (
        matter_energy(
            matter,
            matter_momentum,
            links,
            geometry,
            matter_params,
        )
        + weighted_su3_energy(
            links,
            electric,
            geometry,
            beta,
        )
    )


def total_geometry_source(
    geometry: np.ndarray,
    matter: np.ndarray,
    matter_momentum: np.ndarray,
    links: np.ndarray,
    electric: np.ndarray,
    beta: float,
    matter_params: SU3ScalarMatterParameters,
) -> np.ndarray:
    return (
        matter_geometry_source(
            matter,
            matter_momentum,
            geometry,
            matter_params,
        )
        + local_geometry_source(
            links,
            electric,
            geometry,
            beta,
            group_dimension=3,
        )
    )


@dataclass
class SU3MatterReciprocityDynamics:
    geometry: np.ndarray
    geometry_momentum: np.ndarray
    matter: np.ndarray
    matter_momentum: np.ndarray
    links: np.ndarray
    electric: np.ndarray
    kappa: float = 1.0
    beta: float = 1.0
    matter_params: SU3ScalarMatterParameters = SU3ScalarMatterParameters()
    time: float = 0.0

    def __post_init__(self) -> None:
        self.geometry = np.asarray(self.geometry, dtype=float).copy()
        self.geometry_momentum = np.asarray(
            self.geometry_momentum,
            dtype=float,
        ).copy()
        self.matter = np.asarray(self.matter, dtype=complex).copy()
        self.matter_momentum = np.asarray(
            self.matter_momentum,
            dtype=complex,
        ).copy()
        self.links = np.asarray(self.links, dtype=complex).copy()
        self.electric = np.asarray(self.electric, dtype=float).copy()

        shape = self.geometry.shape
        if self.geometry.ndim != 3:
            raise ValueError("geometry must be 3D")
        if self.geometry_momentum.shape != shape:
            raise ValueError("geometry_momentum shape mismatch")
        if self.matter.shape != shape + (3,):
            raise ValueError("matter shape mismatch")
        if self.matter_momentum.shape != self.matter.shape:
            raise ValueError("matter_momentum shape mismatch")
        if self.links.shape != (3,) + shape + (3,3):
            raise ValueError("links shape mismatch")
        if self.electric.shape != (3,) + shape + (8,):
            raise ValueError("electric shape mismatch")
        if self.kappa <= 0 or self.beta < 0:
            raise ValueError("invalid coupling")

    @property
    def energy(self) -> float:
        return total_energy(
            self.geometry,
            self.geometry_momentum,
            self.matter,
            self.matter_momentum,
            self.links,
            self.electric,
            self.kappa,
            self.beta,
            self.matter_params,
        )

    @property
    def max_gauss(self) -> float:
        return float(
            np.max(
                np.abs(
                    coupled_gauss_components(
                        self.matter,
                        self.matter_momentum,
                        self.links,
                        self.electric,
                    )
                )
            )
        )

    def step(self, dt: float) -> None:
        if dt <= 0:
            raise ValueError("dt must be positive")

        # Momentum half-kicks.
        _, pg_dot = geometry_rhs(
            self.geometry,
            self.geometry_momentum,
            self.matter,
            self.matter_momentum,
            self.links,
            self.electric,
            self.kappa,
            self.beta,
            self.matter_params,
        )
        self.geometry_momentum += 0.5*dt*pg_dot

        self.matter_momentum += 0.5*dt*matter_momentum_force(
            self.matter,
            self.links,
            self.geometry,
            self.matter_params,
        )

        self.electric += 0.5*dt*(
            analytic_weighted_force(
                self.links,
                self.geometry,
                self.beta,
            )
            - matter_link_current(
                self.matter,
                self.links,
            )
        )

        # Coordinate drifts.
        self.geometry += dt*(
            self.kappa
            * np.exp(-4.0*self.geometry)
            * self.geometry_momentum
        )
        self.matter += dt*matter_coordinate_velocity(
            self.matter_momentum,
            self.geometry,
        )
        self.links = drift_links_weighted(
            self.links,
            self.electric,
            self.geometry,
            dt,
        )

        # Second momentum half-kicks.
        self.matter_momentum += 0.5*dt*matter_momentum_force(
            self.matter,
            self.links,
            self.geometry,
            self.matter_params,
        )

        self.electric += 0.5*dt*(
            analytic_weighted_force(
                self.links,
                self.geometry,
                self.beta,
            )
            - matter_link_current(
                self.matter,
                self.links,
            )
        )

        _, pg_dot = geometry_rhs(
            self.geometry,
            self.geometry_momentum,
            self.matter,
            self.matter_momentum,
            self.links,
            self.electric,
            self.kappa,
            self.beta,
            self.matter_params,
        )
        self.geometry_momentum += 0.5*dt*pg_dot

        self.time += dt
