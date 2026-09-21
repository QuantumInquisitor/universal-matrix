"""Unified source channels for the experimental Universal Matrix gauge engine.

This module combines four distinct source mechanisms without conflating them:

1. polarization-induced electric charge:
       rho_pol = -div(P)

2. free electric charge:
       rho_free
   evolved by its own conserved current

3. boundary electric flux:
       changes total internal electric charge according to net boundary inflow

4. compact-U(1) topological magnetic charge:
       integer monopole-like defect from wrapped plaquette flux on a cube

The topological channel is magnetic/dual. It is NOT silently added to ordinary
electric charge density.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

try:
    from .gauge_3d import AXES, U13DField, _zeros3, _get, _set, _shift
except ImportError:
    from gauge_3d import AXES, U13DField, _zeros3, _get, _set, _shift


def _shape_of_scalar(field):
    return (len(field), len(field[0]), len(field[0][0]))


def add_scalar_fields(*fields):
    if not fields:
        raise ValueError("at least one scalar field is required")
    shape = _shape_of_scalar(fields[0])
    out = _zeros3(shape)
    for field in fields:
        if _shape_of_scalar(field) != shape:
            raise ValueError("field shape mismatch")
        for i in range(shape[0]):
            for j in range(shape[1]):
                for k in range(shape[2]):
                    out[i][j][k] += field[i][j][k]
    return out


def total_scalar(field) -> float:
    return sum(v for plane in field for row in plane for v in row)


def current_divergence(currents, shape):
    out = _zeros3(shape)
    nx, ny, nz = shape
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                idx = (i, j, k)
                value = 0.0
                for axis in AXES:
                    xm = _shift(idx, axis, -1, shape)
                    value += _get(currents[axis], idx) - _get(currents[axis], xm)
                _set(out, idx, value)
    return out


@dataclass
class FreeChargeSector:
    """Explicit free electric charge plus a conserved lattice current."""

    rho: list[list[list[float]]]

    def evolve(self, currents, dt: float):
        if dt <= 0:
            raise ValueError("dt must be positive")
        shape = _shape_of_scalar(self.rho)
        divj = current_divergence(currents, shape)
        out = _zeros3(shape)
        for i in range(shape[0]):
            for j in range(shape[1]):
                for k in range(shape[2]):
                    out[i][j][k] = self.rho[i][j][k] - dt * divj[i][j][k]
        self.rho = out
        return self.rho


@dataclass(frozen=True)
class BoundaryFlux:
    """Net electric charge entering the finite domain through six faces.

    Positive values mean inward electric-charge flux.
    """

    x_pos: float = 0.0
    x_neg: float = 0.0
    y_pos: float = 0.0
    y_neg: float = 0.0
    z_pos: float = 0.0
    z_neg: float = 0.0

    def net_inflow_rate(self) -> float:
        return (
            self.x_pos + self.x_neg
            + self.y_pos + self.y_neg
            + self.z_pos + self.z_neg
        )

    def as_dict(self) -> dict[str, float]:
        return {
            "x_pos": self.x_pos,
            "x_neg": self.x_neg,
            "y_pos": self.y_pos,
            "y_neg": self.y_neg,
            "z_pos": self.z_pos,
            "z_neg": self.z_neg,
        }


def apply_boundary_flux(
    rho,
    boundary_flux: BoundaryFlux,
    dt: float,
):
    """Inject/remove free charge through the six external boundary faces.

    The net injected charge is dt * sum(face inflow rates). To keep the map
    explicit and symmetric, each face contribution is distributed uniformly
    over the corresponding face cells.
    """
    if dt <= 0:
        raise ValueError("dt must be positive")
    shape = _shape_of_scalar(rho)
    nx, ny, nz = shape
    out = [[row[:] for row in plane] for plane in rho]

    def add_face(axis, side, rate):
        if rate == 0.0:
            return
        if axis == 0:
            i = nx - 1 if side > 0 else 0
            amount = dt * rate / (ny * nz)
            for j in range(ny):
                for k in range(nz):
                    out[i][j][k] += amount
        elif axis == 1:
            j = ny - 1 if side > 0 else 0
            amount = dt * rate / (nx * nz)
            for i in range(nx):
                for k in range(nz):
                    out[i][j][k] += amount
        else:
            k = nz - 1 if side > 0 else 0
            amount = dt * rate / (nx * ny)
            for i in range(nx):
                for j in range(ny):
                    out[i][j][k] += amount

    add_face(0, +1, boundary_flux.x_pos)
    add_face(0, -1, boundary_flux.x_neg)
    add_face(1, +1, boundary_flux.y_pos)
    add_face(1, -1, boundary_flux.y_neg)
    add_face(2, +1, boundary_flux.z_pos)
    add_face(2, -1, boundary_flux.z_neg)
    return out


def electric_charge_balance(
    old_total: float,
    new_total: float,
    boundary_flux: BoundaryFlux,
    dt: float,
) -> float:
    """Residual of Delta Q - dt * boundary inflow."""
    return (new_total - old_total) - dt * boundary_flux.net_inflow_rate()


def _principal_angle(angle: float) -> float:
    """Principal compact angle in (-pi, pi]."""
    wrapped = (angle + math.pi) % (2.0 * math.pi) - math.pi
    if wrapped <= -math.pi:
        return math.pi
    return wrapped


def _raw_plaquette(
    field: U13DField,
    plane: tuple[str, str],
    idx: tuple[int, int, int],
) -> float:
    """Unwrapped oriented plaquette sum before principal-angle reduction."""
    a, b = plane
    xp_a = _shift(idx, a, 1, field.shape)
    xp_b = _shift(idx, b, 1, field.shape)
    return (
        _get(field.links[a], idx)
        + _get(field.links[b], xp_a)
        - _get(field.links[a], xp_b)
        - _get(field.links[b], idx)
    )


def plaquette_winding_integer(
    field: U13DField,
    plane: tuple[str, str],
    idx: tuple[int, int, int],
) -> int:
    """Integer compact wrapping n where raw F = principal(F) + 2*pi*n."""
    raw = _raw_plaquette(field, plane, idx)
    principal = _principal_angle(raw)
    return int(round((raw - principal) / (2.0 * math.pi)))


def magnetic_monopole_charge(
    field: U13DField,
    cube_origin: tuple[int, int, int],
) -> int:
    """DeGrand-Toussaint-style compact U(1) cube charge.

    Sum outward integer plaquette windings across the six cube faces.
    This is a topological magnetic charge candidate, not electric charge.
    """
    x, y, z = cube_origin
    shape = field.shape
    idx = (x % shape[0], y % shape[1], z % shape[2])

    # Opposite outward faces. Orientation conventions cancel in the difference.
    nx0 = plaquette_winding_integer(field, ("y", "z"), idx)
    nx1 = plaquette_winding_integer(
        field, ("y", "z"), _shift(idx, "x", 1, shape)
    )

    ny0 = plaquette_winding_integer(field, ("z", "x"), idx)
    ny1 = plaquette_winding_integer(
        field, ("z", "x"), _shift(idx, "y", 1, shape)
    )

    nz0 = plaquette_winding_integer(field, ("x", "y"), idx)
    nz1 = plaquette_winding_integer(
        field, ("x", "y"), _shift(idx, "z", 1, shape)
    )

    return (nx1 - nx0) + (ny1 - ny0) + (nz1 - nz0)


def magnetic_monopole_density(field: U13DField):
    """Integer topological magnetic charge on every elementary cube."""
    shape = field.shape
    out = [[[0 for _ in range(shape[2])] for _ in range(shape[1])] for _ in range(shape[0])]
    for i in range(shape[0]):
        for j in range(shape[1]):
            for k in range(shape[2]):
                out[i][j][k] = magnetic_monopole_charge(field, (i, j, k))
    return out


@dataclass
class UnifiedElectricSource:
    """Bookkeeping container for electric source channels."""

    polarization_charge: list[list[list[float]]]
    free_charge: list[list[list[float]]]

    def total(self):
        return add_scalar_fields(self.polarization_charge, self.free_charge)

    def total_charge(self) -> float:
        return total_scalar(self.total())
