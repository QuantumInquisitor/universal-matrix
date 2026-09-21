"""Single-causal-cone bridge between gauge and content-wave sectors.

The weak U(1) gauge adapter has dimensionless long-wavelength speed

    c_gauge = sqrt(beta)

in lattice-spacing / model-time units.

If the experimental content scalar is required to share the same causal cone,
set

    c_content = c_gauge.

This removes one free propagation-speed parameter.

The module also provides a fractional mismatch diagnostic. The default
observational tolerance is intentionally NOT hard-coded as a theorem; callers
must pass the bound appropriate to the experiment being tested.

This is an experimental consistency bridge, not part of the canonical kernel.
"""

from __future__ import annotations

import math

try:
    from .gauge_dispersion import long_wavelength_speed
except ImportError:
    from gauge_dispersion import long_wavelength_speed


def single_cone_dimensionless_speed(beta: float) -> float:
    if beta <= 0:
        raise ValueError("beta must be positive")
    return long_wavelength_speed(beta)


def physical_causal_speed(
    beta: float,
    lattice_spacing: float,
    model_time_unit: float,
) -> float:
    """Convert the shared dimensionless cone speed to physical units."""
    if lattice_spacing <= 0:
        raise ValueError("lattice_spacing must be positive")
    if model_time_unit <= 0:
        raise ValueError("model_time_unit must be positive")
    return (
        single_cone_dimensionless_speed(beta)
        * lattice_spacing
        / model_time_unit
    )


def fractional_speed_mismatch(
    content_speed: float,
    gauge_speed: float,
) -> float:
    if content_speed <= 0 or gauge_speed <= 0:
        raise ValueError("speeds must be positive")
    return (content_speed - gauge_speed) / gauge_speed


def satisfies_speed_bound(
    content_speed: float,
    gauge_speed: float,
    lower_fractional_bound: float,
    upper_fractional_bound: float,
) -> bool:
    if lower_fractional_bound > upper_fractional_bound:
        raise ValueError("lower bound must not exceed upper bound")
    mismatch = fractional_speed_mismatch(content_speed, gauge_speed)
    return lower_fractional_bound <= mismatch <= upper_fractional_bound
