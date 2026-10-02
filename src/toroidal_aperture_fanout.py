"""Fixed edge-2 replacement and rotated host aperture; no whole-network motion claim."""

import math
from collections import Counter
from dataclasses import asdict
from itertools import combinations

import numpy as np

from .toroidal_aperture_attachment import build_aperture_attachment
from .toroidal_aperture_local import Access
from .toroidal_bore_downstream import (
    NamedComponent,
    _cap,
    _classify_pair,
    _field,
    _interface,
    _jacobian,
)
from .toroidal_framed_edge_assembly import AnnularPiolaTransition
from .toroidal_incident_bend_audit import AnnularStraightSegment
from .toroidal_outer_attachment import build_candidate as build_outer
from .toroidal_retained_collision import find_witness
from .toroidal_shared_return_connectors import (
    PlacedAnnularTransition,
    _connect_edge,
    _nested_transition_gaps,
    _piece_contains,
)
from .toroidal_shared_return_route import RoutedTubePiece
from .toroidal_smooth_bends import AnnularQuarterBend


class SecondAperture:
    """Proper rotation of the tested local host chart, centered on A's leg."""

    def __init__(self, ref):
        self.ref = ref
        self.access = Access(sign=ref.sign)
        self.origin = np.array(
            (ref.downstream.routing.edges[2].route.source_frame.origin[0], 0.0, 80 * ref.sign)
        )
        self.rotation = np.array(((0.0, ref.sign, 0.0), (-1.0, 0.0, 0.0), (0.0, 0.0, ref.sign)))
        self.host = next(c for c in ref.retained if c.name == "edge3_piece_00")
        # A rigid proper rotation preserves divergence and physical area.
        if np.linalg.det(self.rotation) != 1.0:
            raise ValueError("orientation must be preserved")
        for z in (-15.0, 15.0):
            if self.host.geometry.penetration(self.to_global((12.4, 0.0, z))) <= 0:
                raise ValueError("patch must be strictly inside the host leg")

    def to_global(self, point):
        return self.origin + self.rotation @ np.asarray(point)

    def to_local(self, point):
        p = np.asarray(point)
        if (
            p.shape != (3,)
            or np.iscomplexobj(p)
            or not np.issubdtype(p.dtype, np.number)
            or not np.all(np.isfinite(p))
        ):
            raise ValueError("point must have three finite real coordinates")
        return self.rotation.T @ (p - self.origin)

    def contains(self, point):
        local = self.to_local(point)
        return _piece_contains(self.host.geometry, point) and (
            abs(local[2]) > 15 or self.access.host_contains(local)
        )

    def current(self, point):
        local = self.to_local(point)
        if not self.contains(point):
            return None
        if abs(local[2]) > 15:
            return _field(self.host.geometry, point, 0.6 * self.ref.downstream.current)
        return abs(self.ref.downstream.current) * (self.rotation @ self.access.host_current(local))


def check_port(ref, connector, node, source):
    junction = ref.downstream.routing.global_routing.junction(node)
    port = junction.junction.port_by_edge(2)
    center, axis, inner, outer = _cap(connector, source)
    normal = (0.0, 0.0, -1.0 if port.face.value == "lower" else 1.0)
    expected_axis = normal if source else tuple(-x for x in normal)
    expected_flux = port.outward_flux if source else -port.outward_flux
    if (
        center != junction.port_axis_point(2)
        or axis != expected_axis
        or center[2] != junction.center[2] + normal[2] * junction.junction.length / 2
        or (inner, outer) != (port.inner_radius, port.outer_radius)
        or connector.transition.flux != expected_flux
        or connector.transition.length <= 0
    ):
        raise ValueError("replacement must preserve exact oriented edge 2 port")
    errors = []
    for q in (0.13, 0.47, 0.82):
        for theta in (0.2, 1.1, 2.7, 4.8):
            radius = inner + q * (outer - inner)
            p = (
                center[0] + radius * math.cos(theta),
                center[1] + radius * math.sin(theta),
                center[2],
            )
            errors.append(
                max(
                    abs(a - b) / abs(expected_flux)
                    for a, b in zip(
                        connector.current(p), _field(junction, p, expected_flux), strict=True
                    )
                )
            )
    if max(errors) > 1e-10:
        raise ValueError("port current profile mismatch")
    return dict(method="exact_port_support_plane", relative_vector_residual=max(errors))


