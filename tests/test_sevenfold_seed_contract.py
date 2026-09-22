import pytest

from src.sevenfold_seed_contract import (
    CENTER_POSITION,
    RING_POSITIONS,
    SEED_POSITION_COUNT,
    SeedModel,
    VesicaUniverseAddress,
    mirror_seed_position,
    mirror_vesica_address,
    mirror_vesica_index,
    modes_for,
    reciprocal_pairs,
    seed_vesicas,
)


@pytest.mark.parametrize("model", list(SeedModel))
def test_each_model_fills_one_center_and_six_ring_positions(model):
    modes = modes_for(model)

    assert len(modes) == SEED_POSITION_COUNT
    assert {mode.position for mode in modes} == {CENTER_POSITION, *RING_POSITIONS}
    assert modes[CENTER_POSITION].name == "consciousness/ether"


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


def test_seed_mirror_fixes_the_center_and_exchanges_opposite_ring_positions():
    assert mirror_seed_position(CENTER_POSITION) == CENTER_POSITION
    assert tuple(mirror_seed_position(position) for position in RING_POSITIONS) == (
        4,
        5,
        6,
        1,
        2,
        3,
    )
    assert all(
        mirror_seed_position(mirror_seed_position(position)) == position
        for position in range(SEED_POSITION_COUNT)
    )


def test_vesica_mirror_preserves_overlap_kind_and_mirrors_both_endpoints():
    vesicas = seed_vesicas()

    for index, endpoints in enumerate(vesicas):
        mirrored_index = mirror_vesica_index(index)
        expected_endpoints = {mirror_seed_position(position) for position in endpoints}

        assert set(vesicas[mirrored_index]) == expected_endpoints
        assert (index < 6) == (mirrored_index < 6)
        assert mirror_vesica_index(mirrored_index) == index


def test_same_mirror_recurs_at_every_vesica_address_depth():
    address = VesicaUniverseAddress((0, 7, 5, 11))
    mirrored = mirror_vesica_address(address)

    assert mirrored.path == tuple(mirror_vesica_index(index) for index in address.path)
    assert mirror_vesica_address(mirrored) == address

    for child_index in range(len(seed_vesicas())):
        assert mirror_vesica_address(address.child(child_index)) == mirrored.child(
            mirror_vesica_index(child_index)
        )


def test_recursive_address_rejects_unknown_vesica():
    with pytest.raises(ValueError):
        VesicaUniverseAddress((12,))


def test_mirror_rejects_unknown_seed_and_vesica_positions():
    with pytest.raises(ValueError):
        mirror_seed_position(7)
    with pytest.raises(ValueError):
        mirror_vesica_index(12)
