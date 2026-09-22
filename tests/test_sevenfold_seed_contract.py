import pytest

from src.sevenfold_seed_contract import (
    CENTER_POSITION,
    RING_POSITIONS,
    SEED_POSITION_COUNT,
    SeedModel,
    VesicaUniverseAddress,
    modes_for,
    reciprocal_pairs,
    seed_vesicas,
)


@pytest.mark.parametrize("model", list(SeedModel))
def test_each_model_fills_one_center_and_six_ring_positions(model):
    modes = modes_for(model)

    assert len(modes) == SEED_POSITION_COUNT
    assert {mode.position for mode in modes} == {CENTER_POSITION, *RING_POSITIONS}
    assert modes[CENTER_POSITION].name == "ether"


def test_models_preserve_both_open_interpretations():
    material = {mode.name for mode in modes_for(SeedModel.MATERIAL)}
    polarity = {mode.name for mode in modes_for(SeedModel.POLARITY)}
    dual = {mode.name for mode in modes_for(SeedModel.DUAL_ASPECT)}

    assert {"metal", "crystal"} <= material
    assert {"positive", "negative"} <= polarity
    assert {"metal/positive", "crystal/negative"} <= dual


@pytest.mark.parametrize("model", list(SeedModel))
def test_reciprocal_pairs_are_opposite_hexagonal_positions(model):
    pairs = reciprocal_pairs(model)

    assert len(pairs) == 3
    assert {(left.position, right.position) for left, right in pairs} == {
        (1, 4),
        (2, 5),
        (3, 6),
    }


def test_seed_has_six_spoke_and_six_ring_vesicas():
    vesicas = seed_vesicas()

    assert len(vesicas) == 12
    assert len(set(vesicas)) == 12
    assert sum(CENTER_POSITION in pair for pair in vesicas) == 6


def test_each_vesica_can_recur_as_a_child_universe():
    root = VesicaUniverseAddress()

    for first in range(12):
        child = root.child(first)
        grandchild = child.child((first + 1) % 12)
        assert child.depth == 1
        assert grandchild.depth == 2
        assert grandchild.path[:1] == child.path


def test_recursive_address_rejects_unknown_vesica():
    with pytest.raises(ValueError):
        VesicaUniverseAddress((12,))
