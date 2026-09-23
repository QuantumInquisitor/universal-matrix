"""Framed local edge assemblies for annular junction and toroidal channels.

Each graph edge is assembled in one local axial frame:

source annular junction port
-> inlet annular Piola transition
-> straightened cut-open toroidal channel
-> exit annular Piola transition
-> target annular junction port.

The graph edge's signed current is used throughout. A one-bit axial frame flip,
equal to the sign of the current, maps the local endpoint vectors back to the
fixed +z current direction of the annular junction volumes for both positive
and negative graph currents.

This checkpoint is local to each edge. It does not yet assign collision-free
global positions or bent routing frames to the full network.
"""

from __future__ import annotations

import math
from collections.abc import Hashable, Sequence
from dataclasses import dataclass

from .conservative_toroidal_field import ToroidalContentCurrent
from .toroidal_annular_junction import (
    AnnularJunctionNetwork,
    AnnularJunctionPort,
)
from .toroidal_connector_topology import annular_connector_source_density
from .vesica_tree_circulation import DirectedCurrent

_TOLERANCE = 1e-12
Point3D = tuple[float, float, float]


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


@dataclass(frozen=True)
class AnnularPiolaTransition:
    source_inner_radius: float
    source_outer_radius: float
    target_inner_radius: float
    target_outer_radius: float
    flux: float
    length: float
    z_start: float = 0.0

    def __post_init__(self) -> None:
        for name in (
            "source_inner_radius",
            "source_outer_radius",
            "target_inner_radius",
            "target_outer_radius",
            "flux",
            "length",
            "z_start",
        ):
            object.__setattr__(self, name, _finite(getattr(self, name), name))
        if self.source_inner_radius <= 0 or self.target_inner_radius <= 0:
            raise ValueError("annular inner radii must be positive")
        if self.source_outer_radius <= self.source_inner_radius:
            raise ValueError("source annulus must have positive width")
        if self.target_outer_radius <= self.target_inner_radius:
            raise ValueError("target annulus must have positive width")
        if self.length <= 0:
            raise ValueError("transition length must be positive")

    @property
    def source_width(self) -> float:
        return self.source_outer_radius - self.source_inner_radius

    @property
    def target_width(self) -> float:
        return self.target_outer_radius - self.target_inner_radius

    @property
    def z_end(self) -> float:
        return self.z_start + self.length

    @staticmethod
    def _smoothstep(s: float) -> float:
        return 3.0 * s**2 - 2.0 * s**3

    @staticmethod
    def _smoothstep_derivative(s: float) -> float:
        return 6.0 * s * (1.0 - s)

    def source_radius(self, q: float) -> float:
        return self.source_inner_radius + self.source_width * q

    def target_radius(self, q: float) -> float:
        return self.target_inner_radius + self.target_width * q

    def radius(self, s: float, q: float) -> float:
        h = self._smoothstep(s)
        return (1.0 - h) * self.source_radius(q) + h * self.target_radius(q)

    def radial_q_derivative(self, s: float) -> float:
        h = self._smoothstep(s)
        return (1.0 - h) * self.source_width + h * self.target_width

    def radial_s_derivative(self, s: float, q: float) -> float:
        return self._smoothstep_derivative(s) * (
            self.target_radius(q) - self.source_radius(q)
        )

    def flux_measure_density(self, q: float) -> float:
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
        radius = self.radius(s, q)
        z = self.z_start + self.length * s
        return radius * math.cos(theta), radius * math.sin(theta), z

    def _inverse_parameters(self, point: Sequence[float]) -> tuple[float, float, float] | None:
        if len(point) != 3:
            raise ValueError("point must contain exactly three coordinates")
        x, y, z = (_finite(value, "coordinate") for value in point)
        s = (z - self.z_start) / self.length
        if s < -_TOLERANCE or s > 1.0 + _TOLERANCE:
            return None
        s = min(1.0, max(0.0, s))
        radius = math.hypot(x, y)
        h = self._smoothstep(s)
        inner = (1.0 - h) * self.source_inner_radius + h * self.target_inner_radius
        width = self.radial_q_derivative(s)
        q = (radius - inner) / width
        if q < -_TOLERANCE or q > 1.0 + _TOLERANCE:
            return None
        q = min(1.0, max(0.0, q))
        return s, q, math.atan2(y, x)

    def current(self, point: Sequence[float]) -> Point3D:
        parameters = self._inverse_parameters(point)
        if parameters is None:
            return 0.0, 0.0, 0.0
        s, q, theta = parameters
        k = self.flux_measure_density(q)
        if k == 0.0:
            return 0.0, 0.0, 0.0
        radius = self.radius(s, q)
        radius_q = self.radial_q_derivative(s)
        radius_s = self.radial_s_derivative(s, q)
        radial = k * radius_s / (self.length * radius * radius_q)
        axial = k / (radius * radius_q)
        return (
            radial * math.cos(theta),
            radial * math.sin(theta),
            axial,
        )

    def jacobian_determinant(self, s: float, q: float) -> float:
        return self.length * self.radius(s, q) * self.radial_q_derivative(s)

    @property
    def source_outward_flux(self) -> float:
        return -self.flux

    @property
    def target_outward_flux(self) -> float:
        return self.flux


