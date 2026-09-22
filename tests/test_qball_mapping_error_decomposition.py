import pytest

from src.qball_mapping_convergence import MappingConvergencePoint
from src.qball_mapping_error_decomposition import (
    fixed_half_width_grids,
    fixed_spacing_grids,
    quadratic_spacing_extrapolation,
)


def _point(spacing, value):
    return MappingConvergencePoint(
        shape=(25, 25, 25),
        spacing=spacing,
        minimum_half_width=6.0,
        radial_energy_per_charge=1.001,
        cartesian_energy_per_charge=value,
        relative_difference=abs(value - 1.001) / 1.001,
        radial_below_threshold=False,
        cartesian_below_threshold=value < 1.0,
        threshold_side_preserved=value >= 1.0,
    )


def test_fixed_half_width_grid_family_preserves_box_half_width():
    grids = fixed_half_width_grids()
    assert [grid.shape[0] for grid in grids] == [25, 31, 41, 49]
    assert all(grid.minimum_half_width == pytest.approx(6.0) for grid in grids)


def test_fixed_spacing_grid_family_varies_only_box_size():
    grids = fixed_spacing_grids()
    assert [grid.shape[0] for grid in grids] == [33, 41, 49, 57]
    assert all(grid.spacing == pytest.approx(0.3) for grid in grids)
    assert [grid.minimum_half_width for grid in grids] == pytest.approx(
        [4.8, 6.0, 7.2, 8.4]
    )


def test_quadratic_spacing_extrapolation_recovers_known_intercept():
    points = tuple(
        _point(h, 1.002 - 0.02 * h * h)
        for h in (0.5, 0.4, 0.3, 0.25)
    )
    assert quadratic_spacing_extrapolation(points) == pytest.approx(1.002)
