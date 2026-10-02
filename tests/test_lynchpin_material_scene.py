"""Original-vertex reference rebasing and exact energy ownership in the overlay."""

import copy
import hashlib
import json

import numpy as np
import pytest

from scripts import export_lynchpin_material_scene as m


@pytest.fixture(scope="module")
def source():
    return json.loads(m.FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def overlay(source):
    return m.build_overlay(source)


def test_rebased_reference_and_negative_control(overlay):
    reference = overlay["reference"]
    assert reference["source_fixture_phase"] == 0.25
    assert reference["divided_out_source_scale"] == 1.1
    np.testing.assert_array_equal(reference["material_q"], m.material.REFERENCE)
    assert reference["old_geometry_reference_q"] == [1, 0]
    at_reference_angle = overlay["frames"][2]
    for body in at_reference_angle["bodies"]:
        if body["kind"] == "panel":
            np.testing.assert_allclose(
                body["material"]["principal_stretches"], [1.1, 1.1], atol=1e-14
            )
    assert overlay["controls"]["maximum_principal_stretch_error"] < 2e-14
    assert overlay["controls"]["mismatched_theta_zero_reference_maximum_discrepancy"] > 0.1


def test_preserves_all_original_body_geometry_and_marks_unmodeled_hubs(source, overlay):
    assert len(overlay["frames"]) == 9
    for original, frame in zip(source["cases"], overlay["frames"], strict=True):
        assert frame["phase"] == original["phase"]
        assert len(frame["bodies"]) == 22
        for before, after in zip(original["bodies"], frame["bodies"], strict=True):
            assert after["id"] == before["name"]
            assert after["kind"] == before["kind"]
            assert after["vertices_reference_length"] == before["vertices_reference_length"]
            assert after["radius_reference_length"] == before["radius_reference_length"]
            assert after["source_coefficient_mean_position"] == before["coefficient_mean_position"]
            np.testing.assert_array_equal(
                after["vertices_m"], 0.1 * np.array(before["vertices_reference_length"])
            )
            if after["kind"] == "hub":
                assert after["material"] == dict(
                    status="unmodeled", energy_j=None, restoring_generalized_force=None
                )
    assert overlay["controls"]["source_vertex_checks"] == 198
    assert overlay["controls"]["panel_stretch_comparisons"] == 54
    assert overlay["controls"]["maximum_source_vertex_error_m"] < 1e-14


def test_energy_and_force_have_eighteen_unique_owners(overlay):
    for frame in overlay["frames"]:
        owned = [b for b in frame["bodies"] if b["material"]["energy_j"] is not None]
        assert len({b["id"] for b in owned}) == 18
        assert sum(b["material"]["energy_j"] for b in owned) == frame["total_energy_j"]
        forces = np.sum([b["material"]["restoring_generalized_force"] for b in owned], axis=0)
        np.testing.assert_allclose(forces, frame["restoring_generalized_force"], atol=1e-15)
        exact = m.material.constitutive(frame["q"])
        np.testing.assert_array_equal(
            frame["restoring_generalized_force"], -np.array(exact["gradient"])
        )
        assert frame["motion"].startswith("prescribed")


def test_affine_stretches_known_rotation_translation_and_anisotropic_extension():
    reference = np.array(((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)))
    current = np.column_stack((np.zeros(4), 2 * reference[:, 0], 0.5 * reference[:, 1])) + (
        3,
        -2,
        5,
    )
    fit = m.affine_stretches(reference, current)
    np.testing.assert_allclose(fit["principal_stretches"], [0.5, 2], atol=1e-14)
    assert fit["maximum_fit_residual_m"] < 1e-14


def test_input_fixture_is_not_mutated(source):
    before = copy.deepcopy(source)
    m.build_overlay(source)
    assert source == before


@pytest.mark.parametrize(
    "corruption", ["pin", "id", "radius", "vertices", "phase", "mean", "nonfinite"]
)
def test_reject_incompatible_fixture(source, corruption):
    changed = copy.deepcopy(source)
    body = changed["cases"][0]["bodies"][0]
    if corruption == "pin":
        changed["reference_commit"] = "0" * 40
    elif corruption == "id":
        body["name"] = "invented-panel"
    elif corruption == "radius":
        body["radius_reference_length"] *= 2
    elif corruption == "vertices":
        body["vertices_reference_length"][0][0] += 0.01
    elif corruption == "phase":
        changed["cases"][0]["scale"] = 1.01
    elif corruption == "mean":
        body["coefficient_mean_position"][0] += 0.1
    else:
        body["vertices_reference_length"][0][0] = float("nan")
    with pytest.raises(ValueError):
        m.build_overlay(changed)


def test_fixture_digest_and_exporter_source_inventory():
    expected = hashlib.sha256(m.FIXTURE.read_text(encoding="utf-8").encode()).hexdigest()
    result = m.report(expected_fixture_sha256=expected)
    assert result["source_fixture"]["sha256_normalized_text"] == expected
    assert result["source_fixture"]["reference_commit"] == m.material.PIN
    assert set(result["sources"]) == {
        "export_lynchpin_material_scene.py",
        "report_fold_constitutive.py",
        "report_fold_kinematics.py",
    }
    for name, digest in result["sources"].items():
        assert (
            digest
            == hashlib.sha256(
                (m.ROOT / "scripts" / name).read_text(encoding="utf-8").encode()
            ).hexdigest()
        )
    json.dumps(result, allow_nan=False)
    with pytest.raises(ValueError, match="SHA256"):
        m.report(expected_fixture_sha256="0" * 64)


def test_degenerate_affine_reference_rejected():
    with pytest.raises(ValueError):
        m.affine_stretches(np.zeros((4, 3)), np.zeros((4, 3)))
