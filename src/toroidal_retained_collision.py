"""Audit actual retained geometry. Samples can reject, never certify clearance."""

import math
from collections import Counter
from dataclasses import asdict
from itertools import combinations

import numpy as np

from .toroidal_aperture_attachment import build_aperture_attachment
from .toroidal_bore_downstream import _bounds, _classify_pair
from .toroidal_incident_bend_audit import AnnularStraightSegment
from .toroidal_shared_return_route import RoutedTubePiece
from .toroidal_smooth_bends import AnnularQuarterBend


def find_witness(left, right):
    if not all(isinstance(c.geometry, RoutedTubePiece) for c in (left, right)):
        return None
    v = left.geometry.volume
    fractions = np.linspace(0.001, 0.999, 49)
    if isinstance(v, AnnularStraightSegment):
        start, end = np.asarray(v.start), np.asarray(v.end)
        axis = np.asarray(v.direction)
        k = int(np.argmax(abs(end - start)))
        lo, hi = _bounds(right.geometry)
        a, b = sorted(
            ((lo[k] - start[k]) / (end[k] - start[k]), (hi[k] - start[k]) / (end[k] - start[k]))
        )
        a, b = max(0.0, a), min(1.0, b)
        if b <= a:
            return None
        fractions = np.linspace(a + (b - a) * 0.001, b - (b - a) * 0.001, 49)
        u = np.eye(3)[(k + 1) % 3]
        w = np.cross(axis, u)
    for t in fractions:
        for q in (0.5, 0.2, 0.8):
            for theta in np.arange(32) * 2 * math.pi / 32:
                if isinstance(v, AnnularQuarterBend):
                    p = v.map_point(float(t * math.pi / 2), q, float(theta))
                else:
                    radius = v.inner_radius + q * (v.outer_radius - v.inner_radius)
                    p = tuple(
                        start
                        + t * (end - start)
                        + radius * (math.cos(theta) * u + math.sin(theta) * w)
                    )
                margins = (left.geometry.penetration(p), right.geometry.penetration(p))
                if min(margins) > 1e-8:
                    return dict(
                        point=[float(x) for x in p], penetration=[float(x) for x in margins]
                    )
    return None


def run(current):
    ref = build_aperture_attachment(current)
    checks, collisions, unknown = [], [], []
    for left, right in combinations(ref.retained, 2):
        check = _classify_pair(left, right)
        checks.append(asdict(check))
        if check.method != "unresolved":
            continue
        hit = find_witness(left, right)
        if hit is None:
            hit = find_witness(right, left)
            if hit:
                hit["penetration"].reverse()
        pair = dict(left=left.name, right=right.name)
        if hit:
            # The aperture changes only this named host in the local patch.
            if ref.host_name in (left.name, right.name) and not ref.modified_host_contains(
                hit["point"]
            ):
                unknown.append(
                    dict(**pair, reason="sample falls in removed aperture; further search required")
                )
            else:
                collisions.append(dict(**pair, **hit))
        else:
            unknown.append(
                dict(
                    **pair,
                    reason="analytic classifier unresolved; no sampled witness is not clearance",
                )
            )
    return dict(
        current=current,
        routing_source="shared_prefix_experiment.original",
        component_count=len(ref.retained),
        pair_count=len(checks),
        methods=dict(Counter(c["method"] for c in checks)),
        collisions=collisions,
        unresolved_without_witness=unknown,
        checks=checks,
        full_geometry_clear=False,
    )
