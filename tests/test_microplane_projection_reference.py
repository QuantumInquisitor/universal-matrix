from __future__ import annotations

import numpy as np
import pytest

from src.microplane_projection_reference import (
    OrientationQuadrature,
    audit_projection,
    project_tensors,
    spherical_quadrature,
)


def test_spherical_moments_distinguish_second_and_fourth_order_accuracy():
    errors = []
    for polar, azimuthal in ((2, 4), (3, 8), (4, 12)):
        rule = spherical_quadrature(polar, azimuthal)
        result = audit_projection(np.eye(3), np.eye(3), rule)
        assert result.directions == polar * azimuthal
        assert result.weight_sum == pytest.approx(1.0, abs=2e-15)
        assert result.first_moment_error < 3e-16
        assert result.second_moment_error < 4e-16
        errors.append(result.fourth_moment_error)
    assert errors[0] > 0.05
    assert errors[1] < 4e-16
    assert errors[2] < 4e-16


def test_isotropic_pair_has_only_normal_work_with_factor_three():
    rule = spherical_quadrature()
    pressure, dilation = 7.0e6, 2.0e-4
    result = audit_projection(pressure * np.eye(3), dilation * np.eye(3), rule)
    expected = 3.0 * pressure * dilation
    assert result.direct_work_density_pa == pytest.approx(expected)
    assert result.normal_work_density_pa == pytest.approx(expected, rel=2e-15)
    assert abs(result.tangent_work_density_pa) < expected * 1e-28
    assert result.relative_work_error < 2e-15
    assert result.reconstructed_stress_pa == pytest.approx(pressure * np.eye(3), abs=2e-8)


def test_uniaxial_work_has_analytic_three_fifths_and_two_fifths_partition():
    stress, strain = np.zeros((3, 3)), np.zeros((3, 3))
    stress[0, 0], strain[0, 0] = 12e6, -0.003
    expected = stress[0, 0] * strain[0, 0]
    result = audit_projection(stress, strain, spherical_quadrature(3, 8))
    assert result.direct_work_density_pa == pytest.approx(expected)
    assert result.normal_work_density_pa == pytest.approx(3.0 * expected / 5.0, rel=3e-15)
    assert result.tangent_work_density_pa == pytest.approx(2.0 * expected / 5.0, rel=3e-15)
    assert result.projected_work_density_pa == pytest.approx(expected, rel=3e-15)


def test_tensorial_shear_uses_half_the_engineering_shear_strain():
    stress, strain = np.zeros((3, 3)), np.zeros((3, 3))
    shear_stress, engineering_shear = 8e6, 0.004
    stress[0, 1] = stress[1, 0] = shear_stress
    strain[0, 1] = strain[1, 0] = engineering_shear / 2.0
    expected = shear_stress * engineering_shear
    result = audit_projection(stress, strain, spherical_quadrature(3, 8))
    assert result.direct_work_density_pa == pytest.approx(expected)
    assert result.normal_work_density_pa == pytest.approx(2.0 * expected / 5.0, rel=3e-15)
    assert result.tangent_work_density_pa == pytest.approx(3.0 * expected / 5.0, rel=3e-15)


def test_projection_decomposition_is_pointwise_orthogonal_and_work_preserving():
    rule = spherical_quadrature()
    stress = np.array(((12.0, 3.0, -2.0), (3.0, -5.0, 4.0), (-2.0, 4.0, 8.0))) * 1e6
    strain = np.array(((2.0, 0.5, -0.25), (0.5, -1.0, 0.2), (-0.25, 0.2, 0.75))) * 1e-4
    projection = project_tensors(stress, strain, rule)
    assert np.einsum("pi,pi->p", projection.tangent_stress_pa, rule.normals) == pytest.approx(0.0, abs=1e-8)
    assert np.einsum("pi,pi->p", projection.tangent_strain, rule.normals) == pytest.approx(0.0, abs=2e-19)
    split = projection.normal_stress_pa * projection.normal_strain + np.sum(
        projection.tangent_stress_pa * projection.tangent_strain, axis=1)
    direct = np.sum(projection.traction_pa * projection.strain_vector, axis=1)
    assert split == pytest.approx(direct, rel=1e-13, abs=2e-12)
    result = audit_projection(stress, strain, rule)
    assert result.direct_work_density_pa == pytest.approx(4060.0)
    assert result.relative_work_error < 2e-15
    assert result.relative_stress_reconstruction_error < 2e-15


def test_rotating_tensors_and_normals_is_covariant_and_fixed_rule_is_isotropic():
    rule = spherical_quadrature(3, 8)
    rotation, _ = np.linalg.qr(np.array(((0.7, -0.2, 0.5), (0.4, 0.9, -0.3), (-0.6, 0.4, 0.8))))
    if np.linalg.det(rotation) < 0:
        rotation[:, 0] *= -1
    stress = np.array(((8, 2, -3), (2, -5, 1), (-3, 1, 4))) * 1e6
    strain = np.array(((1, 0.3, 0.1), (0.3, -0.5, 0.2), (0.1, 0.2, 0.8))) * 1e-3
    rotated_stress, rotated_strain = rotation @ stress @ rotation.T, rotation @ strain @ rotation.T
    rotated_rule = OrientationQuadrature(rule.normals @ rotation.T, rule.weights)
    original = project_tensors(stress, strain, rule)
    rotated = project_tensors(rotated_stress, rotated_strain, rotated_rule)
    assert rotated.traction_pa == pytest.approx(original.traction_pa @ rotation.T, abs=2e-8)
    assert rotated.normal_strain == pytest.approx(original.normal_strain, abs=2e-18)
    first = audit_projection(stress, strain, rule)
    second = audit_projection(rotated_stress, rotated_strain, rule)
    assert second.direct_work_density_pa == pytest.approx(first.direct_work_density_pa, rel=3e-15)
    assert second.normal_work_density_pa == pytest.approx(first.normal_work_density_pa, rel=3e-15)
    assert second.tangent_work_density_pa == pytest.approx(first.tangent_work_density_pa, rel=3e-15)
    assert second.relative_stress_reconstruction_error < 2e-15


