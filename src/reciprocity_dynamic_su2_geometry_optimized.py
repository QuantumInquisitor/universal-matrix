"""Optimized spatially weighted SU(2) reciprocity geometry dynamics.

This module derives the analytic magnetic force for the spatially varying
reciprocity-weighted SU(2) Hamiltonian.

For each target link U_mu(x), the weighted staple is

    K_mu^(psi)(x)
      = sum_{nu != mu} [
          w_p(x;mu,nu) K_forward
          + w_p(x-nu;mu,nu) K_backward
        ].

Then

    F_mu^a(x)
      = -(beta/2)
        Im Tr[
          T_a U_mu(x) K_mu^(psi)(x)
        ].

The force is verified against the slower group finite-difference oracle in
reciprocity_dynamic_su2_geometry.py.

Geometry evolution uses the exact local source from
reciprocity_nonabelian_spatial_geometry.py.

This remains a classical lattice model and the endpoint/corner averaging of psi
is a discretization convention.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

try:
    from .reciprocity_dynamic_su2_geometry import (
        geometry_rhs,
        geometry_kinetic_energy,
        geometry_gradient_energy,
        drift_links_weighted,
        weighted_group_force_reference,
    )
    from .reciprocity_nonabelian_spatial_geometry import (
        plaquette_weight,
        weighted_su2_energy,
    )
    from .su2_hamiltonian_reference import GENERATORS
except ImportError:
    from reciprocity_dynamic_su2_geometry import (
        geometry_rhs,
        geometry_kinetic_energy,
        geometry_gradient_energy,
        drift_links_weighted,
        weighted_group_force_reference,
    )
    from reciprocity_nonabelian_spatial_geometry import (
        plaquette_weight,
        weighted_su2_energy,
    )
    from su2_hamiltonian_reference import GENERATORS


AXES=(0,1,2)


def shift_index(idx,axis,step,shape):
    out=list(idx)
    out[axis]=(out[axis]+step)%shape[axis]
    return tuple(out)


def weighted_staple_sum(
    links: np.ndarray,
    psi: np.ndarray,
    axis: int,
    idx: tuple[int,int,int],
) -> np.ndarray:
    p=np.asarray(psi,dtype=float)
    shape=p.shape
    total=np.zeros((2,2),dtype=complex)
    x_plus_mu=shift_index(idx,axis,1,shape)

    for nu in AXES:
        if nu==axis:
            continue

        x_plus_nu=shift_index(idx,nu,1,shape)
        x_minus_nu=shift_index(idx,nu,-1,shape)
        x_plus_mu_minus_nu=shift_index(
            x_minus_nu,axis,1,shape
        )

        forward=(
            links[(nu,)+x_plus_mu]
            @ links[(axis,)+x_plus_nu].conj().T
            @ links[(nu,)+idx].conj().T
        )
        backward=(
            links[(nu,)+x_plus_mu_minus_nu].conj().T
            @ links[(axis,)+x_minus_nu].conj().T
            @ links[(nu,)+x_minus_nu]
        )

        # plaquette_weight is symmetric in its scalar corner average even when
        # the ordered axis pair is reversed.
        wf=plaquette_weight(p,axis,nu)[idx]
        wb=plaquette_weight(p,axis,nu)[x_minus_nu]

        total += wf*forward + wb*backward

    return total


def analytic_weighted_force(
    links: np.ndarray,
    psi: np.ndarray,
    beta: float,
) -> np.ndarray:
    if beta<0:
        raise ValueError("beta must be non-negative")

    shape=np.asarray(psi).shape
    force=np.zeros(
        (3,)+shape+(3,),
        dtype=float,
    )

    for axis in AXES:
        for idx in np.ndindex(shape):
            product=(
                links[(axis,)+idx]
                @ weighted_staple_sum(
                    links,psi,axis,idx
                )
            )
            for a,generator in enumerate(GENERATORS):
                force[(axis,)+idx+(a,)]=(
                    -0.5*beta
                    * float(
                        np.trace(generator@product).imag
                    )
                )
    return force


def total_energy(
    psi,
    psi_momentum,
    links,
    electric,
    kappa,
    beta,
):
    return (
        geometry_kinetic_energy(
            psi,psi_momentum,kappa
        )
        + geometry_gradient_energy(
            psi,kappa
        )
        + weighted_su2_energy(
            links,electric,psi,beta
        )
    )


@dataclass
class SU2DynamicReciprocity:
    psi: np.ndarray
    psi_momentum: np.ndarray
    links: np.ndarray
    electric: np.ndarray
    kappa: float=1.0
    beta: float=1.0
    time: float=0.0

    def __post_init__(self):
        self.psi=np.asarray(self.psi,dtype=float).copy()
        self.psi_momentum=np.asarray(
            self.psi_momentum,dtype=float
        ).copy()
        self.links=np.asarray(
            self.links,dtype=complex
        ).copy()
        self.electric=np.asarray(
            self.electric,dtype=float
        ).copy()

        shape=self.psi.shape
        if self.psi.ndim!=3:
            raise ValueError("psi must be 3D")
        if self.psi_momentum.shape!=shape:
            raise ValueError("psi_momentum shape mismatch")
        if self.links.shape!=(3,)+shape+(2,2):
            raise ValueError("link shape mismatch")
        if self.electric.shape!=(3,)+shape+(3,):
            raise ValueError("electric shape mismatch")
        if self.kappa<=0 or self.beta<0:
            raise ValueError("invalid coupling")

    @property
    def energy(self):
        return total_energy(
            self.psi,
            self.psi_momentum,
            self.links,
            self.electric,
            self.kappa,
            self.beta,
        )

    def step(self,dt: float):
        if dt<=0:
            raise ValueError("dt must be positive")

        _,p_dot=geometry_rhs(
            self.psi,
            self.psi_momentum,
            self.links,
            self.electric,
            self.kappa,
            self.beta,
        )
        self.psi_momentum += 0.5*dt*p_dot

        force=analytic_weighted_force(
            self.links,self.psi,self.beta
        )
        self.electric += 0.5*dt*force

        psi_dot=(
            self.kappa
            * np.exp(-4.0*self.psi)
            * self.psi_momentum
        )
        self.psi += dt*psi_dot

        self.links=drift_links_weighted(
            self.links,
            self.electric,
            self.psi,
            dt,
        )

        force=analytic_weighted_force(
            self.links,self.psi,self.beta
        )
        self.electric += 0.5*dt*force

        _,p_dot=geometry_rhs(
            self.psi,
            self.psi_momentum,
            self.links,
            self.electric,
            self.kappa,
            self.beta,
        )
        self.psi_momentum += 0.5*dt*p_dot

        self.time += dt
