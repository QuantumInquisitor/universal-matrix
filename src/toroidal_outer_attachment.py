"""Finite rejection probe for an exterior detour, not a global route solver."""

import math
from collections import Counter
from dataclasses import asdict

import numpy as np

from .toroidal_aperture_attachment import build_aperture_attachment
from .toroidal_bore_downstream import (
    NamedComponent,
    _bounds,
    _cap,
    _classify_pair,
    _field,
    _interface,
    _jacobian,
)
from .toroidal_framed_edge_assembly import AnnularPiolaTransition
from .toroidal_incident_bend_audit import AnnularStraightSegment
from .toroidal_shared_return_connectors import PlacedAnnularTransition
from .toroidal_shared_return_route import RoutedTubePiece
from .toroidal_smooth_bends import AnnularQuarterBend


def build_candidate(ref):
    s = ref.sign
    flux = ref.downstream.flux

    def point(p):
        return (p[0], p[1] * s, p[2] * s)

    b = ref.open_boundaries[0]
    items = [
        NamedComponent(
            "B_outer_transition",
            PlacedAnnularTransition(
                AnnularPiolaTransition(b["inner_radius"], b["outer_radius"], 2.0, 2.4, flux, 1.0),
                b["center"],
                int(s),
            ),
        )
    ]

    def straight(name, a, b):
        items.append(
            NamedComponent(
                name, RoutedTubePiece(AnnularStraightSegment(point(a), point(b), 2.0, 2.4))
            )
        )

    def bend(name, corner, a, b):
        items.append(
            NamedComponent(
                name,
                RoutedTubePiece(
                    AnnularQuarterBend(point(corner), point(a), point(b), 5.0, 2.0, 2.4, flux)
                ),
            )
        )

    straight("escape_B", (0, 0, 1.5), (0, 0, 195))
    bend("upper_turn", (0, 0, 200), (0, 0, 1), (1, 0, 0))
    straight("upper_cross", (5, 0, 200), (295, 0, 200))
    bend("outer_turn", (300, 0, 200), (1, 0, 0), (0, 0, -1))
    straight("outer_descent", (300, 0, 195), (300, 0, -75))
    bend("aperture_turn", (300, 0, -80), (0, 0, -1), (-1, 0, 0))
    straight("aperture_feed", (295, 0, -80), (ref.aperture.geometry.volume.start[0], 0, -80))
    return items


def witness(left, right):
    # A found positive penetration is evidence; no hit is NOT clearance.
    if not isinstance(left.geometry, RoutedTubePiece) or not isinstance(
        right.geometry, RoutedTubePiece
    ):
        return None
    v = left.geometry.volume
    fractions = np.linspace(0.0001, 0.9999, 65)
    if isinstance(v, AnnularStraightSegment):
        axis = np.asarray(v.direction)
        start = np.asarray(v.start)
        end = np.asarray(v.end)
        varying = int(np.argmax(abs(end - start)))
        lo, hi = _bounds(right.geometry)
        ta, tb = sorted(
            (
                (lo[varying] - start[varying]) / (end[varying] - start[varying]),
                (hi[varying] - start[varying]) / (end[varying] - start[varying]),
            )
        )
        ta = max(ta, 0.0)
        tb = min(tb, 1.0)
        if tb <= ta:
            return None
        fractions = np.linspace(ta + (tb - ta) * 0.0001, tb - (tb - ta) * 0.0001, 65)
        u = np.eye(3)[(varying + 1) % 3]
        vaxis = np.cross(axis, u)
    for t in fractions:
        for theta in np.arange(24) * 2 * math.pi / 24:
            if isinstance(v, AnnularQuarterBend):
                p = v.map_point(t * math.pi / 2, 0.5, float(theta))
            else:
                p = tuple(
                    start
                    + t * (end - start)
                    + 2.2 * (math.cos(theta) * u + math.sin(theta) * vaxis)
                )
            a = left.geometry.penetration(p)
            b = right.geometry.penetration(p)
            if min(a, b) > 1e-8:
                return dict(point=p, left_penetration=a, right_penetration=b)
    return None


def check_b_port(ref, connector):
    junction = ref.downstream.routing.global_routing.junction("B")
    port = junction.junction.port_by_edge(0)
    center, axis, inner, outer = _cap(connector, True)
    normal = (0.0, 0.0, -1.0 if port.face.value == "lower" else 1.0)
    body_face = junction.center[2] + normal[2] * junction.junction.length / 2
    if (
        center != junction.port_axis_point(0)
        or center[2] != body_face
        or axis != normal
        or (inner, outer) != (port.inner_radius, port.outer_radius)
        or connector.transition.flux != port.outward_flux
        or connector.transition.flux != ref.downstream.flux
        or connector.axis_sign != int(normal[2])
        or connector.transition.length <= 0
    ):
        raise ValueError(
            "B connector must match its exact oriented annular source face and signed flux"
        )
    # Positive length places the entire connector outside the body's support plane.
    # The identical source annulus and zero smoothstep derivative at s=0 give
    # the same axial profile; independent sampled vectors check the implementation.
    residuals = []
    for q in (0.13, 0.47, 0.82):
        for theta in (0.2, 1.1, 2.7, 4.8):
            p = connector.map_point(0.0, q, theta)
            expected = np.asarray(_field(junction, p, ref.downstream.flux))
            actual = np.asarray(connector.current(p))
            residuals.append(float(np.linalg.norm(actual - expected) / np.linalg.norm(expected)))
    maximum = max(residuals)
    if maximum > 1e-10:
        raise ValueError("B source field does not match")
    return dict(
        center=center,
        normal=normal,
        inner_radius=inner,
        outer_radius=outer,
        signed_flux=port.outward_flux,
        maximum_relative_vector_residual=maximum,
        support_plane="connector and junction interiors are on opposite sides of exact port plane",
    )


