"""Controls for the recursive scale-impedance linearization audit."""

import numpy as np
import pytest

from scripts.report_fold_recursive_impedance import (
    INTERFACE_PARENT_SCALES,
    MODULE_SCALES,
    interface_linearization,
    material_stiffness,
    report,
)


@pytest.fixture(scope="module")
def result():
    return report()


def test_module_scale_identities_hold_in_linearization(result):
    for scale in MODULE_SCALES:
        row = result["module_scaling"][str(scale)]
        assert row["mass_s5_max_error"] < 1e-12
        assert row["stiffness_s3_max_error"] < 1e-9
        assert row["damping_s4_max_error"] < 1e-12
        assert row["frequency_inverse_scale_max_error"] < 1e-7
        assert row["impedance_s4_max_error"] < 1e-9
        assert row["damping_ratio_max_error"] < 1e-10


def test_modal_quantities_are_positive_and_finite(result):
    for module in result["modules"].values():
        for mode in module["modes"]:
            for key in (
                "modal_mass",
                "modal_stiffness",
                "modal_damping",
                "omega_rad_per_s",
                "modal_impedance",
                "damping_ratio",
            ):
                assert np.isfinite(mode[key])
                assert mode[key] > 0


def test_connector_and_quasistatic_transfer_are_self_similar(result):
    for scale in INTERFACE_PARENT_SCALES:
        row = result["interface_scaling"][str(scale)]
        assert row["connector_parent_s3_max_error"] < 1e-8
        assert row["transfer_matrix_max_difference"] < 1e-8
        assert row["child_energy_fraction_difference"] < 1e-10


def test_interface_partitions_are_finite_and_nontrivial(result):
    fractions = []
    transfer_norms = []
    for scale in INTERFACE_PARENT_SCALES:
        row = result["interfaces"][str(scale)]
        fraction = row["linearized_child_energy_fraction"]
        assert 0 < fraction < 1
        fractions.append(fraction)
        transfer_norms.append(row["quasistatic_transfer_spectral_norm"])
        assert row["connector_parent_block_to_parent_material_norm_ratio"] > 0
        assert row["connector_child_block_to_child_material_norm_ratio"] > 0
    assert max(fractions) - min(fractions) < 1e-10
    assert max(transfer_norms) - min(transfer_norms) < 1e-8


def test_material_tangent_is_symmetric_positive_definite():
    for scale in MODULE_SCALES:
        stiffness = material_stiffness(scale)
        np.testing.assert_allclose(stiffness, stiffness.T, rtol=0, atol=1e-10)
        assert np.min(np.linalg.eigvalsh(stiffness)) > 0


def test_claim_boundaries_remain_explicit(result):
    assert not result["connector_coefficients_changed"]
    assert not result["material_coefficients_changed"]
    assert not result["damping_coefficients_changed"]
    assert not result["dynamic_child_work_fraction_predicted"]
    assert not result["spatial_recursive_embedding_validated"]
    assert not result["arbitrary_depth_validated"]


@pytest.mark.parametrize("scale", [0, 0.125, 0.75, 2, True, None])
def test_invalid_interface_parent_scale_rejected(scale):
    with pytest.raises(ValueError):
        interface_linearization(scale)
