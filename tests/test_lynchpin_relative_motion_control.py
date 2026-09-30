import math

import numpy as np
import pytest

from src.lynchpin_geometry_audit import LYNCHPIN_PANELS
from src.lynchpin_relative_motion_control import (
    compliant_rays,
    constraint_jacobian,
    panel_angles,
    reference_rays,
    rigidity_report,
)


@pytest.mark.parametrize("dimension,rank,modes", ((3, 9, 3), (4, 10, 6)))
def test_fixed_angles_leave_only_rigid_rotations(dimension, rank, modes):
    report = rigidity_report(dimension)
    assert report["constraint_rank"] == rank
    assert report["nullity"] == report["rigid_rotation_modes"] == modes
    assert report["internal_first_order_modes"] == 0


@pytest.mark.parametrize("dimension", (3, 4))
def test_compliant_motion_preserves_four_panels_and_changes_two(dimension):
    initial = reference_rays(dimension)
    angles = panel_angles(initial)
    for phase in np.linspace(0, 1, 101):
        rays = compliant_rays(float(phase), dimension)
        np.testing.assert_allclose(np.linalg.norm(rays, axis=1), 1, atol=1e-14)
        np.testing.assert_allclose(rays[:3], initial[:3], atol=1e-14)
        changed = panel_angles(rays)
        for name in ("01", "02", "03", "12"):
            assert changed[name] == pytest.approx(angles[name], abs=1e-12)
    midpoint = panel_angles(compliant_rays(0.5, dimension))
    assert abs(midpoint["13"] - angles["13"]) > 1
    assert abs(midpoint["23"] - angles["23"]) > 1
    for phase in (0, 1):
        np.testing.assert_allclose(compliant_rays(phase, dimension), initial, atol=1e-14)


@pytest.mark.parametrize("dimension", (3, 4))
def test_actual_velocity_satisfies_only_the_retained_panel_constraints(dimension):
    phase, h = 0.27, 1e-6
    rays = compliant_rays(phase, dimension)
    velocity = (compliant_rays(phase + h, dimension) - compliant_rays(phase - h, dimension)) / (
        2 * h
    )
    retained = tuple(pair for pair in LYNCHPIN_PANELS if pair not in ((1, 3), (2, 3)))
    assert np.linalg.norm(constraint_jacobian(rays, retained) @ velocity.ravel()) < 1e-8
    assert np.linalg.norm(constraint_jacobian(rays) @ velocity.ravel()) > 0.1


@pytest.mark.parametrize("dimension", (3, 4))
def test_full_gram_is_invariant_under_rotation_but_not_relative_control(dimension):
    rays = reference_rays(dimension)
    rotation = np.eye(dimension)
    c, s = math.cos(0.7), math.sin(0.7)
    rotation[:2, :2] = ((c, -s), (s, c))
    rotated = rays @ rotation.T
    np.testing.assert_allclose(rotated @ rotated.T, rays @ rays.T, atol=1e-14)
    moved = compliant_rays(0.5, dimension)
    assert np.max(abs(moved @ moved.T - rays @ rays.T)) > 0.1


@pytest.mark.parametrize("phase", (-1, 2, float("nan"), float("inf"), 1j, True))
def test_invalid_motion_phase_rejected(phase):
    with pytest.raises(ValueError):
        compliant_rays(phase)
