"""Connected three-dimensional junction control volumes for graph currents.

Each conservative graph node is represented by one rectangular control volume.
Incident edge currents become signed boundary-port fluxes. Negative outward
flux enters through the left face; positive outward flux leaves through the
right face. A deterministic transport decomposition pairs inlet and outlet
fluxes into nonoverlapping internal lanes.

Every lane carries J=(f(y,z),0,0), independent of x. Its divergence is
therefore zero inside the control volume, its side-wall normal flux is zero,
and its integrated left/right face flux is exactly minus/plus the lane flux.

This is a kinematic junction construction. It supplies neither an equation of
motion nor physical units or a material interpretation.
"""

from __future__ import annotations

import math
from collections.abc import Hashable, Sequence
from dataclasses import dataclass
from enum import StrEnum

from .graph_toroidal_flux_bundle import GraphToroidalFluxBundle
from .vesica_tree_circulation import DirectedCurrent

_TOLERANCE = 1e-12
Point3D = tuple[float, float, float]


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


class PortSide(StrEnum):
    INLET = "inlet"
    OUTLET = "outlet"
    ZERO = "zero"


@dataclass(frozen=True)
class JunctionPort[NodeT: Hashable]:
    edge_index: int
    node: NodeT
    outward_flux: float
    side: PortSide

    def __post_init__(self) -> None:
        if not isinstance(self.edge_index, int) or isinstance(self.edge_index, bool):
            raise TypeError("edge_index must be an integer")
        if self.edge_index < 0:
            raise ValueError("edge_index must be nonnegative")
        object.__setattr__(self, "outward_flux", _finite(self.outward_flux, "outward_flux"))
        expected = (
            PortSide.OUTLET
            if self.outward_flux > _TOLERANCE
            else PortSide.INLET
            if self.outward_flux < -_TOLERANCE
            else PortSide.ZERO
        )
        if self.side is not expected:
            raise ValueError("port side must match the signed outward flux")


@dataclass(frozen=True)
class JunctionTransferLane:
    inlet_edge_index: int
    outlet_edge_index: int
    flux: float
    y_lower: float
    y_upper: float
    z_lower: float
    z_upper: float

    def __post_init__(self) -> None:
        if self.inlet_edge_index == self.outlet_edge_index:
            raise ValueError("a transfer lane must join distinct incident edges")
        object.__setattr__(self, "flux", _finite(self.flux, "flux"))
        if self.flux <= 0:
            raise ValueError("lane flux must be positive")
        for name in ("y_lower", "y_upper", "z_lower", "z_upper"):
            object.__setattr__(self, name, _finite(getattr(self, name), name))
        if not self.y_lower < self.y_upper or not self.z_lower < self.z_upper:
            raise ValueError("lane bounds must have positive area")

    @staticmethod
    def _unit_bump(value: float) -> float:
        if value <= 0.0 or value >= 1.0:
            return 0.0
        return 6.0 * value * (1.0 - value)

    def profile(self, y: float, z: float) -> float:
        y = _finite(y, "y")
        z = _finite(z, "z")
        dy = self.y_upper - self.y_lower
        dz = self.z_upper - self.z_lower
        uy = (y - self.y_lower) / dy
        uz = (z - self.z_lower) / dz
        return self.flux * self._unit_bump(uy) * self._unit_bump(uz) / (dy * dz)


