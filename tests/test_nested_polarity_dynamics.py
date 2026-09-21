import math

from src import canonical_kernel as ck
from src.nested_polarity_dynamics import (
    NestedPolarityDynamics,
    ToroidalLayerState,
    injection_flux,
    polarity_flip,
    relative_polarity,
    signed_route,
    self_similar_scale,
    self_similar_rate,
    fractional_rate_shift,
)


def make_layer(i, node, polarity, amp, phase=0.0):
    return ToroidalLayerState(i, node, polarity, phase, amp)


def test_polarity_flip_is_involution():
    s = make_layer(0, 7, 1, 2.0)
    assert polarity_flip(polarity_flip(s)) == s


def test_flip_uses_canonical_antipode():
    s = make_layer(0, 7, 1, 2.0)
    q = polarity_flip(s)
    assert q.node == ck.polarity(7)
    assert q.polarity == -1


def test_signed_routing_reverses_with_polarity():
    plus = make_layer(0, 10, 1, 1.0)
    minus = make_layer(0, 10, -1, 1.0)
    assert signed_route(plus) == ck.route(10)
    assert signed_route(minus) == ck.route(10, -1)


def test_relative_polarity():
    a = make_layer(0, 0, 1, 1.0)
    b = make_layer(1, 0, 1, 1.0)
    c = make_layer(2, 0, -1, 1.0)
    assert relative_polarity(a, b) == 1
    assert relative_polarity(a, c) == -1


def test_injection_is_directed_and_antisymmetric():
    a = make_layer(0, 0, 1, 1.0)
    b = make_layer(1, 0, -1, 1.0)
    same = make_layer(1, 0, 1, 1.0)
    assert injection_flux(a, b, 0.1) > 0
    assert injection_flux(b, a, 0.1) == -injection_flux(a, b, 0.1)
    assert injection_flux(a, same, 0.1) == 0.0


def test_nested_exchange_conserves_total_amplitude():
    system = NestedPolarityDynamics(
        [
            make_layer(0, 0, 1, 1.0),
            make_layer(1, 9, -1, 2.0),
            make_layer(2, 18, 1, 3.0),
        ],
        coupling=0.02,
    )
    initial = system.total_amplitude()
    for _ in range(100):
        system.step()
    assert math.isclose(system.total_amplitude(), initial, rel_tol=0, abs_tol=1e-10)
    assert system.verify_conservation(1e-10)


def test_flip_period_matches_canonical_half_cycle_by_default():
    system = NestedPolarityDynamics([make_layer(0, 0, 1, 1.0)])
    for _ in range(18):
        system.step()
    assert system.layers[0].polarity == -1
    assert system.layers[0].node == ck.polarity(ck.route(0, 18))


def test_self_similar_scale_and_rate():
    assert self_similar_scale(0, 2.0) == 1.0
    assert self_similar_scale(3, 2.0) == 8.0
    assert self_similar_rate(0, 2.0, dynamic_exponent=1.0) == 1.0
    assert self_similar_rate(3, 2.0, dynamic_exponent=1.0) == 1.0 / 8.0


def test_fractional_rate_shift():
    assert fractional_rate_shift(2.0, 2.2) == 0.10000000000000009


def test_scale_ratio_changes_intrinsic_layer_rates():
    system = NestedPolarityDynamics(
        [
            make_layer(0, 0, 1, 1.0),
            make_layer(1, 9, 1, 1.0),
        ],
        coupling=0.0,
        scale_ratio=2.0,
        dynamic_exponent=1.0,
    )
    telemetry = system.step()
    r0 = telemetry[0]["dimensionless_transition_rate"]
    r1 = telemetry[1]["dimensionless_transition_rate"]
    assert r0 > r1
    assert math.isclose(r1 / r0, 0.5, rel_tol=0, abs_tol=1e-12)
