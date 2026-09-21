"""Discrete-exterior-calculus weak U(1) dynamics on an open cubical domain.

Unlike gauge_3d.py, this module has no periodic wraparound links. It implements
the cubical cochain sequence

    0-forms --d0--> 1-forms --d1--> 2-forms

with d1*d0 = 0 exactly.

Link arrays:
    x: (nx-1, ny, nz)
    y: (nx, ny-1, nz)
    z: (nx, ny, nz-1)

Face arrays:
    xy: (nx-1, ny-1, nz)
    yz: (nx, ny-1, nz-1)
    zx: (nx-1, ny, nz-1)

The weak Hamiltonian is

    H = 1/2 <E,E> + beta/2 <d1 A, d1 A>.

The magnetic force is -beta*d1^T*d1 A. Because d1*d0=0,

    div(d1^T F) = 0

under the matching discrete adjoint conventions, so source-free evolution
preserves the interior Gauss constraint exactly up to numerical roundoff.

This is the correct open-link dynamical companion to open_boundary_solver.py.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


AXES = ("x", "y", "z")
PLANES = ("xy", "yz", "zx")


def zero_links(shape):
    nx, ny, nz = shape
    return {
        "x": np.zeros((nx - 1, ny, nz), dtype=float),
        "y": np.zeros((nx, ny - 1, nz), dtype=float),
        "z": np.zeros((nx, ny, nz - 1), dtype=float),
    }


def zero_faces(shape):
    nx, ny, nz = shape
    return {
        "xy": np.zeros((nx - 1, ny - 1, nz), dtype=float),
        "yz": np.zeros((nx, ny - 1, nz - 1), dtype=float),
        "zx": np.zeros((nx - 1, ny, nz - 1), dtype=float),
    }


def gradient(phi):
    """d0 phi on positively oriented open links."""
    phi = np.asarray(phi, dtype=float)
    return {
        "x": phi[1:, :, :] - phi[:-1, :, :],
        "y": phi[:, 1:, :] - phi[:, :-1, :],
        "z": phi[:, :, 1:] - phi[:, :, :-1],
    }


def curl(links):
    """d1 A on oriented xy, yz, zx faces."""
    ax, ay, az = links["x"], links["y"], links["z"]

    fxy = (
        ax[:, :-1, :]
        + ay[1:, :, :]
        - ax[:, 1:, :]
        - ay[:-1, :, :]
    )
    fyz = (
        ay[:, :, :-1]
        + az[:, 1:, :]
        - ay[:, :, 1:]
        - az[:, :-1, :]
    )
    fzx = (
        az[:-1, :, :]
        + ax[:, :, 1:]
        - az[1:, :, :]
        - ax[:, :, :-1]
    )
    return {"xy": fxy, "yz": fyz, "zx": fzx}


def curl_adjoint(faces, shape):
    """Adjoint d1^T defined by exact oriented scatter from faces to links."""
    out = zero_links(shape)
    fxy, fyz, fzx = faces["xy"], faces["yz"], faces["zx"]

    # xy: +Ax(i,j), +Ay(i+1,j), -Ax(i,j+1), -Ay(i,j)
    out["x"][:, :-1, :] += fxy
    out["y"][1:, :, :] += fxy
    out["x"][:, 1:, :] -= fxy
    out["y"][:-1, :, :] -= fxy

    # yz: +Ay(i,j,k), +Az(i,j+1,k), -Ay(i,j,k+1), -Az(i,j,k)
    out["y"][:, :, :-1] += fyz
    out["z"][:, 1:, :] += fyz
    out["y"][:, :, 1:] -= fyz
    out["z"][:, :-1, :] -= fyz

    # zx: +Az(i,j,k), +Ax(i,j,k+1), -Az(i+1,j,k), -Ax(i,j,k)
    out["z"][:-1, :, :] += fzx
    out["x"][:, :, 1:] += fzx
    out["z"][1:, :, :] -= fzx
    out["x"][:, :, :-1] -= fzx

    return out


def divergence(links, shape):
    """Outgoing-minus-incoming divergence of open oriented link field."""
    nx, ny, nz = shape
    out = np.zeros(shape, dtype=float)

    ex = links["x"]
    out[:-1, :, :] += ex
    out[1:, :, :] -= ex

    ey = links["y"]
    out[:, :-1, :] += ey
    out[:, 1:, :] -= ey

    ez = links["z"]
    out[:, :, :-1] += ez
    out[:, :, 1:] -= ez
    return out


def inner_links(a, b) -> float:
    return float(sum(np.vdot(a[axis], b[axis]).real for axis in AXES))


def inner_faces(a, b) -> float:
    return float(sum(np.vdot(a[p], b[p]).real for p in PLANES))


def boundary_source_array(shape, face_flux_density):
    """Cell contribution of prescribed outward six-face electric flux."""
    nx, ny, nz = shape
    out = np.zeros(shape, dtype=float)
    out[nx - 1, :, :] += face_flux_density["x_pos"]
    out[0, :, :] += face_flux_density["x_neg"]
    out[:, ny - 1, :] += face_flux_density["y_pos"]
    out[:, 0, :] += face_flux_density["y_neg"]
    out[:, :, nz - 1] += face_flux_density["z_pos"]
    out[:, :, 0] += face_flux_density["z_neg"]
    return out


@dataclass
class OpenU1Hamiltonian:
    shape: tuple[int, int, int]
    links: dict[str, np.ndarray]
    electric: dict[str, np.ndarray]
    beta: float = 1.0
    time: float = 0.0

    @classmethod
    def zeros(cls, shape=(4, 4, 4), beta=1.0):
        if min(shape) < 2:
            raise ValueError("each dimension must be at least 2")
        if beta <= 0:
            raise ValueError("beta must be positive")
        return cls(shape, zero_links(shape), zero_links(shape), beta, 0.0)

    def magnetic_faces(self):
        return curl(self.links)

    def weak_force(self):
        adj = curl_adjoint(self.magnetic_faces(), self.shape)
        return {axis: -self.beta * adj[axis] for axis in AXES}

    def gauss(self, face_flux_density=None):
        out = divergence(self.electric, self.shape)
        if face_flux_density is not None:
            out = out + boundary_source_array(self.shape, face_flux_density)
        return out

    def energy(self):
        kinetic = 0.5 * inner_links(self.electric, self.electric)
        magnetic = 0.5 * self.beta * inner_faces(
            self.magnetic_faces(), self.magnetic_faces()
        )
        return kinetic + magnetic

    def leapfrog(self, dt: float, current=None):
        if dt <= 0:
            raise ValueError("dt must be positive")
        if current is None:
            current = zero_links(self.shape)

        force = self.weak_force()
        for axis in AXES:
            self.electric[axis] += 0.5 * dt * (force[axis] - current[axis])

        for axis in AXES:
            self.links[axis] += dt * self.electric[axis]

        force = self.weak_force()
        for axis in AXES:
            self.electric[axis] += 0.5 * dt * (force[axis] - current[axis])

        self.time += dt


def restrict_full_current_to_open(full_current, shape):
    """Drop wraparound links from a full node-shaped current representation."""
    nx, ny, nz = shape
    return {
        "x": np.asarray(full_current["x"], dtype=float)[: nx - 1, :, :],
        "y": np.asarray(full_current["y"], dtype=float)[:, : ny - 1, :],
        "z": np.asarray(full_current["z"], dtype=float)[:, :, : nz - 1],
    }
