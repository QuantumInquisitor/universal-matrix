"""Affine pentagon surfaces and bounded-motion clearance of trimmed panel cores.

The collar is a declared exclusion, not an implemented hinge. Thickness is an
isotropic tubular offset of each core surface. No material or whole-joint claim.
"""

from __future__ import annotations

import math
from itertools import combinations

import numpy as np

from .lynchpin_geometry_audit import LYNCHPIN_PANELS
from .lynchpin_relative_motion_control import compliant_rays, reference_rays


def pentagon_coefficients(collar: float = 0.0) -> np.ndarray:
    if isinstance(collar, (bool, complex)) or not math.isfinite(collar) or not 0 <= collar <= 0.25:
        raise ValueError("collar coefficient must be finite and in [0,.25]")
    vertices = [np.zeros(2)]
    for k in range(4):
        vertices.append(
            vertices[-1] + (math.cos(2 * math.pi * k / 5), math.sin(2 * math.pi * k / 5))
        )
    basis = np.array(((1.0, math.cos(3 * math.pi / 5)), (0.0, math.sin(3 * math.pi / 5))))
    polygon = np.linalg.solve(basis, np.array(vertices).T).T
    polygon[0], polygon[1], polygon[-1] = (0.0, 0.0), (1.0, 0.0), (0.0, 1.0)
    for axis in (0, 1):
        clipped = []
        for a, b in zip(polygon, np.roll(polygon, -1, axis=0), strict=True):
            inside_a, inside_b = a[axis] >= collar, b[axis] >= collar
            if inside_a:
                clipped.append(a)
            if inside_a != inside_b:
                t = (collar - a[axis]) / (b[axis] - a[axis])
                clipped.append(a + t * (b - a))
        polygon = np.array(clipped)
    return polygon


def panel_vertices(phase: float, dimensions: int, panel: int, collar: float = 0.0) -> np.ndarray:
    rays = compliant_rays(phase, dimensions)
    i, j = LYNCHPIN_PANELS[panel]
    return pentagon_coefficients(collar) @ rays[[i, j]]


def deformation_metrics(phase: float, dimensions: int, panel: int) -> dict:
    i, j = LYNCHPIN_PANELS[panel]
    original = reference_rays(dimensions)[[i, j]]
    current = compliant_rays(phase, dimensions)[[i, j]]
    initial_metric = original @ original.T
    metric = current @ current.T
    inverse_cholesky = np.linalg.inv(np.linalg.cholesky(initial_metric))
    stretches = np.sqrt(np.linalg.eigvalsh(inverse_cholesky @ metric @ inverse_cholesky.T))
    return dict(
        principal_stretches=stretches.tolist(),
        area_ratio=float(math.sqrt(np.linalg.det(metric) / np.linalg.det(initial_metric))),
    )


def _simplex(vector):
    ordered = np.sort(vector)[::-1]
    sums = np.cumsum(ordered) - 1
    active = np.where(ordered - sums / np.arange(1, len(vector) + 1) > 0)[0][-1]
    return np.maximum(vector - sums[active] / (active + 1), 0)


def separation_bound(left, right, iterations: int = 160) -> dict:
    """Search for an axis; its vertex support gap is a valid lower bound.

    Optimizer convergence is not trusted as clearance evidence. Regardless of
    convergence, all vertices are projected on the returned unit direction.
    Convexity extends those extrema to the complete polygons.
    """
    left, right = np.asarray(left, dtype=float), np.asarray(right, dtype=float)
    if (
        left.ndim != 2
        or right.ndim != 2
        or left.shape[1] != right.shape[1]
        or not len(left)
        or not len(right)
        or not np.all(np.isfinite(left))
        or not np.all(np.isfinite(right))
    ):
        raise ValueError("finite nonempty vertex arrays of matching dimension required")
    n, m = len(left), len(right)
    matrix = np.concatenate((left.T, -right.T), axis=1)
    lipschitz = 2 * np.linalg.norm(matrix, 2) ** 2
    weights = np.concatenate((np.full(n, 1 / n), np.full(m, 1 / m)))
    momentum, time = weights.copy(), 1.0
    for _ in range(iterations):
        if lipschitz == 0:
            break
        step = momentum - 2 * matrix.T @ (matrix @ momentum) / lipschitz
        updated = np.concatenate((_simplex(step[:n]), _simplex(step[n:])))
        next_time = (1 + math.sqrt(1 + 4 * time * time)) / 2
        momentum = updated + (time - 1) / next_time * (updated - weights)
        weights, time = updated, next_time
    p, q = weights[:n] @ left, weights[n:] @ right
    distance = float(np.linalg.norm(q - p))
    if distance < 1e-14:
        return dict(lower_bound=0.0, witness_distance=distance, axis=None)
    axis = (q - p) / distance
    bound = float(np.min(right @ axis) - np.max(left @ axis))
    return dict(lower_bound=bound, witness_distance=distance, axis=axis.tolist())


