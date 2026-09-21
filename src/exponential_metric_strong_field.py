"""Strong-field diagnostics of the reciprocity exponential metric.

For the point-source weak potential promoted to all radii,

    psi(r) = mu / r,

the reciprocity metric is

    ds^2 = -exp(-2 mu/r) c^2 dt^2
           + exp(+2 mu/r) [dr^2 + r^2 dOmega^2].

This module derives several exact geometric consequences:
- no finite-r zero of the lapse;
- areal radius R=r*exp(mu/r);
- a minimum areal radius at isotropic r=mu;
- null circular orbit at isotropic r=2mu;
- critical null impact parameter b_c=2e*mu.

These are diagnostics of the effective metric candidate, not claims that
astrophysical black holes are described by this geometry.
"""

from __future__ import annotations

import math


def validate_mu_radius(mu: float, radius: float) -> None:
    if mu <= 0:
        raise ValueError("mu must be positive")
    if radius <= 0:
        raise ValueError("radius must be positive")


def lapse(radius: float, mu: float) -> float:
    validate_mu_radius(mu, radius)
    return math.exp(-mu / radius)


def spatial_scale(radius: float, mu: float) -> float:
    validate_mu_radius(mu, radius)
    return math.exp(mu / radius)


def areal_radius(radius: float, mu: float) -> float:
    """Areal radius sqrt(g_theta_theta)=r exp(mu/r)."""
    return radius * spatial_scale(radius, mu)


def throat_isotropic_radius(mu: float) -> float:
    if mu <= 0:
        raise ValueError("mu must be positive")
    return mu


def throat_areal_radius(mu: float) -> float:
    if mu <= 0:
        raise ValueError("mu must be positive")
    return math.e * mu


def has_finite_radius_horizon(mu: float) -> bool:
    if mu <= 0:
        raise ValueError("mu must be positive")
    return False


def photon_sphere_isotropic_radius(mu: float) -> float:
    """Extremum of b^2=C/A=r^2 exp(4mu/r)."""
    if mu <= 0:
        raise ValueError("mu must be positive")
    return 2.0 * mu


def photon_sphere_areal_radius(mu: float) -> float:
    r = photon_sphere_isotropic_radius(mu)
    return areal_radius(r, mu)


def critical_impact_parameter(mu: float) -> float:
    """b_c=sqrt(C/A)=r exp(2mu/r) at r=2mu."""
    if mu <= 0:
        raise ValueError("mu must be positive")
    return 2.0 * math.e * mu


def schwarzschild_critical_impact_parameter(mu: float) -> float:
    """Reference GR Schwarzschild b_c=3 sqrt(3) mu, with mu=GM/c^2."""
    if mu <= 0:
        raise ValueError("mu must be positive")
    return 3.0 * math.sqrt(3.0) * mu


def shadow_scale_fractional_difference_from_schwarzschild(mu: float) -> float:
    b_exp = critical_impact_parameter(mu)
    b_schw = schwarzschild_critical_impact_parameter(mu)
    return b_exp / b_schw - 1.0


def redshift_factor_to_infinity(radius: float, mu: float) -> float:
    """Frequency at infinity / local static-emitter frequency = lapse."""
    return lapse(radius, mu)
