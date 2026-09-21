"""Open finite-volume polarity source map.

Polarization is stored cell-centered as P_x,P_y,P_z. Interior face values use
arithmetic averages of adjacent cells. At physical boundaries, the cell value
is used as the outward-normal boundary trace.

The bound source is

    rho_pol = -div(P)

with an open finite-volume divergence. For a changing polarization,

    J_pol = dP/dt

and the same divergence operator gives exact discrete continuity.
"""

from __future__ import annotations

import numpy as np

AXES = ("x", "y", "z")


def _as_array_field(polarization):
    return {axis: np.asarray(polarization[axis], dtype=float) for axis in AXES}


def finite_volume_divergence(vector_field):
    """Open-boundary divergence of a cell-centered vector field."""
    v = _as_array_field(vector_field)
    shape = v["x"].shape
    if any(v[a].shape != shape for a in AXES):
        raise ValueError("vector field shape mismatch")
    nx, ny, nz = shape
    out = np.zeros(shape, dtype=float)

    # x-face fluxes, positive outward in +x coordinate direction internally.
    fx = np.empty((nx + 1, ny, nz), dtype=float)
    fx[1:nx] = 0.5 * (v["x"][:-1] + v["x"][1:])
    fx[0] = v["x"][0]
    fx[nx] = v["x"][-1]
    out += fx[1:] - fx[:-1]

    fy = np.empty((nx, ny + 1, nz), dtype=float)
    fy[:, 1:ny] = 0.5 * (v["y"][:, :-1] + v["y"][:, 1:])
    fy[:, 0] = v["y"][:, 0]
    fy[:, ny] = v["y"][:, -1]
    out += fy[:, 1:] - fy[:, :-1]

    fz = np.empty((nx, ny, nz + 1), dtype=float)
    fz[:, :, 1:nz] = 0.5 * (v["z"][:, :, :-1] + v["z"][:, :, 1:])
    fz[:, :, 0] = v["z"][:, :, 0]
    fz[:, :, nz] = v["z"][:, :, -1]
    out += fz[:, :, 1:] - fz[:, :, :-1]

    return out


def induced_charge_density_open(polarization):
    return -finite_volume_divergence(polarization)


def polarization_current_open(old_polarization, new_polarization, dt: float):
    if dt <= 0:
        raise ValueError("dt must be positive")
    old = _as_array_field(old_polarization)
    new = _as_array_field(new_polarization)
    return {axis: (new[axis] - old[axis]) / dt for axis in AXES}


def continuity_residual_open(old_rho, new_rho, current, dt: float):
    if dt <= 0:
        raise ValueError("dt must be positive")
    return (
        (np.asarray(new_rho) - np.asarray(old_rho)) / dt
        + finite_volume_divergence(current)
    )