def panel_speed_bound(dimensions: int, panel: int, collar: float) -> float:
    i, j = LYNCHPIN_PANELS[panel]
    if 3 not in (i, j):
        return 0.0
    rays = reference_rays(dimensions)
    radius = math.sqrt(1 - float(rays[0] @ rays[3]) ** 2)
    # theta' <= (pi/6)*pi over the whole out-and-back cycle.
    return float(np.max(pentagon_coefficients(collar)[:, 1])) * radius * math.pi**2 / 6


def audit_core_cycle(
    dimensions: int = 3, collar: float = 0.15, thickness: float = 0.02, maximum_depth: int = 10
) -> dict:
    if isinstance(thickness, (bool, complex)) or not math.isfinite(thickness) or thickness <= 0:
        raise ValueError("positive finite total thickness required")
    pentagon_coefficients(collar)
    reference_rays(dimensions)
    if (
        isinstance(maximum_depth, bool)
        or not isinstance(maximum_depth, int)
        or not 0 <= maximum_depth <= 12
    ):
        raise ValueError("maximum_depth must be an integer in [0,12]")
    result = []
    for a, b in combinations(range(6), 2):
        speed = panel_speed_bound(dimensions, a, collar) + panel_speed_bound(dimensions, b, collar)
        pending, leaves = [(0.0, 1.0, 0)], []
        while pending:
            lo, hi, depth = pending.pop()
            midpoint = (lo + hi) / 2
            bound = separation_bound(
                panel_vertices(midpoint, dimensions, a, collar),
                panel_vertices(midpoint, dimensions, b, collar),
            )
            # Each surface's offset radius is thickness/2; subtract their sum.
            continuous = bound["lower_bound"] - speed * (hi - lo) / 2 - thickness
            if continuous > 1e-10:
                leaves.append(
                    dict(interval=[lo, hi], clearance_lower_bound=continuous, status="clear")
                )
            elif bound["witness_distance"] < thickness - 1e-10:
                leaves.append(
                    dict(
                        interval=[lo, hi],
                        phase=midpoint,
                        status="offset_overlap_witness",
                        witness_distance=bound["witness_distance"],
                    )
                )
            elif depth == maximum_depth:
                leaves.append(
                    dict(interval=[lo, hi], status="unresolved", clearance_lower_bound=continuous)
                )
            else:
                pending.extend(((lo, midpoint, depth + 1), (midpoint, hi, depth + 1)))
        result.append(dict(panels=[a, b], leaves=leaves))
    all_leaves = [leaf for pair in result for leaf in pair["leaves"]]
    return dict(
        dimensions=dimensions,
        collar_coefficient=collar,
        total_thickness=thickness,
        pair_count=len(result),
        interval_count=len(all_leaves),
        accepted=all(leaf["status"] == "clear" for leaf in all_leaves),
        minimum_clearance_bound=min(
            (leaf["clearance_lower_bound"] for leaf in all_leaves if leaf["status"] == "clear"),
            default=None,
        ),
        complete_hinge_assembly_certified=False,
        pairs=result,
        arithmetic="floating-point analytic support and velocity bounds; not interval arithmetic",
    )
