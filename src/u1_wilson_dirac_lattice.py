"""U(1)-gauge-covariant spatial Wilson-Dirac Hamiltonian.

Spinor field:
    psi(x) in C^4

Compact U(1) link transporter:
    U_i(x) = exp(i A_i(x))

Local gauge transformation:
    psi(x) -> exp(i alpha(x)) psi(x)
    A_i(x) -> A_i(x) + alpha(x) - alpha(x+i)

Hamiltonian:

    H psi =
      sum_i alpha_i [
        U_i(x) psi(x+i)
        - U_i^*(x-i) psi(x-i)
      ] / (2 i)

      + beta_D [
          m psi
          + (r/2) sum_i (
              2 psi
              - U_i(x) psi(x+i)
              - U_i^*(x-i) psi(x-i)
            )
        ].

At zero gauge field this reduces exactly to the momentum-space Wilson-Dirac
reference:
    H(p) = sum_i alpha_i sin p_i
           + beta_D [m + r sum_i(1-cos p_i)].

This is a classical single-particle lattice spinor operator. It is not a
second-quantized fermion theory.
"""

from __future__ import annotations

import numpy as np

try:
    from .wilson_dirac_reference import ALPHA, BETA
except ImportError:
    from wilson_dirac_reference import ALPHA, BETA


AXES = (0, 1, 2)


def gauge_transform_links(
    links: np.ndarray,
    alpha: np.ndarray,
) -> np.ndarray:
    links = np.asarray(links, dtype=float)
    alpha = np.asarray(alpha, dtype=float)
    shape = alpha.shape
    if links.shape != (3,) + shape:
        raise ValueError("link shape mismatch")

    out = np.empty_like(links)
    for axis in AXES:
        out[axis] = (
            links[axis]
            + alpha
            - np.roll(alpha, -1, axis=axis)
        )
    return out


def gauge_transform_spinor(
    psi: np.ndarray,
    alpha: np.ndarray,
) -> np.ndarray:
    field = np.asarray(psi, dtype=complex)
    alpha = np.asarray(alpha, dtype=float)
    if field.shape != alpha.shape + (4,):
        raise ValueError("spinor shape mismatch")
    return np.exp(1j * alpha)[..., None] * field


def spinor_density(psi: np.ndarray) -> np.ndarray:
    field = np.asarray(psi, dtype=complex)
    if field.ndim != 4 or field.shape[-1] != 4:
        raise ValueError("psi must have shape (nx,ny,nz,4)")
    return np.sum(np.abs(field)**2, axis=-1)


def _forward_spinor(psi: np.ndarray, axis: int) -> np.ndarray:
    return np.roll(psi, -1, axis=axis)


def _backward_spinor(psi: np.ndarray, axis: int) -> np.ndarray:
    return np.roll(psi, 1, axis=axis)


def _backward_link(links: np.ndarray, axis: int) -> np.ndarray:
    return np.roll(links[axis], 1, axis=axis)


def apply_wilson_dirac(
    psi: np.ndarray,
    links: np.ndarray,
    mass: float = 0.0,
    wilson_r: float = 1.0,
) -> np.ndarray:
    field = np.asarray(psi, dtype=complex)
    links = np.asarray(links, dtype=float)

    shape = field.shape[:3]
    if field.shape != shape + (4,):
        raise ValueError("psi must have shape (nx,ny,nz,4)")
    if links.shape != (3,) + shape:
        raise ValueError("link shape mismatch")
    if wilson_r < 0:
        raise ValueError("wilson_r must be non-negative")

    out = np.zeros_like(field, dtype=complex)

    for axis in AXES:
        u_forward = np.exp(1j * links[axis])[..., None]
        u_backward = np.exp(-1j * _backward_link(links, axis))[..., None]

        psi_forward = _forward_spinor(field, axis)
        psi_backward = _backward_spinor(field, axis)

        transported_forward = u_forward * psi_forward
        transported_backward = u_backward * psi_backward

        kinetic_vec = (
            transported_forward - transported_backward
        ) / (2.0j)

        wilson_vec = (
            2.0 * field
            - transported_forward
            - transported_backward
        ) * (0.5 * wilson_r)

        out += np.einsum(
            "ab,...b->...a",
            ALPHA[axis],
            kinetic_vec,
        )
        out += np.einsum(
            "ab,...b->...a",
            BETA,
            wilson_vec,
        )

    if mass != 0.0:
        out += mass * np.einsum(
            "ab,...b->...a",
            BETA,
            field,
        )

    return out


def inner_product(a: np.ndarray, b: np.ndarray) -> complex:
    return np.vdot(
        np.asarray(a, dtype=complex),
        np.asarray(b, dtype=complex),
    )
