"""Weak-field normal-mode dispersion for the Matrix U(1) gauge sector.

For a transverse mode living on inter-layer links and varying around the
36-state routing cycle, the quadratic Hamiltonian gives

    s_ddot(k) = beta * [s(k+1)-2 s(k)+s(k-1)]

with periodic k in Z_36. Plane waves s ~ exp(i(q k - omega t)) satisfy

    omega^2 = 4 beta sin^2(q/2).

Allowed routing momenta are q_m = 2*pi*m/36.

This is an exact lattice result in dimensionless routing/time units. It is not
an SI speed of light until a physical lattice spacing and time unit are fixed.
"""

from __future__ import annotations

import math

try:
    from .gauge_dynamics import ROUTING_PERIOD
except ImportError:
    from gauge_dynamics import ROUTING_PERIOD


def routing_wave_number(mode: int, period: int = ROUTING_PERIOD) -> float:
    if period <= 0:
        raise ValueError("period must be positive")
    return 2.0 * math.pi * (mode % period) / period


def weak_field_angular_frequency(
    mode: int,
    beta: float = 1.0,
    period: int = ROUTING_PERIOD,
) -> float:
    """Exact positive-frequency lattice branch."""
    if beta <= 0:
        raise ValueError("beta must be positive")
    q = routing_wave_number(mode, period)
    return 2.0 * math.sqrt(beta) * abs(math.sin(0.5 * q))


def weak_field_frequency_squared(
    mode: int,
    beta: float = 1.0,
    period: int = ROUTING_PERIOD,
) -> float:
    omega = weak_field_angular_frequency(mode, beta, period)
    return omega * omega


def weak_field_group_velocity(
    mode: int,
    beta: float = 1.0,
    period: int = ROUTING_PERIOD,
) -> float:
    """d omega / d q on the principal branch 0 <= q <= pi.

    Modes above Nyquist are represented by their negative-wave-number partner.
    """
    if beta <= 0:
        raise ValueError("beta must be positive")
    m = mode % period
    if m > period // 2:
        m -= period
    q = 2.0 * math.pi * m / period
    sign = 1.0 if q >= 0 else -1.0
    return math.sqrt(beta) * math.cos(0.5 * abs(q)) * sign


def long_wavelength_speed(beta: float = 1.0) -> float:
    """Limit omega/|q| as q->0 in lattice units."""
    if beta <= 0:
        raise ValueError("beta must be positive")
    return math.sqrt(beta)


def phase_velocity(
    mode: int,
    beta: float = 1.0,
    period: int = ROUTING_PERIOD,
) -> float:
    """omega/|q| for nonzero mode."""
    m = mode % period
    if m > period // 2:
        m -= period
    if m == 0:
        return long_wavelength_speed(beta)
    q = abs(2.0 * math.pi * m / period)
    return weak_field_angular_frequency(m, beta, period) / q


def dimensional_speed(
    beta: float,
    lattice_spacing: float,
    time_unit: float,
) -> float:
    """Convert long-wave lattice speed to physical units.

    c_phys = sqrt(beta) * a / tau.

    The function makes the calibration dependence explicit. Neither a nor tau
    is fixed by the canonical v0.4 kernel.
    """
    if lattice_spacing <= 0 or time_unit <= 0:
        raise ValueError("lattice_spacing and time_unit must be positive")
    return long_wavelength_speed(beta) * lattice_spacing / time_unit
