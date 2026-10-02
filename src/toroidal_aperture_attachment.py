"""Fixed opt-in aperture plus inner attachment on the recovered downstream engine.

Two nonzero-flux faces remain open. Retained-retained collisions and motion
are expressly outside the certificate. This module changes no default builder.
"""

import math
from dataclasses import asdict, dataclass

import numpy as np

from .toroidal_aperture_local import Access
from .toroidal_bore_downstream import (
    BoreDownstreamReference,
    NamedComponent,
    _classify_pair,
    _coaxial_envelope,
    _field,
    _interface,
    _jacobian,
    audit_bore_downstream,
    build_bore_downstream_reference,
)
from .toroidal_incident_bend_audit import AnnularStraightSegment
from .toroidal_shared_return_connectors import _connect_edge, _piece_contains
from .toroidal_shared_return_route import RoutedTubePiece
from .toroidal_smooth_bends import AnnularQuarterBend


@dataclass(frozen=True)
class ApertureAttachment:
    downstream: BoreDownstreamReference
    access: Access
    origin: tuple[float, float, float]
    aperture: NamedComponent
    bend: NamedComponent
    straight: NamedComponent
    retained: tuple[NamedComponent, ...]
    host_name: str

    @property
    def sign(self):
        return math.copysign(1.0, self.downstream.current)

    @property
    def host(self):
        return next(item for item in self.retained if item.name == self.host_name)

    @property
    def added(self):
        return self.bend, self.straight

    def local_point(self, point):
        p = np.asarray(point)
        if (
            p.shape != (3,)
            or np.iscomplexobj(p)
            or not np.issubdtype(p.dtype, np.number)
            or not np.all(np.isfinite(p))
        ):
            raise ValueError("point must have three finite real coordinates")
        return (p - self.origin) * (1.0, self.sign, self.sign)

    def modified_host_contains(self, point):
        local = self.local_point(point)
        if not _piece_contains(self.host.geometry, point):
            return False
        return abs(local[2]) > self.access.half_length or self.access.host_contains(local)

    def modified_host_current(self, point):
        """None outside retained host material; exact old field outside patch."""
        local = self.local_point(point)
        if not self.modified_host_contains(point):
            return None
        if abs(local[2]) > self.access.half_length:
            return _field(self.host.geometry, point, 0.6 * self.downstream.current)
        vector = (
            abs(self.downstream.current)
            * self.access.host_current(local)
            * (1.0, self.sign, self.sign)
        )
        return tuple(float(v) for v in vector)

    @property
    def open_boundaries(self):
        junction = self.downstream.routing.global_routing.junction("B")
        port = junction.junction.port_by_edge(0)
        return (
            dict(
                name="B_edge0_port",
                center=junction.port_axis_point(0),
                outward_normal=(0.0, 0.0, -1.0 if port.face.value == "lower" else 1.0),
                inner_radius=port.inner_radius,
                outer_radius=port.outer_radius,
                outward_flux=self.downstream.flux,
            ),
            dict(
                name="aperture_outer_cap",
                center=self.aperture.geometry.volume.start,
                outward_normal=(1.0, 0.0, 0.0),
                inner_radius=2.0,
                outer_radius=2.4,
                outward_flux=-self.downstream.flux,
            ),
        )


def retained_components(downstream):
    retained = []
    for routed in downstream.routing.edges[1:]:
        connected = _connect_edge(routed)
        retained.extend(
            (
                NamedComponent(f"edge{routed.edge_index}_inlet", connected.inlet),
                *(
                    NamedComponent(f"edge{routed.edge_index}_piece_{i:02}", piece)
                    for i, piece in enumerate(connected.pieces)
                ),
                NamedComponent(f"edge{routed.edge_index}_outlet", connected.outlet),
            )
        )
    retained.extend(
        NamedComponent(f"junction_{j.node}", j) for j in downstream.routing.global_routing.junctions
    )
    return tuple(retained)


def build_aperture_attachment(current=1.0):
    downstream = build_bore_downstream_reference(current)
    sign = math.copysign(1.0, downstream.current)
    access = Access(sign=sign)
    c = downstream.passage.junction.center[0]
    origin = (c, 0.0, -80 * sign)
    aperture = NamedComponent(
        "aperture_transit",
        RoutedTubePiece(
            AnnularStraightSegment(
                (c + access.transit_outside_x, 0.0, origin[2]),
                (c + access.transit_inside_x, 0.0, origin[2]),
                2.0,
                2.4,
            )
        ),
    )
    bend = NamedComponent(
        "new_core_quarter_bend",
        RoutedTubePiece(
            AnnularQuarterBend(
                origin,
                (-1.0, 0.0, 0.0),
                (0.0, 0.0, sign),
                access.transit_inside_x,
                2.0,
                2.4,
                downstream.flux,
            )
        ),
    )
    straight = NamedComponent(
        "new_core_axial_straight",
        RoutedTubePiece(
            AnnularStraightSegment(
                bend.geometry.volume.end, downstream.passage.transit.inlet.origin, 2.0, 2.4
            )
        ),
    )
    retained = retained_components(downstream)
    host_name = f"edge3_piece_{len(_connect_edge(downstream.routing.edges[3]).pieces) - 1:02}"
    result = ApertureAttachment(
        downstream, access, origin, aperture, bend, straight, tuple(retained), host_name
    )
    audit_aperture_attachment(result)
    return result