@dataclass(frozen=True)
class StraightenedCutOpenToroidalChannel:
    """Flux-equivalent straightened chart for a purely poloidal cut-open torus."""

    field: ToroidalContentCurrent
    length: float
    z_start: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "length", _finite(self.length, "length"))
        object.__setattr__(self, "z_start", _finite(self.z_start, "z_start"))
        if self.length <= 0:
            raise ValueError("channel length must be positive")
        if abs(self.field.toroidal_flux) > _TOLERANCE:
            raise ValueError("straightened cut-open channel requires purely poloidal flux")

    @property
    def inner_radius(self) -> float:
        return self.field.major_radius - self.field.minor_radius

    @property
    def outer_radius(self) -> float:
        return self.field.major_radius

    @property
    def z_end(self) -> float:
        return self.z_start + self.length

    def current(self, point: Sequence[float]) -> Point3D:
        if len(point) != 3:
            raise ValueError("point must contain exactly three coordinates")
        x, y, z = (_finite(value, "coordinate") for value in point)
        radius = math.hypot(x, y)
        if (
            z < self.z_start - _TOLERANCE
            or z > self.z_end + _TOLERANCE
            or radius < self.inner_radius
            or radius > self.outer_radius
        ):
            return 0.0, 0.0, 0.0
        axial = annular_connector_source_density(
            self.field.poloidal_flux,
            self.inner_radius,
            self.outer_radius,
            radius,
        )
        return 0.0, 0.0, axial

    def original_cut_vector_residual(self, radius: float) -> float:
        radius = _finite(radius, "radius")
        straight = self.current((radius, 0.0, self.z_start + self.length / 2))
        original = self.field.current((radius, 0.0, 0.0))
        return max(abs(a - b) for a, b in zip(straight, original, strict=True))

    @property
    def source_outward_flux(self) -> float:
        return -self.field.poloidal_flux

    @property
    def target_outward_flux(self) -> float:
        return self.field.poloidal_flux


