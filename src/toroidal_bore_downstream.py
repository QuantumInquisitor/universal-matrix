"""Fixed, opt-in bore-to-A partial route with two explicit open boundaries.

The changed components are checked against one another and retained edges
1/2/3 and junctions. Retained/retained collisions, upstream attachment and
motion are outside this dimensionless geometric reference.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from dataclasses import asdict, dataclass, replace
from typing import Literal

from .toroidal_global_routing import GlobalJunctionPlacement
from .toroidal_incident_bend_audit import AnnularStraightSegment
from .toroidal_junction_bore_passage import (
    BorePassageCertificate,
    JunctionBorePassage,
    build_junction_bore_passage,
    certify_junction_bore_passage,
)
from .toroidal_shared_prefix_fanout import build_shared_prefix_fanout_experiment
from .toroidal_shared_return_connectors import (
    PlacedAnnularTransition,
    _box_signed_separation,
    _connect_edge,
    _nested_transition_gaps,
    _piece_contains,
    _piece_current,
    _validate_interface_geometry,
)
from .toroidal_shared_return_route import RoutedTubePiece
from .toroidal_smooth_bends import AnnularQuarterBend, SmoothGlobalToroidalRouting

Point = tuple[float, float, float]
Geometry = RoutedTubePiece | PlacedAnnularTransition | GlobalJunctionPlacement
PairMethod = Literal["boxes", "coaxial_shells", "shared_straight", "shared_bend",
                     "opposite_caps", "nested_transitions", "unresolved"]
Contact = Literal["none", "transit_interface", "A_port_face", "A_target_circle", "unresolved"]
_TOLERANCE = 1e-10


@dataclass(frozen=True)
class NamedComponent:
    name: str
    geometry: Geometry


@dataclass(frozen=True)
class BoreDownstreamReference:
    current: float
    passage: JunctionBorePassage
    routing: SmoothGlobalToroidalRouting
    pieces: tuple[RoutedTubePiece, ...]
    outlet: PlacedAnnularTransition

    @property
    def flux(self) -> float:
        return self.passage.transit.flux

    @property
    def components(self) -> tuple[NamedComponent, ...]:
        """The partial transit only; original edge 0 is not another path."""
        transit = self.passage.transit
        return (NamedComponent("transit_contract", transit.inlet),
                *(NamedComponent(f"transit_bore_{i}", p) for i, p in enumerate(transit.pieces)),
                NamedComponent("transit_expand", transit.outlet),
                *(NamedComponent(f"downstream_{i:02}", p) for i, p in enumerate(self.pieces)),
                NamedComponent("A_edge0_connector", self.outlet))

    def current_if_inside(self, point) -> Point | None:
        """Select one partial-transit chart; do not evaluate a global network.

        Builder results are audited. A manually replaced candidate must pass
        audit_bore_downstream before this evaluator is used as a reference.
        """
        try:
            point = tuple(float(x) for x in point)
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError("point must have three finite coordinates") from error
        if len(point) != 3 or not all(math.isfinite(x) for x in point):
            raise ValueError("point must have three finite coordinates")
        for component in self.components:
            obj = component.geometry
            inside = obj.contains(point) if isinstance(obj, PlacedAnnularTransition) else _piece_contains(obj, point)
            if inside:
                return _field(obj, point, self.flux)
        return None


@dataclass(frozen=True)
class PairCheck:
    left: str
    right: str
    method: PairMethod
    contact: Contact
    bound: float | None = None
    endpoint_gaps: tuple[float, float] | None = None


@dataclass(frozen=True)
class InterfaceCheck:
    left: str
    right: str
    origin: Point
    axis: Point
    inner_radius: float
    outer_radius: float
    signed_flux: float
    sampled_relative_current_residual: float


@dataclass(frozen=True)
class JacobianBound:
    component: str
    chart: str
    determinant_lower_bound: float
    cartesian_scale_lower_bound: float | None = None


@dataclass(frozen=True)
class JunctionPortAttachment:
    node: str
    edge_index: int
    origin: Point
    outward_normal: Point
    inner_radius: float
    outer_radius: float
    outward_flux: float
    component: str | None


@dataclass(frozen=True)
class OpenBoundary:
    name: str
    origin: Point
    outward_normal: Point
    inner_radius: float
    outer_radius: float
    outward_flux: float


@dataclass(frozen=True)
class BoreDownstreamAudit:
    component_ids: tuple[str, ...]
    retained_component_ids: tuple[str, ...]
    pair_checks: tuple[PairCheck, ...]
    interfaces: tuple[InterfaceCheck, ...]
    jacobians: tuple[JacobianBound, ...]
    junction_ports: tuple[JunctionPortAttachment, ...]
    open_boundaries: tuple[OpenBoundary, ...]
    bore_certificate: BorePassageCertificate

    @property
    def unresolved_pair_count(self) -> int:
        return sum(check.method == "unresolved" for check in self.pair_checks)

    @property
    def net_open_boundary_flux(self) -> float:
        """A zero sum does not connect the two distinct nonzero openings."""
        return math.fsum(boundary.outward_flux for boundary in self.open_boundaries)


def _current(value) -> float:
    if isinstance(value, bool):
        raise ValueError("current must be finite with magnitude greater than 1e-10")
    try:
        value = float(value)
    except (ValueError, TypeError, OverflowError) as error:
        raise ValueError("current must be finite with magnitude greater than 1e-10") from error
    if not math.isfinite(value) or abs(value) <= _TOLERANCE:
        raise ValueError("current must be finite with magnitude greater than 1e-10")
    return value


def _build_reference(current: float) -> BoreDownstreamReference:
    try:
        passage = build_junction_bore_passage(current)
        routing = build_shared_prefix_fanout_experiment(current).original
        host = _connect_edge(routing.edges[1])
        channel = routing.edges[0].route.assembly.channel
        pieces = []
        for piece in host.pieces:
            radii = dict(inner_radius=channel.inner_radius, outer_radius=channel.outer_radius)
            if isinstance(piece.volume, AnnularQuarterBend):
                radii["flux"] = passage.transit.flux
            pieces.append(RoutedTubePiece(replace(piece.volume, **radii)))
        pieces[0] = RoutedTubePiece(replace(pieces[0].volume, start=passage.transit.outlet.end))
        outlet = PlacedAnnularTransition(routing.edges[0].route.assembly.outlet,
                                         host.outlet.origin, host.outlet.axis_sign)
        return BoreDownstreamReference(current, passage, routing, tuple(pieces), outlet)
    except (ArithmeticError, RuntimeError, ValueError) as error:
        raise ValueError(f"current is unsupported by the existing reference builders: {error}") from error


def build_bore_downstream_reference(current: float = 1.0) -> BoreDownstreamReference:
    """Build and audit only the fixed shell-gap-3 downstream partial route."""
    reference = _build_reference(_current(current))
    audit_bore_downstream(reference)
    return reference


def _volume(obj: Geometry):
    return obj.volume if isinstance(obj, RoutedTubePiece) else obj


def _bounds(obj: Geometry):
    if isinstance(obj, GlobalJunctionPlacement):
        c, j = obj.center, obj.junction
        return ((c[0] - j.outer_radius, c[1] - j.outer_radius, c[2] - j.length / 2),
                (c[0] + j.outer_radius, c[1] + j.outer_radius, c[2] + j.length / 2))
    return obj.bounds


def _cap(obj: Geometry, source: bool) -> tuple[Point, Point, float, float]:
    """Cap center, along-chart axis and radii; geometry uses exact axes."""
    v = _volume(obj)
    if isinstance(v, PlacedAnnularTransition):
        side, t = "source" if source else "target", v.transition
        return (v.origin if source else v.end, (0.0, 0.0, float(v.axis_sign)),
                getattr(t, f"{side}_inner_radius"), getattr(t, f"{side}_outer_radius"))
    if isinstance(v, AnnularStraightSegment):
        delta = tuple(b - a for a, b in zip(v.start, v.end, strict=True))
        if sum(x != 0 for x in delta) != 1:
            raise ValueError("fixed reference requires axis-aligned straights")
        axis = tuple(0.0 if x == 0 else math.copysign(1.0, x) for x in delta)
        return v.start if source else v.end, axis, v.inner_radius, v.outer_radius
    if isinstance(v, AnnularQuarterBend):
        return (v.start if source else v.end, v.source_tangent if source else v.target_tangent,
                v.inner_radius, v.outer_radius)
    c, j = v.center, v.junction
    return ((c[0], c[1], c[2] + (-1 if source else 1) * j.length / 2),
            (0.0, 0.0, 1.0), j.inner_radius, j.outer_radius)


def _coaxial_envelope(obj: Geometry):
    v = _volume(obj)
    if isinstance(v, PlacedAnnularTransition):
        t = v.transition
        return (v.origin[:2], min(t.source_inner_radius, t.target_inner_radius),
                max(t.source_outer_radius, t.target_outer_radius))
    if isinstance(v, GlobalJunctionPlacement):
        return v.center[:2], v.junction.inner_radius, v.junction.outer_radius
    if isinstance(v, AnnularStraightSegment) and v.start[:2] == v.end[:2]:
        return v.start[:2], v.inner_radius, v.outer_radius
    return None


def _classify_pair(left: NamedComponent, right: NamedComponent) -> PairCheck:
    a, b = left.geometry, right.geometry
    va, vb = _volume(a), _volume(b)
    names = left.name, right.name
    if isinstance(va, PlacedAnnularTransition) and isinstance(vb, PlacedAnnularTransition):
        if va.origin == vb.origin and va.axis_sign == vb.axis_sign and va.transition.length == vb.transition.length:
            gaps = _nested_transition_gaps(va, vb)
            if min(gaps) > _TOLERANCE:
                return PairCheck(*names, "nested_transitions", "none", endpoint_gaps=gaps)
            if (set(names) == {"A_edge0_connector", "edge1_outlet"}
                    and gaps[0] > _TOLERANCE and gaps[1] == 0.0
                    and va.end == vb.end):
                return PairCheck(*names, "nested_transitions", "A_target_circle", endpoint_gaps=gaps)
    same_straight = (isinstance(va, AnnularStraightSegment) and isinstance(vb, AnnularStraightSegment)
                     and va.start == vb.start and va.end == vb.end)
    same_bend = (isinstance(va, AnnularQuarterBend) and isinstance(vb, AnnularQuarterBend)
                 and all(getattr(va, k) == getattr(vb, k)
                         for k in ("corner", "source_tangent", "target_tangent", "bend_radius")))
    if same_straight or same_bend:
        gap = max(va.inner_radius - vb.outer_radius, vb.inner_radius - va.outer_radius)
        if gap > _TOLERANCE:
            return PairCheck(*names, "shared_straight" if same_straight else "shared_bend", "none", gap)
    ea, eb = _coaxial_envelope(a), _coaxial_envelope(b)
    if ea is not None and eb is not None and ea[0] == eb[0]:
        gap = max(ea[1] - eb[2], eb[1] - ea[2])
        if gap > _TOLERANCE:
            return PairCheck(*names, "coaxial_shells", "none", gap)
    for sa in (True, False):
        for sb in (True, False):
            ca, ta, ia, oa = _cap(a, sa)
            cb, tb, ib, ob = _cap(b, sb)
            na = tuple((-1 if sa else 1) * x for x in ta)
            nb = tuple((-1 if sb else 1) * x for x in tb)
            # Exact centers/axes: a sub-tolerance inward shift is not a proof
            # of opposite support half-planes and must not be accepted here.
            if ca != cb or na != tuple(-x for x in nb):
                continue
            gap = max(ia - ob, ib - oa)
            if gap > _TOLERANCE:
                return PairCheck(*names, "opposite_caps", "none", gap)
            if set(names) == {"A_edge0_connector", "junction_A"}:
                return PairCheck(*names, "opposite_caps", "A_port_face")
            if (ia, oa) == (ib, ob) and not isinstance(va, GlobalJunctionPlacement) and not isinstance(vb, GlobalJunctionPlacement):
                return PairCheck(*names, "opposite_caps", "transit_interface")
    separation = _box_signed_separation(_bounds(a), _bounds(b))
    if separation > _TOLERANCE:
        return PairCheck(*names, "boxes", "none", separation)
    return PairCheck(*names, "unresolved", "unresolved", separation)


def _field(obj: Geometry, point: Point, flux: float) -> Point:
    if isinstance(obj, RoutedTubePiece):
        result = _piece_current(obj, point, flux)
    elif isinstance(obj, PlacedAnnularTransition):
        result = obj.current(point)
    else:
        local = tuple(x - c + d for x, c, d in zip(point, obj.center, obj.junction.center, strict=True))
        result = obj.junction.current(local)
    if not all(math.isfinite(x) for x in result):
        raise ValueError("current field exceeds the resolved finite numerical range")
    return result


def _interface(left: NamedComponent, right: NamedComponent, flux: float, *, junction: bool = False) -> InterfaceCheck:
    a, b = left.geometry, right.geometry
    origin, axis, inner, outer = _cap(a, False)
    if not junction and _cap(b, True) != (origin, axis, inner, outer):
        raise ValueError("partial-route interface position, axis or annulus mismatch")
    for obj in (a, b):
        v = _volume(obj)
        declared = v.transition.flux if isinstance(v, PlacedAnnularTransition) else getattr(v, "flux", flux)
        if declared != flux:
            raise ValueError("partial-route interface signed current mismatch")
    nonzero_axis = next(i for i, x in enumerate(axis) if x != 0)
    first, second = (nonzero_axis + 1) % 3, (nonzero_axis + 2) % 3
    residuals = []
    for q in (0.15, 0.4, 0.7, 0.9):
        for theta in (0.0, 0.7, 2.0):
            point = list(origin)
            radius = inner + q * (outer - inner)
            point[first] += radius * math.cos(theta)
            point[second] += radius * math.sin(theta)
            residuals.extend(abs(x - y) / abs(flux) for x, y in zip(
                _field(a, tuple(point), flux), _field(b, tuple(point), flux), strict=True))
    residual = max(residuals)
    if not math.isfinite(residual) or residual > 1e-8:
        raise ValueError("sampled interface current profiles do not match at resolved scale")
    return InterfaceCheck(left.name, right.name, origin, axis, inner, outer, flux, residual)


def _jacobian(component: NamedComponent) -> JacobianBound:
    v = _volume(component.geometry)
    scale = None
    if isinstance(v, PlacedAnnularTransition):
        t = v.transition
        bound = t.length * min(t.source_inner_radius, t.target_inner_radius) * min(t.source_width, t.target_width)
        chart = "s,q,theta"
    elif isinstance(v, AnnularQuarterBend):
        bound = (v.bend_radius - v.outer_radius) * v.inner_radius * v.width
        scale, chart = v.minimum_jacobian_scale, "phi,q,theta"
    else:
        bound = v.length * v.inner_radius * (v.outer_radius - v.inner_radius)
        chart = "normalized_axial_s,q,theta"
    if not math.isfinite(bound) or bound <= 0 or (scale is not None and scale <= 0):
        raise ValueError("partial-route Jacobian bound must be finite and positive")
    return JacobianBound(component.name, chart, bound, scale)


def audit_bore_downstream(reference: BoreDownstreamReference) -> BoreDownstreamAudit:
    """Reject modified references and unresolved pairs; inventory open faces.

    Clearance arguments use analytic inequalities evaluated in floating point.
    Interface field residuals are finite diagnostics, separately identified.
    Retained/retained pairs are deliberately not certified.
    """
    if not isinstance(reference, BoreDownstreamReference):
        raise ValueError("an explicit BoreDownstreamReference is required")
    expected = _build_reference(_current(reference.current))
    if reference != expected:
        raise ValueError("modified candidate does not match the fixed downstream reference")
    bore_certificate = certify_junction_bore_passage(reference.passage)
    retained = []
    for edge in reference.routing.edges[1:]:
        _validate_interface_geometry(reference.routing, edge)
        connected = _connect_edge(edge)
        retained.extend((NamedComponent(f"edge{edge.edge_index}_inlet", connected.inlet),
                         *(NamedComponent(f"edge{edge.edge_index}_piece_{i:02}", p)
                           for i, p in enumerate(connected.pieces)),
                         NamedComponent(f"edge{edge.edge_index}_outlet", connected.outlet)))
    retained.extend(NamedComponent(f"junction_{j.node}", j) for j in reference.routing.global_routing.junctions)
    components = reference.components
    pairs = tuple(_classify_pair(a, b) for i, a in enumerate(components)
                  for b in (*components[i + 1:], *retained))
    unresolved = [p for p in pairs if p.method == "unresolved"]
    if unresolved:
        raise ValueError(f"{len(unresolved)} unresolved component pairs; first: {unresolved[0].left}/{unresolved[0].right}")
    expected_count = len(components) * (len(components) - 1) // 2 + len(components) * len(retained)
    if len(pairs) != expected_count or len({(p.left, p.right) for p in pairs}) != expected_count:
        raise ValueError("component-pair inventory is incomplete or duplicated")
    interfaces = tuple(_interface(a, b, reference.flux) for a, b in zip(components, components[1:], strict=False))
    placement = reference.routing.global_routing.junction("A")
    original = reference.routing.edges[0].route
    port = placement.junction.port_by_edge(0)
    if (reference.outlet.end != original.target_frame.origin
            or _cap(reference.outlet, False)[1] != original.target_frame.axis
            or _cap(reference.outlet, False)[2:] != (port.inner_radius, port.outer_radius)
            or port.outward_flux != -reference.flux):
        raise ValueError("downstream connector must match A's original edge-0 port")
    interfaces += (_interface(components[-1], NamedComponent("junction_A", placement), reference.flux, junction=True),)
    ports, openings = [], []
    for junction in reference.routing.global_routing.junctions:
        for port in junction.junction.ports:
            if port.edge_index == 0:
                attachment = "A_edge0_connector" if junction.node == "A" else None
            else:
                edge = reference.routing.edges[port.edge_index].route.edge
                side = "inlet" if edge.source == junction.node else "outlet"
                attachment = f"edge{port.edge_index}_{side}"
            normal = (0.0, 0.0, -1.0 if port.face.value == "lower" else 1.0)
            origin = junction.port_axis_point(port.edge_index)
            ports.append(JunctionPortAttachment(junction.node, port.edge_index, origin, normal,
                port.inner_radius, port.outer_radius, port.outward_flux, attachment))
            if attachment is None:
                openings.append(OpenBoundary(f"{junction.node}_edge{port.edge_index}_port", origin, normal,
                    port.inner_radius, port.outer_radius, port.outward_flux))
    inlet = reference.passage.transit.inlet
    openings.append(OpenBoundary("transit_inlet_near_C", inlet.origin, (0.0, 0.0, -float(inlet.axis_sign)),
        inlet.transition.source_inner_radius, inlet.transition.source_outer_radius, -reference.flux))
    if ({b.name for b in openings} != {"B_edge0_port", "transit_inlet_near_C"}
            or len(openings) != 2 or any(b.outward_flux == 0 for b in openings)):
        raise ValueError("fixed partial route must retain exactly its two nonzero open boundaries")
    return BoreDownstreamAudit(tuple(c.name for c in components), tuple(c.name for c in retained), pairs,
        interfaces, tuple(_jacobian(c) for c in components), tuple(ports), tuple(openings), bore_certificate)


def main() -> None:
    reports = []
    for current in (1.0, -1.0):
        audit = audit_bore_downstream(build_bore_downstream_reference(current))
        reports.append({"current": current, "partial_components": len(audit.component_ids),
            "retained_components": len(audit.retained_component_ids), "pair_count": len(audit.pair_checks),
            "pair_methods": dict(Counter(p.method for p in audit.pair_checks)),
            "contact_classes": dict(Counter(p.contact for p in audit.pair_checks)),
            "unresolved_pairs": audit.unresolved_pair_count, "interfaces": len(audit.interfaces),
            "minimum_parameter_jacobian_bound": min(j.determinant_lower_bound for j in audit.jacobians),
            "maximum_sampled_relative_interface_residual": max(i.sampled_relative_current_residual for i in audit.interfaces),
            "open_boundaries": [asdict(b) for b in audit.open_boundaries],
            "net_open_boundary_flux": audit.net_open_boundary_flux})
    print(json.dumps({"scope": "fixed_downstream_partial_route_only",
        "excluded": "retained-retained collisions; upstream attachment; closed graph embedding; motion",
        "boundary_note": "opposite nonzero open-face fluxes do not connect the faces",
        "reports": reports}, indent=2))


if __name__ == "__main__":
    main()
