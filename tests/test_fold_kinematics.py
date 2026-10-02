"""Derivative and inertial controls; original-source replay is a separate test."""

import math

import numpy as np
import pytest

from scripts.report_fold_kinematics import inventory, kinematics, prescribed, report


def test_inventory_ownership():
    rows = inventory()
    assert len(rows) == len({row[0] for row in rows}) == 22
    assert sum(row[2] for row in rows) == pytest.approx(0.74)
    assert [
        sum(row[0].startswith(kind) for row in rows) for kind in ("panel", "hub", "bridge")
    ] == [6, 4, 12]


@pytest.mark.parametrize("q", [(1.0, 0.17), (0.93, 0.4), (1.07, 0.07)])
def test_first_and_second_derivatives(q):
    q = np.array(q)
    state = kinematics(q)
    for a in range(2):
        step = np.eye(2)[a] * 1e-5
        lo, hi = kinematics(q - step), kinematics(q + step)
        np.testing.assert_allclose(
            (hi["position"] - lo["position"]) / 2e-5,
            state["jacobian"][:, :, a],
            atol=2e-11,
            rtol=2e-9,
        )
        np.testing.assert_allclose(
            (hi["jacobian"] - lo["jacobian"]) / 2e-5,
            state["hessian"][:, :, :, a],
            atol=2e-11,
            rtol=2e-9,
        )


def test_inertia_positive_and_kinetic_identity():
    for s in (0.9, 1.0, 1.1):
        for theta in np.linspace(0, math.pi / 6, 9):
            state = kinematics((s, theta))
            matrix = state["mass_matrix"]
            assert np.linalg.eigvalsh(matrix)[0] > 0
            np.testing.assert_allclose(matrix, matrix.T, atol=1e-18)
            for rate in ((1.0, 0.0), (0.0, 1.0), (-0.31, 0.57)):
                rate = np.array(rate)
                point_v = state["jacobian"] @ rate
                energy = np.sum(state["mass"][:, None] * point_v**2) / 2
                assert energy == pytest.approx(rate @ matrix @ rate / 2, rel=1e-13)


def test_mass_and_length_scaling():
    q = (1.0, 0.2)
    a = kinematics(q)
    masses = {name: 3 * mass for name, _, mass in inventory()}
    b = kinematics(q, length_m=0.2, masses=masses)
    np.testing.assert_allclose(b["mass_matrix"], 12 * a["mass_matrix"], rtol=1e-14)
    np.testing.assert_allclose(b["position"], 2 * a["position"], rtol=1e-14)


def test_path_landmarks_and_closure():
    assert prescribed(0) == prescribed(1) == (1.0, 0.0)
    assert prescribed(0.5) == (1.0, math.pi / 6)
    assert prescribed(0.25)[0] == 1.1
    assert prescribed(0.75)[0] == 0.9
    np.testing.assert_array_equal(
        kinematics(prescribed(0))["position"], kinematics(prescribed(1))["position"]
    )


@pytest.mark.parametrize(
    "q",
    [(0.0, 0.0), (1.2, 0.0), (1.0, -0.1), (1.0, 1.0), (True, 0.0), (1.0, float("nan")), (1.0, 1j)],
)
def test_reject_coordinates(q):
    with pytest.raises(ValueError):
        kinematics(q)


@pytest.mark.parametrize("mass", [0.0, -1.0, float("inf"), True])
def test_reject_mass(mass):
    masses = {name: m for name, _, m in inventory()}
    masses["panel-0"] = mass
    with pytest.raises(ValueError):
        kinematics((1.0, 0.0), masses=masses)


def test_reject_missing_owner_and_scale():
    with pytest.raises(ValueError):
        kinematics((1.0, 0.0), masses={})
    for scale in (0.0, float("nan"), True, 1e20):
        with pytest.raises(ValueError):
            kinematics((1.0, 0.0), length_m=scale)


def test_reject_overflowing_integer():
    with pytest.raises(ValueError, match="finite real scalar"):
        kinematics((1.0, 0.0), length_m=10**1000)


def test_report_bounds_and_identity():
    result = report()
    assert result["dynamics_implemented"] is False
    assert result["physical_material_validation"] is False
    assert len(result["samples"]) == 17
    assert max(row["kinetic_identity_absolute_error_j"] for row in result["samples"]) < 1e-18
