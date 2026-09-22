"""Separate radial-to-Cartesian Q-ball mapping error into spacing and volume trends."""

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
class MappingErrorDecomposition:
    resolution_points: tuple[MappingConvergencePoint, ...]
    volume_points: tuple[MappingConvergencePoint, ...]
    fixed_half_width: float
    fixed_spacing: float
    quadratic_spacing_extrapolated_energy_per_charge: float
    resolution_span: float
    volume_span: float

    @property
    def extrapolated_above_threshold(self) -> bool:
        return self.quadratic_spacing_extrapolated_energy_per_charge > 1.0


def _odd_shape_for_half_width(half_width: float, spacing: float) -> int:
    cells_each_side = half_width / spacing
    rounded = round(cells_each_side)
    if not math.isclose(cells_each_side, rounded, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("half_width must be an integer multiple of spacing")
    return 2 * int(rounded) + 1


def fixed_half_width_grids(
    *,
    half_width: float = 6.0,
    spacings: Iterable[float] = (0.5, 0.4, 0.3, 0.25),
) -> tuple[MappingGrid, ...]:
    """Create centered cubic grids that hold physical half-width fixed."""
    if not math.isfinite(half_width) or half_width <= 0:
        raise ValueError("half_width must be finite and positive")

    out: list[MappingGrid] = []
    for spacing in spacings:
        spacing = float(spacing)
        n = _odd_shape_for_half_width(half_width, spacing)
        out.append(MappingGrid((n, n, n), spacing))
    if len(out) < 3:
        raise ValueError("at least three spacing levels are required")
    return tuple(out)


def fixed_spacing_grids(
    *,
    spacing: float = 0.3,
    half_widths: Iterable[float] = (4.8, 6.0, 7.2, 8.4),
) -> tuple[MappingGrid, ...]:
    """Create centered cubic grids that hold spacing fixed while box size changes."""
    spacing = float(spacing)
    if not math.isfinite(spacing) or spacing <= 0:
        raise ValueError("spacing must be finite and positive")

    out: list[MappingGrid] = []
    for half_width in half_widths:
        half_width = float(half_width)
        n = _odd_shape_for_half_width(half_width, spacing)
        out.append(MappingGrid((n, n, n), spacing))
    if len(out) < 2:
        raise ValueError("at least two volume levels are required")
    return tuple(out)


def quadratic_spacing_extrapolation(
    points: Iterable[MappingConvergencePoint],
) -> float:
    """Fit E/Q = c0 + c2 h^2 and return the h->0 intercept."""
    values = tuple(points)
    if len(values) < 3:
        raise ValueError("at least three resolution points are required")
    x = np.array([point.spacing**2 for point in values], dtype=float)
    y = np.array([point.cartesian_energy_per_charge for point in values], dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    if not math.isfinite(float(slope)) or not math.isfinite(float(intercept)):
        raise RuntimeError("spacing extrapolation produced non-finite coefficients")
    return float(intercept)


def run_mapping_error_decomposition() -> MappingErrorDecomposition:
    """Run resolution and finite-volume audits on the same refined radial point."""
    refinement = refine_energy_per_charge_threshold(
        refinement_rounds=2,
        interior_points_per_round=4,
    )
    left, right = threshold_bracket(refinement.records)
    above = left if not left.below_free_mass_threshold else right
    if above.below_free_mass_threshold:
        raise RuntimeError("refined bracket does not contain an above-threshold point")

    resolution_grids = fixed_half_width_grids()
    volume_grids = fixed_spacing_grids()

    resolution = audit_mapping_convergence(above, grids=resolution_grids)
    volume = audit_mapping_convergence(above, grids=volume_grids)

    resolution_values = [point.cartesian_energy_per_charge for point in resolution]
    volume_values = [point.cartesian_energy_per_charge for point in volume]

    return MappingErrorDecomposition(
        resolution_points=resolution,
        volume_points=volume,
        fixed_half_width=resolution_grids[0].minimum_half_width,
        fixed_spacing=volume_grids[0].spacing,
        quadratic_spacing_extrapolated_energy_per_charge=(
            quadratic_spacing_extrapolation(resolution)
        ),
        resolution_span=max(resolution_values) - min(resolution_values),
        volume_span=max(volume_values) - min(volume_values),
    )


def format_mapping_error_decomposition_report(
    result: MappingErrorDecomposition,
) -> str:
    radial_eq = result.resolution_points[0].radial_energy_per_charge
    lines = [
        "Q-BALL MAPPING ERROR DECOMPOSITION",
        f"radial_E_over_Q={radial_eq:.10f}",
        f"fixed_half_width={result.fixed_half_width:.10f}",
    ]

    for index, point in enumerate(result.resolution_points):
        lines.extend(
            [
                f"resolution_{index}_shape={point.shape}",
                f"resolution_{index}_spacing={point.spacing:.10f}",
                f"resolution_{index}_cartesian_E_over_Q={point.cartesian_energy_per_charge:.10f}",
                f"resolution_{index}_relative_difference={point.relative_difference:.6e}",
                f"resolution_{index}_threshold_side_preserved={point.threshold_side_preserved}",
            ]
        )

    lines.extend(
        [
            f"quadratic_spacing_extrapolated_E_over_Q={result.quadratic_spacing_extrapolated_energy_per_charge:.10f}",
            f"quadratic_spacing_extrapolated_above_threshold={result.extrapolated_above_threshold}",
            f"resolution_span={result.resolution_span:.6e}",
            f"fixed_spacing={result.fixed_spacing:.10f}",
        ]
    )

    for index, point in enumerate(result.volume_points):
        lines.extend(
            [
                f"volume_{index}_shape={point.shape}",
                f"volume_{index}_half_width={point.minimum_half_width:.10f}",
                f"volume_{index}_cartesian_E_over_Q={point.cartesian_energy_per_charge:.10f}",
                f"volume_{index}_relative_difference={point.relative_difference:.6e}",
                f"volume_{index}_threshold_side_preserved={point.threshold_side_preserved}",
            ]
        )

    lines.append(f"volume_span={result.volume_span:.6e}")
    return "\n".join(lines)


def main() -> None:
    print(format_mapping_error_decomposition_report(run_mapping_error_decomposition()))


if __name__ == "__main__":
    main()
