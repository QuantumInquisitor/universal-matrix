"""Effective inverse-square coupling implied by the content field + reciprocity metric.

Point-source content potential:
    chi(r) = kappa_C * Q_C / (4*pi*r)

Dimensionless clock/geometry potential:
    psi = g_chi * chi

If source content charge is proportional to source mass,
    Q_C = q_M * M,

then
    psi(r) = mu/r

with
    mu = g_chi * kappa_C * q_M * M / (4*pi).

The weak reciprocity-metric acceleration is
    a = c_*^2 * grad(psi),

so the radial magnitude becomes
    |a| = G_eff * M / r^2

with
    G_eff = c_*^2 * g_chi * kappa_C * q_M / (4*pi).

This module exposes that factorization. It does not derive Newton's constant.
A successful theory must derive or independently determine the constituent
couplings without fitting the same gravity measurement multiple times.
"""

from __future__ import annotations

import math


def effective_newton_coupling(
    causal_speed: float,
    clock_coupling: float,
    field_coupling: float,
    content_charge_per_mass: float,
) -> float:
    if causal_speed <= 0:
        raise ValueError("causal_speed must be positive")
    if clock_coupling < 0:
        raise ValueError("clock_coupling must be non-negative")
    if field_coupling < 0:
        raise ValueError("field_coupling must be non-negative")
    if content_charge_per_mass < 0:
        raise ValueError("content_charge_per_mass must be non-negative")

    return (
        causal_speed**2
        * clock_coupling
        * field_coupling
        * content_charge_per_mass
        / (4.0 * math.pi)
    )


def point_source_mu(
    source_mass: float,
    clock_coupling: float,
    field_coupling: float,
    content_charge_per_mass: float,
) -> float:
    if source_mass < 0:
        raise ValueError("source_mass must be non-negative")
    if clock_coupling < 0 or field_coupling < 0:
        raise ValueError("couplings must be non-negative")
    if content_charge_per_mass < 0:
        raise ValueError("content_charge_per_mass must be non-negative")

    return (
        clock_coupling
        * field_coupling
        * content_charge_per_mass
        * source_mass
        / (4.0 * math.pi)
    )


def inverse_square_acceleration_magnitude(
    source_mass: float,
    radius: float,
    causal_speed: float,
    clock_coupling: float,
    field_coupling: float,
    content_charge_per_mass: float,
) -> float:
    if radius <= 0:
        raise ValueError("radius must be positive")
    g_eff = effective_newton_coupling(
        causal_speed,
        clock_coupling,
        field_coupling,
        content_charge_per_mass,
    )
    return g_eff * source_mass / (radius * radius)


def required_combined_coupling(
    target_newton_constant: float,
    causal_speed: float,
    content_charge_per_mass: float,
) -> float:
    """Return g_chi*kappa_C required for a chosen G and q_M.

    This is a calibration diagnostic, not a derivation.
    """
    if target_newton_constant < 0:
        raise ValueError("target_newton_constant must be non-negative")
    if causal_speed <= 0:
        raise ValueError("causal_speed must be positive")
    if content_charge_per_mass <= 0:
        raise ValueError("content_charge_per_mass must be positive")

    return (
        4.0
        * math.pi
        * target_newton_constant
        / (causal_speed**2 * content_charge_per_mass)
    )


def source_equivalence_ratio(
    charge_per_mass_a: float,
    charge_per_mass_b: float,
) -> float:
    """Relative source-strength mismatch for two compositions."""
    if charge_per_mass_a <= 0 or charge_per_mass_b <= 0:
        raise ValueError("charge-per-mass values must be positive")
    mean = 0.5 * (charge_per_mass_a + charge_per_mass_b)
    return (charge_per_mass_a - charge_per_mass_b) / mean
