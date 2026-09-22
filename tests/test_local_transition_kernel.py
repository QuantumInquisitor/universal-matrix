import math

import pytest

from src.local_transition_kernel import (
    EdgeTransitionParameters,
    branch_sign,
    conservative_exchange,
    gauge_covariant_phase_difference,
    gauge_transform_edge,
    local_edge_generator,
    local_edge_generator_from_addresses,
    oriented_polarity,
    polarity_exchange_carrier,
    quadratic_content,
    reverse_oriented_edge,
    transition_edge,
)
from src.matrix_ontology import CanonicalCoreAddress


def test_branch_sign_tracks_exact_canonical_branch():
    assert branch_sign(CanonicalCoreAddress.from_n(0)) == 1
    assert branch_sign(CanonicalCoreAddress.from_n(53)) == 1
    assert branch_sign(CanonicalCoreAddress.from_n(54)) == -1
    assert branch_sign(CanonicalCoreAddress.from_n(107)) == -1


def test_nested_scale_orientation_flips_each_level():
    address = CanonicalCoreAddress.from_n(7)
    assert oriented_polarity(address, 0) == 1
    assert oriented_polarity(address, 1) == -1
    assert oriented_polarity(address, 2) == 1


def test_gauge_covariant_phase_difference_is_invariant():
    source = 0.2
    target = 1.3
    link = -0.4

    before = gauge_covariant_phase_difference(
        source,
        target,
        link,
    )

    transformed = gauge_transform_edge(
        source,
        target,
        link,
        source_gauge_phase=0.73,
        target_gauge_phase=-0.29,
    )
    after = gauge_covariant_phase_difference(*transformed)

    assert after == pytest.approx(before)


def test_polarity_channel_vanishes_for_like_polarity():
    for delta in (0.0, 0.4, math.pi / 2, math.pi):
        assert polarity_exchange_carrier(1, 1, delta) == pytest.approx(0.0)
        assert polarity_exchange_carrier(-1, -1, delta) == pytest.approx(0.0)


def test_phase_aligned_opposite_polarities_have_opposite_oriented_carriers():
    assert polarity_exchange_carrier(1, -1, 0.0) == pytest.approx(1.0)
    assert polarity_exchange_carrier(-1, 1, 0.0) == pytest.approx(-1.0)


def test_edge_generator_is_gauge_invariant():
    params = EdgeTransitionParameters(
        phase_coupling=0.2,
        polarity_coupling=0.4,
    )

    source_phase = -0.7
    target_phase = 0.6
    link_phase = 0.3

    before = local_edge_generator(
        source_phase,
        target_phase,
        link_phase,
        1,
        -1,
        params,
    )

    transformed = gauge_transform_edge(
        source_phase,
        target_phase,
        link_phase,
        1.1,
        -0.8,
    )

    after = local_edge_generator(
        *transformed,
        1,
        -1,
        params,
    )

    assert after == pytest.approx(before)


def test_reversing_edge_reverses_generator():
    params = EdgeTransitionParameters(
        phase_coupling=0.23,
        polarity_coupling=0.41,
    )
    data = (0.1, 1.2, -0.37, 1, -1)

    forward = local_edge_generator(
        *data,
        params,
    )
    reverse_data = reverse_oriented_edge(*data)
    reverse = local_edge_generator(
        *reverse_data,
        params,
    )

    assert reverse == pytest.approx(-forward)


def test_local_rotation_conserves_quadratic_content():
    before = (0.7, -1.3)
    after = conservative_exchange(
        *before,
        generator=0.87,
        step=0.31,
    )

    assert quadratic_content(*after) == pytest.approx(
        quadratic_content(*before),
        rel=0.0,
        abs=1e-14,
    )


def test_local_rotation_is_time_reversible():
    initial = (0.7, -1.3)
    forward = conservative_exchange(
        *initial,
        generator=0.87,
        step=0.31,
    )
    recovered = conservative_exchange(
        *forward,
        generator=0.87,
        step=-0.31,
    )

    assert recovered == pytest.approx(initial, abs=1e-14)


def test_zero_couplings_give_identity_transition():
    params = EdgeTransitionParameters()

    source = CanonicalCoreAddress.from_n(4)
    target = CanonicalCoreAddress.from_n(62)

    result = transition_edge(
        0.25,
        0.9,
        source,
        target,
        source_phase=0.3,
        target_phase=1.2,
        link_phase=-0.4,
        parameters=params,
        step=1.0,
    )

    assert result == pytest.approx((0.25, 0.9))


def test_address_based_generator_includes_alternating_scale_orientation():
    params = EdgeTransitionParameters(
        phase_coupling=0.0,
        polarity_coupling=1.0,
    )

    a = CanonicalCoreAddress.from_n(3)
    b = CanonicalCoreAddress.from_n(4)

    same_scale = local_edge_generator_from_addresses(
        a,
        b,
        source_phase=0.0,
        target_phase=0.0,
        link_phase=0.0,
        parameters=params,
        source_scale_level=0,
        target_scale_level=0,
    )
    adjacent_scale = local_edge_generator_from_addresses(
        a,
        b,
        source_phase=0.0,
        target_phase=0.0,
        link_phase=0.0,
        parameters=params,
        source_scale_level=0,
        target_scale_level=1,
    )

    assert same_scale == pytest.approx(0.0)
    assert adjacent_scale == pytest.approx(1.0)


def test_invalid_couplings_are_rejected():
    with pytest.raises(ValueError):
        EdgeTransitionParameters(phase_coupling=-0.1)

    with pytest.raises(ValueError):
        EdgeTransitionParameters(polarity_coupling=float("nan"))