def test_underintegrated_partition_can_fail_while_total_work_is_exact():
    stress, strain = np.diag((1.0, 0.0, 0.0)), np.diag((1.0, 0.0, 0.0))
    coarse = audit_projection(stress, strain, spherical_quadrature(2, 4))
    accurate = audit_projection(stress, strain, spherical_quadrature(3, 8))
    assert coarse.relative_work_error < 2e-15
    assert coarse.relative_stress_reconstruction_error < 2e-15
    assert abs(coarse.normal_work_density_pa - 0.6) > 0.01
    assert accurate.normal_work_density_pa == pytest.approx(0.6, abs=2e-15)


def test_nonisotropic_orientation_rule_does_not_claim_reconstruction():
    rule = OrientationQuadrature(np.array(((1.0, 0.0, 0.0),)), np.array((1.0,)))
    result = audit_projection(np.diag((0.0, 1.0, 0.0)), np.diag((0.0, 1.0, 0.0)), rule)
    assert result.first_moment_error == 1.0
    assert result.second_moment_error > 0.6
    assert result.relative_work_error == 1.0
    assert result.relative_stress_reconstruction_error == 1.0


def test_zero_and_orthogonal_pairs_have_defined_absolute_scale_residuals():
    rule = spherical_quadrature()
    for stress, strain in ((np.zeros((3, 3)), np.eye(3)),
                           (np.eye(3), np.zeros((3, 3))),
                           (np.eye(3), np.diag((1.0, -1.0, 0.0)))):
        result = audit_projection(stress, strain, rule)
        assert result.direct_work_density_pa == 0.0
        assert result.relative_work_error < 2e-15


@pytest.mark.parametrize("invalid", (np.eye(2), np.ones((3, 2)),
    np.array(((1.0, 0.1, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))),
    np.full((3, 3), np.nan), np.full((3, 3), np.inf),
    np.eye(3, dtype=complex), np.eye(3, dtype=bool)))
def test_nonfinite_nonsymmetric_and_nonreal_tensors_are_rejected(invalid):
    rule = spherical_quadrature()
    for stress, strain in ((invalid, np.eye(3)), (np.eye(3), invalid)):
        with pytest.raises(ValueError):
            audit_projection(stress, strain, rule)


@pytest.mark.parametrize("polar,azimuthal", ((True, 8), (1, 8), (2.5, 8), (3, True), (3, 3)))
def test_invalid_quadrature_orders_are_rejected(polar, azimuthal):
    with pytest.raises(ValueError):
        spherical_quadrature(polar, azimuthal)


@pytest.mark.parametrize("normals,weights", (([[2, 0, 0]], [1]), ([[1, 0, 0]], [0]),
    ([[1, 0, 0]], [2]), ([[1, 0, 0]], [np.nan]), ([[1, 0, 0]], [0.5]),
    ([[1, 0, 0]], [0.5, 0.5]), ([[np.inf, 0, 0]], [1])))
def test_invalid_orientation_data_are_rejected(normals, weights):
    with pytest.raises(ValueError):
        OrientationQuadrature(normals, weights)


def test_finite_work_scaling_does_not_overflow_an_intermediate_product():
    result = audit_projection(np.eye(3) * 1e200, np.eye(3) * 1e-200, spherical_quadrature())
    assert result.direct_work_density_pa == pytest.approx(3.0)
    assert result.projected_work_density_pa == pytest.approx(3.0, rel=2e-15)
    assert result.relative_work_error < 2e-15
    with pytest.raises(ValueError, match="work density"):
        audit_projection(np.eye(3) * 1e200, np.eye(3) * 1e200, spherical_quadrature())
    with pytest.raises(ValueError, match="work density"):
        audit_projection(np.eye(3) * 1e-200, np.eye(3) * 1e-200, spherical_quadrature())


def test_exact_symmetric_subnormal_input_is_preserved_or_explicitly_rejected():
    smallest = np.nextafter(0.0, 1.0)
    stress = np.diag((smallest, 0.0, 0.0))
    strain = np.diag((1e308, 0.0, 0.0))
    axial = OrientationQuadrature(np.array(((1.0, 0.0, 0.0),)), np.array((1.0,)))
    assert project_tensors(stress, strain, axial).traction_pa[0, 0] == smallest
    result = audit_projection(stress, strain, axial)
    expected = smallest * 1e308
    assert result.direct_work_density_pa == pytest.approx(expected, rel=1e-15, abs=0)
    # A spherical reconstruction may contain unresolved subnormal roundoff.
    # Rejecting that range is acceptable; reporting a successful zero is not.
    try:
        result = audit_projection(stress, strain, spherical_quadrature())
    except ValueError as error:
        assert "resolved numerical range" in str(error)
    else:
        assert result.direct_work_density_pa == pytest.approx(expected, rel=1e-15, abs=0)
