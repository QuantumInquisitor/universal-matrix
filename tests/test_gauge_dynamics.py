import math

from src.gauge_dynamics import (
    ROUTING_PERIOD,
    U1CylinderField,
    gauge_covariant_phase_difference,
    pure_gauge_field,
    routing_index_to_core_state,
    weak_field_relative_error,
)
from src import canonical_kernel as ck


def test_routing_index_matches_canonical_orbit():
    for r in range(3):
        orbit = [routing_index_to_core_state(r, k) for k in range(36)]
        assert len(set(orbit)) == 36
        assert orbit == [ck.route(r, k) for k in range(36)]


def test_local_gauge_transformation_preserves_plaquettes_action_and_holonomy():
    field = U1CylinderField.zeros(3, beta=2.0)
    field.routing_links[0][0] = 0.31
    field.routing_links[1][4] = -0.22
    field.scale_links[0][7] = 0.17
    field.scale_links[1][9] = -0.11

    gauge = [
        [0.013 * (l + 1) * (k + 2) for k in range(ROUTING_PERIOD)]
        for l in range(3)
    ]
    transformed = field.gauge_transform(gauge)

    before = field.plaquettes()
    after = transformed.plaquettes()
    for row_a, row_b in zip(before, after):
        for a, b in zip(row_a, row_b):
            assert abs(a - b) < 1e-12

    assert abs(field.wilson_action() - transformed.wilson_action()) < 1e-12
    for l in range(3):
        assert abs(field.routing_holonomy(l) - transformed.routing_holonomy(l)) < 1e-12


def test_pure_gauge_connection_has_zero_curvature_and_action():
    phases = [
        [0.01 * (l + 2) * k for k in range(ROUTING_PERIOD)]
        for l in range(4)
    ]
    field = pure_gauge_field(phases)
    assert max(abs(p) for row in field.plaquettes() for p in row) < 1e-12
    assert abs(field.wilson_action()) < 1e-12
    assert field.max_abs_residual() < 1e-12


def test_covariant_phase_difference_is_gauge_invariant():
    source = 0.4
    target = -0.7
    link = 0.2
    a_s = 1.1
    a_t = -0.3

    before = gauge_covariant_phase_difference(source, target, link)
    after = gauge_covariant_phase_difference(
        source + a_s,
        target + a_t,
        link + a_s - a_t,
    )
    assert abs(before - after) < 1e-12


def test_analytic_action_gradient_matches_finite_difference():
    field = U1CylinderField.zeros(3, beta=1.7)
    field.routing_links[1][5] = 0.27
    field.scale_links[0][5] = -0.19
    field.scale_links[1][6] = 0.13

    routing_grad, scale_grad = field.euler_lagrange_residuals()
    eps = 1e-7

    original = field.routing_links[1][5]
    field.routing_links[1][5] = original + eps
    plus = field.wilson_action()
    field.routing_links[1][5] = original - eps
    minus = field.wilson_action()
    field.routing_links[1][5] = original
    numerical = (plus - minus) / (2 * eps)
    assert abs(numerical - routing_grad[1][5]) < 1e-7

    original = field.scale_links[0][5]
    field.scale_links[0][5] = original + eps
    plus = field.wilson_action()
    field.scale_links[0][5] = original - eps
    minus = field.wilson_action()
    field.scale_links[0][5] = original
    numerical = (plus - minus) / (2 * eps)
    assert abs(numerical - scale_grad[0][5]) < 1e-7


def test_weak_field_action_converges_to_compact_action():
    field = U1CylinderField.zeros(2, beta=1.0)
    field.routing_links[0][0] = 1e-3
    field.routing_links[1][0] = -5e-4
    assert weak_field_relative_error(field) < 1e-6
