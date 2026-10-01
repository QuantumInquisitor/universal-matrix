"""Independent controls for the experimental 0.125 material scale audit."""

import numpy as np
import pytest

from scripts.report_fold_dynamics import Q0
from scripts.report_fold_scale_extension import (
    audit_scale,
    connector,
    material_response,
    mechanical,
    report,
    rhs,
    simulate,
)
from scripts.report_fold_scaling import scale_value


def test_production_scale_guard_remains_unchanged():
    with pytest.raises(ValueError):
        scale_value(0.125)
    assert audit_scale(0.125) == 0.125


@pytest.mark.parametrize("scale", [1.0, 0.25, 0.125])
def test_static_scaling_identities(scale):
    q = Q0 + (0.03, -0.04)
    v = np.array((0.11, -0.12))
    base, bias0, _, gradient0 = mechanical(q, v, 1)
    state, bias, _, gradient = mechanical(q, v, scale)
    np.testing.assert_allclose(
        state["position"], scale * base["position"], rtol=1e-13, atol=1e-16
    )
    np.testing.assert_allclose(
        state["mass_matrix"], scale**5 * base["mass_matrix"], rtol=2e-13, atol=1e-20
    )
    np.testing.assert_allclose(bias, scale**5 * bias0, rtol=2e-13, atol=1e-20)
    np.testing.assert_allclose(gradient, scale**3 * gradient0, rtol=2e-13, atol=1e-20)

    response = material_response(q, scale)
    reference = material_response(q, 1)
    assert response["total_energy_j"] == pytest.approx(
        scale**3 * reference["total_energy_j"], rel=2e-13, abs=1e-20
    )


def test_eighth_scale_energy_derivative_closes():
    scale = 0.125
    y = np.r_[Q0 + (0.02, -0.03), 0.08, -0.06, 0.0]

    def total(z):
        return mechanical(z[:2], z[2:4], scale)[2] + z[4]

    derivative = rhs(y, scale)
    eps = 1e-7
    slope = (total(y + eps * derivative) - total(y - eps * derivative)) / (2 * eps)
    assert abs(slope) < 1e-11


@pytest.fixture(scope="module")
def result():
    return report()


def test_eighth_scale_trajectory_similarity(result):
    eighth = result["similarity"]["eighth"]
    assert eighth["coordinate_max_difference"] < 1e-11
    assert eighth["rescaled_rate_max_difference"] < 1e-10
    assert eighth["rescaled_energy_max_difference_j"] < 1e-14
    assert eighth["rescaled_loss_max_difference_j"] < 1e-14
    assert result["trajectories"]["eighth"]["max_balance_residual_j"] < 1e-14
    assert result["eighth_refinement_max_state_difference"] < 1e-8


def test_connector_gradient_and_uniform_scaling_at_eighth():
    qa = Q0 + (0.02, -0.03)
    qb = Q0 + (-0.01, 0.04)
    direction_a = np.array((0.3, -0.2))
    direction_b = np.array((-0.1, 0.4))
    energy, force_a, force_b = connector(qa, qb, 0.25, 0.125)
    assert energy > 0
    eps = 1e-6
    slope = (
        connector(qa + eps * direction_a, qb + eps * direction_b, 0.25, 0.125)[0]
        - connector(qa - eps * direction_a, qb - eps * direction_b, 0.25, 0.125)[0]
    ) / (2 * eps)
    assert slope == pytest.approx(
        -force_a @ direction_a - force_b @ direction_b, rel=1e-8, abs=1e-14
    )
    base = connector(qa, qb, 1, 1)[0]
    eighth = connector(qa, qb, 0.125, 0.125)[0]
    assert eighth == pytest.approx(0.125**3 * base, rel=2e-13, abs=1e-20)


def test_report_keeps_claim_boundaries(result):
    assert result["declared_repository_scale_floor"] == 0.25
    assert result["audit_scale_floor"] == 0.125
    assert not result["global_scale_guard_changed"]
    assert not result["depth_three_recursive_tree_executed"]
    assert not result["physical_scale_extension_validated"]
    assert result["numerical_scale_extension_audited"]


@pytest.mark.parametrize("value", [0.124, 0, -1, 1.1, True, float("nan")])
def test_invalid_audit_scale_rejected(value):
    with pytest.raises(ValueError):
        audit_scale(value)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"scale": 0.124},
        {"scale": 0.125, "reference_duration": 0},
        {"scale": 0.125, "reference_duration": 0.201},
        {"scale": 0.125, "refinement": 3},
    ],
)
def test_invalid_simulation_inputs_rejected(kwargs):
    with pytest.raises(ValueError):
        simulate(**kwargs)
