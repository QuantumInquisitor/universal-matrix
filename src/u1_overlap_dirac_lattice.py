"""Finite-lattice U(1)-gauge-covariant overlap Dirac operator.

This module upgrades the free momentum-space overlap reference to a small
periodic 4D Euclidean lattice with compact U(1) links.

Massless Wilson kernel:
    D_W(x,y)
      = 4 r delta_xy
        - 1/2 sum_mu [
            (r-gamma_mu) U_mu(x) delta_{x+mu,y}
            + (r+gamma_mu) U_mu^*(x-mu) delta_{x-mu,y}
          ].

This reproduces
    D_W(p)
      = i gamma_mu sin p_mu
        + r sum_mu (1-cos p_mu)

for zero gauge field.

Define
    H_W = Gamma5 (D_W - rho I),

where Gamma5 is gamma5 on every site.

For an admissible kernel with no zero eigenvalues, define
    sign(H_W)
      = V diag(sign(lambda_i)) V^dagger.

Then
    D_ov
      = rho [ I + Gamma5 sign(H_W) ].

It satisfies:
- local U(1) gauge covariance;
- gamma5 Hermiticity;
- Ginsparg-Wilson relation.

This dense implementation is a correctness reference for small lattices, not a
production overlap-fermion solver.
"""

from __future__ import annotations

import math
import numpy as np

try:
    from .overlap_dirac_reference import GAMMA, GAMMA5
except ImportError:
    from overlap_dirac_reference import GAMMA, GAMMA5


def site_count(shape: tuple[int,int,int,int]) -> int:
    if len(shape) != 4 or min(shape) < 1:
        raise ValueError("shape must contain four positive dimensions")
    return int(np.prod(shape))


def site_index(
    coord: tuple[int,int,int,int],
    shape: tuple[int,int,int,int],
) -> int:
    return int(np.ravel_multi_index(coord, shape))


def shift_coord(
    coord: tuple[int,int,int,int],
    axis: int,
    step: int,
    shape: tuple[int,int,int,int],
) -> tuple[int,int,int,int]:
    out=list(coord)
    out[axis]=(out[axis]+step)%shape[axis]
    return tuple(out)


def zero_links(shape: tuple[int,int,int,int]) -> np.ndarray:
    return np.zeros((4,)+shape,dtype=float)


def gauge_transform_links(
    links: np.ndarray,
    alpha: np.ndarray,
) -> np.ndarray:
    links=np.asarray(links,dtype=float)
    alpha=np.asarray(alpha,dtype=float)
    shape=alpha.shape
    if len(shape)!=4 or links.shape!=(4,)+shape:
        raise ValueError("link/alpha shape mismatch")

    out=np.empty_like(links)
    for mu in range(4):
        out[mu]=(
            links[mu]
            + alpha
            - np.roll(alpha,-1,axis=mu)
        )
    return out


def gauge_matrix(
    alpha: np.ndarray,
) -> np.ndarray:
    a=np.asarray(alpha,dtype=float)
    if a.ndim!=4:
        raise ValueError("alpha must be 4D")
    phases=np.exp(1j*a.reshape(-1))
    return np.kron(np.diag(phases),np.eye(4,dtype=complex))


def gamma5_lattice(shape: tuple[int,int,int,int]) -> np.ndarray:
    return np.kron(
        np.eye(site_count(shape),dtype=complex),
        GAMMA5,
    )


