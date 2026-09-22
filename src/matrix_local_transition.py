"""Minimal local transition law for repeated Matrix cells.

This module introduces an experimental nearest-neighbor Hamiltonian for the
candidate repeated-cell ontology. It does not modify the exact canonical
Z_108 core.

Site variables
--------------
Each site carries:
    phi_x : dimensionless phase
    pi_x  : conjugate phase momentum

Link variables
--------------
Each positively oriented nearest-neighbor link carries:
    theta_xy : compact U(1) transport phase

Gauge convention
----------------
    phi_x   -> phi_x + alpha_x
    theta_xy -> theta_xy + alpha_x - alpha_y

so the link phase difference

    delta_xy = phi_y - phi_x + theta_xy

is gauge invariant.

Hamiltonian
-----------
    H = sum_x pi_x^2 / (2 I)
        + kappa * sum_<xy> [1 - cos(delta_xy)]

with positive inertia I and coupling kappa.

This construction guarantees:
- strict nearest-neighbor locality;
- global phase-shift symmetry;
- exact gauge invariance of the Hamiltonian;
- pairwise antisymmetric momentum exchange;
- exact conservation of total phase momentum in continuous time;
- a weak-field lattice-wave limit with c_lat^2 = kappa / I.

The dimensional map from lattice units to physical length and time remains
unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


AXES = ("x", "y", "z")


def _validate_shape(shape: tuple[int, int, int]) -> tuple[int, int, int]:
    if len(shape) != 3:
        raise ValueError("shape must have exactly three dimensions")
    if any(not isinstance(v, int) or isinstance(v, bool) or v < 2 for v in shape):
        raise ValueError("each shape dimension must be an integer >= 2")
    return shape


def zero_site_field(shape: tuple[int, int, int]) -> np.ndarray:
    return np.zeros(_validate_shape(shape), dtype=float)


def zero_link_field(
    shape: tuple[int, int, int],
    boundary_mode: str = "open",
) -> dict[str, np.ndarray]:
    nx, ny, nz = _validate_shape(shape)
    if boundary_mode == "open":
        return {
            "x": np.zeros((nx - 1, ny, nz), dtype=float),
            "y": np.zeros((nx, ny - 1, nz), dtype=float),
            "z": np.zeros((nx, ny, nz - 1), dtype=float),
        }
    if boundary_mode == "periodic":
        return {
            "x": np.zeros((nx, ny, nz), dtype=float),
            "y": np.zeros((nx, ny, nz), dtype=float),
            "z": np.zeros((nx, ny, nz), dtype=float),
        }
    raise ValueError("boundary_mode must be 'open' or 'periodic'")


def _principal_angle(value: np.ndarray) -> np.ndarray:
    return (value + np.pi) % (2.0 * np.pi) - np.pi


def _link_delta(
    phase: np.ndarray,
    links: dict[str, np.ndarray],
    axis: str,
    boundary_mode: str,
) -> np.ndarray:
    if axis == "x":
        if boundary_mode == "open":
            return phase[1:, :, :] - phase[:-1, :, :] + links["x"]
        return np.roll(phase, -1, axis=0) - phase + links["x"]
    if axis == "y":
        if boundary_mode == "open":
            return phase[:, 1:, :] - phase[:, :-1, :] + links["y"]
        return np.roll(phase, -1, axis=1) - phase + links["y"]
    if axis == "z":
        if boundary_mode == "open":
            return phase[:, :, 1:] - phase[:, :, :-1] + links["z"]
        return np.roll(phase, -1, axis=2) - phase + links["z"]
    raise ValueError(f"unknown axis {axis!r}")


def gauge_transform_links(
    links: dict[str, np.ndarray],
    alpha: np.ndarray,
    boundary_mode: str = "open",
) -> dict[str, np.ndarray]:
    """Return theta' = theta + alpha_source - alpha_target."""
    alpha = np.asarray(alpha, dtype=float)
    shape = alpha.shape
    expected = zero_link_field(shape, boundary_mode)

    out: dict[str, np.ndarray] = {}
    for axis in AXES:
        if np.shape(links[axis]) != np.shape(expected[axis]):
            raise ValueError(f"link shape mismatch on axis {axis}")

    if boundary_mode == "open":
        out["x"] = _principal_angle(
            links["x"] + alpha[:-1, :, :] - alpha[1:, :, :]
        )
        out["y"] = _principal_angle(
            links["y"] + alpha[:, :-1, :] - alpha[:, 1:, :]
        )
        out["z"] = _principal_angle(
            links["z"] + alpha[:, :, :-1] - alpha[:, :, 1:]
        )
    elif boundary_mode == "periodic":
        out["x"] = _principal_angle(
            links["x"] + alpha - np.roll(alpha, -1, axis=0)
        )
        out["y"] = _principal_angle(
            links["y"] + alpha - np.roll(alpha, -1, axis=1)
        )
        out["z"] = _principal_angle(
            links["z"] + alpha - np.roll(alpha, -1, axis=2)
        )
    else:
        raise ValueError("boundary_mode must be 'open' or 'periodic'")

    return out


