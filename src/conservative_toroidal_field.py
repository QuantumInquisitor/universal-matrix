"""Compact, divergence-free three-dimensional toroidal content-current candidate.

This is a prescribed kinematic field with explicit cut-flux normalization.
It supplies neither a force law nor an identification of content with energy,
charge, or any measured quantity. Legacy resonance/winding modules are separate.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


@dataclass(frozen=True)
class ToroidalContentCurrent:
    major_radius: float = 2.0
    minor_radius: float = 0.5
    poloidal_flux: float = 1.0
    toroidal_flux: float = 1.0

    def __post_init__(self):
        for name in ("major_radius", "minor_radius", "poloidal_flux", "toroidal_flux"):
            object.__setattr__(self, name, _finite(getattr(self, name), name))
        if not 0 < self.minor_radius < self.major_radius:
            raise ValueError("require 0 < minor radius < major radius")
        _finite(self.major_radius + self.minor_radius, "outer radius")
        area = _finite(math.pi * self.minor_radius * self.minor_radius, "cross-section area")
        if area == 0:
            raise ValueError("cross-section area is numerically unresolved")
        _finite(3 * self.poloidal_flux / area, "poloidal coefficient")
        _finite(3 * self.toroidal_flux / area, "toroidal coefficient")

    def _coordinates(self, point):
        x, y, z = (_finite(v, "coordinate") for v in point)
        rho = _finite(math.hypot(x, y), "cylindrical radius")
        u = rho - self.major_radius
        # Outside points need no divisions by rho, including the whole axis.
        if abs(u) >= self.minor_radius or abs(z) >= self.minor_radius:
            return x, y, z, rho, u, 0.0
        q = max(0.0, 1 - (u / self.minor_radius) ** 2 - (z / self.minor_radius) ** 2)
        return x, y, z, rho, u, q

    def stream_function(self, point) -> float:
        q = self._coordinates(point)[-1]
        return self.poloidal_flux * q**3 / (2 * math.pi)

    def current(self, point) -> tuple[float, float, float]:
        x, y, z, rho, u, q = self._coordinates(point)
        if q == 0:
            return 0.0, 0.0, 0.0
        area = math.pi * self.minor_radius * self.minor_radius
        poloidal = 3 * self.poloidal_flux / area
        toroidal = 3 * self.toroidal_flux / area
        radial = poloidal * z * q**2 / rho
        axial = -poloidal * u * q**2 / rho
        azimuthal = toroidal * q**2
        return tuple(
            _finite(v, "current component")
            for v in (
                radial * x / rho - azimuthal * y / rho,
                radial * y / rho + azimuthal * x / rho,
                axial,
            )
        )

    def central_mirror(self) -> ToroidalContentCurrent:
        """Pushforward by (x,y,z)->(-x,-y,-z): J'(r)=-J(-r)."""
        return replace(self, poloidal_flux=-self.poloidal_flux)

    def axial_plane_mirror(self) -> ToroidalContentCurrent:
        """Pushforward by (x,y,z)->(x,-y,z)."""
        return replace(self, toroidal_flux=-self.toroidal_flux)

    def reverse_flow(self) -> ToroidalContentCurrent:
        return replace(self, poloidal_flux=-self.poloidal_flux, toroidal_flux=-self.toroidal_flux)


if __name__ == "__main__":
    field = ToroidalContentCurrent()
    print("Domain: solid ring torus, R =", field.major_radius, "a =", field.minor_radius)
    print("Outer equatorial cut flux:", -field.poloidal_flux)
    print("Inner equatorial cut flux:", field.poloidal_flux)
    print("Meridional disk cut flux:", field.toroidal_flux)
    print("Local conservation: div(J) = 0 by the stream-function construction")
    print("Physical content identity and evolution law remain unspecified")
