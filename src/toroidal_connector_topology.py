"""Topology audit and annular Piola connector for toroidal edge channels.

A rectangular junction port is disk-like while the canonical poloidal cut of a
solid torus is annular. A nonsingular steady connector whose streamlines define
a one-to-one sweep between cross-sections would induce a diffeomorphism between
those cross-sections, so the present rectangle-to-annulus interface is a no-fit.

This module also supplies the compatible case: an annular source port connected
to one boundary copy of a cut-open toroidal channel. The connector is generated
by an explicit coordinate map and the contravariant Piola transform. Its
divergence is therefore zero, its flux is preserved on every transverse
section, and its target vector matches the existing purely poloidal toroidal
field pointwise on the canonical inner cut.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from .conservative_toroidal_field import ToroidalContentCurrent

_TOLERANCE = 1e-12
Point3D = tuple[float, float, float]


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


@dataclass(frozen=True)
class CrossSectionTopology:
    name: str
    boundary_components: int
    first_betti_number: int
    euler_characteristic: int


DISK_LIKE_PORT = CrossSectionTopology(
    name="disk_like_rectangle",
    boundary_components=1,
    first_betti_number=0,
    euler_characteristic=1,
)
ANNULAR_PORT = CrossSectionTopology(
    name="annulus",
    boundary_components=2,
    first_betti_number=1,
    euler_characteristic=0,
)


def nonsingular_sweep_compatible(
    source: CrossSectionTopology,
    target: CrossSectionTopology,
) -> bool:
    """Return whether the recorded invariants permit a one-to-one smooth sweep."""
    return (
        source.boundary_components == target.boundary_components
        and source.first_betti_number == target.first_betti_number
        and source.euler_characteristic == target.euler_characteristic
    )


def rectangular_to_toroidal_cut_is_no_fit() -> bool:
    """The existing rectangular junction lane cannot diffeomorphically sweep to an annulus."""
    return not nonsingular_sweep_compatible(DISK_LIKE_PORT, ANNULAR_PORT)


class CutSide(StrEnum):
    INLET_COPY = "inlet_copy"
    OUTLET_COPY = "outlet_copy"


@dataclass(frozen=True)
class CutOpenToroidalChannel:
    """A solid torus cut along its canonical inner equatorial annulus.

    The two boundary copies occupy the same coordinates in the original torus
    chart but are distinct manifold-boundary records with opposite outward
    normals. This class records the cut topology and inherited flux density; it
    does not yet construct a separated Euclidean embedding of the two copies.
    """

    field: ToroidalContentCurrent
    center_z: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "center_z", _finite(self.center_z, "center_z"))

    @property
    def topology(self) -> CrossSectionTopology:
        return ANNULAR_PORT

    @property
    def inner_radius(self) -> float:
        return self.field.major_radius - self.field.minor_radius

    @property
    def outer_radius(self) -> float:
        return self.field.major_radius

    def outward_flux(self, side: CutSide) -> float:
        """Return the signed flux through one cut boundary copy."""
        if side is CutSide.INLET_COPY:
            return -self.field.poloidal_flux
        if side is CutSide.OUTLET_COPY:
            return self.field.poloidal_flux
        raise ValueError("unknown cut side")

    def positive_normal_density(self, radius: float) -> float:
        """Return +z normal current density on the canonical inner cut."""
        radius = _finite(radius, "radius")
        if not self.inner_radius <= radius <= self.outer_radius:
            return 0.0
        return self.field.current((radius, 0.0, 0.0))[2]

    def boundary_normal_density(self, radius: float, side: CutSide) -> float:
        density = self.positive_normal_density(radius)
        return -density if side is CutSide.INLET_COPY else density


def annular_connector_source_density(
    flux: float,
    inner_radius: float,
    outer_radius: float,
    radius: float,
) -> float:
    """Return the connector-compatible normal density on an annular source port."""
    flux = _finite(flux, "flux")
    inner_radius = _finite(inner_radius, "inner_radius")
    outer_radius = _finite(outer_radius, "outer_radius")
    radius = _finite(radius, "radius")
    if inner_radius <= 0 or outer_radius <= inner_radius:
        raise ValueError("source annulus must have positive ordered radii")
    if not inner_radius <= radius <= outer_radius:
        return 0.0
    q = (radius - inner_radius) / (outer_radius - inner_radius)
    if q <= 0.0 or q >= 1.0:
        return 0.0
    t = 1.0 - q
    measure_density = 3.0 * flux / math.pi * t * (1.0 - t**2) ** 2
    return measure_density / (radius * (outer_radius - inner_radius))


@dataclass(frozen=True)
class AnnularPiolaConnector:
    """Divergence-free connector from an annular source port to a toroidal cut.

    Parameter coordinates are s in [0,1], q in [0,1], and theta in [0,2*pi].
    The source annulus lies at s=0. The target annulus is the toroidal inner cut
    at s=1. A cubic smoothstep changes the radial geometry with zero radial
    derivative at both ends, making the field normal to both interface planes.
    """

    channel: CutOpenToroidalChannel
    source_inner_radius: float
    source_outer_radius: float
    length: float = 1.0

    def __post_init__(self) -> None:
        for name in ("source_inner_radius", "source_outer_radius", "length"):
            object.__setattr__(self, name, _finite(getattr(self, name), name))
        if self.source_inner_radius <= 0:
            raise ValueError("source_inner_radius must be positive")
        if self.source_outer_radius <= self.source_inner_radius:
            raise ValueError("source annulus must have positive radial width")
        if self.length <= 0:
            raise ValueError("connector length must be positive")
        if abs(self.channel.field.toroidal_flux) > _TOLERANCE:
            raise ValueError("annular connector currently requires a purely poloidal toroidal field")
        if not nonsingular_sweep_compatible(ANNULAR_PORT, self.channel.topology):
            raise RuntimeError("connector cross-sections must be topologically compatible")

    @property
    def source_z(self) -> float:
        return self.channel.center_z - self.length

    @property
    def target_z(self) -> float:
        return self.channel.center_z

    @property
    def flux(self) -> float:
        return self.channel.field.poloidal_flux

    @property
    def source_width(self) -> float:
        return self.source_outer_radius - self.source_inner_radius

    @staticmethod
    def _smoothstep(s: float) -> float:
        return 3.0 * s**2 - 2.0 * s**3

    @staticmethod
    def _smoothstep_derivative(s: float) -> float:
        return 6.0 * s * (1.0 - s)

    def _source_radius(self, q: float) -> float:
        return self.source_inner_radius + self.source_width * q

    def _target_radius(self, q: float) -> float:
        return self.channel.inner_radius + self.channel.field.minor_radius * q

    def radius(self, s: float, q: float) -> float:
        h = self._smoothstep(s)
        return (1.0 - h) * self._source_radius(q) + h * self._target_radius(q)

    def radial_q_derivative(self, s: float) -> float:
        h = self._smoothstep(s)
        return (1.0 - h) * self.source_width + h * self.channel.field.minor_radius

    def radial_s_derivative(self, s: float, q: float) -> float:
        return self._smoothstep_derivative(s) * (
            self._target_radius(q) - self._source_radius(q)
        )

    def flux_measure_density(self, q: float) -> float:
        """Return flux per dq dtheta inherited from the toroidal inner cut."""
        if q <= 0.0 or q >= 1.0:
            return 0.0
        t = 1.0 - q
        return 3.0 * self.flux / math.pi * t * (1.0 - t**2) ** 2

    def map_point(self, s: float, q: float, theta: float) -> Point3D:
        s = _finite(s, "s")
        q = _finite(q, "q")
        theta = _finite(theta, "theta")
        if not 0.0 <= s <= 1.0 or not 0.0 <= q <= 1.0:
            raise ValueError("s and q must lie in [0, 1]")
        rho = self.radius(s, q)
        z = self.source_z + self.length * s
        return rho * math.cos(theta), rho * math.sin(theta), z

    def _inverse_parameters(self, point: Point3D) -> tuple[float, float, float] | None:
        x, y, z = (_finite(value, "coordinate") for value in point)
        s = (z - self.source_z) / self.length
        if s < -_TOLERANCE or s > 1.0 + _TOLERANCE:
            return None
        s = min(1.0, max(0.0, s))
        rho = math.hypot(x, y)
        h = self._smoothstep(s)
        inner = (1.0 - h) * self.source_inner_radius + h * self.channel.inner_radius
        width = self.radial_q_derivative(s)
        q = (rho - inner) / width
        if q < -_TOLERANCE or q > 1.0 + _TOLERANCE:
            return None
        q = min(1.0, max(0.0, q))
        return s, q, math.atan2(y, x)

    def jacobian_determinant(self, s: float, q: float) -> float:
        rho = self.radius(s, q)
        return self.length * rho * self.radial_q_derivative(s)

    def current(self, point: Point3D) -> Point3D:
        parameters = self._inverse_parameters(point)
        if parameters is None:
            return 0.0, 0.0, 0.0
        s, q, theta = parameters
        k = self.flux_measure_density(q)
        if k == 0.0:
            return 0.0, 0.0, 0.0
        rho = self.radius(s, q)
        rho_q = self.radial_q_derivative(s)
        rho_s = self.radial_s_derivative(s, q)
        radial = k * rho_s / (self.length * rho * rho_q)
        axial = k / (rho * rho_q)
        return (
            radial * math.cos(theta),
            radial * math.sin(theta),
            axial,
        )

    def source_normal_density(self, radius: float) -> float:
        return annular_connector_source_density(
            self.flux,
            self.source_inner_radius,
            self.source_outer_radius,
            radius,
        )

    def target_vector_residual(self, radius: float) -> float:
        radius = _finite(radius, "radius")
        connector = self.current((radius, 0.0, self.target_z))
        toroidal = self.channel.field.current((radius, 0.0, 0.0))
        return max(abs(a - b) for a, b in zip(connector, toroidal, strict=True))


if rectangular_to_toroidal_cut_is_no_fit() is not True:
    raise RuntimeError("disk-like rectangular ports must remain distinct from annular cuts")