@dataclass(frozen=True)
class FramedToroidalEdgeAssembly[NodeT: Hashable]:
    edge_index: int
    edge: DirectedCurrent[NodeT]
    source_port: AnnularJunctionPort[NodeT]
    target_port: AnnularJunctionPort[NodeT]
    inlet: AnnularPiolaTransition
    channel: StraightenedCutOpenToroidalChannel
    outlet: AnnularPiolaTransition
    axis_sign: int

    def __post_init__(self) -> None:
        if self.axis_sign not in (-1, 1):
            raise ValueError("axis_sign must be -1 or 1")
        if self.source_port.edge_index != self.edge_index or self.target_port.edge_index != self.edge_index:
            raise ValueError("edge ports must match the assembly edge index")
        if not math.isclose(self.source_port.outward_flux, self.edge.current, abs_tol=_TOLERANCE):
            raise ValueError("source port flux must equal the signed edge current")
        if not math.isclose(self.target_port.outward_flux, -self.edge.current, abs_tol=_TOLERANCE):
            raise ValueError("target port flux must oppose the signed edge current")
        if not math.isclose(self.inlet.flux, self.edge.current, abs_tol=_TOLERANCE):
            raise ValueError("inlet transition flux must equal the edge current")
        if not math.isclose(self.channel.field.poloidal_flux, self.edge.current, abs_tol=_TOLERANCE):
            raise ValueError("channel flux must equal the edge current")
        if not math.isclose(self.outlet.flux, self.edge.current, abs_tol=_TOLERANCE):
            raise ValueError("outlet transition flux must equal the edge current")
        if not math.isclose(self.inlet.z_end, self.channel.z_start, abs_tol=_TOLERANCE):
            raise ValueError("inlet and channel intervals must be contiguous")
        if not math.isclose(self.channel.z_end, self.outlet.z_start, abs_tol=_TOLERANCE):
            raise ValueError("channel and outlet intervals must be contiguous")

    @property
    def total_length(self) -> float:
        return self.outlet.z_end - self.inlet.z_start

    def local_current(self, point: Sequence[float]) -> Point3D:
        z = _finite(point[2], "z")
        if z <= self.inlet.z_end + _TOLERANCE:
            return self.inlet.current(point)
        if z <= self.channel.z_end + _TOLERANCE:
            return self.channel.current(point)
        return self.outlet.current(point)

    def interface_vector_residual(self) -> float:
        residuals = []
        for q in (0.1, 0.25, 0.5, 0.75, 0.9):
            channel_radius = self.channel.inner_radius + (
                self.channel.outer_radius - self.channel.inner_radius
            ) * q
            inlet_point = (channel_radius, 0.0, self.channel.z_start)
            outlet_point = (channel_radius, 0.0, self.channel.z_end)
            inlet_vector = self.inlet.current(inlet_point)
            channel_in = self.channel.current(inlet_point)
            channel_out = self.channel.current(outlet_point)
            outlet_vector = self.outlet.current(outlet_point)
            residuals.extend(
                abs(a - b) for a, b in zip(inlet_vector, channel_in, strict=True)
            )
            residuals.extend(
                abs(a - b) for a, b in zip(channel_out, outlet_vector, strict=True)
            )
        return max(residuals, default=0.0)

    def flux_chain_residual(self) -> float:
        pairs = (
            self.source_port.outward_flux + self.inlet.source_outward_flux,
            self.inlet.target_outward_flux + self.channel.source_outward_flux,
            self.channel.target_outward_flux + self.outlet.source_outward_flux,
            self.outlet.target_outward_flux + self.target_port.outward_flux,
        )
        return max(abs(value) for value in pairs)

    def endpoint_vector_residual(
        self,
        source_junction,
        target_junction,
    ) -> float:
        residuals = []
        for port, transition, junction, s_value in (
            (self.source_port, self.inlet, source_junction, 0.0),
            (self.target_port, self.outlet, target_junction, 1.0),
        ):
            for q in (0.15, 0.4, 0.7, 0.9):
                radius = port.inner_radius + port.width * q
                local_point = transition.map_point(s_value, q, 0.0)
                local_vector = transition.current(local_point)
                framed = (
                    local_vector[0],
                    local_vector[1],
                    self.axis_sign * local_vector[2],
                )
                face_z = junction.center[2] + (
                    -junction.length / 2
                    if port.outward_flux < -_TOLERANCE
                    else junction.length / 2
                    if port.outward_flux > _TOLERANCE
                    else (
                        -junction.length / 2
                        if port.face.value == "lower"
                        else junction.length / 2
                    )
                )
                junction_point = (
                    junction.center[0] + radius,
                    junction.center[1],
                    face_z,
                )
                junction_vector = junction.current(junction_point)
                residuals.extend(
                    abs(a - b) for a, b in zip(framed, junction_vector, strict=True)
                )
        return max(residuals, default=0.0)


