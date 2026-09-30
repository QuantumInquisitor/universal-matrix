"""Connected compliant specimen with localized contacts, not a material solver.

All lengths are dimensionless. Convex hulls offset by balls describe material.
Four hubs replace the excluded common-origin collars; this is a declared new
joint construction, not a recovered rigid hinge or a physical time crystal.
"""

import math
from itertools import combinations

import numpy as np

from .lynchpin_breathing_control import BreathingCycle
from .lynchpin_finite_panel_control import pentagon_coefficients, separation_bound
from .lynchpin_geometry_audit import LYNCHPIN_PANELS
from .lynchpin_relative_motion_control import compliant_rays, reference_rays

HUB_RADIUS = 0.05
BRIDGE_RADIUS = 0.008
BRIDGE_LENGTH = 0.17
ATTACHMENT_RADIUS = 0.08


def bodies():
    """Return six panel cores, four shared hubs and twelve bonded bridges."""
    result = []
    for panel, (i, j) in enumerate(LYNCHPIN_PANELS):
        coefficients = np.zeros((len(pentagon_coefficients(0.15)), 4))
        coefficients[:, [i, j]] = pentagon_coefficients(0.15)
        result.append(
            dict(
                name=f"panel-{panel}",
                kind="panel",
                panel=panel,
                coefficients=coefficients,
                radius=0.01,
            )
        )
    for hub in range(4):
        center = np.eye(4)[hub] * 0.5
        result.append(
            dict(
                name=f"hub-{hub}",
                kind="hub",
                hub=hub,
                coefficients=center[None, :],
                radius=HUB_RADIUS,
            )
        )
    for panel, pair in enumerate(LYNCHPIN_PANELS):
        for hub, other in (pair, pair[::-1]):
            start = np.eye(4)[hub] * 0.5
            tip = start + BRIDGE_LENGTH * np.eye(4)[other]
            result.append(
                dict(
                    name=f"bridge-{panel}-{hub}",
                    kind="bridge",
                    hub=hub,
                    panel=panel,
                    coefficients=np.array([start, tip]),
                    radius=BRIDGE_RADIUS,
                )
            )
    return result


def contact_check(left, right):
    """Reduce each permitted contact to a bounded region plus a separation test.

    A prefix of axis length R-r and its radius-r offset lies inside a radius-R
    joint ball. Similarly a terminal axis length A-r lies inside its attachment
    ball. Separation of the remaining convex pieces rules out contact elsewhere.
    """
    a, b = left["coefficients"].copy(), right["coefficients"].copy()
    if left["kind"] == "bridge" and right["kind"] != "bridge":
        left, right, a, b = right, left, b, a
    if left["kind"] == "hub" and right["kind"] == "bridge" and left["hub"] == right["hub"]:
        return "inside_shared_hub", None, None
    if left["kind"] == "panel" and right["kind"] == "bridge" and left["panel"] == right["panel"]:
        b[1] = b[0] + (b[1] - b[0]) * (1 - (ATTACHMENT_RADIUS - BRIDGE_RADIUS) / BRIDGE_LENGTH)
        return "inside_attachment_ball", a, b
    if left["kind"] == right["kind"] == "bridge" and left["hub"] == right["hub"]:
        fraction = (HUB_RADIUS - BRIDGE_RADIUS) / BRIDGE_LENGTH
        a[0] += fraction * (a[1] - a[0])
        b[0] += fraction * (b[1] - b[0])
        return "inside_shared_hub", a, b
    return "separated", a, b


def _intervals(a, b, radius_sum, dimensions, maximum_depth):
    rays = reference_rays(dimensions)
    speed = (
        (np.max(np.abs(a[:, 3])) + np.max(np.abs(b[:, 3])))
        * math.sqrt(1 - float(rays[0] @ rays[3]) ** 2)
        * math.pi**2
        / 6
    )
    pending, leaves = [(0.0, 1.0, 0)], []
    while pending:
        lo, hi, depth = pending.pop()
        midpoint = (lo + hi) / 2
        rays = compliant_rays(midpoint, dimensions)
        bound = separation_bound(a @ rays, b @ rays)
        margin = bound["lower_bound"] - speed * (hi - lo) / 2 - radius_sum
        if margin > 1e-10:
            leaves.append(
                dict(interval=[lo, hi], status="clear", clearance_lower_bound=float(margin))
            )
        elif bound["witness_distance"] < radius_sum - 1e-10:
            leaves.append(
                dict(
                    interval=[lo, hi],
                    phase=midpoint,
                    status="overlap_witness",
                    witness_distance=bound["witness_distance"],
                )
            )
        elif depth == maximum_depth:
            leaves.append(
                dict(interval=[lo, hi], status="unresolved", clearance_lower_bound=float(margin))
            )
        else:
            pending.extend(((lo, midpoint, depth + 1), (midpoint, hi, depth + 1)))
    return leaves


def audit_connected_cycle(dimensions=3, amplitude=0.1, maximum_depth=10):
    """Audit all 231 pairs across the complete fold and common breathing cycle."""
    reference_rays(dimensions)
    cycle = BreathingCycle(amplitude)
    if (
        isinstance(maximum_depth, bool)
        or not isinstance(maximum_depth, int)
        or not 0 <= maximum_depth <= 12
    ):
        raise ValueError("maximum_depth must be an integer in [0,12]")
    pairs = []
    for left, right in combinations(bodies(), 2):
        contact, a, b = contact_check(left, right)
        leaves = (
            []
            if a is None
            else _intervals(a, b, left["radius"] + right["radius"], dimensions, maximum_depth)
        )
        pairs.append(dict(bodies=[left["name"], right["name"]], contact=contact, leaves=leaves))
    leaves = [leaf for pair in pairs for leaf in pair["leaves"]]
    accepted = all(leaf["status"] == "clear" for leaf in leaves)
    bounds = [leaf["clearance_lower_bound"] for leaf in leaves if leaf["status"] == "clear"]
    return dict(
        dimensions=dimensions,
        breathing_amplitude=cycle.amplitude,
        body_count=22,
        pair_count=len(pairs),
        interval_count=len(leaves),
        accepted=accepted,
        minimum_breathing_separation_bound=(1 - cycle.amplitude) * min(bounds)
        if accepted
        else None,
        pairs=pairs,
        physical_material_validation=False,
        recursive_assembly_validation=False,
        arithmetic="floating-point support and analytic velocity bounds; not interval arithmetic",
    )


def scene(phase, dimensions=3, amplitude=0.1):
    scale = BreathingCycle(amplitude).state(phase)["scale"]
    rays = compliant_rays(phase, dimensions)
    return [
        dict(
            name=body["name"],
            kind=body["kind"],
            vertices=(scale * body["coefficients"] @ rays).tolist(),
            offset_radius=scale * body["radius"],
        )
        for body in bodies()
    ]
