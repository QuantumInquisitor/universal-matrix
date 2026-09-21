"""Variational search for localized classical U(1) matter lumps.

Use a time-harmonic classical complex scalar ansatz

    Phi(t,r) = exp(i omega t) f(r)

with Gaussian radial profile

    f(r) = A exp(-r^2/(2 R^2)).

Matter potential:

    U(f) = m2 f^2 + lambda4 f^4 + lambda6 f^6

with lambda6 > 0 for large-amplitude boundedness.

For the Gaussian ansatz in 3D:

    I2   = int f^2 d^3x
         = A^2 pi^(3/2) R^3

    Igrad = int |grad f|^2 d^3x
          = (3/2) A^2 pi^(3/2) R

    I4   = int f^4 d^3x
         = A^4 pi^(3/2) R^3 / 2^(3/2)

    I6   = int f^6 d^3x
         = A^6 pi^(3/2) R^3 / 3^(3/2).

With the classical normalization used here:

    Q = 2 omega I2

and

    E = omega^2 I2 + Igrad + m2 I2
        + lambda4 I4 + lambda6 I6.

A useful classical localization diagnostic is

    E/Q < m_free

with

    m_free = sqrt(m2).

If satisfied, the configuration lies below the free-particle energy per unit
U(1) charge in this normalization.

This is only a variational candidate test. It is not proof of nonlinear
stability, quantization, or particle identity.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from collections.abc import Iterable


@dataclass(frozen=True)
class MatterPotential:
    mass2: float = 1.0
    lambda4: float = -2.0
    lambda6: float = 1.0

    def __post_init__(self) -> None:
        if self.mass2 <= 0:
            raise ValueError("mass2 must be positive")
        if self.lambda6 <= 0:
            raise ValueError("lambda6 must be positive")

    @property
    def free_mass(self) -> float:
        return math.sqrt(self.mass2)


@dataclass(frozen=True)
class GaussianMatterCandidate:
    amplitude: float
    radius: float
    omega: float
    potential: MatterPotential = MatterPotential()

    def __post_init__(self) -> None:
        if self.amplitude <= 0:
            raise ValueError("amplitude must be positive")
        if self.radius <= 0:
            raise ValueError("radius must be positive")
        if self.omega <= 0:
            raise ValueError("omega must be positive")

    @property
    def i2(self) -> float:
        return (
            self.amplitude**2
            * math.pi**1.5
            * self.radius**3
        )

    @property
    def gradient_integral(self) -> float:
        return (
            1.5
            * self.amplitude**2
            * math.pi**1.5
            * self.radius
        )

    @property
    def i4(self) -> float:
        return (
            self.amplitude**4
            * math.pi**1.5
            * self.radius**3
            / (2.0**1.5)
        )

    @property
    def i6(self) -> float:
        return (
            self.amplitude**6
            * math.pi**1.5
            * self.radius**3
            / (3.0**1.5)
        )

    @property
    def charge(self) -> float:
        return 2.0 * self.omega * self.i2

    @property
    def energy(self) -> float:
        p = self.potential
        return (
            self.omega**2 * self.i2
            + self.gradient_integral
            + p.mass2 * self.i2
            + p.lambda4 * self.i4
            + p.lambda6 * self.i6
        )

    @property
    def energy_per_charge(self) -> float:
        return self.energy / self.charge

    @property
    def below_free_mass_threshold(self) -> bool:
        return self.energy_per_charge < self.potential.free_mass

    def snapshot(self) -> dict[str, float | bool | str]:
        return {
            "amplitude": self.amplitude,
            "radius": self.radius,
            "omega": self.omega,
            "charge": self.charge,
            "energy": self.energy,
            "energy_per_charge": self.energy_per_charge,
            "free_mass": self.potential.free_mass,
            "below_free_mass_threshold": self.below_free_mass_threshold,
            "model_status": "classical_variational_localized_matter_candidate",
        }


def scan_gaussian_candidates(
    amplitudes: Iterable[float],
    radii: Iterable[float],
    omegas: Iterable[float],
    potential: MatterPotential = MatterPotential(),
) -> GaussianMatterCandidate:
    best: GaussianMatterCandidate | None = None
    for amplitude in amplitudes:
        for radius in radii:
            for omega in omegas:
                candidate = GaussianMatterCandidate(
                    amplitude=float(amplitude),
                    radius=float(radius),
                    omega=float(omega),
                    potential=potential,
                )
                if best is None or (
                    candidate.energy_per_charge
                    < best.energy_per_charge
                ):
                    best = candidate

    if best is None:
        raise ValueError("scan ranges must be non-empty")
    return best
