"""Equal-weight finite point-pattern descriptors; no material scattering model."""

import numpy as np


def _points(value, name):
    if np.iscomplexobj(value):
        raise ValueError(f"{name} must be real")
    array = np.asarray(value, dtype=float)
    if array.ndim != 2 or array.shape[1] != 3 or len(array) == 0:
        raise ValueError(f"{name} must be a nonempty Nx3 array")
    if not np.isfinite(array).all():
        raise ValueError(f"{name} must be finite")
    return array


def structure_factor(points_m, wavevectors_rad_m):
    """Return |sum exp(i k.r)|²/N for declared equal unit weights.

    Coordinates and reciprocal vectors must use reciprocal units. A value is a
    finite geometric descriptor, not a measured diffraction intensity.
    """
    points = _points(points_m, "points")
    wavevectors = _points(wavevectors_rad_m, "wavevectors")
    phases = wavevectors @ points.T
    amplitude = np.exp(1j * phases).sum(axis=1)
    return (np.abs(amplitude) ** 2 / len(points)).real


def exact_unique_population(points_m, identities):
    """Deduplicate exact float-coordinate tuples, retaining every owner identity.

    No geometric tolerance or mass interpretation is introduced. Signed zero
    has equal numeric identity; nearly coincident coordinates remain separate.
    """
    points = _points(points_m, "points")
    if len(identities) != len(points) or len(set(identities)) != len(identities):
        raise ValueError("one unique identity per occurrence is required")
    owners = {}
    for point, identity in zip(points, identities, strict=True):
        owners.setdefault(tuple(point), []).append(identity)
    return np.array(list(owners)), list(owners.values())


def pair_distances(points_m):
    """All unordered pair distances, including exact coincident occurrences."""
    points = _points(points_m, "points")
    left, right = np.triu_indices(len(points), k=1)
    return np.linalg.norm(points[left] - points[right], axis=1)
