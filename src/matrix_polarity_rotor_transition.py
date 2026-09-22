"""Polarity-aware nearest-neighbor rotor dynamics.

This module composes the existing local rotor Hamiltonian with the exact
canonical polarity/phase bridge.

Two phase representations are supported.

independent:
    The site phase is independent of canonical polarity. The exact branch bit
    is represented by a pi offset, phi_eff = phi + pi p.

canonical_clock:
    The supplied phase already contains the canonical polarity-clock evolution.
    No branch offset is applied, preventing the same polarity reversal from
    being counted twice.

The canonical polarity bit remains an exact address property. The repeated
lattice, phase dynamics, and Hamiltonian interpretation remain candidate
physical structure.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .matrix_local_transition import (
    MatrixLocalTransition,
    gauge_transform_links,
    zero_link_field,
    zero_site_field,
)


PHASE_REPRESENTATIONS = {"independent", "canonical_clock"}


def effective_phase_field(
    phase: np.ndarray,
    polarity_bits: np.ndarray,
    phase_representation: str = "independent",
) -> np.ndarray:
    """Return the phase field used by the rotor interaction."""
    phase = np.asarray(phase, dtype=float)
    polarity_bits = np.asarray(polarity_bits)

    if phase.shape != polarity_bits.shape:
        raise ValueError("phase and polarity_bits must have identical shape")
    if not np.all(np.isfinite(phase)):
        raise ValueError("phase must be finite")
    if phase_representation not in PHASE_REPRESENTATIONS:
        raise ValueError(
            "phase_representation must be 'independent' or 'canonical_clock'"
        )
    if not np.all(np.isin(polarity_bits, (0, 1))):
        raise ValueError("polarity_bits must contain only 0 or 1")

    out = phase.copy()
    if phase_representation == "independent":
        out = out + math.pi * polarity_bits.astype(float)
    return (out + np.pi) % (2.0 * np.pi) - np.pi


@dataclass
class MatrixPolarityRotorTransition:
    """Nearest-neighbor rotor Hamiltonian with exact canonical branch offsets."""

    shape: tuple[int, int, int]
    phase: np.ndarray
    momentum: np.ndarray
    polarity_bits: np.ndarray
    links: dict[str, np.ndarray]
    coupling: float = 1.0
    inertia: float = 1.0
    boundary_mode: str = "open"
    phase_representation: str = "independent"
    time: float = 0.0

    def __post_init__(self) -> None:
        probe = MatrixLocalTransition(
            shape=self.shape,
            phase=self.phase,
            momentum=self.momentum,
            links=self.links,
            coupling=self.coupling,
            inertia=self.inertia,
            boundary_mode=self.boundary_mode,
            time=self.time,
        )
        self.shape = probe.shape
        self.phase = probe.phase
        self.momentum = probe.momentum
        self.links = probe.links

        bits = np.asarray(self.polarity_bits)
        if bits.shape != self.shape:
            raise ValueError("polarity_bits shape mismatch")
        if not np.all(np.isin(bits, (0, 1))):
            raise ValueError("polarity_bits must contain only 0 or 1")
        self.polarity_bits = bits.astype(np.int8, copy=True)

        if self.phase_representation not in PHASE_REPRESENTATIONS:
            raise ValueError(
                "phase_representation must be 'independent' or 'canonical_clock'"
            )

    @classmethod
    def zeros(
        cls,
        shape: tuple[int, int, int] = (4, 4, 4),
        *,
        coupling: float = 1.0,
        inertia: float = 1.0,
        boundary_mode: str = "open",
        phase_representation: str = "independent",
    ) -> "MatrixPolarityRotorTransition":
        return cls(
            shape=shape,
            phase=zero_site_field(shape),
            momentum=zero_site_field(shape),
            polarity_bits=np.zeros(shape, dtype=np.int8),
            links=zero_link_field(shape, boundary_mode),
            coupling=coupling,
            inertia=inertia,
            boundary_mode=boundary_mode,
            phase_representation=phase_representation,
        )

    @property
    def lattice_wave_speed(self) -> float:
        return math.sqrt(self.coupling / self.inertia)

    def effective_phase(self) -> np.ndarray:
        return effective_phase_field(
            self.phase,
            self.polarity_bits,
            self.phase_representation,
        )

    def _effective_model(self) -> MatrixLocalTransition:
        return MatrixLocalTransition(
            shape=self.shape,
            phase=self.effective_phase(),
            momentum=self.momentum,
            links=self.links,
            coupling=self.coupling,
            inertia=self.inertia,
            boundary_mode=self.boundary_mode,
            time=self.time,
        )

    def link_deltas(self) -> dict[str, np.ndarray]:
        return self._effective_model().link_deltas()

    def kinetic_energy(self) -> float:
        return float(0.5 * np.sum(self.momentum * self.momentum) / self.inertia)

    def interaction_energy(self) -> float:
        return self._effective_model().interaction_energy()

    def energy(self) -> float:
        return self.kinetic_energy() + self.interaction_energy()

    def total_momentum(self) -> float:
        return float(np.sum(self.momentum))

    def force(self) -> np.ndarray:
        return self._effective_model().force()

    def gauge_transform(self, alpha: np.ndarray) -> "MatrixPolarityRotorTransition":
        alpha = np.asarray(alpha, dtype=float)
        if alpha.shape != self.shape:
            raise ValueError("alpha shape mismatch")
        if not np.all(np.isfinite(alpha)):
            raise ValueError("alpha must be finite")

        return MatrixPolarityRotorTransition(
            shape=self.shape,
            phase=self.phase + alpha,
            momentum=self.momentum.copy(),
            polarity_bits=self.polarity_bits.copy(),
            links=gauge_transform_links(
                self.links,
                alpha,
                self.boundary_mode,
            ),
            coupling=self.coupling,
            inertia=self.inertia,
            boundary_mode=self.boundary_mode,
            phase_representation=self.phase_representation,
            time=self.time,
        )

    def flip_polarity(self, mask: np.ndarray | None = None) -> None:
        """Toggle exact branch bits globally or on a supplied Boolean mask."""
        if mask is None:
            self.polarity_bits = 1 - self.polarity_bits
            return

        mask = np.asarray(mask, dtype=bool)
        if mask.shape != self.shape:
            raise ValueError("mask shape mismatch")
        self.polarity_bits[mask] = 1 - self.polarity_bits[mask]

    def leapfrog(self, dt: float, steps: int = 1) -> None:
        """Advance phase/momentum with a symplectic kick-drift-kick step."""
        if not math.isfinite(dt) or dt <= 0:
            raise ValueError("dt must be finite and positive")
        if not isinstance(steps, int) or isinstance(steps, bool) or steps < 1:
            raise ValueError("steps must be a positive integer")

        for _ in range(steps):
            self.momentum += 0.5 * dt * self.force()
            self.phase += dt * self.momentum / self.inertia
            self.phase = (self.phase + np.pi) % (2.0 * np.pi) - np.pi
            self.momentum += 0.5 * dt * self.force()
            self.time += dt
