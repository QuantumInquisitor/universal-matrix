"""Fixed-angle rigidity and a declared two-panel compliant motion control.

Uses the repository's four common-origin rays and six panel incidences.
Ray motion is not a finite-thickness panel or material model.
"""

from __future__ import annotations

import math

import numpy as np

from .lynchpin_geometry_audit import LYNCHPIN_PANELS, PENTAGON_INTERIOR_COSINE


def reference_rays(dimensions: int = 3) -> np.ndarray:
    if isinstance(dimensions, bool) or dimensions not in (3, 4):
        raise ValueError("reference dimension must be 3 or 4")
    if dimensions == 3:
        return np.array(((1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1))) / math.sqrt(3)
    cosine = float(PENTAGON_INTERIOR_COSINE)
    gram = (1 - cosine) * np.eye(4) + cosine * np.ones((4, 4))
    return np.linalg.cholesky(gram)


def constraint_jacobian(rays: np.ndarray, panels=LYNCHPIN_PANELS) -> np.ndarray:
    """Derivatives of four squared lengths and the selected panel dot products."""
    rays = np.asarray(rays, dtype=float)
    if rays.ndim != 2 or rays.shape[0] != 4 or not np.all(np.isfinite(rays)):
        raise ValueError("four finite ray vectors required")
    rows = []
    for i in range(4):
        row = np.zeros_like(rays)
        row[i] = 2 * rays[i]
        rows.append(row.ravel())
    for i, j in panels:
        row = np.zeros_like(rays)
        row[i], row[j] = rays[j], rays[i]
        rows.append(row.ravel())
    return np.array(rows)


def rigidity_report(dimensions: int = 3) -> dict:
    rays = reference_rays(dimensions)
    matrix = constraint_jacobian(rays)
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    rank = int(np.count_nonzero(singular_values > 1e-10))
    rotations = []
    for a in range(dimensions):
        for b in range(a + 1, dimensions):
            generator = np.zeros((dimensions, dimensions))
            generator[a, b], generator[b, a] = 1, -1
            rotations.append((rays @ generator.T).ravel())
    rotation_rank = int(np.linalg.matrix_rank(np.array(rotations).T, tol=1e-10))
    nullity = rays.size - rank
    return dict(
        dimensions=dimensions,
        constraint_rank=rank,
        nullity=nullity,
        rigid_rotation_modes=rotation_rank,
        internal_first_order_modes=nullity - rotation_rank,
        singular_values=singular_values.tolist(),
        scope="fixed unit rays, common origin, all six fixed panel angles",
    )


def compliant_rays(phase: float, dimensions: int = 3, amplitude: float = math.pi / 6) -> np.ndarray:
    """Out-and-back ray-3 motion; panels 13 and 23 must change corner angle.

    The pi/6 amplitude is an explicit test input, not a recovered hinge range.
    No recursive phase or elapsed physical time is inferred from this phase.
    """
    if isinstance(phase, (bool, complex)) or isinstance(amplitude, (bool, complex)):
        raise ValueError("phase and amplitude must be finite real scalars")
    phase, amplitude = float(phase), float(amplitude)
    if (
        not math.isfinite(phase)
        or not 0 <= phase <= 1
        or not math.isfinite(amplitude)
        or not 0 < amplitude <= math.pi / 6
    ):
        raise ValueError("phase in [0,1] and amplitude in (0,pi/6] required")
    rays = reference_rays(dimensions)
    axis = rays[0]
    cosine = float(rays[3] @ axis)
    u = rays[3] - cosine * axis
    radius = np.linalg.norm(u)
    u /= radius
    w = rays[1] - (rays[1] @ axis) * axis - (rays[1] @ u) * u
    w /= np.linalg.norm(w)
    angle = 0.0 if phase in (0.0, 1.0) else amplitude * math.sin(math.pi * phase) ** 2
    rays[3] = cosine * axis + radius * (math.cos(angle) * u + math.sin(angle) * w)
    return rays


def panel_angles(rays: np.ndarray) -> dict:
    return {
        f"{i}{j}": math.degrees(math.acos(float(np.clip(rays[i] @ rays[j], -1, 1))))
        for i, j in LYNCHPIN_PANELS
    }