@dataclass(frozen=True)
class JunctionControlVolume[NodeT: Hashable]:
    node: NodeT
    center: Point3D
    length: float
    width: float
    height: float
    lane_gap: float
    ports: tuple[JunctionPort[NodeT], ...]
    lanes: tuple[JunctionTransferLane, ...]

    def __post_init__(self) -> None:
        if len(self.center) != 3:
            raise ValueError("center must contain three coordinates")
        object.__setattr__(
            self,
            "center",
            tuple(_finite(value, "center coordinate") for value in self.center),
        )
        for name in ("length", "width", "height", "lane_gap"):
            object.__setattr__(self, name, _finite(getattr(self, name), name))
        if self.length <= 0 or self.width <= 0 or self.height <= 0:
            raise ValueError("junction dimensions must be positive")
        if self.lane_gap < 0:
            raise ValueError("lane_gap must be nonnegative")
        if len({port.edge_index for port in self.ports}) != len(self.ports):
            raise ValueError("each incident edge must have one junction port")
        if not self.lanes_are_disjoint():
            raise ValueError("junction transfer lanes must be disjoint")
        if self.maximum_port_flux_residual() > _TOLERANCE:
            raise ValueError("lane fluxes do not reproduce the declared ports")
        if abs(self.total_outward_flux) > _TOLERANCE:
            raise ValueError("junction control volume must be conservative")

    @property
    def total_outward_flux(self) -> float:
        return math.fsum(port.outward_flux for port in self.ports)

    def port_by_edge(self, edge_index: int) -> JunctionPort[NodeT]:
        try:
            return next(port for port in self.ports if port.edge_index == edge_index)
        except StopIteration as error:
            raise ValueError("edge is not incident on this junction") from error

    def measured_port_flux(self, edge_index: int) -> float:
        port = self.port_by_edge(edge_index)
        if port.side is PortSide.ZERO:
            return 0.0
        if port.side is PortSide.INLET:
            return -math.fsum(
                lane.flux for lane in self.lanes if lane.inlet_edge_index == edge_index
            )
        return math.fsum(
            lane.flux for lane in self.lanes if lane.outlet_edge_index == edge_index
        )

    def maximum_port_flux_residual(self) -> float:
        return max(
            (
                abs(self.measured_port_flux(port.edge_index) - port.outward_flux)
                for port in self.ports
            ),
            default=0.0,
        )

    def lanes_are_disjoint(self) -> bool:
        ordered = sorted(self.lanes, key=lambda lane: lane.y_lower)
        return all(
            left.y_upper <= right.y_lower + _TOLERANCE
            for left, right in zip(ordered, ordered[1:])
        )

    def _local_point(self, point: Sequence[float]) -> Point3D:
        if len(point) != 3:
            raise ValueError("point must contain exactly three coordinates")
        values = tuple(_finite(value, "coordinate") for value in point)
        return tuple(value - center for value, center in zip(values, self.center, strict=True))

    def current(self, point: Sequence[float]) -> Point3D:
        x, y, z = self._local_point(point)
        if abs(x) > self.length / 2 or abs(y) > self.width / 2 or abs(z) > self.height / 2:
            return 0.0, 0.0, 0.0
        x_current = math.fsum(lane.profile(y, z) for lane in self.lanes)
        return x_current, 0.0, 0.0

    @property
    def side_wall_flux(self) -> float:
        return 0.0


def _incident_ports[NodeT: Hashable](
    node: NodeT,
    currents: Sequence[DirectedCurrent[NodeT]],
) -> tuple[JunctionPort[NodeT], ...]:
    ports = []
    for edge_index, edge in enumerate(currents):
        if edge.source == node:
            outward = edge.current
        elif edge.target == node:
            outward = -edge.current
        else:
            continue
        side = (
            PortSide.OUTLET
            if outward > _TOLERANCE
            else PortSide.INLET
            if outward < -_TOLERANCE
            else PortSide.ZERO
        )
        ports.append(JunctionPort(edge_index, node, outward, side))
    return tuple(ports)


def _transport_plan(
    ports: Sequence[JunctionPort],
) -> tuple[tuple[int, int, float], ...]:
    inlet = [[port.edge_index, -port.outward_flux] for port in ports if port.side is PortSide.INLET]
    outlet = [[port.edge_index, port.outward_flux] for port in ports if port.side is PortSide.OUTLET]
    inlet_total = math.fsum(item[1] for item in inlet)
    outlet_total = math.fsum(item[1] for item in outlet)
    if not math.isclose(inlet_total, outlet_total, rel_tol=0.0, abs_tol=_TOLERANCE):
        raise ValueError("node incident fluxes are not conservative")

    plan = []
    in_index = out_index = 0
    while in_index < len(inlet) and out_index < len(outlet):
        amount = min(inlet[in_index][1], outlet[out_index][1])
        if amount > _TOLERANCE:
            plan.append((inlet[in_index][0], outlet[out_index][0], amount))
        inlet[in_index][1] -= amount
        outlet[out_index][1] -= amount
        if inlet[in_index][1] <= _TOLERANCE:
            in_index += 1
        if outlet[out_index][1] <= _TOLERANCE:
            out_index += 1
    return tuple(plan)


