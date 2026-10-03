import math

import numpy as np
import pytest

from src.recursive_mirror_motion_control import LiftedMirrorControl
from src.stella_octangula_register_bridge import (
    STELLA_VERTICES,
    central_mirror_register_address,
    register_vertex_pair,
)


@pytest.mark.parametrize("dimensions", (4, 8, 13))
def test_all_register_endpoints_match_existing_mirror_and_return(dimensions):
    mirror = LiftedMirrorControl(1, dimensions)
    returned = LiftedMirrorControl(2, dimensions)
    for address in range(64):
        original = register_vertex_pair(address)
        expected = register_vertex_pair(central_mirror_register_address(address))
        assert tuple(mirror.map_point(p)[:3] for p in original) == expected
        assert tuple(returned.map_point(p)[:3] for p in original) == original
        assert all(all(x == 0 for x in mirror.map_point(p)[3:]) for p in original)


@pytest.mark.parametrize("phase", (0, 0.13, 0.5, 0.83, 1, 1.5, 1.91, 2))
def test_independent_metric_and_flux_pairing_through_cycle(phase):
    motion = LiftedMirrorControl(phase, 13)
    jacobian = np.array(motion.jacobian())
    np.testing.assert_allclose(jacobian.T @ jacobian, np.eye(3), atol=1e-14)
    assert math.sqrt(np.linalg.det(jacobian.T @ jacobian)) == pytest.approx(1)
    # Pairing is in the transported intrinsic tangent chart, not an ambient
    # 4D physical normal or an implemented dynamical current law.
    current = np.array((0.7, -1.3, 0.2))
    area_dual = np.array((-0.2, 0.4, 1.7))
    assert np.dot(jacobian @ current, jacobian @ area_dual) == pytest.approx(
        np.dot(current, area_dual)
    )
    mapped = [motion.map_point(p) for p in STELLA_VERTICES]
    for i, left in enumerate(STELLA_VERTICES):
        for j, right in enumerate(STELLA_VERTICES):
            assert math.dist(mapped[i], mapped[j]) == pytest.approx(
                math.dist(left, right), abs=1e-14
            )


@pytest.mark.parametrize("phase", (0.5, 1.5))
def test_projected_crossing_is_not_a_lifted_collision(phase):
    motion = LiftedMirrorControl(phase)
    upper = motion.map_point((1, 1, 1))
    lower = motion.map_point((1, 1, -1))
    assert upper[:3] == lower[:3]
    assert math.dist(upper, lower) == 2
    assert motion.projected_rank == 2
    assert motion.projected_determinant == 0
    assert np.linalg.matrix_rank(motion.jacobian()) == 3


def test_jacobian_matches_finite_differences_and_path_is_continuous():
    point = np.array((0.7, -2.1, 0.9))
    motion = LiftedMirrorControl(0.37)
    h = 1e-5
    numerical = np.column_stack(
        [
            (np.array(motion.map_point(point + h * e)) - motion.map_point(point - h * e)) / (2 * h)
            for e in np.eye(3)
        ]
    )
    np.testing.assert_allclose(numerical, motion.jacobian(), atol=1e-10)
    for landmark in (0.5, 1, 1.5):
        before = LiftedMirrorControl(landmark - h).map_point(point)
        after = LiftedMirrorControl(landmark + h).map_point(point)
        assert math.dist(before, after) <= 2 * math.pi * h * np.linalg.norm(point) * (1 + 1e-10)


@pytest.mark.parametrize("phase", (float("nan"), float("inf"), -1, 2.01, True, 1j))
def test_invalid_phases_rejected(phase):
    with pytest.raises(ValueError):
        LiftedMirrorControl(phase)


@pytest.mark.parametrize("dimensions", (3, 14, True, 4.5))
def test_unsupported_dimensions_rejected(dimensions):
    with pytest.raises(ValueError):
        LiftedMirrorControl(0, dimensions)


@pytest.mark.parametrize("point", ((1, 2), (1, 2, float("nan")), (1, 2, 1j)))
def test_invalid_points_rejected(point):
    with pytest.raises(ValueError):
        LiftedMirrorControl(0.5).map_point(point)
