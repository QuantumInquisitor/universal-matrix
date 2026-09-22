"""Joint spacing and finite-volume extrapolation for Q-ball Cartesian mapping."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable
import math

import numpy as np

from .qball_mapping_convergence import (
    MappingConvergencePoint,
    MappingGrid,
    audit_mapping_convergence,
)
from .qball_threshold_refinement import (
    refine_energy_per_charge_threshold,
    threshold_bracket,
)


@dataclass(frozen=True)
class JointMappingFit:
    points: tuple[MappingConvergencePoint, ...]
    mu: float
    continuum_infinite_volume_energy_per_charge: float
    spacing_coefficient: float
    tail_coefficient: float
    rms_residual: float
    maximum_absolute_residual: float
    design_condition_number: float
    radial_energy_per_charge: float

    @property
    def extrapolated_above_threshold(self) -> bool:
        return self.continuum_infinite_volume_energy_per_charge > 1.0

    @property
    def relative_difference_from_radial(self) -> float:
        return abs(
            self.continuum_infinite_volume_energy_per_charge
            - self.radial_energy_per_charge
        ) / abs(self.radial_energy_per_charge)


def asymptotic_tail_basis(half_width: float, mu: float) -> float:
    """Return the integrated r^2 exp(-2 mu r) tail basis beyond half_width."""
    if not math.isfinite(half_width) or half_width <= 0:
        raise ValueError("half_width must be finite and positive")
    if not math.isfinite(mu) or mu <= 0:
        raise ValueError("mu must be finite and positive")

    decay = math.exp(-2.0 * mu * half_width)
    return decay * (
        half_width**2 / (2.0 * mu)
        + half_width / (2.0 * mu**2)
        + 1.0 / (4.0 * mu**3)
    )


def joint_grid_family(
    *,
    spacings: Iterable[float] = (0.5, 0.375, 0.3, 0.25),
    half_widths: Iterable[float] = (6.0, 7.5, 9.0),
) -> tuple[MappingGrid, ...]:
    """Build a Cartesian product of compatible centered grids."""
    out: list[MappingGrid] = []
    for half_width in half_widths:
        half_width = float(half_width)
        for spacing in spacings:
            spacing = float(spacing)
            cells_each_side = half_width / spacing
            rounded = round(cells_each_side)
            if not math.isclose(
                cells_each_side,
                rounded,
                rel_tol=0.0,
                abs_tol=1e-12,
            ):
                raise ValueError(
                    "each half-width must be an integer multiple of each spacing"
                )
            n = 2 * int(rounded) + 1
            out.append(MappingGrid((n, n, n), spacing))
    if len(out) < 6:
        raise ValueError("joint fit requires at least six grid points")
    return tuple(out)


def fit_joint_mapping_limit(
    points: Iterable[MappingConvergencePoint],
    *,
    mu: float,
) -> JointMappingFit:
    """Fit E/Q = c0 + c_h h^2 + c_L T(L;mu)."""
    values = tuple(points)
    if len(values) < 6:
        raise ValueError("at least six mapping points are required")
    if not math.isfinite(mu) or mu <= 0:
        raise ValueError("mu must be finite and positive")

    tail_raw = np.array(
        [asymptotic_tail_basis(p.minimum_half_width, mu) for p in values],
        dtype=float,
    )
    tail_scale = float(np.max(np.abs(tail_raw)))
    if tail_scale <= 0 or not math.isfinite(tail_scale):
        raise RuntimeError("invalid tail basis scale")
    tail = tail_raw / tail_scale

    design = np.column_stack(
        [
            np.ones(len(values), dtype=float),
            np.array([p.spacing**2 for p in values], dtype=float),
            tail,
        ]
    )
    target = np.array(
        [p.cartesian_energy_per_charge for p in values],
        dtype=float,
    )

    coeffs, _, _, _ = np.linalg.lstsq(design, target, rcond=None)
    fitted = design @ coeffs
    residuals = target - fitted
    condition = float(np.linalg.cond(design))

    return JointMappingFit(
        points=values,
        mu=float(mu),
        continuum_infinite_volume_energy_per_charge=float(coeffs[0]),
        spacing_coefficient=float(coeffs[1]),
        tail_coefficient=float(coeffs[2] / tail_scale),
        rms_residual=float(math.sqrt(np.mean(residuals**2))),
        maximum_absolute_residual=float(np.max(np.abs(residuals))),
        design_condition_number=condition,
        radial_energy_per_charge=values[0].radial_energy_per_charge,
    )


def run_joint_mapping_extrapolation() -> JointMappingFit:
    """Run the joint fit on the refined radial point just above E/Q=m_free."""
    refinement = refine_energy_per_charge_threshold(
        refinement_rounds=2,
        interior_points_per_round=4,
    )
    left, right = threshold_bracket(refinement.records)
    above = left if not left.below_free_mass_threshold else right
    if above.below_free_mass_threshold:
        raise RuntimeError("refined bracket does not contain an above-threshold point")

    free_mass = above.solution.potential.free_mass
    omega = above.solution.omega
    mu2 = free_mass**2 - omega**2
    if mu2 <= 0:
        raise RuntimeError("selected branch point has no positive asymptotic decay rate")
    mu = math.sqrt(mu2)

    points = audit_mapping_convergence(
        above,
        grids=joint_grid_family(),
    )
    return fit_joint_mapping_limit(points, mu=mu)


def format_joint_mapping_report(result: JointMappingFit) -> str:
    lines = [
        "Q-BALL JOINT MAPPING EXTRAPOLATION",
        f"mu={result.mu:.10f}",
        f"radial_E_over_Q={result.radial_energy_per_charge:.10f}",
        f"joint_extrapolated_E_over_Q={result.continuum_infinite_volume_energy_per_charge:.10f}",
        f"joint_extrapolated_above_threshold={result.extrapolated_above_threshold}",
        f"joint_relative_difference_from_radial={result.relative_difference_from_radial:.6e}",
        f"spacing_coefficient={result.spacing_coefficient:.10e}",
        f"tail_coefficient={result.tail_coefficient:.10e}",
        f"rms_residual={result.rms_residual:.6e}",
        f"maximum_absolute_residual={result.maximum_absolute_residual:.6e}",
        f"design_condition_number={result.design_condition_number:.6e}",
    ]
    for index, point in enumerate(result.points):
        lines.extend(
            [
                f"point_{index}_shape={point.shape}",
                f"point_{index}_spacing={point.spacing:.10f}",
                f"point_{index}_half_width={point.minimum_half_width:.10f}",
                f"point_{index}_cartesian_E_over_Q={point.cartesian_energy_per_charge:.10f}",
            ]
        )
    return "\n".join(lines)


def main() -> None:
    print(format_joint_mapping_report(run_joint_mapping_extrapolation()))


if __name__ == "__main__":
    main()
