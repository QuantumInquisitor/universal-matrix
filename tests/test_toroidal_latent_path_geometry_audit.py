from __future__ import annotations

import pytest

from src.toroidal_latent_path_geometry_audit import (
    audit_tree_latent_path_geometry,
)


@pytest.fixture(scope="module")
def audits():
    return {
        rings: audit_tree_latent_path_geometry(rings)
        for rings in (1, 2, 3)
    }


@pytest.mark.parametrize(
    ("rings", "active_edges", "latent_edges"),
    (
        (1, 12, 6),
        (2, 48, 18),
        (3, 108, 36),
    ),
)
def test_zero_weave_paths_have_expected_tree_counts(
    audits,
    rings,
    active_edges,
    latent_edges,
):
    audit = audits[rings]
    assert audit.active_edge_count == active_edges
    assert audit.latent_edge_count == latent_edges
    assert audit.full_edge_count == active_edges + latent_edges
    assert audit.latent_port_count == 2 * latent_edges


@pytest.mark.parametrize("rings", (1, 2, 3))
def test_latent_paths_translate_active_channel_stack_uniformly(audits, rings):
    audit = audits[rings]
    assert audit.center_shift_is_uniform
    assert audit.maximum_major_radius_residual == pytest.approx(0.0, abs=1e-12)

    # Default shell-stack spacing is 2*0.4 + 0.2 = 1.0. Because latent weave
    # edges are appended after the active radial currents, retaining L latent
    # channels moves the common stack midpoint by -L/2 spacing units.
    expected_shift = -0.5 * audit.latent_edge_count
    assert audit.minimum_center_shift == pytest.approx(expected_shift)
    assert audit.maximum_center_shift == pytest.approx(expected_shift)


@pytest.mark.parametrize("rings", (1, 2, 3))
def test_latent_paths_change_active_annular_port_geometry(audits, rings):
    audit = audits[rings]
    assert audit.active_port_geometry_changes
    assert audit.minimum_active_port_width_ratio < 1.0
    assert audit.maximum_active_port_width_difference > 0.0


def test_latent_center_shift_grows_with_tree_depth(audits):
    magnitudes = [
        abs(audits[rings].minimum_center_shift)
        for rings in (1, 2, 3)
    ]
    assert magnitudes[0] < magnitudes[1] < magnitudes[2]


@pytest.mark.parametrize("radial_current", (-2.5, -1.0, 0.25, 3.0))
def test_latent_geometry_is_independent_of_radial_current(audits, radial_current):
    # Reversing circulation exchanges inlet/outlet roles. Rescaling current
    # changes flux, but neither should change this geometric comparison.
    assert audit_tree_latent_path_geometry(
        2, radial_current=radial_current
    ) == audits[2]


@pytest.mark.parametrize("shell_width,axial_gap", ((0.2, 0.6), (0.3, 0.8)))
def test_stack_shift_tracks_axial_spacing_not_radial_gap(shell_width, axial_gap):
    audits = [
        audit_tree_latent_path_geometry(
            2, shell_width=shell_width, axial_gap=axial_gap, shell_gap=gap
        )
        for gap in (0.0, 1.0, 3.0)
    ]
    for audit in audits:
        expected = -0.5 * audit.latent_edge_count * (2 * shell_width + axial_gap)
        assert audit.minimum_center_shift == pytest.approx(expected)
        assert audit.maximum_center_shift == pytest.approx(expected)
        assert audit.maximum_major_radius_residual == pytest.approx(0.0)
        assert audit.minimum_active_port_width_ratio == pytest.approx(0.5)


@pytest.mark.parametrize("radial_current", (0.0, 1e-13, -1e-13))
def test_latent_audit_rejects_empty_active_support(radial_current):
    with pytest.raises(ValueError, match="radial_current must be nonzero"):
        audit_tree_latent_path_geometry(2, radial_current=radial_current)


@pytest.mark.parametrize("rings", (0, -1))
def test_latent_path_audit_requires_positive_ring_depth(rings):
    with pytest.raises(ValueError):
        audit_tree_latent_path_geometry(rings)
