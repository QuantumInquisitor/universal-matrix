"""Controls for recursive 22-body material placement envelope."""

import numpy as np

from scripts.report_fold_recursive_material_placement import report


def test_three_seed_axes_are_rigidly_equivalent_and_mirror_closed():
    result = report()
    assert len(result["axes"]) == 3
    for axis in result["axes"]:
        assert axis["module_count"] == 15
        assert axis["maximum_recursive_mirror_xy_error_m"] < 1e-12
        assert axis["maximum_recursive_mirror_z_error_m"] < 1e-12
        assert axis["maximum_rigid_axis_equivalence_error_m"] < 1e-12


def test_common_scale_envelope_is_positive_and_ordered():
    result = report()
    envelope = result["common_scale_envelope"]
    assert envelope["minimum_ratio_for_planar_vertex_containment"] > 1
    assert (
        envelope["minimum_ratio_for_spherical_vertex_containment"]
        >= envelope["minimum_ratio_for_planar_vertex_containment"]
    )
    assert (
        envelope["minimum_ratio_for_conservative_all_module_sphere_nonoverlap"]
        >= envelope["minimum_ratio_for_conservative_sibling_sphere_nonoverlap"]
    )
    assert (
        envelope["minimum_root_vessel_radius_m_if_conservative_all_module_nonoverlap"]
        >= envelope["minimum_root_vessel_radius_m_if_planar_containment_only"]
    )


def test_all_axes_have_identical_clearance_requirements():
    result = report()
    sibling = {
        axis["minimum_conservative_sibling_nonoverlap_ratio"]
        for axis in result["axes"]
    }
    all_pairs = {
        axis["minimum_conservative_all_module_nonoverlap_ratio"]
        for axis in result["axes"]
    }
    assert len(sibling) == 1
    assert len(all_pairs) == 1


def test_spatial_connector_requires_rest_and_branch_frame_adapters():
    result = report()
    for axis in result["axes"]:
        connector = axis["connector_spatial_compatibility"]
        assert connector["rest_offset_coefficient_min"] == np.testing.assert_approx_equal(
            connector["rest_offset_coefficient_min"],
            0.5,
            significant=12,
        )
        assert connector["rest_offset_coefficient_max"] == np.testing.assert_approx_equal(
            connector["rest_offset_coefficient_max"],
            0.5,
            significant=12,
        )
        mismatch = connector["maximum_frame_mismatch_by_child_bit"]
        assert mismatch[0] < 1e-12
        assert mismatch[1] > 1e-3


def test_claim_boundaries_remain_explicit():
    result = report()
    assert not result["common_vessel_to_module_ratio_selected"]
    assert not result["canonical_seed_axis_selected"]
    assert not result["conservative_bounding_sphere_is_exact_collision_certificate"]
    assert not result["direct_existing_connector_spatially_compatible"]
    assert result["spatial_rest_offset_adapter_required"]
    assert result["branch_orientation_adapter_required_for_mirror_placement"]
    assert not result["physical_spatial_assembly_validated"]