@dataclass
class MatrixLocalTransition:
    """Experimental local Hamiltonian on the repeated Matrix-cell complex."""

    shape: tuple[int, int, int]
    phase: np.ndarray
    momentum: np.ndarray
    links: dict[str, np.ndarray]
    coupling: float = 1.0
    inertia: float = 1.0
    boundary_mode: str = "open"
    time: float = 0.0

    def __post_init__(self) -> None:
        self.shape = _validate_shape(self.shape)
        if self.boundary_mode not in {"open", "periodic"}:
            raise ValueError("boundary_mode must be 'open' or 'periodic'")
        if not math.isfinite(self.coupling) or self.coupling <= 0:
            raise ValueError("coupling must be finite and positive")
        if not math.isfinite(self.inertia) or self.inertia <= 0:
            raise ValueError("inertia must be finite and positive")

        self.phase = np.asarray(self.phase, dtype=float).copy()
        self.momentum = np.asarray(self.momentum, dtype=float).copy()
        if self.phase.shape != self.shape:
            raise ValueError("phase shape mismatch")
        if self.momentum.shape != self.shape:
            raise ValueError("momentum shape mismatch")
        if not np.all(np.isfinite(self.phase)):
            raise ValueError("phase must be finite")
        if not np.all(np.isfinite(self.momentum)):
            raise ValueError("momentum must be finite")

        expected = zero_link_field(self.shape, self.boundary_mode)
        copied: dict[str, np.ndarray] = {}
        for axis in AXES:
            if axis not in self.links:
                raise ValueError(f"missing link field {axis}")
            arr = np.asarray(self.links[axis], dtype=float)
            if arr.shape != expected[axis].shape:
                raise ValueError(f"link shape mismatch on axis {axis}")
            if not np.all(np.isfinite(arr)):
                raise ValueError(f"link field {axis} must be finite")
            copied[axis] = arr.copy()
        self.links = copied

    @classmethod
    def zeros(
        cls,
        shape: tuple[int, int, int] = (4, 4, 4),
        *,
        coupling: float = 1.0,
        inertia: float = 1.0,
        boundary_mode: str = "open",
    ) -> "MatrixLocalTransition":
        return cls(
            shape=shape,
            phase=zero_site_field(shape),
            momentum=zero_site_field(shape),
            links=zero_link_field(shape, boundary_mode),
            coupling=coupling,
            inertia=inertia,
            boundary_mode=boundary_mode,
        )

    @property
    def lattice_wave_speed(self) -> float:
        """Weak-field characteristic speed in lattice sites per model-time unit."""
        return math.sqrt(self.coupling / self.inertia)

    def link_deltas(self) -> dict[str, np.ndarray]:
        return {
            axis: _link_delta(
                self.phase,
                self.links,
                axis,
                self.boundary_mode,
            )
            for axis in AXES
        }

    def kinetic_energy(self) -> float:
        return float(
            0.5 * np.sum(self.momentum * self.momentum) / self.inertia
        )

    def interaction_energy(self) -> float:
        return float(
            self.coupling
            * sum(
                np.sum(1.0 - np.cos(delta))
                for delta in self.link_deltas().values()
            )
        )

    def energy(self) -> float:
        return self.kinetic_energy() + self.interaction_energy()

    def total_momentum(self) -> float:
        return float(np.sum(self.momentum))

    def phase_velocity(self) -> np.ndarray:
        return self.momentum / self.inertia

    def force(self) -> np.ndarray:
        """Return pi_dot = -dH/dphi from pairwise nearest-neighbor exchange."""
        out = np.zeros(self.shape, dtype=float)
        deltas = self.link_deltas()

        if self.boundary_mode == "open":
            sx = self.coupling * np.sin(deltas["x"])
            out[:-1, :, :] += sx
            out[1:, :, :] -= sx

            sy = self.coupling * np.sin(deltas["y"])
            out[:, :-1, :] += sy
            out[:, 1:, :] -= sy

            sz = self.coupling * np.sin(deltas["z"])
            out[:, :, :-1] += sz
            out[:, :, 1:] -= sz
            return out

        for axis_index, axis in enumerate(AXES):
            flow = self.coupling * np.sin(deltas[axis])
            out += flow
            out -= np.roll(flow, 1, axis=axis_index)
        return out

    def linearized_force(self) -> np.ndarray:
        """Small-gradient force obtained by replacing sin(delta) with delta."""
        out = np.zeros(self.shape, dtype=float)
        deltas = self.link_deltas()

        if self.boundary_mode == "open":
            dx = self.coupling * deltas["x"]
            out[:-1, :, :] += dx
            out[1:, :, :] -= dx

            dy = self.coupling * deltas["y"]
            out[:, :-1, :] += dy
            out[:, 1:, :] -= dy

            dz = self.coupling * deltas["z"]
            out[:, :, :-1] += dz
            out[:, :, 1:] -= dz
            return out

        for axis_index, axis in enumerate(AXES):
            flow = self.coupling * deltas[axis]
            out += flow
            out -= np.roll(flow, 1, axis=axis_index)
        return out

    def gauge_transform(self, alpha: np.ndarray) -> "MatrixLocalTransition":
        """Return a gauge-equivalent state."""
        alpha = np.asarray(alpha, dtype=float)
        if alpha.shape != self.shape:
            raise ValueError("alpha shape mismatch")
        if not np.all(np.isfinite(alpha)):
            raise ValueError("alpha must be finite")

        return MatrixLocalTransition(
            shape=self.shape,
            phase=self.phase + alpha,
            momentum=self.momentum.copy(),
            links=gauge_transform_links(
                self.links,
                alpha,
                self.boundary_mode,
            ),
            coupling=self.coupling,
            inertia=self.inertia,
            boundary_mode=self.boundary_mode,
            time=self.time,
        )

    def leapfrog(self, dt: float, steps: int = 1) -> None:
        """Advance with a second-order symplectic kick-drift-kick integrator."""
        if not math.isfinite(dt) or dt <= 0:
            raise ValueError("dt must be finite and positive")
        if not isinstance(steps, int) or isinstance(steps, bool) or steps < 1:
            raise ValueError("steps must be a positive integer")

        for _ in range(steps):
            self.momentum += 0.5 * dt * self.force()
            self.phase += dt * self.phase_velocity()
            self.phase = _principal_angle(self.phase)
            self.momentum += 0.5 * dt * self.force()
            self.time += dt
