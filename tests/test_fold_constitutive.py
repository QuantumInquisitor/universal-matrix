"""Geometry replay, objective surface strain and independent virtual-work controls."""

import json
from pathlib import Path

import numpy as np
import pytest

from scripts import report_fold_constitutive as m


def test_reference_is_unstressed_with_exact_body_ownership():
    state = m.constitutive(m.REFERENCE)
    assert state["total_energy_j"] == 0
    np.testing.assert_array_equal(state["gradient"], [0, 0])
    assert [p["ray_pair"] for p in state["panels"]] == [list(p) for p in m.PANELS]
    assert len({p["id"] for p in state["panels"] + state["bridges"]}) == 18
    assert state["omitted_hubs"] == [f"hub-{i}" for i in range(4)]


def test_uniform_scale_matches_independent_isotropic_and_bar_formulas():
    s, young, nu, thickness, ea, length = 1.04, 2700, 0.2, 0.0003, 0.7, 0.15
    response = m.constitutive(
        (s, m.REFERENCE[1]),
        young_pa=young,
        poisson=nu,
        thickness_m=thickness,
        bridge_ea_n=ea,
        length_m=length,
    )
    area = sum(p["reference_area_m2"] for p in response["panels"])
    strain = (s * s - 1) / 2
    factor = area * thickness * young / (1 - nu)
    energy = factor * strain**2 + 12 * ea * 0.17 * length * (s - 1) ** 2 / 2
    scale_gradient = 2 * factor * strain * s + 12 * ea * 0.17 * length * (s - 1)
    assert response["total_energy_j"] == pytest.approx(energy, rel=1e-13)
    assert response["gradient"][0] == pytest.approx(scale_gradient, rel=1e-13)
    for panel in response["panels"]:
        np.testing.assert_allclose(panel["green_strain"], np.eye(2) * strain, atol=2e-15)


def test_fold_strains_only_two_panel_metrics_and_no_axial_bridge():
    result = m.constitutive((1, m.REFERENCE[1] + 0.1))
    for panel in result["panels"]:
        if panel["ray_pair"] in ([1, 3], [2, 3]):
            assert panel["energy_j"] > 1e-8
        else:
            assert panel["energy_j"] < 1e-30
    assert all(b["energy_j"] == 0 for b in result["bridges"])
    assert all(b["gradient"][1] == 0 for b in result["bridges"])


def test_surface_objectivity_under_independent_spatial_rotation():
    r = m.rays(0.37)[0]
    r0 = m.rays(m.REFERENCE[1])[0]
    a, a0 = 0.103 * r[[1, 3]].T, 0.1 * r0[[1, 3]].T
    rotation = np.array(((0, -1, 0), (1, 0, 0), (0, 0, 1)))
    before, after = m.membrane_response(a, a0), m.membrane_response(rotation @ a, a0)
    assert after["energy_j"] == pytest.approx(before["energy_j"], rel=1e-13)
    np.testing.assert_allclose(after["strain"], before["strain"], atol=1e-15)
    assert m.membrane_response(rotation @ a0, a0)["energy_j"] < 1e-30


@pytest.mark.parametrize("q", [(0.96, 0.1), (1.03, 0.33), (1.01, 0.45)])
@pytest.mark.parametrize("young,ea", [(1000, 0.1), (1000, 0), (0, 0.1)])
def test_independent_virtual_work(q, young, ea):
    q = np.array(q)
    direction, eps = np.array((0.31, -0.72)), 1e-6
    options = dict(young_pa=young, bridge_ea_n=ea)
    numerical = (
        m.constitutive(q + eps * direction, **options)["total_energy_j"]
        - m.constitutive(q - eps * direction, **options)["total_energy_j"]
    ) / (2 * eps)
    exact = np.array(m.constitutive(q, **options)["gradient"]) @ direction
    assert numerical == pytest.approx(exact, rel=2e-8, abs=1e-12)


def test_reference_stiffness_is_symmetric_positive_and_membrane_fold_stiffness_exists():
    eps = 1e-6
    tangent = np.column_stack(
        [
            (
                np.array(m.constitutive(m.REFERENCE + eps * d, bridge_ea_n=0)["gradient"])
                - m.constitutive(m.REFERENCE - eps * d, bridge_ea_n=0)["gradient"]
            )
            / (2 * eps)
            for d in np.eye(2)
        ]
    )
    np.testing.assert_allclose(tangent, tangent.T, atol=1e-10)
    assert np.linalg.eigvalsh(tangent)[0] > 0


def test_zero_law_and_source_geometry_replay():
    zero = m.constitutive((1.03, 0.4), young_pa=0, bridge_ea_n=0)
    assert zero["total_energy_j"] == 0
    np.testing.assert_array_equal(zero["gradient"], [0, 0])
    fixture = json.loads(
        (
            Path(__file__).resolve().parents[1]
            / "docs/experiments/fold-original-source-fixture.json"
        ).read_text()
    )
    assert fixture["reference_commit"] == m.PIN
    for case in fixture["cases"]:
        current = m.geometry((case["scale"], case["theta"]))
        assert [b["id"] for b in current] == [b["name"] for b in case["bodies"]]
        for actual, expected in zip(current, case["bodies"], strict=True):
            np.testing.assert_allclose(
                actual["vertices_m"],
                0.1 * np.array(expected["vertices_reference_length"]),
                atol=1e-15,
            )


@pytest.mark.parametrize(
    "options",
    [
        {"young_pa": True},
        {"young_pa": np.bool_(True)},
        {"young_pa": -1},
        {"young_pa": float("inf")},
        {"poisson": -1},
        {"poisson": 0.5},
        {"poisson": float("nan")},
        {"thickness_m": 0},
        {"thickness_m": True},
        {"bridge_ea_n": -1},
        {"bridge_ea_n": float("nan")},
        {"length_m": True},
        {"length_m": 0},
    ],
)
def test_invalid_material_or_scale(options):
    with pytest.raises(ValueError):
        m.constitutive(m.REFERENCE, **options)


@pytest.mark.parametrize("q", [(True, 0.2), (1, float("nan")), (0.89, 0.2), (1, 0.6)])
def test_invalid_coordinates(q):
    with pytest.raises(ValueError):
        m.constitutive(q)


def test_reject_degenerate_or_nonfinite_reference_surface():
    for matrix in (np.ones((3, 2)), np.full((3, 2), np.nan), np.ones((3, 2), dtype=bool)):
        with pytest.raises(ValueError):
            m.membrane_response(np.eye(3)[:, :2], matrix)
