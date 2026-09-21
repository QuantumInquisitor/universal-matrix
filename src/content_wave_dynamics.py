"""Finite-speed dynamical scalar content potential.

Experimental PDE:

    chi_tt + gamma(x) chi_t
        = c_chi^2 * (laplacian chi + kappa_C * rho_C)

with fixed-zero outermost boundary cells and an optional damping sponge near the
six faces.

Static limit:
    laplacian chi + kappa_C rho_C = 0

or
    -laplacian chi = kappa_C rho_C,

matching content_potential_field.py.

Numerics:
- second-order centered finite differences in space;
- kick-drift-kick time stepping;
- exact multiplicative half-step damping;
- explicit CFL guard c*dt/h <= 1/sqrt(3) for the 3D stencil.

This is an experimental scalar-wave adapter, not a gravitational field equation.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np


def interior_laplacian(field: np.ndarray, spacing: float = 1.0) -> np.ndarray:
    a = np.asarray(field, dtype=float)
    if a.ndim != 3:
        raise ValueError("field must be 3D")
    if min(a.shape) < 3:
        raise ValueError("each dimension must be at least 3")
    if spacing <= 0:
        raise ValueError("spacing must be positive")

    out = np.zeros_like(a)
    h2 = spacing * spacing
    out[1:-1, 1:-1, 1:-1] = (
        a[2:, 1:-1, 1:-1]
        + a[:-2, 1:-1, 1:-1]
        + a[1:-1, 2:, 1:-1]
        + a[1:-1, :-2, 1:-1]
        + a[1:-1, 1:-1, 2:]
        + a[1:-1, 1:-1, :-2]
        - 6.0 * a[1:-1, 1:-1, 1:-1]
    ) / h2
    return out


def sponge_profile(
    shape: tuple[int, int, int],
    width: int = 0,
    strength: float = 0.0,
) -> np.ndarray:
    if min(shape) < 3:
        raise ValueError("each dimension must be at least 3")
    if width < 0:
        raise ValueError("width must be non-negative")
    if strength < 0:
        raise ValueError("strength must be non-negative")
    if width == 0 or strength == 0:
        return np.zeros(shape, dtype=float)

    max_width = max(1, min(shape) // 2)
    width = min(width, max_width)

    profile = np.zeros(shape, dtype=float)
    nx, ny, nz = shape
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                d = min(
                    i,
                    nx - 1 - i,
                    j,
                    ny - 1 - j,
                    k,
                    nz - 1 - k,
                )
                if d < width:
                    x = (width - d) / width
                    profile[i, j, k] = strength * x * x
    return profile


@dataclass
class ContentWaveField:
    shape: tuple[int, int, int]
    wave_speed: float = 1.0
    source_coupling: float = 1.0
    spacing: float = 1.0
    sponge_width: int = 0
    sponge_strength: float = 0.0

    def __post_init__(self) -> None:
        if min(self.shape) < 3:
            raise ValueError("each dimension must be at least 3")
        if self.wave_speed <= 0:
            raise ValueError("wave_speed must be positive")
        if self.source_coupling < 0:
            raise ValueError("source_coupling must be non-negative")
        if self.spacing <= 0:
            raise ValueError("spacing must be positive")

        self.potential = np.zeros(self.shape, dtype=float)
        self.velocity = np.zeros(self.shape, dtype=float)
        self.source_density = np.zeros(self.shape, dtype=float)
        self.damping = sponge_profile(
            self.shape,
            self.sponge_width,
            self.sponge_strength,
        )
        self.time = 0.0

    def set_source_density(self, source_density: np.ndarray) -> None:
        rho = np.asarray(source_density, dtype=float)
        if rho.shape != self.shape:
            raise ValueError("source shape mismatch")
        if np.any(rho < 0):
            raise ValueError("content source density must be non-negative")
        self.source_density = rho.copy()

    def static_residual(self) -> np.ndarray:
        return (
            interior_laplacian(self.potential, self.spacing)
            + self.source_coupling * self.source_density
        )

    def acceleration(self) -> np.ndarray:
        return self.wave_speed**2 * self.static_residual()

    def _enforce_boundary(self) -> None:
        for a in (self.potential, self.velocity):
            a[0, :, :] = 0.0
            a[-1, :, :] = 0.0
            a[:, 0, :] = 0.0
            a[:, -1, :] = 0.0
            a[:, :, 0] = 0.0
            a[:, :, -1] = 0.0

    def max_stable_dt(self) -> float:
        return self.spacing / (self.wave_speed * math.sqrt(3.0))

    def step(self, dt: float) -> None:
        if dt <= 0:
            raise ValueError("dt must be positive")
        if dt > self.max_stable_dt() * (1.0 + 1e-14):
            raise ValueError("dt exceeds the 3D explicit CFL limit")

        damping_half = np.exp(-0.5 * self.damping * dt)

        self.velocity *= damping_half
        self.velocity += 0.5 * dt * self.acceleration()

        self.potential += dt * self.velocity
        self._enforce_boundary()

        self.velocity += 0.5 * dt * self.acceleration()
        self.velocity *= damping_half
        self._enforce_boundary()

        self.time += dt

    def energy(self) -> float:
        """Source-free scalar-wave energy for diagnostic use."""
        v_term = 0.5 * np.sum((self.velocity / self.wave_speed) ** 2)

        dx = (self.potential[1:, :, :] - self.potential[:-1, :, :]) / self.spacing
        dy = (self.potential[:, 1:, :] - self.potential[:, :-1, :]) / self.spacing
        dz = (self.potential[:, :, 1:] - self.potential[:, :, :-1]) / self.spacing
        grad_term = 0.5 * (
            np.sum(dx * dx) + np.sum(dy * dy) + np.sum(dz * dz)
        )
        return float(v_term + grad_term)

    def max_static_residual(self) -> float:
        residual = self.static_residual()
        return float(np.max(np.abs(residual[1:-1, 1:-1, 1:-1])))
