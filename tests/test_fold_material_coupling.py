"""Independent energy and control checks for constitutive reservoir coupling."""

import numpy as np
import pytest

from scripts import report_fold_coupling as pair
from scripts import report_fold_reservoir as source
from scripts.report_fold_constitutive import constitutive
from scripts.report_fold_dynamics import DAMPING, Q0
from scripts.report_fold_dynamics import simulate as passive
from scripts.report_fold_kinematics import kinematics


def energy(block):
    # Independently assemble point kinetic and element potential energies.
    state = kinematics(block[:2])
    cartesian_rates = np.einsum("nxa,a->nx", state["jacobian"], block[2:4])
    kinetic = np.sum(state["mass"] * np.sum(cartesian_rates**2, axis=1)) / 2
    return kinetic + constitutive(block[:2])["total_energy_j"]


def directional(function, state, derivative):
    eps = 1e-6
    return (function(state + eps * derivative) - function(state - eps * derivative)) / (2 * eps)


def test_single_material_energy_direction_and_omitted_debit():
    y = np.r_[Q0 + (0.025, -0.04), 0.1, -0.15, 2e-5, 0.0, 0.0, 0.0, 0.0]
    derivative = source.rhs(y, potential="constitutive")

    def total(z):
        return energy(z) + z[4] + sum(z[6:])

    assert abs(directional(total, y, derivative)) < 1e-11
    material_slope = directional(energy, y, derivative)
    assert material_slope == pytest.approx(derivative[5] - derivative[6], abs=1e-11)
    wrong = source.rhs(y, potential="constitutive", omit_debit=True)
    assert directional(total, y, wrong) == pytest.approx(derivative[5] / 0.8, abs=1e-11)
    assert directional(total, y, wrong) > 1e-6


def test_pair_material_energy_direction_and_wrong_reaction():
    y = pair.initial_state()
    y[11:13] = (0.03, -0.04)

    def total(z):
        a, b = z[:9], z[9:18]
        delta = a[:2] - b[:2]
        connection = (0.003 * delta[0] ** 2 + 0.001 * delta[1] ** 2) / 2
        return energy(a) + energy(b) + a[4] + b[4] + sum(a[6:]) + sum(b[6:]) + connection

    good = pair.rhs(y, potential="constitutive")
    assert abs(directional(total, y, good)) < 1e-11
    for offset, work in ((0, 18), (9, 19)):
        slope = directional(lambda z, offset=offset: energy(z[offset : offset + 9]), y, good)
        assert slope == pytest.approx(good[offset + 5] - good[offset + 6] + good[work], abs=1e-11)
    wrong = pair.rhs(y, potential="constitutive", wrong_reaction=True)
    expected = -2 * np.array((0.003, 0.001)) * (y[:2] - y[9:11])
    assert directional(total, y, wrong) == pytest.approx(expected @ y[11:13], abs=1e-11)
    assert abs(directional(total, y, wrong)) > 1e-6
    assert pair.measure(y, potential="constitutive")[2] == pytest.approx(total(y), abs=1e-18)


@pytest.mark.parametrize("settings", [dict(gain=0), dict(reserve=0)])
def test_material_source_off_matches_passive(settings):
    run = source.simulate(duration=0.2, potential="constitutive", **settings)
    reference = passive(duration=0.2, dt=0.02, potential="constitutive")
    np.testing.assert_allclose(
        run["final_state"][:4], reference["final_state"][:4], atol=1e-15, rtol=0
    )
    assert run["final_state"][5] == 0
    assert run["settings"]["potential"] == "constitutive"


def test_disconnected_material_pair_matches_single():
    run = pair.simulate(duration=0.2, coupling=0, potential="constitutive")
    reference = source.simulate(duration=0.2, potential="constitutive")
    np.testing.assert_allclose(run["final_state"][:9], reference["final_state"], atol=1e-16, rtol=0)
    assert run["final_state"][18:] == [0.0, 0.0]
    assert run["settings"]["potential"] == "constitutive"


@pytest.mark.parametrize("module", [source, pair])
def test_material_total_conservation_refines(module):
    coarse = module.simulate(duration=0.4, dt=0.04, potential="constitutive")
    fine = module.simulate(duration=0.4, dt=0.02, potential="constitutive")
    assert fine["max_total_residual_j"] < coarse["max_total_residual_j"] / 8
    assert fine["max_total_residual_j"] < 1e-12
    if module is pair:
        assert fine["max_module_residual_j"] < 1e-12
        assert fine["max_connection_residual_j"] < 1e-12
    else:
        assert fine["max_mechanical_residual_j"] < 1e-12
        assert fine["max_reservoir_residual_j"] < 1e-18


@pytest.mark.parametrize(
    "module,settings", [(source, dict(omit_debit=True)), (pair, dict(wrong_reaction=True))]
)
def test_material_negative_control_breaks_integrated_account(module, settings):
    run = module.simulate(duration=0.4, potential="constitutive", **settings)
    assert run["max_total_residual_j"] > 1e-10


@pytest.mark.parametrize("module", [source, pair])
def test_unknown_potential_rejected(module):
    with pytest.raises(ValueError, match="potential"):
        module.simulate(duration=0.02, potential="unknown")


def test_material_force_selection_changes_acceleration_not_inertia_or_loss():
    y = np.r_[Q0 + (0.02, -0.03), 0.1, -0.15, 2e-5, 0.0, 0.0, 0.0, 0.0]
    material = source.rhs(y, potential="constitutive")
    quadratic = source.rhs(y)
    assert np.linalg.norm(material[2:4] - quadratic[2:4]) > 1e-3
    np.testing.assert_array_equal(material[4:], quadratic[4:])
    assert material[6] == pytest.approx(y[2:4] @ DAMPING @ y[2:4])
