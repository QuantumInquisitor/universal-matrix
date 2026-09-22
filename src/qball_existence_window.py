"""Analytic necessary existence window for time-harmonic charged matter lumps.

For the repository matter potential

    U(rho) = m2*rho + lambda4*rho^2 + lambda6*rho^3,

a time-harmonic ansatz

    Phi(t,r) = exp(i omega t) f(r)

can have a localized branch approaching f=0 only if the effective radial
potential has a nonzero field region below the free quadratic slope.

A standard necessary condition in the repository normalization is

    min_{rho>0} U(rho)/rho < omega^2 < m2.

Since

    U(rho)/rho = m2 + lambda4*rho + lambda6*rho^2,

the minimum is analytic.

This is an existence-window diagnostic only.  It does not prove convergence,
nonlinear stability, E/Q stability, or particle identity.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from .localized_matter_variational import MatterPotential


@dataclass(frozen=True)
class QBallExistenceWindow:
    minimum_ratio: float
    minimizing_density: float | None
    omega_squared_lower: float
    omega_squared_upper: float
    has_open_window: bool

    @property
    def omega_lower(self) -> float:
        return math.sqrt(max(0.0, self.omega_squared_lower))

    @property
    def omega_upper(self) -> float:
        return math.sqrt(self.omega_squared_upper)

    def allows_omega(self, omega: float) -> bool:
        if not math.isfinite(omega) or omega <= 0:
            return False
        value = omega * omega
        return (
            self.has_open_window
            and value > self.omega_squared_lower
            and value < self.omega_squared_upper
        )


def potential_ratio(
    density: float,
    potential: MatterPotential,
) -> float:
    """Return U(rho)/rho for rho>0."""
    if not math.isfinite(density) or density <= 0:
        raise ValueError("density must be finite and positive")
    return (
        potential.mass2
        + potential.lambda4 * density
        + potential.lambda6 * density * density
    )


def qball_existence_window(
    potential: MatterPotential,
) -> QBallExistenceWindow:
    """Return the analytic necessary omega^2 window for a zero-vacuum Q-ball."""
    if potential.lambda6 > 0 and potential.lambda4 < 0:
        rho_star = -potential.lambda4 / (2.0 * potential.lambda6)
        minimum = potential_ratio(rho_star, potential)
        minimizing_density: float | None = rho_star
    else:
        # The infimum over positive density lies at rho -> 0+.
        minimum = potential.mass2
        minimizing_density = None

    lower = max(0.0, minimum)
    upper = potential.mass2
    has_window = minimum < upper and lower < upper

    return QBallExistenceWindow(
        minimum_ratio=float(minimum),
        minimizing_density=(
            None if minimizing_density is None else float(minimizing_density)
        ),
        omega_squared_lower=float(lower),
        omega_squared_upper=float(upper),
        has_open_window=bool(has_window),
    )


def asymptotic_decay_rate(
    omega: float,
    potential: MatterPotential,
) -> float:
    """Return sqrt(m2-omega^2) for a localized zero-vacuum tail."""
    if not math.isfinite(omega) or omega <= 0:
        raise ValueError("omega must be finite and positive")
    value = potential.mass2 - omega * omega
    if value <= 0:
        raise ValueError("localized exponential tail requires omega^2 < mass2")
    return math.sqrt(value)


def effective_radial_density(
    density: float,
    omega: float,
    potential: MatterPotential,
) -> float:
    """Return U(rho)-omega^2*rho, whose negative region enables a bounce."""
    if not math.isfinite(density) or density < 0:
        raise ValueError("density must be finite and non-negative")
    if not math.isfinite(omega) or omega <= 0:
        raise ValueError("omega must be finite and positive")
    rho = density
    return (
        potential.mass2 * rho
        + potential.lambda4 * rho**2
        + potential.lambda6 * rho**3
        - omega * omega * rho
    )
