from __future__ import annotations

import math
from dataclasses import replace

import numpy as np
import pytest

from src.toroidal_incident_bend_audit import audit_incident_bend_collisions
from src.toroidal_inversion_control import SphereInversion, audit_inverted_collision_witnesses
from src.toroidal_separated_channels import build_separated_framed_edge_network
from src.toroidal_smooth_bends import AnnularQuarterBend
from src.vesica_tree_circulation import PORT_NODES, vesica_circulation


@pytest.mark.parametrize("point", ((1.0, 2.0, 3.0), (7.0, -1.0, 0.0), (-2.0, 5.0, 1.0)))
def test_inversion_is_self_inverse_and_reciprocates_radius(point):
    inversion = SphereInversion(center=(0.5, -0.25, 1.0), radius=2.0)
    image = inversion.map_point(point)
    assert inversion.map_point(image) == pytest.approx(point, abs=1e-12)
    assert math.dist(point, inversion.center) * math.dist(image, inversion.center) == pytest.approx(4.0)


def test_inside_outside_exchange_and_fixed_sphere():
    inversion = SphereInversion(radius=2.0)
    assert inversion.map_point((1.0, 0.0, 0.0)) == pytest.approx((4.0, 0.0, 0.0))
    assert inversion.map_point((4.0, 0.0, 0.0)) == pytest.approx((1.0, 0.0, 0.0))
    assert inversion.map_point((0.0, 2.0, 0.0)) == pytest.approx((0.0, 2.0, 0.0))


def test_jacobian_matches_independent_finite_differences_and_reverses_orientation():
    inversion = SphereInversion(center=(0.25, -0.5, 0.75), radius=2.0)
    point = np.array((1.5, 2.0, -0.25))
    h = 1e-5
    numerical = np.column_stack([
        (np.array(inversion.map_point(point + h * axis))
         - np.array(inversion.map_point(point - h * axis))) / (2 * h)
        for axis in np.eye(3)
    ])
    assert np.array(inversion.jacobian(point)) == pytest.approx(numerical, abs=1e-10)
    assert np.linalg.det(numerical) == pytest.approx(inversion.determinant(point), rel=1e-9)
    assert inversion.determinant(point) < 0.0


def test_straight_interpolation_has_a_singular_intermediate_map():
    inversion = SphereInversion(radius=2.0)
    point = (1.5, 2.0, -0.25)
    fraction = inversion.singular_blend_fraction(point)
    jacobian = np.array(inversion.jacobian(point))
    assert 0.0 < fraction < 1.0
    assert np.linalg.det((1 - fraction) * np.eye(3) + fraction * jacobian) == pytest.approx(0.0, abs=1e-14)


def _bend(flux):
    return AnnularQuarterBend(
        corner=(3.0, 0.5, 2.0), source_tangent=(0.0, 0.0, 1.0),
        target_tangent=(0.0, 1.0, 0.0), bend_radius=2.0,
        inner_radius=0.4, outer_radius=1.2, flux=flux,
    )


@pytest.mark.parametrize("flux", (-0.8, 1.3))
@pytest.mark.parametrize("outward", (False, True))
def test_mapped_bend_cut_preserves_integrated_flux_with_matched_normals(flux, outward):
    # Derive area from finite differences of the transformed surface itself,
    # independently of map_area's analytic cofactor formula.
    inversion = SphereInversion(radius=2.0)
    bend = _bend(flux)
    nodes, weights = np.polynomial.legendre.leggauss(8)
    h, theta_count, phi = 1e-5, 24, 0.7
    contributions = []
    for q, weight in zip((nodes + 1) / 2, weights / 2, strict=True):
        for theta in np.arange(theta_count) * (2 * math.pi / theta_count):
            def surface(q_value, theta_value):
                return np.array(inversion.map_point(bend.map_point(phi, q_value, theta_value)))
            dq = (surface(q + h, theta) - surface(q - h, theta)) / (2 * h)
            dt = (surface(q, theta + h) - surface(q, theta - h)) / (2 * h)
            area = np.cross(dq, dt) * (-1 if outward else 1)
            point = bend.map_point(phi, q, theta)
            mapped = inversion.piola_current(point, bend.current(point), outward=outward)
            contributions.append(np.dot(mapped, area) * weight * 2 * math.pi / theta_count)
    assert math.fsum(contributions) == pytest.approx(flux, rel=2e-8, abs=2e-8)


