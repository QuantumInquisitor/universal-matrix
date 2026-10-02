"""Material-force integration with independently evaluated energy and inertia."""

import numpy as np
import pytest

from scripts.report_fold_constitutive import constitutive
from scripts.report_fold_dynamics import (
    Q0,
    STIFFNESS,
    energy_identity_control,
    mechanical,
    rhs,
    simulate,
)
from scripts.report_fold_kinematics import kinematics


def independent_energy(q, v):
    state = kinematics(q)
    cartesian_v = np.einsum("nxa,a->nx", state["jacobian"], v)
    kinetic = np.sum(state["mass"][:, None] * cartesian_v**2) / 2
    return kinetic + constitutive(q)["total_energy_j"]


def test_material_potential_replaces_modal_spring_and_keeps_owned_inertia():
    q, v = Q0 + (0.025, 0.05), np.array((0.012, -0.03))
    quadratic, quadratic_bias, old_energy = mechanical(q, v)
    material, material_bias, new_energy = mechanical(q, v, potential="constitutive")
    np.testing.assert_array_equal(material["mass_matrix"], quadratic["mass_matrix"])
    np.testing.assert_array_equal(material_bias, quadratic_bias)
    assert len(material["ids"]) == 22
    assert new_energy == pytest.approx(independent_energy(q, v), abs=1e-18)
    old_potential = (q - Q0) @ STIFFNESS @ (q - Q0) / 2
    assert old_potential > 1e-6
    assert old_energy - old_potential + constitutive(q)["total_energy_j"] == pytest.approx(
        new_energy, abs=1e-18
    )


def test_material_acceleration_uses_independent_energy_gradient():
    q, v = Q0 + (0.025, 0.05), np.array((0.012, -0.03))
    state, bias, _ = mechanical(q, v)
    step = 1e-6
    gradient = np.array(
        [
            (
                constitutive(q + step * e)["total_energy_j"]
                - constitutive(q - step * e)["total_energy_j"]
            )
            / (2 * step)
            for e in np.eye(2)
        ]
    )
    actual = rhs(0, np.r_[q, v, 0.0, 0.0], damping=0, potential="constitutive")[2:4]
    np.testing.assert_allclose(
        state["mass_matrix"] @ actual + bias, -gradient, rtol=2e-8, atol=1e-12
    )
    # A silent old spring addition would measurably change acceleration.
    double = actual - np.linalg.solve(state["mass_matrix"], STIFFNESS @ (q - Q0))
    assert np.linalg.norm(double - actual) > 0.01


def test_independent_cartesian_energy_rate_and_wrong_law_controls():
    q, v = Q0 + (0.04, -0.06), np.array((0.12, -0.2))
    y = np.r_[q, v, 0.0, 0.0]
    derivative = rhs(0.37, y, 0.8, 1.0, potential="constitutive")
    step = 1e-6

    def energy_rate(acceleration):
        return (
            independent_energy(q + step * v, v + step * acceleration)
            - independent_energy(q - step * v, v - step * acceleration)
        ) / (2 * step)

    power = derivative[4] - derivative[5]
    assert abs(energy_rate(derivative[2:4]) - power) < 1e-11
    wrong = rhs(0.37, y, 0.8, 1.0)
    assert abs(energy_rate(wrong[2:4]) - power) > 1e-6
    check = energy_identity_control(potential="constitutive")
    assert check["absolute_error_j_s"] < 1e-11
    assert check["omitted_bias_absolute_error_j_s"] > 1e-8


@pytest.mark.parametrize("damping,drive", [(0, 0), (1, 0), (1, 1)])
def test_material_energy_ledger_and_refinement(damping, drive):
    coarse, fine = [
        simulate(duration=0.4, dt=dt, damping=damping, drive=drive, potential="constitutive")
        for dt in (0.02, 0.01)
    ]
    assert fine["potential"] == "constitutive"
    assert fine["maximum_balance_residual_j"] < coarse["maximum_balance_residual_j"] / 8
    assert fine["maximum_balance_residual_j"] < 1e-10
    assert fine["final_state"][5] >= 0
    assert (fine["final_state"][4] != 0) == bool(drive)
    if damping and not drive:
        assert fine["maximum_energy_step_increase_j"] < 0
    for sample in fine["trace"]:
        assert sample["energy_j"] == pytest.approx(
            independent_energy(sample["q"], sample["rates"]), abs=1e-17
        )


def test_material_equilibrium_and_default_compatibility():
    equilibrium = rhs(0, np.r_[Q0, 0.0, 0.0, 0.0, 0.0], potential="constitutive")
    np.testing.assert_allclose(equilibrium, 0, atol=1e-14)
    y = np.r_[Q0 + (0.02, -0.03), 0.01, 0.02, 0.0, 0.0]
    np.testing.assert_array_equal(rhs(0.2, y), rhs(0.2, y, potential="quadratic"))


@pytest.mark.parametrize("potential", [None, "both", "material", 1, True])
def test_invalid_potential_is_rejected(potential):
    with pytest.raises(ValueError, match="potential must"):
        simulate(duration=0.01, potential=potential)
