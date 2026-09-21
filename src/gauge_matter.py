"""Gauge-covariant source/current sector for the experimental 3D Matrix field.

Matter lives on lattice sites with:
    amplitude >= 0
    polarity in {-1,+1}
    phase

The oriented link current is

    J_i(x) = kappa * sqrt(A_x A_y) * sigma_x sigma_y
             * sin(phi_y - phi_x + theta_i(x))

for y=x+e_i.

The phase combination is locally U(1)-gauge invariant. Reversing link
orientation reverses the current. Charge density is evolved by the exact
finite-volume continuity equation

    rho_dot = - div J.

This is an experimental matter/gauge adapter, not an established microscopic
law of electromagnetism.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

try:
    from .gauge_3d import AXES, U13DHamiltonian, _zeros3, _get, _set, _shift
    from .gauge_dynamics import gauge_covariant_phase_difference
except ImportError:
    from gauge_3d import AXES, U13DHamiltonian, _zeros3, _get, _set, _shift
    from gauge_dynamics import gauge_covariant_phase_difference


@dataclass
class MatterSite:
    amplitude: float
    polarity: int
    phase: float

    def __post_init__(self) -> None:
        if self.amplitude < 0:
            raise ValueError("amplitude must be non-negative")
        if self.polarity not in (-1, 1):
            raise ValueError("polarity must be -1 or +1")


def uniform_matter(shape, amplitude=1.0, polarity=1, phase=0.0):
    nx, ny, nz = shape
    return [
        [
            [MatterSite(amplitude, polarity, phase) for _ in range(nz)]
            for _ in range(ny)
        ]
        for _ in range(nx)
    ]


def site_gauge_transform(matter, alpha):
    """phi(x) -> phi(x)+alpha(x), preserving amplitudes and polarities."""
    nx = len(matter)
    ny = len(matter[0])
    nz = len(matter[0][0])
    out = []
    for i in range(nx):
        plane = []
        for j in range(ny):
            row = []
            for k in range(nz):
                s = matter[i][j][k]
                row.append(MatterSite(s.amplitude, s.polarity, s.phase + alpha[i][j][k]))
            plane.append(row)
        out.append(plane)
    return out


def link_current(
    source: MatterSite,
    target: MatterSite,
    link_phase: float,
    coupling: float,
) -> float:
    """Gauge-invariant oriented matter current."""
    if coupling < 0:
        raise ValueError("coupling must be non-negative")
    if source.amplitude == 0 or target.amplitude == 0:
        return 0.0
    delta = gauge_covariant_phase_difference(
        source.phase,
        target.phase,
        link_phase,
    )
    return (
        coupling
        * math.sqrt(source.amplitude * target.amplitude)
        * source.polarity
        * target.polarity
        * math.sin(delta)
    )


def current_field(matter, field, coupling: float):
    """Return oriented J_x,J_y,J_z on the same links as the gauge field."""
    shape = field.shape
    out = {axis: _zeros3(shape) for axis in AXES}
    nx, ny, nz = shape
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                idx = (i, j, k)
                source = matter[i][j][k]
                for axis in AXES:
                    xp = _shift(idx, axis, 1, shape)
                    target = matter[xp[0]][xp[1]][xp[2]]
                    value = link_current(
                        source,
                        target,
                        _get(field.links[axis], idx),
                        coupling,
                    )
                    _set(out[axis], idx, value)
    return out


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


def continuity_step(charge_density, currents, shape, dt: float):
    """rho <- rho - dt div J, exactly conserving total periodic charge."""
    if dt <= 0:
        raise ValueError("dt must be positive")
    divj = current_divergence(currents, shape)
    nx, ny, nz = shape
    out = _zeros3(shape)
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                out[i][j][k] = charge_density[i][j][k] - dt * divj[i][j][k]
    return out


def total_charge(charge_density) -> float:
    return sum(v for plane in charge_density for row in plane for v in row)


def gauss_residual(state: U13DHamiltonian, charge_density):
    div_e = state.gauss()
    nx, ny, nz = state.field.shape
    out = _zeros3(state.field.shape)
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                out[i][j][k] = div_e[i][j][k] - charge_density[i][j][k]
    return out


def max_abs(field) -> float:
    return max(abs(v) for plane in field for row in plane for v in row)


def sourced_weak_step(
    state: U13DHamiltonian,
    charge_density,
    currents,
    dt: float,
):
    """Leapfrog-like weak-field step with external conserved current.

    E_dot = weak_force - J
    rho_dot = -div J

    With a current held constant across the step, this preserves div(E)-rho
    up to integration/roundoff error because div(weak_force)=0 identically.
    """
    if dt <= 0:
        raise ValueError("dt must be positive")

    force = state.weak_force()
    shape = state.field.shape
    nx, ny, nz = shape

    # Half kick with source.
    for axis in AXES:
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    idx = (i, j, k)
                    e = _get(state.electric[axis], idx)
                    rhs = _get(force[axis], idx) - _get(currents[axis], idx)
                    _set(state.electric[axis], idx, e + 0.5 * dt * rhs)

    # Drift gauge links.
    from .gauge_dynamics import wrap_angle
    for axis in AXES:
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    idx = (i, j, k)
                    _set(
                        state.field.links[axis],
                        idx,
                        wrap_angle(
                            _get(state.field.links[axis], idx)
                            + dt * _get(state.electric[axis], idx)
                        ),
                    )

    # Advance charge with the same current.
    new_rho = continuity_step(charge_density, currents, shape, dt)

    # Second half kick with refreshed gauge force, same external current.
    force = state.weak_force()
    for axis in AXES:
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    idx = (i, j, k)
                    e = _get(state.electric[axis], idx)
                    rhs = _get(force[axis], idx) - _get(currents[axis], idx)
                    _set(state.electric[axis], idx, e + 0.5 * dt * rhs)

    state.time += dt
    return new_rho
