"""Sevenfold Seed geometry for competing elemental interpretations.

This module encodes a center plus six surrounding positions, the twelve
circle-overlap relationships in that neighborhood, and recursively nested
Vesica addresses.  Element names are interpretation labels, not claims that
the corresponding categories are chemical elements or established fields.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

CENTER_POSITION = 0
RING_POSITIONS = tuple(range(1, 7))
SEED_POSITION_COUNT = 7


class SeedModel(StrEnum):
    """Alternative readings of the same seven-position geometry."""

    MATERIAL = "material_six"
    POLARITY = "polarity_six"
    DUAL_ASPECT = "dual_aspect_six"


@dataclass(frozen=True)
class SeedMode:
    """One interpretation label attached to a geometric Seed position."""

    position: int
    name: str
    function: str


_COMMON = {
    0: SeedMode(
        0,
        "consciousness/ether",
        "directing consciousness expressed through a relational medium",
    ),
    1: SeedMode(1, "fire", "transformation and radiation"),
    2: SeedMode(2, "air", "motion and exchange"),
    4: SeedMode(4, "water", "cohesion and adaptation"),
    5: SeedMode(5, "earth", "structure and stabilization"),
}

_MODEL_MODES = {
    SeedModel.MATERIAL: {
        **_COMMON,
        3: SeedMode(3, "metal", "conduction and reflection"),
        6: SeedMode(6, "crystal", "coherent order and patterned memory"),
    },
    SeedModel.POLARITY: {
        **_COMMON,
        3: SeedMode(3, "positive", "outward and emissive polarity"),
        6: SeedMode(6, "negative", "inward and receptive polarity"),
    },
    SeedModel.DUAL_ASPECT: {
        **_COMMON,
        3: SeedMode(3, "metal/positive", "conductive outward expression"),
        6: SeedMode(6, "crystal/negative", "coherent inward expression"),
    },
}


def modes_for(model: SeedModel) -> tuple[SeedMode, ...]:
    """Return all seven positions for one interpretation."""
    return tuple(_MODEL_MODES[model][position] for position in range(7))


def reciprocal_pairs(model: SeedModel) -> tuple[tuple[SeedMode, SeedMode], ...]:
    """Return the three opposite axes of the surrounding hexagon."""
    modes = _MODEL_MODES[model]
    return tuple((modes[position], modes[position + 3]) for position in range(1, 4))


def seed_vesicas() -> tuple[tuple[int, int], ...]:
    """Return six center overlaps and six adjacent-ring overlaps."""
    spokes = tuple((CENTER_POSITION, position) for position in RING_POSITIONS)
    ring = tuple(
        (position, 1 if position == 6 else position + 1)
        for position in RING_POSITIONS
    )
    return spokes + ring


@dataclass(frozen=True, order=True)
class VesicaUniverseAddress:
    """A path through recursively nested Vesica universe domains."""

    path: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        vesica_count = len(seed_vesicas())
        if any(index not in range(vesica_count) for index in self.path):
            raise ValueError(f"each Vesica index must be in 0..{vesica_count - 1}")

    @property
    def depth(self) -> int:
        return len(self.path)

    def child(self, vesica_index: int) -> VesicaUniverseAddress:
        """Enter one Vesica universe and expose its child Seed."""
        return VesicaUniverseAddress(self.path + (vesica_index,))