def audit_aperture_attachment(ref):
    """Conservative fixed-reference geometry gate; rejects unresolved pairs."""
    audit_bore_downstream(ref.downstream)
    if ref.retained != retained_components(ref.downstream):
        raise ValueError("retained inventory does not match downstream source")
    expected_host = (
        f"edge3_piece_{len(_connect_edge(ref.downstream.routing.edges[3]).pieces) - 1:02}"
    )
    if ref.host_name != expected_host:
        raise ValueError("modified host identity changed")
    sign = ref.sign
    c = ref.downstream.passage.junction.center[0]
    if ref.access != Access(sign=sign) or ref.origin != (c, 0.0, -80 * sign):
        raise ValueError("only the reviewed fixed aperture parameters are supported")
    host = ref.host.geometry.volume
    if (
        host.start[:2] != (c, 0.0)
        or host.end[:2] != (c, 0.0)
        or (host.inner_radius, host.outer_radius) != (12.2, 12.6)
    ):
        raise ValueError("host does not match the reviewed enclosing annulus")
    host_z = sorted((sign * host.start[2], sign * host.end[2]))
    if not host_z[0] < -95 < -65 < host_z[1]:
        raise ValueError("aperture patch must lie strictly inside host")
    volume = ref.bend.geometry.volume
    if (
        volume.corner != ref.origin
        or volume.bend_radius != 8.2
        or volume.source_tangent != (-1.0, 0.0, 0.0)
        or volume.target_tangent != (0.0, 0.0, sign)
    ):
        raise ValueError("bend does not match fixed-reference bound")
    if ref.aperture.geometry.volume.start != (c + 16.6, 0.0, -80 * sign):
        raise ValueError("aperture outer face changed")
    interfaces = [
        asdict(_interface(a, b, ref.downstream.flux))
        for a, b in (
            (ref.aperture, ref.bend),
            (ref.bend, ref.straight),
            (ref.straight, ref.downstream.components[0]),
        )
    ]
    envelope = math.hypot(volume.bend_radius, volume.outer_radius)
    gap = ref.access.inner_radius - envelope
    if gap <= 0:
        raise ValueError("whole bend leaves host core")
    environment = (*ref.downstream.components, *ref.retained, ref.aperture)
    pairs = []
    for i, left in enumerate(ref.added):
        for right in (*ref.added[i + 1 :], *environment):
            row = asdict(_classify_pair(left, right))
            if row["method"] == "unresolved" and left is ref.bend:
                shell = _coaxial_envelope(right.geometry)
                if shell is not None and shell[0] == (c, 0.0) and shell[1] > envelope:
                    row.update(
                        method="whole_bend_radial_core_bound",
                        contact="none",
                        bound=shell[1] - envelope,
                    )
            pairs.append(row)
    aperture_pairs = [
        asdict(_classify_pair(ref.aperture, item))
        for item in (*ref.downstream.components, *ref.retained)
        if item.name != ref.host_name
    ]
    if (
        len(ref.retained) != 42
        or len({x.name for x in ref.retained}) != 42
        or len(pairs) != 117
        or len(aperture_pairs) != 56
    ):
        raise ValueError("fixed-reference inventory changed")
    if any(p["method"] == "unresolved" for p in pairs) or any(
        p["method"] != "boxes" or p["contact"] != "none" or p["bound"] <= 0 for p in aperture_pairs
    ):
        raise ValueError("unresolved component clearance")
    return dict(
        interfaces=interfaces,
        inner_pair_count=len(pairs),
        inner_pairs=pairs,
        aperture_pair_count=len(aperture_pairs),
        aperture_pairs=aperture_pairs,
        whole_bend_core_gap=gap,
        aperture_host_gap=ref.access.clearance_bound(),
        jacobians=[asdict(_jacobian(p)) for p in ref.added],
        open_boundaries=ref.open_boundaries,
        full_graph_closed=False,
        retained_collisions_resolved=False,
        safe_motion_established=False,
    )