def build_framed_edge_assembly[NodeT: Hashable](
    network: AnnularJunctionNetwork[NodeT],
    edge_index: int,
    *,
    connector_length: float = 1.0,
    channel_length: float = 1.0,
) -> FramedToroidalEdgeAssembly[NodeT]:
    if edge_index not in range(len(network.bundle.channels)):
        raise ValueError("edge_index must select one toroidal channel")
    channel_record = network.bundle.channels[edge_index]
    edge = channel_record.edge
    source_port = network.junction(edge.source).port_by_edge(edge_index)
    target_port = network.junction(edge.target).port_by_edge(edge_index)
    connector_length = _finite(connector_length, "connector_length")
    channel_length = _finite(channel_length, "channel_length")
    if connector_length <= 0 or channel_length <= 0:
        raise ValueError("edge assembly lengths must be positive")

    inner = channel_record.major_radius - channel_record.minor_radius
    outer = channel_record.major_radius
    inlet = AnnularPiolaTransition(
        source_port.inner_radius,
        source_port.outer_radius,
        inner,
        outer,
        edge.current,
        connector_length,
        0.0,
    )
    channel = StraightenedCutOpenToroidalChannel(
        channel_record.field,
        channel_length,
        inlet.z_end,
    )
    outlet = AnnularPiolaTransition(
        inner,
        outer,
        target_port.inner_radius,
        target_port.outer_radius,
        edge.current,
        connector_length,
        channel.z_end,
    )
    axis_sign = 1 if edge.current >= 0 else -1
    assembly = FramedToroidalEdgeAssembly(
        edge_index,
        edge,
        source_port,
        target_port,
        inlet,
        channel,
        outlet,
        axis_sign,
    )
    if assembly.interface_vector_residual() > _TOLERANCE:
        raise RuntimeError("edge assembly internal vectors do not match")
    if assembly.flux_chain_residual() > _TOLERANCE:
        raise RuntimeError("edge assembly boundary flux chain does not close")
    return assembly


@dataclass(frozen=True)
class FramedToroidalEdgeNetwork[NodeT: Hashable]:
    junction_network: AnnularJunctionNetwork[NodeT]
    assemblies: tuple[FramedToroidalEdgeAssembly[NodeT], ...]

    def maximum_interface_residual(self) -> float:
        return max(
            (assembly.interface_vector_residual() for assembly in self.assemblies),
            default=0.0,
        )

    def maximum_flux_chain_residual(self) -> float:
        return max(
            (assembly.flux_chain_residual() for assembly in self.assemblies),
            default=0.0,
        )

    def maximum_endpoint_vector_residual(self) -> float:
        residuals = []
        for assembly in self.assemblies:
            residuals.append(
                assembly.endpoint_vector_residual(
                    self.junction_network.junction(assembly.edge.source),
                    self.junction_network.junction(assembly.edge.target),
                )
            )
        return max(residuals, default=0.0)


def build_framed_edge_network[NodeT: Hashable](
    junction_network: AnnularJunctionNetwork[NodeT],
    *,
    connector_length: float = 1.0,
    channel_length: float = 1.0,
) -> FramedToroidalEdgeNetwork[NodeT]:
    assemblies = tuple(
        build_framed_edge_assembly(
            junction_network,
            edge_index,
            connector_length=connector_length,
            channel_length=channel_length,
        )
        for edge_index in range(len(junction_network.bundle.channels))
    )
    result = FramedToroidalEdgeNetwork(junction_network, assemblies)
    if result.maximum_interface_residual() > _TOLERANCE:
        raise RuntimeError("framed edge network has an internal vector mismatch")
    if result.maximum_flux_chain_residual() > _TOLERANCE:
        raise RuntimeError("framed edge network has a flux-chain mismatch")
    if result.maximum_endpoint_vector_residual() > _TOLERANCE:
        raise RuntimeError("framed edge endpoint vectors do not match junction fields")
    return result