def wilson_dirac_matrix(
    links: np.ndarray,
    wilson_r: float=1.0,
) -> np.ndarray:
    if wilson_r<=0:
        raise ValueError("wilson_r must be positive")

    a=np.asarray(links,dtype=float)
    shape=a.shape[1:]
    if a.shape!=(4,)+shape or len(shape)!=4:
        raise ValueError("links must have shape (4,n0,n1,n2,n3)")

    n=site_count(shape)
    dim=4*n
    d=np.zeros((dim,dim),dtype=complex)
    i4=np.eye(4,dtype=complex)

    for coord in np.ndindex(shape):
        x=site_index(coord,shape)
        xs=slice(4*x,4*x+4)

        d[xs,xs] += 4.0*wilson_r*i4

        for mu in range(4):
            xp=shift_coord(coord,mu,1,shape)
            xm=shift_coord(coord,mu,-1,shape)
            yp=site_index(xp,shape)
            ym=site_index(xm,shape)
            yps=slice(4*yp,4*yp+4)
            yms=slice(4*ym,4*ym+4)

            u_forward=np.exp(1j*a[(mu,)+coord])
            u_backward=np.exp(-1j*a[(mu,)+xm])

            d[xs,yps] += (
                -0.5
                * u_forward
                * (wilson_r*i4 - GAMMA[mu])
            )
            d[xs,yms] += (
                -0.5
                * u_backward
                * (wilson_r*i4 + GAMMA[mu])
            )

    return d


def hermitian_wilson_matrix(
    links: np.ndarray,
    rho: float=1.0,
    wilson_r: float=1.0,
) -> np.ndarray:
    if not 0<rho<2.0*wilson_r:
        raise ValueError("require 0 < rho < 2*wilson_r")
    shape=np.asarray(links).shape[1:]
    d=wilson_dirac_matrix(links,wilson_r)
    g5=gamma5_lattice(shape)
    return g5@(d-rho*np.eye(d.shape[0],dtype=complex))


def matrix_sign_hermitian(
    h: np.ndarray,
    spectral_tolerance: float=1e-10,
) -> np.ndarray:
    matrix=np.asarray(h,dtype=complex)
    if not np.allclose(
        matrix,matrix.conj().T,atol=1e-10,rtol=0
    ):
        raise ValueError("matrix must be Hermitian")
    values,vectors=np.linalg.eigh(matrix)
    if np.min(np.abs(values))<=spectral_tolerance:
        raise ValueError("Hermitian Wilson kernel is not spectrally admissible")
    signs=np.sign(values)
    return (vectors*signs)@vectors.conj().T


def overlap_dirac_matrix(
    links: np.ndarray,
    rho: float=1.0,
    wilson_r: float=1.0,
    spectral_tolerance: float=1e-10,
) -> np.ndarray:
    shape=np.asarray(links).shape[1:]
    h=hermitian_wilson_matrix(links,rho,wilson_r)
    sign_h=matrix_sign_hermitian(h,spectral_tolerance)
    g5=gamma5_lattice(shape)
    identity=np.eye(h.shape[0],dtype=complex)
    return rho*(identity+g5@sign_h)


def ginsparg_wilson_residual(
    links: np.ndarray,
    rho: float=1.0,
    wilson_r: float=1.0,
) -> np.ndarray:
    d=overlap_dirac_matrix(links,rho,wilson_r)
    g5=gamma5_lattice(np.asarray(links).shape[1:])
    return g5@d+d@g5-(1.0/rho)*d@g5@d


def gamma5_hermiticity_residual(
    links: np.ndarray,
    rho: float=1.0,
    wilson_r: float=1.0,
) -> np.ndarray:
    d=overlap_dirac_matrix(links,rho,wilson_r)
    g5=gamma5_lattice(np.asarray(links).shape[1:])
    return d.conj().T-g5@d@g5


def covariance_residual(
    links: np.ndarray,
    alpha: np.ndarray,
    rho: float=1.0,
    wilson_r: float=1.0,
) -> np.ndarray:
    d=overlap_dirac_matrix(links,rho,wilson_r)
    transformed_links=gauge_transform_links(links,alpha)
    d2=overlap_dirac_matrix(
        transformed_links,rho,wilson_r
    )
    g=gauge_matrix(alpha)
    return d2-g@d@g.conj().T


def free_zero_mode_count(
    shape: tuple[int,int,int,int],
    rho: float=1.0,
    wilson_r: float=1.0,
    tolerance: float=1e-9,
) -> int:
    d=overlap_dirac_matrix(
        zero_links(shape),
        rho,
        wilson_r,
    )
    singular=np.linalg.svd(d,compute_uv=False)
    return int(np.count_nonzero(singular<tolerance))
