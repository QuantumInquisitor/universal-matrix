"""Spherical tensor projection and virtual-work identities, not concrete M4.

Stress is in Pa and infinitesimal symmetric strain is dimensionless. The
stress/strain pairing has units Pa = J/m^3; it is virtual work, not stored
energy unless a separate constitutive law and loading path establish that.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass

import numpy as np


def _real_array(value, name: str) -> np.ndarray:
    try:
        array = np.asarray(value)
        if array.dtype.kind not in "iuf":
            raise ValueError(f"{name} must be real numeric data")
        array = np.array(array, dtype=float, copy=True)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{name} must be finite real numeric data") from error
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must be finite real numeric data")
    return array


def _symmetric_tensor(value, name: str) -> np.ndarray:
    array = _real_array(value, name)
    if array.shape != (3, 3):
        raise ValueError(f"{name} must be a symmetric 3 by 3 tensor")
    scale = float(np.max(np.abs(array)))
    normalized = array / scale if scale else array
    if np.max(np.abs(normalized - normalized.T)) > 1e-12:
        raise ValueError(f"{name} must be symmetric")
    # Preserve equal entries, including the smallest subnormal; halving those
    # before summing would silently erase valid symmetric input.
    unequal = array != array.T
    symmetric = array.copy()
    symmetric[unequal] = 0.5 * array[unequal] + 0.5 * array.T[unequal]
    return symmetric


def _finite_product(*factors: float) -> float:
    """Scale a small scalar product without spurious intermediate overflow."""
    if any(factor == 0.0 for factor in factors):
        return 0.0
    mantissa, exponent = 1.0, 0
    for factor in factors:
        part, power = math.frexp(factor)
        mantissa *= part
        exponent += power
    try:
        result = math.ldexp(mantissa, exponent)
    except OverflowError as error:
        raise ValueError("work density exceeds finite numerical range") from error
    if not math.isfinite(result) or result == 0.0:
        raise ValueError("work density exceeds resolved numerical range")
    return result


@dataclass(frozen=True)
class OrientationQuadrature:
    """Unit directions with positive weights for a normalized sphere average."""

    normals: np.ndarray
    weights: np.ndarray

    def __post_init__(self) -> None:
        normals = _real_array(self.normals, "normals")
        weights = _real_array(self.weights, "weights")
        if normals.ndim != 2 or normals.shape[1] != 3 or not len(normals):
            raise ValueError("normals must be a nonempty N by 3 array")
        if weights.shape != (len(normals),) or np.any(weights <= 0.0):
            raise ValueError("each normal needs a positive weight")
        if np.any(np.abs(normals) > 1.0 + 1e-12):
            raise ValueError("normals must have unit length")
        if not np.allclose(np.sum(normals * normals, axis=1), 1.0, rtol=0, atol=1e-12):
            raise ValueError("normals must have unit length")
        if np.any(weights > 1.0) or not math.isclose(math.fsum(weights), 1.0, rel_tol=0, abs_tol=1e-12):
            raise ValueError("normalized spherical weights must sum to one")
        normals.setflags(write=False)
        weights.setflags(write=False)
        object.__setattr__(self, "normals", normals)
        object.__setattr__(self, "weights", weights)


def spherical_quadrature(polar_order: int = 4, azimuthal_order: int = 12) -> OrientationQuadrature:
    """Gauss-Legendre in z=cos(theta), uniform periodic azimuth; not the M4 rule."""
    if type(polar_order) is not int or polar_order < 2:
        raise ValueError("polar_order must be an integer at least two")
    if type(azimuthal_order) is not int or azimuthal_order < 4:
        raise ValueError("azimuthal_order must be an integer at least four")
    z, polar_weights = np.polynomial.legendre.leggauss(polar_order)
    phi = 2.0 * math.pi * (np.arange(azimuthal_order) + 0.173) / azimuthal_order
    radius = np.sqrt(np.maximum(0.0, 1.0 - z * z))
    normals = np.stack((radius[:, None] * np.cos(phi),
                        radius[:, None] * np.sin(phi),
                        np.broadcast_to(z[:, None], (polar_order, azimuthal_order))), axis=-1)
    weights = np.broadcast_to(polar_weights[:, None] / (2.0 * azimuthal_order),
                              (polar_order, azimuthal_order))
    return OrientationQuadrature(normals.reshape(-1, 3), weights.ravel())


@dataclass(frozen=True)
class PlaneProjection:
    traction_pa: np.ndarray
    strain_vector: np.ndarray
    normal_stress_pa: np.ndarray
    normal_strain: np.ndarray
    tangent_stress_pa: np.ndarray
    tangent_strain: np.ndarray


def project_tensors(stress_pa, strain, quadrature: OrientationQuadrature) -> PlaneProjection:
    """Project sigma@n and epsilon@n, with basis-independent tangential parts.

    epsilon is tensorial strain, so epsilon_xy = engineering gamma_xy / 2.
    No constitutive law is applied to the prescribed stress and strain.
    """
    stress = _symmetric_tensor(stress_pa, "stress")
    strain = _symmetric_tensor(strain, "strain")
    if not isinstance(quadrature, OrientationQuadrature):
        raise ValueError("an explicit OrientationQuadrature is required")
    normals = quadrature.normals
    try:
        with np.errstate(over="raise", invalid="raise", under="raise"):
            traction = normals @ stress.T
            vector = normals @ strain.T
            normal_stress = np.sum(normals * traction, axis=1)
            normal_strain = np.sum(normals * vector, axis=1)
            tangent_stress = traction - normal_stress[:, None] * normals
            tangent_strain = vector - normal_strain[:, None] * normals
    except FloatingPointError as error:
        raise ValueError("projection exceeds resolved numerical range") from error
    if not all(np.all(np.isfinite(item)) for item in
               (traction, vector, normal_stress, normal_strain, tangent_stress, tangent_strain)):
        raise ValueError("projection exceeds finite numerical range")
    return PlaneProjection(traction, vector, normal_stress, normal_strain,
                           tangent_stress, tangent_strain)


@dataclass(frozen=True)
class ProjectionAudit:
    directions: int
    weight_sum: float
    first_moment_error: float
    second_moment_error: float
    fourth_moment_error: float
    direct_work_density_pa: float
    normal_work_density_pa: float
    tangent_work_density_pa: float
    projected_work_density_pa: float
    relative_work_error: float
    relative_stress_reconstruction_error: float
    reconstructed_stress_pa: np.ndarray


def audit_projection(stress_pa, strain, quadrature: OrientationQuadrature) -> ProjectionAudit:
    """Check orientation moments, stress reconstruction and virtual work.

    Errors use the Frobenius stress/strain norms, not the possibly zero work.
    Normal and tangential work contributions include the sphere factor three.
    A finite rule need not be isotropic; its errors are reported, not hidden.
    """
    stress = _symmetric_tensor(stress_pa, "stress")
    strain = _symmetric_tensor(strain, "strain")
    if not isinstance(quadrature, OrientationQuadrature):
        raise ValueError("an explicit OrientationQuadrature is required")
    stress_scale = float(np.max(np.abs(stress))) or 1.0
    strain_scale = float(np.max(np.abs(strain))) or 1.0
    normalized_stress, normalized_strain = stress / stress_scale, strain / strain_scale
    projection = project_tensors(normalized_stress, normalized_strain, quadrature)
    normals, weights = quadrature.normals, quadrature.weights
    first = np.einsum("p,pi->i", weights, normals)
    second = np.einsum("p,pi,pj->ij", weights, normals, normals)
    fourth = np.einsum("p,pi,pj,pk,pl->ijkl", weights, normals, normals, normals, normals)
    identity = np.eye(3)
    exact_fourth = (np.einsum("ij,kl->ijkl", identity, identity)
                    + np.einsum("ik,jl->ijkl", identity, identity)
                    + np.einsum("il,jk->ijkl", identity, identity)) / 15.0
    reconstructed = 3.0 * np.einsum("p,pi,pj->ij", weights, projection.traction_pa, normals)
    reconstructed = 0.5 * reconstructed + 0.5 * reconstructed.T
    direct = float(np.sum(normalized_stress * normalized_strain))
    normal_work = 3.0 * float(np.dot(weights, projection.normal_stress_pa * projection.normal_strain))
    tangent_work = 3.0 * float(np.dot(weights, np.sum(projection.tangent_stress_pa
                                                    * projection.tangent_strain, axis=1)))
    projected = normal_work + tangent_work
    stress_norm, strain_norm = np.linalg.norm(normalized_stress), np.linalg.norm(normalized_strain)
    work_scale = float(stress_norm * strain_norm)
    work_error = abs(projected - direct) / work_scale if work_scale else 0.0
    stress_error = float(np.linalg.norm(reconstructed - normalized_stress) / stress_norm) if stress_norm else 0.0
    try:
        with np.errstate(over="raise", invalid="raise", under="raise"):
            physical_reconstruction = reconstructed * stress_scale
    except FloatingPointError as error:
        raise ValueError("reconstructed stress exceeds resolved numerical range") from error
    return ProjectionAudit(len(normals), math.fsum(weights), float(np.max(np.abs(first))),
        float(np.max(np.abs(second - identity / 3.0))),
        float(np.max(np.abs(fourth - exact_fourth))),
        *(_finite_product(value, stress_scale, strain_scale)
          for value in (direct, normal_work, tangent_work, projected)),
        work_error, stress_error, physical_reconstruction)


def main() -> None:
    stress = np.array(((12.0, 3.0, -2.0), (3.0, -5.0, 4.0), (-2.0, 4.0, 8.0))) * 1e6
    strain = np.array(((2.0, 0.5, -0.25), (0.5, -1.0, 0.2), (-0.25, 0.2, 0.75))) * 1e-4
    reports = []
    for polar, azimuthal in ((2, 4), (3, 8), (4, 12)):
        audit = audit_projection(stress, strain, spherical_quadrature(polar, azimuthal))
        reports.append({"orders": [polar, azimuthal], "directions": audit.directions,
                        "weight_sum": audit.weight_sum, "first_moment_error": audit.first_moment_error,
                        "second_moment_error": audit.second_moment_error,
                        "fourth_moment_error": audit.fourth_moment_error,
                        "direct_work_density_J_per_m3": audit.direct_work_density_pa,
                        "relative_work_error": audit.relative_work_error,
                        "relative_stress_error": audit.relative_stress_reconstruction_error})
    print(json.dumps({"scope": "tensor_projection_and_virtual_work_identity_only",
                      "quadrature": "normalized_sphere_Gauss_Legendre_times_periodic_azimuth",
                      "material_calibration": "none", "reports": reports}, indent=2))


if __name__ == "__main__":
    main()
