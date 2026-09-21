"""Experimental 3D U(1) gauge field built from the six canonical boundary orientations.

Spatial axes are identified only at the adapter level:
    +X/-X, +Y/-Y, +Z/-Z

This uses the canonical six-gate orientation set as a spatial lattice scaffold.
It does not alter the v0.4 kernel and does not claim that physical space has
already been derived from the kernel.

The weak-field Hamiltonian is the standard lattice Abelian form

    H = 1/2 sum_links E_i^2 + beta/2 sum_plaquettes F_ij^2

with compact Wilson form available through cos(F_ij). Time remains the
Hamiltonian evolution parameter.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Tuple

try:
    from .gauge_dynamics import wrap_angle
except ImportError:
    from gauge_dynamics import wrap_angle


AXES = ("x", "y", "z")
PLAQUETTE_PLANES = (("x", "y"), ("y", "z"), ("z", "x"))


def _zeros3(shape: tuple[int, int, int]) -> list[list[list[float]]]:
    nx, ny, nz = shape
    return [[[0.0 for _ in range(nz)] for _ in range(ny)] for _ in range(nx)]


def _copy3(a):
    return [[row[:] for row in plane] for plane in a]


def _axis_index(axis: str) -> int:
    if axis not in AXES:
        raise ValueError("axis must be x, y, or z")
    return AXES.index(axis)


def _shift(idx: tuple[int, int, int], axis: str, step: int, shape):
    out = list(idx)
    i = _axis_index(axis)
    out[i] = (out[i] + step) % shape[i]
    return tuple(out)


def _get(a, idx):
    x, y, z = idx
    return a[x][y][z]


def _set(a, idx, value):
    x, y, z = idx
    a[x][y][z] = value


@dataclass
class U13DField:
    """Compact U(1) connection on a periodic 3D cubic adapter lattice."""

    shape: tuple[int, int, int]
    links: dict[str, list[list[list[float]]]]
    beta: float = 1.0

    def __post_init__(self):
        if any(n <= 1 for n in self.shape):
            raise ValueError("each spatial dimension must be at least 2")
        if self.beta <= 0:
            raise ValueError("beta must be positive")
        if set(self.links) != set(AXES):
            raise ValueError("links must contain x, y, z")

    @classmethod
    def zeros(cls, shape=(4, 4, 4), beta: float = 1.0):
        return cls(
            shape=shape,
            links={axis: _zeros3(shape) for axis in AXES},
            beta=beta,
        )

    def raw_plaquette(self, plane: tuple[str, str], idx: tuple[int, int, int]) -> float:
        """Unwrapped oriented curvature used by the weak quadratic theory."""
        a, b = plane
        xp_a = _shift(idx, a, 1, self.shape)
        xp_b = _shift(idx, b, 1, self.shape)
        return (
            _get(self.links[a], idx)
            + _get(self.links[b], xp_a)
            - _get(self.links[a], xp_b)
            - _get(self.links[b], idx)
        )

    def plaquette(self, plane: tuple[str, str], idx: tuple[int, int, int]) -> float:
        """Principal compact U(1) plaquette angle."""
        return wrap_angle(self.raw_plaquette(plane, idx))

    def magnetic_components(self):
        """Return Bx=F_yz, By=F_zx, Bz=F_xy."""
        return {
            "x": [
                [
                    [self.raw_plaquette(("y", "z"), (i, j, k)) for k in range(self.shape[2])]
                    for j in range(self.shape[1])
                ]
                for i in range(self.shape[0])
            ],
            "y": [
                [
                    [self.raw_plaquette(("z", "x"), (i, j, k)) for k in range(self.shape[2])]
                    for j in range(self.shape[1])
                ]
                for i in range(self.shape[0])
            ],
            "z": [
                [
                    [self.raw_plaquette(("x", "y"), (i, j, k)) for k in range(self.shape[2])]
                    for j in range(self.shape[1])
                ]
                for i in range(self.shape[0])
            ],
        }

    def wilson_energy(self) -> float:
        total = 0.0
        nx, ny, nz = self.shape
        for plane in PLAQUETTE_PLANES:
            for i in range(nx):
                for j in range(ny):
                    for k in range(nz):
                        f = self.plaquette(plane, (i, j, k))
                        total += self.beta * 2.0 * math.sin(0.5 * f) ** 2
        return total

    def weak_magnetic_energy(self) -> float:
        total = 0.0
        nx, ny, nz = self.shape
        for plane in PLAQUETTE_PLANES:
            for i in range(nx):
                for j in range(ny):
                    for k in range(nz):
                        f = self.raw_plaquette(plane, (i, j, k))
                        total += 0.5 * self.beta * f * f
        return total

    def gauge_transform(self, alpha):
        transformed = {axis: _copy3(self.links[axis]) for axis in AXES}
        nx, ny, nz = self.shape
        for axis in AXES:
            for i in range(nx):
                for j in range(ny):
                    for k in range(nz):
                        idx = (i, j, k)
                        xp = _shift(idx, axis, 1, self.shape)
                        value = (
                            _get(self.links[axis], idx)
                            + _get(alpha, idx)
                            - _get(alpha, xp)
                        )
                        _set(transformed[axis], idx, wrap_angle(value))
        return U13DField(self.shape, transformed, self.beta)


@dataclass
class U13DHamiltonian:
    """Hamiltonian time evolution for the 3D U(1) adapter."""

    field: U13DField
    electric: dict[str, list[list[list[float]]]]
    time: float = 0.0

    @classmethod
    def zeros(cls, shape=(4, 4, 4), beta: float = 1.0):
        return cls(
            field=U13DField.zeros(shape, beta),
            electric={axis: _zeros3(shape) for axis in AXES},
        )

    def electric_energy(self) -> float:
        return 0.5 * sum(
            v * v
            for axis in AXES
            for plane in self.electric[axis]
            for row in plane
            for v in row
        )

    def total_energy(self) -> float:
        return self.electric_energy() + self.field.wilson_energy()

    def gauss(self):
        """Discrete div E on periodic cubic lattice."""
        out = _zeros3(self.field.shape)
        nx, ny, nz = self.field.shape
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    idx = (i, j, k)
                    value = 0.0
                    for axis in AXES:
                        xm = _shift(idx, axis, -1, self.field.shape)
                        value += _get(self.electric[axis], idx) - _get(self.electric[axis], xm)
                    _set(out, idx, value)
        return out

    def weak_force(self):
        """-dV/dA in the quadratic weak-field theory.

        This is the discrete curl-curl operator on link fields.
        """
        shape = self.field.shape
        force = {axis: _zeros3(shape) for axis in AXES}
        nx, ny, nz = shape

        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    idx = (i, j, k)
                    for axis in AXES:
                        total = 0.0
                        for other in AXES:
                            if other == axis:
                                continue

                            if (axis, other) in PLAQUETTE_PLANES:
                                plane = (axis, other)
                                sign = 1.0
                            else:
                                plane = (other, axis)
                                sign = -1.0

                            f_here = sign * self.field.raw_plaquette(plane, idx)
                            xm = _shift(idx, other, -1, shape)
                            f_prev = sign * self.field.raw_plaquette(plane, xm)
                            total += f_here - f_prev

                        _set(force[axis], idx, -self.field.beta * total)
        return force

    def leapfrog_weak(self, dt: float):
        """Symplectic weak-field evolution."""
        if dt <= 0:
            raise ValueError("dt must be positive")

        force = self.weak_force()
        nx, ny, nz = self.field.shape
        for axis in AXES:
            for i in range(nx):
                for j in range(ny):
                    for k in range(nz):
                        idx = (i, j, k)
                        _set(
                            self.electric[axis],
                            idx,
                            _get(self.electric[axis], idx)
                            + 0.5 * dt * _get(force[axis], idx),
                        )

        for axis in AXES:
            for i in range(nx):
                for j in range(ny):
                    for k in range(nz):
                        idx = (i, j, k)
                        _set(
                            self.field.links[axis],
                            idx,
                            wrap_angle(
                                _get(self.field.links[axis], idx)
                                + dt * _get(self.electric[axis], idx)
                            ),
                        )

        force = self.weak_force()
        for axis in AXES:
            for i in range(nx):
                for j in range(ny):
                    for k in range(nz):
                        idx = (i, j, k)
                        _set(
                            self.electric[axis],
                            idx,
                            _get(self.electric[axis], idx)
                            + 0.5 * dt * _get(force[axis], idx),
                        )

        self.time += dt


def divergence(field_components: dict[str, list[list[list[float]]]], shape):
    out = _zeros3(shape)
    nx, ny, nz = shape
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                idx = (i, j, k)
                value = 0.0
                for axis in AXES:
                    xm = _shift(idx, axis, -1, shape)
                    value += _get(field_components[axis], idx) - _get(field_components[axis], xm)
                _set(out, idx, value)
    return out



def forward_divergence(field_components: dict[str, list[list[list[float]]]], shape):
    """Forward-difference divergence for plaquette-derived magnetic components.

    With Bx=F_yz, By=F_zx, Bz=F_xy built from forward-oriented plaquettes,
    the discrete Bianchi identity is Δ_x^+ Bx + Δ_y^+ By + Δ_z^+ Bz = 0.
    """
    out = _zeros3(shape)
    nx, ny, nz = shape
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                idx = (i, j, k)
                value = 0.0
                for axis in AXES:
                    xp = _shift(idx, axis, 1, shape)
                    value += _get(field_components[axis], xp) - _get(
                        field_components[axis], idx
                    )
                _set(out, idx, value)
    return out

def max_abs_scalar(field) -> float:
    return max(abs(v) for plane in field for row in plane for v in row)
