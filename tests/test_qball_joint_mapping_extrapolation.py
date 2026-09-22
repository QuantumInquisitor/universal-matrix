import math

import pytest

from src.qball_mapping_convergence import MappingConvergencePoint
from src.qball_joint_mapping_extrapolation import (
    asymptotic_tail_basis,
    fit_joint_mapping_limit,
    joint_grid_family,
)


def _synthetic_point(h, L, mu, c0=1.002, ch=-0.02, cL=-0.003):
    tail = asymptotic_tail_basis(L, mu)
    value = c0 + ch * h * h + cL * tail
    return MappingConvergencePoint(
        shape=(25, 25, 25),
        spacing=h,
        minimum_half_width=L,
        radial_energy_per_charge=c0,
        cartesian_energy_per_charge=value,
        relative_difference=abs(value - c0) / c0,
        radial_below_threshold=False,
        cartesian_below_threshold=value < 1.0,
        threshold_side_preserved=value >= 1.0,
    )


def test_joint_grid_family_is_compatible_and_centered():
    grids = joint_grid_family()
    assert len(grids) == 12
    assert all(all(n % 2 == 1 for n in grid.shape) for grid in grids)
    assert {grid.minimum_half_width for grid in grids} == pytest.approx(
        {6.0, 7.5, 9.0}
    )


def test_tail_basis_decreases_with_box_size():
    mu = 0.6
    assert asymptotic_tail_basis(9.0, mu) < asymptotic_tail_basis(6.0, mu)


def test_joint_fit_recovers_synthetic_continuum_limit():
    mu = 0.6
    points = tuple(
        _synthetic_point(h, L, mu)
        for L in (6.0, 7.5, 9.0)
        for h in (0.5, 0.375, 0.3, 0.25)
    )
    result = fit_joint_mapping_limit(points, mu=mu)

    assert result.continuum_infinite_volume_energy_per_charge == pytest.approx(
        1.002,
        abs=1e-10,
    )
    assert result.rms_residual < 1e-12
    assert result.maximum_absolute_residual < 1e-12
    assert math.isfinite(result.design_condition_number)
