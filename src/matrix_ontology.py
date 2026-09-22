"""Primitive ontology contract for the Universal Matrix.

This module answers the first ontology questions without promoting hypotheses
to canonical facts.

Exact layer
-----------
Every n in Z_108 decomposes uniquely as

    n = pair_id + 54 * polarity_bit,

with pair_id in {0,...,53} and polarity_bit in {0,1}. The canonical polarity
operator P=T_54 toggles polarity_bit while preserving pair_id.

Candidate physical layer
------------------------
A repeated spatial cell complex, scale level, phase, and conjugate momentum are
explicit hypotheses/adapters. Gauge variables belong on links rather than being
silently duplicated as site scalars.

No dimensional length, time, mass, charge, or experimentally validated physical
interpretation is introduced here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import math
from typing import Iterator

from .canonical_kernel import N_CORE, POLARITY_STEP, polarity


PAIR_COUNT = POLARITY_STEP
if N_CORE != 2 * PAIR_COUNT:
    raise RuntimeError("canonical ontology requires N_CORE = 2 * POLARITY_STEP")


class PolarityBranch(StrEnum):
    LOWER = "lower"
    UPPER = "upper"


@dataclass(frozen=True, order=True)
class CanonicalCoreAddress:
    """Exact Z_108 address written as antipodal pair plus polarity branch."""

    pair_id: int
    branch: PolarityBranch = PolarityBranch.LOWER

    def __post_init__(self) -> None:
        if not 0 <= self.pair_id < PAIR_COUNT:
            raise ValueError(f"pair_id must be in 0..{PAIR_COUNT - 1}")

    @property
    def polarity_bit(self) -> int:
        return 0 if self.branch is PolarityBranch.LOWER else 1

    @property
    def n(self) -> int:
        return self.pair_id + PAIR_COUNT * self.polarity_bit

    @classmethod
    def from_n(cls, n: int) -> "CanonicalCoreAddress":
        canonical = n % N_CORE
        branch = (
            PolarityBranch.LOWER
            if canonical < PAIR_COUNT
            else PolarityBranch.UPPER
        )
        return cls(
            pair_id=canonical % PAIR_COUNT,
            branch=branch,
        )

    def flipped(self) -> "CanonicalCoreAddress":
        branch = (
            PolarityBranch.UPPER
            if self.branch is PolarityBranch.LOWER
            else PolarityBranch.LOWER
        )
        return CanonicalCoreAddress(
            pair_id=self.pair_id,
            branch=branch,
        )

    def canonical_polarity_matches(self) -> bool:
        return self.flipped().n == polarity(self.n)


class OntologyStatus(StrEnum):
    EXACT_CANONICAL = "exact_canonical"
    FUNDAMENTAL_CANDIDATE = "fundamental_candidate"
    EDGE_DEGREE_CANDIDATE = "edge_degree_candidate"
    CONNECTIVITY_BOOKKEEPING = "connectivity_bookkeeping"
    DERIVED_CANDIDATE = "derived_candidate"
    GAUGE_REDUNDANCY = "gauge_redundancy"
    OPEN = "open"


@dataclass(frozen=True)
class OntologyEntry:
    name: str
    status: OntologyStatus
    reason: str


def ontology_ledger() -> tuple[OntologyEntry, ...]:
    """Return the current conservative ontology classification."""

    return (
        OntologyEntry(
            "core_pair_id",
            OntologyStatus.EXACT_CANONICAL,
            "Exact quotient label of the 54 antipodal P-orbits in Z_108.",
        ),
        OntologyEntry(
            "polarity_bit",
            OntologyStatus.EXACT_CANONICAL,
            "Exact branch within one antipodal pair; P=T_54 toggles it.",
        ),
        OntologyEntry(
            "scale_level",
            OntologyStatus.FUNDAMENTAL_CANDIDATE,
            "Nested scale exists in current models but is not derived from the finite kernel.",
        ),
        OntologyEntry(
            "phase",
            OntologyStatus.FUNDAMENTAL_CANDIDATE,
            "Used by current dynamical models; physical primitiveness remains a hypothesis.",
        ),
        OntologyEntry(
            "phase_momentum",
            OntologyStatus.FUNDAMENTAL_CANDIDATE,
            "Candidate conjugate variable needed for Hamiltonian phase dynamics.",
        ),
        OntologyEntry(
            "boundary_gate",
            OntologyStatus.CONNECTIVITY_BOOKKEEPING,
            "The six labels provide orientation/connectivity rather than an automatic matter degree of freedom.",
        ),
        OntologyEntry(
            "gauge_link",
            OntologyStatus.EDGE_DEGREE_CANDIDATE,
            "Gauge connections transform on links between cells, not as independent scalar site labels.",
        ),
        OntologyEntry(
            "electric_field",
            OntologyStatus.EDGE_DEGREE_CANDIDATE,
            "Hamiltonian gauge momentum is naturally associated with oriented links.",
        ),
        OntologyEntry(
            "gauge_choice",
            OntologyStatus.GAUGE_REDUNDANCY,
            "Local gauge frame is not itself a physical observable.",
        ),
        OntologyEntry(
            "particle_species",
            OntologyStatus.DERIVED_CANDIDATE,
            "Should arise from stable excitations or representations rather than be a primitive label.",
        ),
        OntologyEntry(
            "mass",
            OntologyStatus.DERIVED_CANDIDATE,
            "Should be an excitation or self-energy observable if the model is fundamental.",
        ),
        OntologyEntry(
            "charge",
            OntologyStatus.DERIVED_CANDIDATE,
            "Should be fixed by representation or topology if charge quantization is to be explained.",
        ),
        OntologyEntry(
            "curvature",
            OntologyStatus.DERIVED_CANDIDATE,
            "Current reciprocity geometry is an effective field construction.",
        ),
        OntologyEntry(
            "entropy",
            OntologyStatus.DERIVED_CANDIDATE,
            "Requires a statistical or coarse-grained state-counting rule.",
        ),
        OntologyEntry(
            "absolute_length_scale",
            OntologyStatus.OPEN,
            "No dimensional lattice spacing is derived by the finite kernel.",
        ),
        OntologyEntry(
            "absolute_time_scale",
            OntologyStatus.OPEN,
            "No dimensional time interval is derived by the finite kernel.",
        ),
    )


@dataclass(frozen=True)
class CandidateCellState:
    """Minimal current candidate dynamical state of one repeated Matrix cell.

    Only the address field is exact canonical structure. The remaining fields
    are explicit physical hypotheses used by later dynamical models.
    """

    address: CanonicalCoreAddress
    scale_level: int = 0
    phase: float = 0.0
    phase_momentum: float = 0.0

    def __post_init__(self) -> None:
        if self.scale_level < 0:
            raise ValueError("scale_level must be non-negative")
        if not math.isfinite(self.phase):
            raise ValueError("phase must be finite")
        if not math.isfinite(self.phase_momentum):
            raise ValueError("phase_momentum must be finite")


CellCoordinate = tuple[int, int, int]


GATE_VECTORS: dict[str, CellCoordinate] = {
    "X_POS": (1, 0, 0),
    "X_NEG": (-1, 0, 0),
    "Y_POS": (0, 1, 0),
    "Y_NEG": (0, -1, 0),
    "Z_POS": (0, 0, 1),
    "Z_NEG": (0, 0, -1),
}


@dataclass(frozen=True)
class RepeatedMatrixCellComplex:
    """Candidate repeated-cell locality adapter.

    This is not part of the exact Z_108 theorem. It formalizes the current
    hypothesis that macroscopic locality is represented by many Matrix cells
    connected through the six oriented gates.

    Coordinates are dimensionless. No physical lattice spacing is assigned.
    """

    shape: CellCoordinate
    boundary_mode: str = "open"

    def __post_init__(self) -> None:
        if len(self.shape) != 3 or any(
            not isinstance(v, int) or isinstance(v, bool) or v <= 0
            for v in self.shape
        ):
            raise ValueError("shape must contain three positive integers")
        if self.boundary_mode not in {"open", "periodic"}:
            raise ValueError("boundary_mode must be 'open' or 'periodic'")

    @property
    def site_count(self) -> int:
        nx, ny, nz = self.shape
        return nx * ny * nz

    def contains(self, coord: CellCoordinate) -> bool:
        return all(
            0 <= coord[i] < self.shape[i]
            for i in range(3)
        )

    def coordinates(self) -> Iterator[CellCoordinate]:
        nx, ny, nz = self.shape
        for x in range(nx):
            for y in range(ny):
                for z in range(nz):
                    yield (x, y, z)

    def neighbor(
        self,
        coord: CellCoordinate,
        gate: str,
    ) -> CellCoordinate | None:
        if not self.contains(coord):
            raise ValueError("coord lies outside the cell complex")
        if gate not in GATE_VECTORS:
            raise ValueError(f"unknown gate {gate!r}")

        step = GATE_VECTORS[gate]
        candidate = tuple(
            coord[i] + step[i]
            for i in range(3)
        )

        if self.boundary_mode == "periodic":
            return tuple(
                candidate[i] % self.shape[i]
                for i in range(3)
            )

        if self.contains(candidate):
            return candidate
        return None

    def oriented_links(
        self,
    ) -> Iterator[tuple[CellCoordinate, str, CellCoordinate]]:
        for coord in self.coordinates():
            for gate in GATE_VECTORS:
                target = self.neighbor(coord, gate)
                if target is not None:
                    yield coord, gate, target
