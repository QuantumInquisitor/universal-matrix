"""Dimensionless recursive scale contract for the Omniverse hypothesis.

This module formalizes three structural ideas without claiming that they are
already established physical laws:

* one 36-step canonical routing orbit is one complete spiral turn;
* completing a turn returns to the same local code at an adjacent scale;
* inner/outer correspondence reverses the unwrapped spiral coordinate.

The three routing channels and 36 phase positions cover all 108 canonical core
states exactly. No length, time, energy, multiverse count, or empirical scale
factor is introduced.
"""

from __future__ import annotations

from dataclasses import dataclass

from .canonical_kernel import N_CORE, route

ROUTING_CHANNEL_COUNT = 3
PHASES_PER_TURN = 36

if ROUTING_CHANNEL_COUNT * PHASES_PER_TURN != N_CORE:
    raise RuntimeError("recursive contract must cover the 108-state core")


@dataclass(frozen=True, order=True)
class SpiralConeAddress:
    """One dimensionless address in a nested spiral-cone scale stack."""

    routing_channel: int
    scale_level: int = 0
    phase_index: int = 0

    def __post_init__(self) -> None:
        if self.routing_channel not in range(ROUTING_CHANNEL_COUNT):
            raise ValueError("routing_channel must be in 0..2")
        if self.phase_index not in range(PHASES_PER_TURN):
            raise ValueError("phase_index must be in 0..35")

    @property
    def unwrapped_position(self) -> int:
        return self.scale_level * PHASES_PER_TURN + self.phase_index

    @property
    def core_state(self) -> int:
        return route(self.routing_channel, self.phase_index)

    @property
    def inheritance_signature(self) -> tuple[int, int]:
        """Local code inherited whenever a full turn changes scale."""
        return self.routing_channel, self.phase_index

    @classmethod
    def from_unwrapped(
        cls,
        routing_channel: int,
        unwrapped_position: int,
    ) -> SpiralConeAddress:
        scale_level, phase_index = divmod(
            unwrapped_position,
            PHASES_PER_TURN,
        )
        return cls(routing_channel, scale_level, phase_index)


def advance_spiral(
    address: SpiralConeAddress,
    steps: int = 1,
) -> SpiralConeAddress:
    """Advance locally; complete turns become exact scale transitions."""
    if not isinstance(steps, int) or isinstance(steps, bool):
        raise TypeError("steps must be an integer")
    return SpiralConeAddress.from_unwrapped(
        address.routing_channel,
        address.unwrapped_position + steps,
    )


def reciprocal_mirror(address: SpiralConeAddress) -> SpiralConeAddress:
    """Return the dimensionless inner/outer reciprocal address."""
    return SpiralConeAddress.from_unwrapped(
        address.routing_channel,
        -address.unwrapped_position,
    )


def same_local_code(
    left: SpiralConeAddress,
    right: SpiralConeAddress,
) -> bool:
    """Whether two scale addresses carry the same inherited local code."""
    return left.inheritance_signature == right.inheritance_signature