def build_junction_control_volume[NodeT: Hashable](
    node: NodeT,
    currents: Sequence[DirectedCurrent[NodeT]],
    *,
    center: Point3D = (0.0, 0.0, 0.0),
    length: float = 1.0,
    width: float = 1.0,
    height: float = 1.0,
    lane_gap: float = 0.02,
) -> JunctionControlVolume[NodeT]:
    length = _finite(length, "length")
    width = _finite(width, "width")
    height = _finite(height, "height")
    lane_gap = _finite(lane_gap, "lane_gap")
    if length <= 0 or width <= 0 or height <= 0:
        raise ValueError("junction dimensions must be positive")
    if lane_gap < 0:
        raise ValueError("lane_gap must be nonnegative")

    ports = _incident_ports(node, currents)
    plan = _transport_plan(ports)
    lane_count = len(plan)
    if lane_count == 0:
        lanes = ()
    else:
        available = width - (lane_count - 1) * lane_gap
        if available <= 0:
            raise ValueError("junction width is too small for requested lane gaps")
        lane_width = available / lane_count
        y = -width / 2
        lanes_list = []
        for inlet_edge, outlet_edge, flux in plan:
            lanes_list.append(
                JunctionTransferLane(
                    inlet_edge_index=inlet_edge,
                    outlet_edge_index=outlet_edge,
                    flux=flux,
                    y_lower=y,
                    y_upper=y + lane_width,
                    z_lower=-height / 2,
                    z_upper=height / 2,
                )
            )
            y += lane_width + lane_gap
        lanes = tuple(lanes_list)

    return JunctionControlVolume(
        node=node,
        center=center,
        length=length,
        width=width,
        height=height,
        lane_gap=lane_gap,
        ports=ports,
        lanes=lanes,
    )


@dataclass(frozen=True)
class ToroidalJunctionNetwork[NodeT: Hashable]:
    bundle: GraphToroidalFluxBundle[NodeT]
    nodes: tuple[NodeT, ...]
    junctions: tuple[JunctionControlVolume[NodeT], ...]

    def junction(self, node: NodeT) -> JunctionControlVolume[NodeT]:
        try:
            return next(junction for junction in self.junctions if junction.node == node)
        except StopIteration as error:
            raise ValueError("unknown network node") from error

    def edge_interface_residual(self) -> float:
        residuals = []
        for channel in self.bundle.channels:
            edge = channel.edge
            source_port = self.junction(edge.source).measured_port_flux(channel.edge_index)
            target_port = self.junction(edge.target).measured_port_flux(channel.edge_index)
            residuals.extend(
                (
                    abs(source_port - edge.current),
                    abs(target_port + edge.current),
                    abs(channel.oriented_cut_flux - edge.current),
                )
            )
        return max(residuals, default=0.0)

    def maximum_node_balance_residual(self) -> float:
        return max((abs(junction.total_outward_flux) for junction in self.junctions), default=0.0)

    def junction_boxes_are_disjoint(self) -> bool:
        ordered = sorted(self.junctions, key=lambda junction: junction.center[2])
        return all(
            left.center[2] + left.height / 2 <= right.center[2] - right.height / 2 + _TOLERANCE
            for left, right in zip(ordered, ordered[1:])
        )


def connect_toroidal_bundle_with_junctions[NodeT: Hashable](
    bundle: GraphToroidalFluxBundle[NodeT],
    nodes: Sequence[NodeT],
    *,
    junction_length: float = 1.0,
    junction_width: float = 1.0,
    junction_height: float = 1.0,
    lane_gap: float = 0.02,
    junction_gap: float = 0.25,
) -> ToroidalJunctionNetwork[NodeT]:
    ordered_nodes = tuple(nodes)
    if len(set(ordered_nodes)) != len(ordered_nodes):
        raise ValueError("network nodes must be unique")
    endpoints = {endpoint for edge in bundle.edges for endpoint in (edge.source, edge.target)}
    if endpoints - set(ordered_nodes):
        raise ValueError("network nodes must contain every graph endpoint")
    junction_height = _finite(junction_height, "junction_height")
    junction_gap = _finite(junction_gap, "junction_gap")
    if junction_height <= 0:
        raise ValueError("junction_height must be positive")
    if junction_gap < 0:
        raise ValueError("junction_gap must be nonnegative")

    outer_radius = max(
        (channel.major_radius + channel.minor_radius for channel in bundle.channels),
        default=0.0,
    )
    center_x = outer_radius + _finite(junction_length, "junction_length")
    spacing = junction_height + junction_gap
    midpoint = (len(ordered_nodes) - 1) / 2
    junctions = tuple(
        build_junction_control_volume(
            node,
            bundle.edges,
            center=(center_x, 0.0, (index - midpoint) * spacing),
            length=junction_length,
            width=junction_width,
            height=junction_height,
            lane_gap=lane_gap,
        )
        for index, node in enumerate(ordered_nodes)
    )
    network = ToroidalJunctionNetwork(bundle, ordered_nodes, junctions)
    if not network.junction_boxes_are_disjoint():
        raise RuntimeError("junction control volumes must be disjoint")
    if network.edge_interface_residual() > _TOLERANCE:
        raise RuntimeError("junction and toroidal edge fluxes do not match")
    return network
