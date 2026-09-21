"""Electroweak symmetry-breaking reference bridge.

This module implements the standard tree-level SU(2)_L x U(1)_Y gauge-boson
mass algebra for one complex scalar doublet with vacuum scale v.

It is included as a correspondence target for future Matrix-derived symmetry
breaking. It is NOT claimed to be derived from the canonical Matrix kernel.

Conventions:
    Higgs hypercharge Y = 1/2
    <Phi> = (0, v/sqrt(2))^T

Then
    m_W^2 = g^2 v^2 / 4

and the neutral (W3, B) mass-squared matrix is

    (v^2/4) [[ g^2, -g g' ],
             [ -g g', g'^2 ]].

Eigenvalues:
    0
    (g^2 + g'^2) v^2 / 4.

Define
    sin(theta_W) = g' / sqrt(g^2+g'^2)
    cos(theta_W) = g  / sqrt(g^2+g'^2).

Then
    A = sin(theta_W) W3 + cos(theta_W) B
is massless and
    Z = cos(theta_W) W3 - sin(theta_W) B
has
    m_Z = v/2 sqrt(g^2+g'^2).

Also
    m_W = m_Z cos(theta_W).
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np


@dataclass(frozen=True)
class ElectroweakParameters:
    g_su2: float
    g_u1: float
    vacuum_scale: float

    def __post_init__(self) -> None:
        if self.g_su2 <= 0 or self.g_u1 <= 0:
            raise ValueError("gauge couplings must be positive")
        if self.vacuum_scale <= 0:
            raise ValueError("vacuum_scale must be positive")

    @property
    def normalization(self) -> float:
        return math.sqrt(self.g_su2**2 + self.g_u1**2)

    @property
    def sin_theta_w(self) -> float:
        return self.g_u1 / self.normalization

    @property
    def cos_theta_w(self) -> float:
        return self.g_su2 / self.normalization

    @property
    def theta_w(self) -> float:
        return math.atan2(self.g_u1, self.g_su2)

    @property
    def w_mass(self) -> float:
        return 0.5 * self.g_su2 * self.vacuum_scale

    @property
    def z_mass(self) -> float:
        return 0.5 * self.normalization * self.vacuum_scale


def neutral_mass_squared_matrix(
    params: ElectroweakParameters,
) -> np.ndarray:
    g = params.g_su2
    gp = params.g_u1
    factor = params.vacuum_scale**2 / 4.0
    return factor * np.array(
        [
            [g*g, -g*gp],
            [-g*gp, gp*gp],
        ],
        dtype=float,
    )


def neutral_eigensystem(
    params: ElectroweakParameters,
) -> tuple[np.ndarray, np.ndarray]:
    values, vectors = np.linalg.eigh(neutral_mass_squared_matrix(params))
    order = np.argsort(values)
    return values[order], vectors[:, order]


def photon_direction(params: ElectroweakParameters) -> np.ndarray:
    """Unit vector in basis (W3, B)."""
    return np.array(
        [
            params.sin_theta_w,
            params.cos_theta_w,
        ],
        dtype=float,
    )


def z_direction(params: ElectroweakParameters) -> np.ndarray:
    """Unit vector in basis (W3, B)."""
    return np.array(
        [
            params.cos_theta_w,
            -params.sin_theta_w,
        ],
        dtype=float,
    )


def electric_coupling(params: ElectroweakParameters) -> float:
    return (
        params.g_su2
        * params.g_u1
        / params.normalization
    )


def mass_relation_residual(params: ElectroweakParameters) -> float:
    return params.w_mass - params.z_mass * params.cos_theta_w
