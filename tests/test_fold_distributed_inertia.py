"""Independent moment, derivative and energy-rate controls for distributed inertia."""

import numpy as np
import pytest

from scripts.report_fold_constitutive import constitutive
from scripts.report_fold_distributed_inertia import (
    centroid_mass_matrix,
    distributed_kinematics,
    inertial_bias,
    material_points,
    report,
)
from scripts.report_fold_kinematics import core_coefficients, inventory, kinematics


def test_panel_moments_against_independent_polygon_boundary_integrals():
    ids, c, weights = material_points()
    mask = np.asarray(ids) == "panel-0"
    weights = weights[mask] / 0.1
    points = c[mask, :2]
    polygon = core_coefficients()
    x, y = polygon.T
    xx, yy = np.roll(polygon, -1, axis=0).T
    cross = x * yy - xx * y
    area = cross.sum() / 2
    mean = np.array([((x + xx) * cross).sum(), ((y + yy) * cross).sum()]) / (6 * area)
    second = np.array(
        [
            [
                ((x * x + x * xx + xx * xx) * cross).sum() / (12 * area),
                ((2 * x * y + x * yy + xx * y + 2 * xx * yy) * cross).sum() / (24 * area),
            ],
            [
                ((2 * x * y + x * yy + xx * y + 2 * xx * yy) * cross).sum() / (24 * area),
                ((y * y + y * yy + yy * yy) * cross).sum() / (12 * area),
            ],
        ]
    )
    np.testing.assert_allclose(weights @ points, mean, rtol=1e-13, atol=1e-15)
    np.testing.assert_allclose(
        np.einsum("n,na,nb->ab", weights, points, points), second, rtol=1e-13
    )


def test_each_body_owns_same_mass_and_uniform_rod_second_moment():
    ids, c, weights = material_points()
    for name, _, mass in inventory():
        mask = np.asarray(ids) == name
        assert weights[mask].sum() == pytest.approx(mass, abs=1e-15)
    mask = np.asarray(ids) == "bridge-0-0"
    t = c[mask, 1] / 0.17
    assert weights[mask] @ t / 0.005 == pytest.approx(0.5)
    assert weights[mask] @ (t * t) / 0.005 == pytest.approx(1 / 3)


@pytest.mark.parametrize("q", [(1.0, 0.17), (0.93, 0.4), (1.07, 0.07)])
def test_position_and_jacobian_derivatives(q):
    q = np.asarray(q)
    state = distributed_kinematics(q)
    for axis in range(2):
        step = np.eye(2)[axis] * 1e-5
        lo, hi = distributed_kinematics(q - step), distributed_kinematics(q + step)
        np.testing.assert_allclose(
            (hi["position"] - lo["position"]) / 2e-5,
            state["jacobian"][:, :, axis],
            rtol=2e-9,
            atol=2e-11,
        )
        np.testing.assert_allclose(
            (hi["jacobian"] - lo["jacobian"]) / 2e-5,
            state["hessian"][:, :, :, axis],
            rtol=2e-9,
            atol=2e-11,
        )


def test_centroid_approximation_omits_positive_internal_inertia():
    state = distributed_kinematics((1, 0.2))
    difference = state["mass_matrix"] - centroid_mass_matrix(state)
    assert np.linalg.eigvalsh(difference)[0] > 0
    assert difference[1, 1] > 1e-6
    assert np.max(abs(state["mass_matrix"] - kinematics((1, 0.2))["mass_matrix"])) > 1e-5


def test_homothetic_length_and_mass_scaling():
    q = (1, 0.2)
    base = distributed_kinematics(q)
    masses = {name: mass * 0.5**3 for name, _, mass in inventory()}
    half = distributed_kinematics(q, length_m=0.05, masses=masses)
    np.testing.assert_allclose(half["mass_matrix"], 0.5**5 * base["mass_matrix"], rtol=1e-13)


def test_conservative_energy_rate_and_missing_bias_negative_control():
    q = np.array((1.02, 0.2))
    v = np.array((0.3, -0.4))
    state = distributed_kinematics(q)
    gradient = np.asarray(constitutive(q)["gradient"])
    bias = inertial_bias(state, v)
    acceleration = np.linalg.solve(state["mass_matrix"], -gradient - bias)
    wrong = np.linalg.solve(state["mass_matrix"], -gradient)

    def energy(q, v):
        m = distributed_kinematics(q)["mass_matrix"]
        return v @ m @ v / 2 + constitutive(q)["total_energy_j"]

    def slope(a):
        eps = 1e-6
        return (energy(q + eps * v, v + eps * a) - energy(q - eps * v, v - eps * a)) / (2 * eps)

    assert abs(slope(acceleration)) < 1e-10
    assert abs(slope(wrong)) > 1e-7


@pytest.mark.parametrize("q", [(0.8, 0.2), (1, -0.1), (True, 0.2), (1, float("nan"))])
def test_existing_domain_guards_preserved(q):
    with pytest.raises(ValueError):
        distributed_kinematics(q)


def test_report_keeps_scope_explicit():
    r = report()
    assert len(r["samples"]) == 27
    assert not r["production_dynamics_changed"]
    assert not r["physical_calibration"]
    assert not r["hub_rotational_inertia"]
