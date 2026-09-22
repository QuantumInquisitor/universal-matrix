"""Linear phase and radial amplitude modes of the existing complex matter field.

The repository's classical matter sector uses

    U(rho) = m2*rho + lambda4*rho^2 + lambda6*rho^3,
    rho = |Phi|^2,

and equation

    Phi_tt = Delta_A Phi - U'(rho) Phi.

For a uniform zero-link nonzero stationary background

    Phi_0 = R,
    rho_0 = R^2 > 0,
    U'(rho_0) = 0,

small Cartesian perturbations split into:

    radial:     h = Re(delta Phi)
    tangential: y = Im(delta Phi)

with exact lattice dispersions

    omega_phase^2(k)  = L(k)
    omega_radial^2(k) = L(k) + 2 rho_0 U''(rho_0)

where

    L(k) = 4 sum_a sin^2(k_a / 2).

Thus a stable nonzero vacuum supplies a genuinely independent radial branch.
The phase branch is the fixed-amplitude rotor limit.

This module derives those relations from the existing MatterPotential
normalization. It does not introduce a new matter theory.
"""

from __future__ import annotations

import math

import numpy as np

from .localized_matter_variational import MatterPotential


def density_potential_derivative(
    density: float,
    potential: MatterPotential,
) -> float:
    """Return dU/drho for U=m2*rho+lambda4*rho^2+lambda6*rho^3."""
    if not math.isfinite(density) or density < 0:
        raise ValueError("density must be finite and non-negative")
    return (
        potential.mass2
        + 2.0 * potential.lambda4 * density
        + 3.0 * potential.lambda6 * density * density
    )


def density_potential_second_derivative(
    density: float,
    potential: MatterPotential,
) -> float:
    """Return d^2U/drho^2."""
    if not math.isfinite(density) or density < 0:
        raise ValueError("density must be finite and non-negative")
    return 2.0 * potential.lambda4 + 6.0 * potential.lambda6 * density


def nonzero_stationary_densities(
    potential: MatterPotential,
    *,
    tolerance: float = 1e-12,
) -> tuple[float, ...]:
    """Return positive real roots of U'(rho)=0 in ascending order."""
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be finite and non-negative")

    a = 3.0 * potential.lambda6
    b = 2.0 * potential.lambda4
    c = potential.mass2

    roots: list[float] = []
    if abs(a) <= tolerance:
        if abs(b) <= tolerance:
            return ()
        root = -c / b
        if root > tolerance:
            roots.append(float(root))
    else:
        disc = b * b - 4.0 * a * c
        if disc < -tolerance:
            return ()
        disc = max(disc, 0.0)
        s = math.sqrt(disc)
        for root in ((-b - s) / (2.0 * a), (-b + s) / (2.0 * a)):
            if root > tolerance and not any(
                math.isclose(root, existing, rel_tol=0.0, abs_tol=tolerance)
                for existing in roots
            ):
                roots.append(float(root))

    return tuple(sorted(roots))


def radial_mass_squared(
    density: float,
    potential: MatterPotential,
    *,
    stationary_tolerance: float = 1e-10,
) -> float:
    """Return the radial k=0 omega^2 at a nonzero stationary density."""
    if not math.isfinite(density) or density <= 0:
        raise ValueError("density must be finite and positive")
    residual = density_potential_derivative(density, potential)
    if abs(residual) > stationary_tolerance:
        raise ValueError("density is not a stationary nonzero matter background")
    return (
        2.0
        * density
        * density_potential_second_derivative(density, potential)
    )


def stationary_density_summary(
    density: float,
    potential: MatterPotential,
    *,
    tolerance: float = 1e-10,
) -> dict[str, float | str | bool]:
    """Classify a nonzero stationary density by its radial curvature."""
    mass2 = radial_mass_squared(
        density,
        potential,
        stationary_tolerance=tolerance,
    )
    if mass2 > tolerance:
        stability = "stable"
    elif mass2 < -tolerance:
        stability = "unstable"
    else:
        stability = "marginal"

    return {
        "density": float(density),
        "amplitude": math.sqrt(density),
        "radial_mass_squared": float(mass2),
        "radial_gap": math.sqrt(mass2) if mass2 > 0 else 0.0,
        "stability": stability,
        "stable": stability == "stable",
    }


def lattice_laplacian_eigenvalue(
    wavevector: tuple[float, float, float] | np.ndarray,
) -> float:
    """Return L(k)=4 sum sin^2(k_a/2) for the unit cubic lattice."""
    k = np.asarray(wavevector, dtype=float)
    if k.shape != (3,) or not np.all(np.isfinite(k)):
        raise ValueError("wavevector must contain three finite components")
    return float(4.0 * np.sum(np.sin(0.5 * k) ** 2))


def matter_linear_branches(
    wavevector: tuple[float, float, float] | np.ndarray,
    density: float,
    potential: MatterPotential,
) -> dict[str, float]:
    """Return phase and radial omega^2 for a stationary nonzero background."""
    lap = lattice_laplacian_eigenvalue(wavevector)
    radial_gap2 = radial_mass_squared(density, potential)
    return {
        "phase_omega_squared": lap,
        "radial_omega_squared": lap + radial_gap2,
        "radial_gap_squared": radial_gap2,
    }


def fixed_amplitude_rotor_parameters(density: float) -> dict[str, float]:
    """Map the phase-only complex scalar sector to the rotor normalization.

    For Phi=R exp(i theta) with rho=R^2,

        |dot Phi|^2 = rho * dot(theta)^2

    and each unit-coefficient spatial link contributes

        2 rho [1-cos(Delta)].

    Matching H_rotor = p_theta^2/(2 I) + kappa[1-cos(Delta)] gives

        I = 2 rho,
        kappa = 2 rho,

    hence c_lat^2=kappa/I=1 in the scalar field's native lattice units.
    """
    if not math.isfinite(density) or density <= 0:
        raise ValueError("density must be finite and positive")
    inertia = 2.0 * density
    coupling = 2.0 * density
    return {
        "inertia": inertia,
        "coupling": coupling,
        "lattice_wave_speed_squared": coupling / inertia,
        "lattice_wave_speed": 1.0,
    }
