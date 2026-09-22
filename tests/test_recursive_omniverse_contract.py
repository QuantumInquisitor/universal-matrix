import pytest

from src.canonical_kernel import N_CORE
from src.recursive_omniverse_contract import (
    PHASES_PER_TURN,
    SpiralConeAddress,
    advance_spiral,
    reciprocal_mirror,
    same_local_code,
)


def test_three_channels_times_one_turn_cover_the_core_exactly():
    states = {
        SpiralConeAddress(channel, phase_index=phase).core_state
        for channel in range(3)
        for phase in range(PHASES_PER_TURN)
    }
    assert states == set(range(N_CORE))


def test_full_turn_returns_local_code_at_next_scale():
    address = SpiralConeAddress(2, scale_level=-3, phase_index=11)
    advanced = advance_spiral(address, PHASES_PER_TURN)

    assert advanced.scale_level == -2
    assert advanced.phase_index == address.phase_index
    assert advanced.core_state == address.core_state
    assert same_local_code(address, advanced)


def test_reciprocal_mirror_is_an_involution():
    for level in range(-3, 4):
        for phase in range(PHASES_PER_TURN):
            address = SpiralConeAddress(1, level, phase)
            assert reciprocal_mirror(reciprocal_mirror(address)) == address


def test_mirror_reverses_spiral_evolution():
    address = SpiralConeAddress(0, scale_level=2, phase_index=7)

    for steps in (-73, -36, -1, 0, 1, 36, 73):
        assert reciprocal_mirror(advance_spiral(address, steps)) == advance_spiral(
            reciprocal_mirror(address),
            -steps,
        )


def test_backward_turn_moves_inward_without_losing_code():
    address = SpiralConeAddress(1, scale_level=4, phase_index=25)
    inward = advance_spiral(address, -PHASES_PER_TURN)

    assert inward.scale_level == 3
    assert same_local_code(address, inward)


def test_contract_has_no_dimensional_or_population_parameters():
    assert set(SpiralConeAddress.__dataclass_fields__) == {
        "routing_channel",
        "scale_level",
        "phase_index",
    }


def test_invalid_addresses_and_nonintegral_steps_are_rejected():
    with pytest.raises(ValueError):
        SpiralConeAddress(3)
    with pytest.raises(ValueError):
        SpiralConeAddress(0, phase_index=36)
    with pytest.raises(TypeError):
        advance_spiral(SpiralConeAddress(0), 1.5)