def physical_cut(field, center, axis, inner, outer):
    axis = np.asarray(axis, dtype=float)
    u = np.eye(3)[(np.argmax(abs(axis)) + 1) % 3]
    u -= axis * np.dot(u, axis)
    u /= np.linalg.norm(u)
    v = np.cross(axis, u)
    roots, weights = np.polynomial.legendre.leggauss(12)
    terms = []
    for x, w in zip(roots, weights, strict=True):
        r = inner + (x + 1) * (outer - inner) / 2
        for theta in np.arange(24) * 2 * math.pi / 24:
            p = np.asarray(center) + r * (math.cos(theta) * u + math.sin(theta) * v)
            terms.append(
                float(np.dot(field(p), axis)) * r * w * (outer - inner) / 2 * 2 * math.pi / 24
            )
    return math.fsum(terms)


def run(current):
    ref = build_aperture_attachment(current)
    candidate = build_candidate(ref)
    port_check = check_b_port(ref, candidate[0].geometry)
    joins = [
        asdict(_interface(a, b, ref.downstream.flux))
        for a, b in zip(candidate, (*candidate[1:], ref.aperture), strict=True)
    ]
    environment = (*ref.downstream.components, *ref.retained, ref.aperture, *ref.added)
    rows = []
    for i, a in enumerate(candidate):
        for b in (*candidate[i + 1 :], *environment):
            row = asdict(_classify_pair(a, b))
            if a is candidate[0] and b.name == "junction_B":
                row.update(method="exact_B_port_support_plane", contact="B_port_face", bound=0.0)
            if row["method"] == "unresolved":
                found = witness(a, b)
                if found:
                    row["interior_collision_witness"] = found
            rows.append(row)
    collisions = [row for row in rows if "interior_collision_witness" in row]
    unresolved = [row for row in rows if row["method"] == "unresolved"]
    cuts = []
    for item in candidate:
        obj = item.geometry
        if isinstance(obj, PlacedAnnularTransition):
            cut_specs = [
                (
                    (obj.origin[0], obj.origin[1], obj.origin[2] + ref.sign * t),
                    (0.0, 0.0, ref.sign),
                    obj.transition.radius(t, 0.0),
                    obj.transition.radius(t, 1.0),
                )
                for t in (0.0, 0.37, 1.0)
            ]
        else:
            v = obj.volume
            if isinstance(v, AnnularQuarterBend):
                cut_specs = [
                    (v.centerline_point(phi), v.tangent(phi), 2.0, 2.4)
                    for phi in (0.0, 0.31, 0.91, math.pi / 2)
                ]
            else:
                cut_specs = [
                    (
                        tuple(np.asarray(v.start) * (1 - t) + np.asarray(v.end) * t),
                        v.direction,
                        2.0,
                        2.4,
                    )
                    for t in (0.0, 0.37, 1.0)
                ]
        for center, axis, inner, outer in cut_specs:
            measured = physical_cut(
                lambda p, obj=obj: _field(obj, p, ref.downstream.flux), center, axis, inner, outer
            )
            relative = abs(measured - ref.downstream.flux) / abs(ref.downstream.flux)
            if relative > 1e-10:
                raise ValueError("outer-route cut flux mismatch")
            cuts.append(
                dict(
                    component=item.name,
                    center=center,
                    measured_flux=measured,
                    expected_flux=ref.downstream.flux,
                    relative_residual=relative,
                )
            )
    if len(rows) != 508 or len({(r["left"], r["right"]) for r in rows}) != 508:
        raise ValueError("outer pair inventory incomplete")
    return dict(
        current=current,
        proposal="fixed exterior detour: z=200 sign(I), x=300, R=5",
        components=[dict(name=p.name, geometry=asdict(p.geometry)) for p in candidate],
        internal_and_aperture_interfaces=joins,
        pair_count=len(rows),
        pairs=rows,
        methods=dict(Counter(r["method"] for r in rows)),
        collision_count=len(collisions),
        unresolved_count=len(unresolved),
        candidate_accepted=not unresolved and not collisions,
        verdict="local_outer_attachment_passes"
        if not unresolved and not collisions
        else "not_certified",
        B_port_check=port_check,
        physical_cuts=cuts,
        maximum_relative_cut_flux_residual=max(r["relative_residual"] for r in cuts),
        jacobians=[asdict(_jacobian(p)) for p in candidate],
        retained_retained_collisions_resolved=False,
        safe_motion_established=False,
        limits="Analytic box/shell/support-plane inequalities evaluated in floating point, not formal interval arithmetic. Retained edge 2/3 collision remains. Fixed static detour only; no safe opening/deformation or material dynamics.",
    )
