"""Polarity-to-source map via a lattice polarization field.

This module avoids identifying signed charge directly with sigma*A, which would
generally fail conservation under amplitude exchange between opposite
polarities.

Instead define a polarization-like vector field

    P(x) = A(x) * sigma(x) * u(x)

where u(x) is one of the canonical axis directions x,y,z and sigma supplies
the +/- orientation. The induced source is the lattice bound-charge analogue

    rho_P = - div P.

If P changes in time, define the associated current

    J_P = dP/dt.

Then

    d rho_P/dt + div J_P = 0

holds identically by construction.

This is an experimental physical mapping, not yet a claim that Matrix polarity
is measured electric polarization.
"""

from __future__ import annotations

from dataclasses import dataclass

try:
    from .gauge_3d import AXES, _zeros3, _get, _set, _shift
except ImportError:
    from gauge_3d import AXES, _zeros3, _get, _set, _shift


@dataclass
class PolaritySourceSite:
    amplitude: float
    polarity: int
    axis: str

    def __post_init__(self) -> None:
        if self.amplitude < 0:
            raise ValueError("amplitude must be non-negative")
        if self.polarity not in (-1, 1):
            raise ValueError("polarity must be -1 or +1")
        if self.axis not in AXES:
            raise ValueError("axis must be x, y, or z")


def polarization_field(sites):
    """Convert site amplitude/polarity/axis into P_x,P_y,P_z."""
    nx = len(sites)
    ny = len(sites[0])
    nz = len(sites[0][0])
    shape = (nx, ny, nz)
    out = {axis: _zeros3(shape) for axis in AXES}
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                site = sites[i][j][k]
                out[site.axis][i][j][k] = site.amplitude * site.polarity
    return out


def polarization_divergence(polarization, shape):
    """Backward-difference lattice divergence."""
    out = _zeros3(shape)
    nx, ny, nz = shape
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                idx = (i, j, k)
                value = 0.0
                for axis in AXES:
                    xm = _shift(idx, axis, -1, shape)
                    value += _get(polarization[axis], idx) - _get(
                        polarization[axis], xm
                    )
                _set(out, idx, value)
    return out


def induced_charge_density(polarization, shape):
    """rho = -div(P). Total periodic charge is identically zero."""
    divp = polarization_divergence(polarization, shape)
    nx, ny, nz = shape
    rho = _zeros3(shape)
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                rho[i][j][k] = -divp[i][j][k]
    return rho


def polarization_current(old_polarization, new_polarization, dt: float, shape):
    """J = (P_new-P_old)/dt."""
    if dt <= 0:
        raise ValueError("dt must be positive")
    out = {axis: _zeros3(shape) for axis in AXES}
    nx, ny, nz = shape
    for axis in AXES:
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    out[axis][i][j][k] = (
                        new_polarization[axis][i][j][k]
                        - old_polarization[axis][i][j][k]
                    ) / dt
    return out


def continuity_residual(old_rho, new_rho, current, dt: float, shape):
    """(rho_new-rho_old)/dt + div(J). Should vanish identically."""
    if dt <= 0:
        raise ValueError("dt must be positive")
    divj = polarization_divergence(current, shape)
    nx, ny, nz = shape
    out = _zeros3(shape)
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                out[i][j][k] = (
                    (new_rho[i][j][k] - old_rho[i][j][k]) / dt
                    + divj[i][j][k]
                )
    return out


def total_charge(rho) -> float:
    return sum(v for plane in rho for row in plane for v in row)


def max_abs(field) -> float:
    return max(abs(v) for plane in field for row in plane for v in row)
