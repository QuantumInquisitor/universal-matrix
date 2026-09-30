"""Explicit local host aperture; derived from the reviewed transverse-access specimen.

Kinematic current model only. No complete network or safe opening motion claim.
"""

import math
from dataclasses import asdict, dataclass

import numpy as np

from .toroidal_connector_topology import annular_connector_source_density
from .toroidal_incident_bend_audit import AnnularStraightSegment
from .toroidal_shared_return_connectors import _piece_current
from .toroidal_shared_return_route import RoutedTubePiece


@dataclass(frozen=True)
class Access:
    sign: float = 1.0
    alpha: float = 0.5
    height_scale: float = 6.0
    half_length: float = 15.0
    inner_radius: float = 12.2
    outer_radius: float = 12.6
    transit_inner: float = 2.0
    transit_outer: float = 2.4
    transit_outside_x: float = 16.6
    transit_inside_x: float = 8.2

    def __post_init__(self):
        values = asdict(self)
        if any(isinstance(v, bool) or not math.isfinite(v) for v in values.values()):
            raise ValueError("parameters must be finite real numbers")
        if self.sign not in (-1.0, 1.0):
            raise ValueError("bounded specimen sign must be +/-1")
        if not (0 < self.alpha < math.pi / 2 and 0 < 2 * self.height_scale < self.half_length):
            raise ValueError("streamfunction patch must avoid periodic seam and axial caps")
        if not (
            0 < self.inner_radius < self.outer_radius
            and 0 < self.transit_inner < self.transit_outer
        ):
            raise ValueError("ordered positive radii required")
        if not (
            self.transit_outside_x > self.outer_radius
            and 0 < self.transit_inside_x < self.inner_radius
        ):
            raise ValueError("transit caps must straddle the host wall")
        if math.hypot(self.transit_inside_x, self.transit_outer) >= self.inner_radius:
            raise ValueError("inside transit cap must be entirely in the host core")
        if self.clearance_bound() <= 0:
            raise ValueError("analytic host/transit clearance must be positive")

    def hole_coordinate(self, point):
        x, y, z = point
        theta = math.atan2(y, x)
        return math.hypot(theta / self.alpha, z / self.height_scale)

    def host_contains(self, point):
        r = math.hypot(point[0], point[1])
        return (
            self.inner_radius <= r <= self.outer_radius
            and abs(point[2]) <= self.half_length
            and self.hole_coordinate(point) >= 1
        )

    def clearance_bound(self):
        # For x>=0 host material, distance to the x-axis is at least
        # min(ri*sin(alpha), h).  For x<0, transit is at least inside_x away.
        return min(
            self.transit_inside_x,
            min(self.inner_radius * math.sin(self.alpha), self.height_scale) - self.transit_outer,
        )

    def psi_derivatives(self, theta, z):
        rho = math.hypot(theta / self.alpha, z / self.height_scale)
        if rho <= 1:
            return 0.0, 0.0
        if rho >= 2:
            return 1.0, 0.0
        t = rho - 1
        f = t**3 * (10 - 15 * t + 6 * t * t)
        df = 30 * t * t * (1 - t) ** 2
        return (
            f + df * theta * theta / (self.alpha * self.alpha * rho),
            theta * df * z / (self.height_scale * self.height_scale * rho),
        )

    def host_current(self, point):
        x, y, z = point
        r = math.hypot(x, y)
        if r < self.inner_radius or r > self.outer_radius or abs(z) > self.half_length:
            return np.zeros(3)
        theta = math.atan2(y, x)
        ptheta, pz = self.psi_derivatives(theta, z)
        density = annular_connector_source_density(
            0.6 * self.sign, self.inner_radius, self.outer_radius, r
        )
        tangential = -r * density * pz
        return np.array(
            (-math.sin(theta) * tangential, math.cos(theta) * tangential, density * ptheta)
        )

    def transit_piece(self):
        return RoutedTubePiece(
            AnnularStraightSegment(
                (self.transit_outside_x, 0.0, 0.0),
                (self.transit_inside_x, 0.0, 0.0),
                self.transit_inner,
                self.transit_outer,
            )
        )

    def transit_current(self, point):
        return np.array(_piece_current(self.transit_piece(), point, 0.4 * self.sign))