def build_candidate(ref):
    s = ref.sign

    # Original retained lanes stay at positive y for both current signs.
    # Keep the detour at negative y; current reversal is not a whole-scene rotation.
    def p(a):
        return (a[0], a[1], s * a[2])

    old = _connect_edge(ref.downstream.routing.edges[2])
    x = old.inlet.origin[0]
    flux = old.flux
    items = [
        NamedComponent(
            "replacement2_inlet",
            PlacedAnnularTransition(
                AnnularPiolaTransition(0.5, 1.0, 2.0, 2.4, flux, 1.0), old.inlet.origin, int(s)
            ),
        )
    ]

    def straight(name, a, b):
        items.append(
            NamedComponent(name, RoutedTubePiece(AnnularStraightSegment(p(a), p(b), 2.0, 2.4)))
        )

    def bend(name, c, a, b, r=5.0):
        items.append(
            NamedComponent(
                name, RoutedTubePiece(AnnularQuarterBend(p(c), p(a), p(b), r, 2.0, 2.4, flux))
            )
        )

    straight("A_core", (x, 0, 1.5), (x, 0, 71.8))
    bend("A_core_turn", (x, 0, 80), (0, 0, 1), (0, -1, 0), 8.2)
    straight("A_aperture", (x, -8.2, 80), (x, -16.6, 80))
    straight("A_escape", (x, -16.6, 80), (x, -95, 80))
    bend("negative_y_turn", (x, -100, 80), (0, -1, 0), (0, 0, -1))
    straight("negative_y_descent", (x, -100, 75), (x, -100, -295))
    bend("lower_x_turn", (x, -100, -300), (0, 0, -1), (1, 0, 0))
    straight("lower_x_cross", (x + 5, -100, -300), (-5, -100, -300))
    bend("lower_y_turn", (0, -100, -300), (1, 0, 0), (0, 1, 0))
    straight("lower_y_cross", (0, -95, -300), (0, -5, -300))
    bend("B_return_turn", (0, 0, -300), (0, 1, 0), (0, 0, 1))
    straight("B_return", (0, 0, -295), (0, 0, -1.5))
    items.append(
        NamedComponent(
            "replacement2_outlet",
            PlacedAnnularTransition(
                AnnularPiolaTransition(2.0, 2.4, 0.5, 1.5, flux, 1.0, z_start=2.0),
                old.outlet.origin,
                int(s),
            ),
        )
    )
    return items


def run(current):
    ref = build_aperture_attachment(current)
    items = build_candidate(ref)
    patch = SecondAperture(ref)
    ports = {
        "replacement2_inlet": check_port(ref, items[0].geometry, "A", True),
        "replacement2_outlet": check_port(ref, items[-1].geometry, "B", False),
    }
    environment = [c for c in ref.retained if not c.name.startswith("edge2_")]
    environment += list(ref.downstream.components) + [ref.aperture, *ref.added] + build_outer(ref)
    interfaces = [_interface(a, b, 0.4 * current) for a, b in zip(items, items[1:], strict=False)]
    checks = []
    unresolved = []
    witnesses = []
    for a, b in [*combinations(items, 2), *((a, b) for a in items for b in environment)]:
        check = _classify_pair(a, b)
        record = asdict(check)
        if check.method == "unresolved":
            if (a.name, b.name) in (
                ("replacement2_inlet", "junction_A"),
                ("replacement2_outlet", "junction_B"),
            ):
                record.update(
                    method="exact_port_support_plane",
                    contact="edge2_port_face",
                    proof=ports[a.name],
                )
            elif (a.name, b.name) == ("replacement2_inlet", "edge3_inlet"):
                gaps = _nested_transition_gaps(a.geometry, b.geometry)
                if gaps[0] != 0 or gaps[1] <= 0:
                    raise ValueError("nested source contact changed")
                record.update(
                    method="nested_smoothstep",
                    contact="A_source_circle",
                    endpoint_gaps=gaps,
                    proof="gap=9.8*(3*s^2-2*s^3), strictly positive for 0<s<=1",
                )
            elif (a.name, b.name) == ("A_core_turn", "edge3_piece_00"):
                bound = 12.2 - math.hypot(8.2, 2.4)
                if bound <= 0:
                    raise ValueError("bend leaves host core")
                record.update(method="whole_bend_core_envelope", contact="none", bound=bound)
            elif (a.name, b.name) == ("A_aperture", "edge3_piece_00"):
                record.update(
                    method="rotated_aperture_clearance",
                    contact="none",
                    bound=patch.access.clearance_bound(),
                )
        checks.append(record)
        if record["method"] == "unresolved":
            hit = find_witness(a, b)
            if hit:
                witnesses.append(dict(left=a.name, right=b.name, **hit))
            else:
                unresolved.append(dict(left=a.name, right=b.name))
    return dict(
        current=current,
        component_count=len(items),
        environment_count=len(environment),
        pair_count=len(checks),
        methods=dict(Counter(c["method"] for c in checks)),
        interfaces=[asdict(i) for i in interfaces],
        jacobians=[asdict(_jacobian(c)) for c in items],
        raw_host_intersections=witnesses,
        unresolved=unresolved,
        certified=not unresolved and not witnesses,
        certificate_scope="fixed replacement route pairs; floating point analytic bounds, not interval arithmetic",
        second_aperture_origin=patch.origin.tolist(),
        second_aperture_rotation=patch.rotation.tolist(),
        full_network_certified=False,
        motion_certified=False,
        checks=checks,
    )