def test_orientation_conventions_must_not_be_mixed():
    inversion = SphereInversion(radius=2.0)
    point, current, area = (1.0, 2.0, 3.0), (0.2, -0.3, 1.0), (0.0, 0.0, 2.0)
    signed = inversion.piola_current(point, current)
    parametric_area = inversion.map_area(point, area)
    outward_area = inversion.map_area(point, area, outward=True)
    assert np.dot(signed, parametric_area) == pytest.approx(np.dot(current, area))
    assert np.dot(signed, outward_area) == pytest.approx(-np.dot(current, area))


def test_transformed_bend_field_remains_numerically_divergence_free():
    inversion = SphereInversion(radius=2.0)
    bend = _bend(1.3)
    image = np.array(inversion.map_point(bend.map_point(0.7, 0.4, 0.3)))
    def current_at_image(point):
        preimage = inversion.map_point(point)
        return np.array(inversion.piola_current(preimage, bend.current(preimage)))
    h = 1e-6
    divergence = math.fsum(
        (current_at_image(image + h * axis)[i] - current_at_image(image - h * axis)[i]) / (2 * h)
        for i, axis in enumerate(np.eye(3))
    )
    assert abs(divergence) < 1e-6


@pytest.fixture(scope="module")
def collision_audit():
    circulation = vesica_circulation(1.0, return_split=0.4)
    network = build_separated_framed_edge_network(circulation.edges, PORT_NODES, shell_gap=3.0)
    return audit_incident_bend_collisions(
        network, bend_margin=0.05, phi_samples=13, q_samples=5, theta_samples=24,
        phi_offset=0.5, q_offset=0.5, theta_offset=0.5,
    )


def test_actual_gap_three_collision_witnesses_survive_inversion(collision_audit):
    control = audit_inverted_collision_witnesses(collision_audit)
    assert control.source_witness_count == control.retained_witness_count == 2
    assert control.minimum_pole_clearance_bound > 12.0
    assert control.maximum_roundtrip_error < 1e-10
    assert control.maximum_flux_pairing_residual < 1e-12
    assert control.minimum_absolute_jacobian > 0.0
    assert 0.0 < control.minimum_singular_blend_fraction <= control.maximum_singular_blend_fraction < 1.0


def test_control_rejects_unexcluded_pole_in_a_witness_volume(collision_audit):
    inversion = SphereInversion(center=collision_audit.collisions[0].witness_point)
    with pytest.raises(ValueError, match="exclude the inversion pole"):
        audit_inverted_collision_witnesses(collision_audit, inversion)


def test_control_does_not_pass_vacuously_without_witnesses(collision_audit):
    with pytest.raises(ValueError, match="at least one collision witness"):
        audit_inverted_collision_witnesses(replace(collision_audit, collisions=()))


def test_floating_point_collapse_to_pole_is_rejected():
    inversion = SphereInversion(center=(1e16, 0.0, 0.0), radius=1.0)
    with pytest.raises(ValueError, match="not representable"):
        inversion.map_point((1e16 + 2.0, 0.0, 0.0))


@pytest.mark.parametrize("radius", (0.0, -1.0, float("inf"), float("nan")))
def test_invalid_inversion_radius_is_rejected(radius):
    with pytest.raises(ValueError):
        SphereInversion(radius=radius)


@pytest.mark.parametrize("point", ((0.0, 0.0, 0.0), (1.0, 2.0), (float("inf"), 0.0, 1.0)))
def test_pole_and_invalid_points_are_rejected(point):
    with pytest.raises(ValueError):
        SphereInversion().map_point(point)
