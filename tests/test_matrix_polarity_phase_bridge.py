import cmath
import math

import pytest

from src.canonical_polarity_clock import (
    clock_node,
    polarity_phase_from_tick,
)
from src.matrix_ontology import CanonicalCoreAddress, PolarityBranch
from src.matrix_polarity_phase_bridge import (
    canonical_half_cycle_consistency,
    canonical_polarity_sign,
    effective_phase_sine,
    equivalent_rotor_coupling,
    fixed_amplitude_complex_link_energy,
    gauge_covariant_difference,
    phase_with_canonical_polarity,
    polarity_current_equivalence_error,
    polarity_weighted_sine,
    rotor_link_energy,
)


def _addresses():
    return (
        CanonicalCoreAddress(7, PolarityBranch.LOWER),
        CanonicalCoreAddress(7, PolarityBranch.UPPER),
    )


def test_canonical_sign_matches_branch_bit():
    lower, upper = _addresses()
    assert canonical_polarity_sign(lower) == 1
    assert canonical_polarity_sign(upper) == -1


def test_branch_offset_is_exact_pi_shift():
    lower, upper = _addresses()
    phase = 0.37

    lower_eff = phase_with_canonical_polarity(phase, lower)
    upper_eff = phase_with_canonical_polarity(phase, upper)

    assert math.cos(upper_eff) == pytest.approx(-math.cos(lower_eff))
    assert math.sin(upper_eff) == pytest.approx(-math.sin(lower_eff))


@pytest.mark.parametrize("source_upper", [False, True])
@pytest.mark.parametrize("target_upper", [False, True])
def test_polarity_weighted_sine_equals_effective_phase_sine(
    source_upper,
    target_upper,
):
    source = CanonicalCoreAddress(
        3,
        PolarityBranch.UPPER if source_upper else PolarityBranch.LOWER,
    )
    target = CanonicalCoreAddress(
        11,
        PolarityBranch.UPPER if target_upper else PolarityBranch.LOWER,
    )

    values = [
        (-2.1, 0.7, 0.4),
        (0.1, -1.2, 2.3),
        (math.pi / 5, math.pi / 7, -math.pi / 9),
    ]

    for source_phase, target_phase, link_phase in values:
        explicit = polarity_weighted_sine(
            source_phase,
            target_phase,
            link_phase,
            source,
            target,
        )
        reduced = effective_phase_sine(
            source_phase,
            target_phase,
            link_phase,
            source,
            target,
        )
        assert reduced == pytest.approx(explicit, abs=1e-12)
        assert polarity_current_equivalence_error(
            source_phase,
            target_phase,
            link_phase,
            source,
            target,
        ) == pytest.approx(0.0, abs=1e-12)


def test_fixed_amplitude_link_energy_matches_direct_complex_expression():
    amplitude = 0.83
    source_phase = -0.31
    target_phase = 1.07
    link_phase = 0.28

    source = CanonicalCoreAddress(5, PolarityBranch.UPPER)
    target = CanonicalCoreAddress(19, PolarityBranch.LOWER)

    source_eff = phase_with_canonical_polarity(source_phase, source)
    target_eff = phase_with_canonical_polarity(target_phase, target)

    phi_source = amplitude * cmath.exp(1j * source_eff)
    phi_target = amplitude * cmath.exp(1j * target_eff)
    direct = abs(cmath.exp(1j * link_phase) * phi_target - phi_source) ** 2

    reduced = fixed_amplitude_complex_link_energy(
        amplitude,
        source_phase,
        target_phase,
        link_phase,
        source,
        target,
    )

    assert reduced == pytest.approx(direct, abs=1e-12)


def test_fixed_amplitude_complex_matter_reduces_to_rotor_link_energy():
    amplitude = 0.6
    coupling = equivalent_rotor_coupling(amplitude)
    source_phase = 0.2
    target_phase = -0.9
    link_phase = 0.33

    matter_energy = fixed_amplitude_complex_link_energy(
        amplitude,
        source_phase,
        target_phase,
        link_phase,
    )
    rotor_energy = rotor_link_energy(
        coupling,
        source_phase,
        target_phase,
        link_phase,
    )

    assert coupling == pytest.approx(2.0 * amplitude**2)
    assert rotor_energy == pytest.approx(matter_energy, abs=1e-12)


def test_half_cycle_flips_exact_branch_and_clock_phase_by_pi():
    base = 13
    before_address = CanonicalCoreAddress.from_n(clock_node(base, 0))
    after_address = CanonicalCoreAddress.from_n(clock_node(base, 18))

    assert after_address == before_address.flipped()

    before_phase = polarity_phase_from_tick(0)
    after_phase = polarity_phase_from_tick(18)
    assert gauge_covariant_difference(before_phase, after_phase, 0.0) == pytest.approx(
        -math.pi
    )


def test_half_cycle_representation_warns_against_double_counting():
    before = CanonicalCoreAddress(4, PolarityBranch.LOWER)
    result = canonical_half_cycle_consistency(0.41, before)

    assert result["before_branch"] == 0
    assert result["after_branch"] == 1
    assert result["branch_sign_flipped"] is True
    assert result["clock_sign_flipped"] is True
    assert result["double_count_returns_original_sign"] is True


def test_half_cycle_warning_also_holds_from_upper_branch():
    before = CanonicalCoreAddress(4, PolarityBranch.UPPER)
    result = canonical_half_cycle_consistency(-0.22, before)

    assert result["before_branch"] == 1
    assert result["after_branch"] == 0
    assert result["branch_sign_flipped"] is True
    assert result["clock_sign_flipped"] is True
    assert result["double_count_returns_original_sign"] is True


def test_invalid_amplitude_and_partial_address_arguments_are_rejected():
    lower, _ = _addresses()

    with pytest.raises(ValueError):
        equivalent_rotor_coupling(-0.1)

    with pytest.raises(ValueError):
        fixed_amplitude_complex_link_energy(
            1.0,
            0.0,
            0.0,
            0.0,
            source_address=lower,
            target_address=None,
        )
