"""Exact arithmetic and geometry audit for Howard's Terryology claims.

The public label ``Terryology`` and the book's ``Terryen Wave Fields`` are
related source material, but they are not the same mathematical object.  This
module therefore keeps four layers separate:

* source statements and their evidence status;
* ordinary arithmetic and exact counterexamples;
* consistently named alternative operations;
* candidate polytope models for the reported 4, 8, 6, 12, and 24 counts.

The candidate polytope correspondence is an engine hypothesis.  It does not
validate the electromagnetic, particle, chemical, or cosmological meanings
assigned to the pictured forms.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
from itertools import combinations, product
from math import acos, degrees, sqrt

from .platonic_solid_bridge import (
    CUBE_VERTICES,
    MIRROR_TETRAHEDRON_VERTICES,
    TETRAHEDRON_VERTICES,
    Coordinate,
    platonic_solid,
)
from .twenty_four_cell_bridge import TWENTY_FOUR_CELL_VERTICES

BinaryOperation = Callable[[int, int], int]


class EvidenceStatus(StrEnum):
    """Strongest warranted status for one source claim or engine mapping."""

    SOURCE_REPORTED = "source-reported"
    EXACT_MATHEMATICAL_RESULT = "exact-mathematical-result"
    CONSISTENT_RENAMED_OPERATION = "consistent-renamed-operation"
    INCONSISTENT_WITH_STATED_AXIOMS = "inconsistent-with-stated-axioms"
    CATEGORY_ERROR = "category-error"
    UNDERSPECIFIED = "underspecified"
    CANDIDATE_MAPPING = "candidate-mapping"
    UNTESTED_PHYSICAL = "untested-physical"


@dataclass(frozen=True)
class ClaimAudit:
    """One claim transcribed from the source and its audit conclusion."""

    key: str
    pages: tuple[int, ...]
    claim: str
    status: EvidenceStatus
    finding: str


TERRYOLOGY_CLAIMS = (
    ClaimAudit(
        key="one_times_one_equals_two",
        pages=(15, 16, 20, 21, 22, 23, 24),
        claim="Ordinary multiplication should satisfy one times one equals two.",
        status=EvidenceStatus.INCONSISTENT_WITH_STATED_AXIOMS,
        finding=(
            "A multiplicative identity necessarily satisfies one times one equals one. "
            "The book's repeated-addition sentence instead defines an off-by-one operation."
        ),
    ),
    ClaimAudit(
        key="square_root_two_is_not_exact",
        pages=(26, 51, 52, 53, 54, 55, 56, 57, 61, 74, 75, 76, 77),
        claim="A nonterminating decimal prevents the square root of two from being exact.",
        status=EvidenceStatus.CATEGORY_ERROR,
        finding=(
            "The square root of two is exact as an algebraic number satisfying x squared "
            "equals two; every finite decimal is only an approximation to that exact value."
        ),
    ),
    ClaimAudit(
        key="zero_is_not_a_number",
        pages=(94, 95, 96, 97),
        claim="Physical nothingness invalidates zero and multiplication by zero.",
        status=EvidenceStatus.CATEGORY_ERROR,
        finding=(
            "A mathematical zero is an additive identity, not a claim that a physical vacuum "
            "contains no fields or particles. The equation zero times x equals a nonzero value "
            "has no solution, while zero times x equals zero has non-unique solutions."
        ),
    ),
    ClaimAudit(
        key="terryen_wave_counts",
        pages=(135, 137, 139, 140, 141),
        claim="The five named wave fields use 4, 8, 6, 12, and 24 meeting bubbles.",
        status=EvidenceStatus.SOURCE_REPORTED,
        finding="The counts and names are explicit in the book; unique coordinates are not supplied.",
    ),
    ClaimAudit(
        key="terryen_physical_identifications",
        pages=(135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145),
        claim=(
            "The named forms determine hydrogen, particles, light, gravity, electricity, "
            "magnetism, and states of matter."
        ),
        status=EvidenceStatus.UNTESTED_PHYSICAL,
        finding=(
            "The book supplies no quantitative field equations, boundary conditions, measured "
            "data, uncertainty model, or falsification threshold for these identifications."
        ),
    ),
    ClaimAudit(
        key="nonunique_final_product",
        pages=(149,),
        claim="One times one first equals two, then all things, and ultimately one.",
        status=EvidenceStatus.UNDERSPECIFIED,
        finding=(
            "An operation is not well-defined when the same ordered inputs have multiple outputs "
            "without an additional state, type, or evaluation rule."
        ),
    ),
)


def ordinary_product(left: int, right: int) -> int:
    """Return ordinary integer multiplication."""
    return left * right


def howard_literal_product(left: int, right: int) -> int:
    """Implement the book's repeated-addition sentence literally.

    The instruction says to start with ``left`` and add it to itself ``right``
    times.  On nonnegative integer counts this is ``left * (right + 1)``.  It
    is intentionally given a separate name because it is not multiplication.
    """
    if right < 0:
        raise ValueError("the literal repeated-addition count must be nonnegative")
    return left * (right + 1)


def symmetric_one_one_patch(left: int, right: int) -> int:
    """Change only ``1 * 1`` to two while retaining the other usual products."""
    if left == right == 1:
        return 2
    return left * right


def participant_union_count(left: int, right: int) -> int:
    """Count both nonnegative groups without calling the operation multiplication."""
    if left < 0 or right < 0:
        raise ValueError("participant counts must be nonnegative")
    return left + right


@dataclass(frozen=True)
class LawFailure:
    """An exact finite counterexample to one proposed binary-operation law."""

    law: str
    inputs: tuple[int, ...]
    left_value: int
    right_value: int


@dataclass(frozen=True)
class FiniteOperationAudit:
    """Counterexample search over an explicitly supplied finite integer domain."""

    samples: tuple[int, ...]
    failures: tuple[LawFailure, ...]
    two_sided_identities: tuple[int, ...]

    def failure(self, law: str) -> LawFailure | None:
        """Return the first witness for ``law``, if the finite search found one."""
        return next((failure for failure in self.failures if failure.law == law), None)


def _first_failure(
    law: str,
    cases: tuple[tuple[int, ...], ...],
    evaluator: Callable[[tuple[int, ...]], tuple[int, int]],
) -> LawFailure | None:
    for inputs in cases:
        left_value, right_value = evaluator(inputs)
        if left_value != right_value:
            return LawFailure(law, inputs, left_value, right_value)
    return None


def audit_operation_on_samples(
    operation: BinaryOperation,
    samples: tuple[int, ...] = (0, 1, 2, 3),
) -> FiniteOperationAudit:
    """Find exact law failures on a finite domain.

    A witness disproves a universal law.  The absence of a finite witness is
    not presented as a proof that the law holds outside ``samples``.
    """
    if not samples or len(set(samples)) != len(samples):
        raise ValueError("samples must be a nonempty tuple of distinct integers")

    pairs = tuple(product(samples, repeat=2))
    triples = tuple(product(samples, repeat=3))
    checks = (
        _first_failure(
            "commutativity",
            pairs,
            lambda values: (
                operation(values[0], values[1]),
                operation(values[1], values[0]),
            ),
        ),
        _first_failure(
            "associativity",
            triples,
            lambda values: (
                operation(operation(values[0], values[1]), values[2]),
                operation(values[0], operation(values[1], values[2])),
            ),
        ),
        _first_failure(
            "left-distributivity-over-addition",
            triples,
            lambda values: (
                operation(values[0], values[1] + values[2]),
                operation(values[0], values[1]) + operation(values[0], values[2]),
            ),
        ),
        _first_failure(
            "right-distributivity-over-addition",
            triples,
            lambda values: (
                operation(values[0] + values[1], values[2]),
                operation(values[0], values[2]) + operation(values[1], values[2]),
            ),
        ),
    )
    identities = tuple(
        candidate
        for candidate in samples
        if all(
            operation(candidate, value) == value and operation(value, candidate) == value
            for value in samples
        )
    )
    return FiniteOperationAudit(samples, tuple(check for check in checks if check), identities)


@dataclass(frozen=True)
class SqrtTwoNumber:
    """Exact element ``rational + radical * sqrt(2)`` of Q(sqrt(2))."""

    rational: Fraction = Fraction(0)
    radical: Fraction = Fraction(0)

    def __post_init__(self) -> None:
        object.__setattr__(self, "rational", Fraction(self.rational))
        object.__setattr__(self, "radical", Fraction(self.radical))

    @staticmethod
    def coerce(value: SqrtTwoNumber | int | Fraction) -> SqrtTwoNumber:
        if isinstance(value, SqrtTwoNumber):
            return value
        return SqrtTwoNumber(Fraction(value))

    def __add__(self, other: SqrtTwoNumber | int | Fraction) -> SqrtTwoNumber:
        other = self.coerce(other)
        return SqrtTwoNumber(self.rational + other.rational, self.radical + other.radical)

    __radd__ = __add__

    def __neg__(self) -> SqrtTwoNumber:
        return SqrtTwoNumber(-self.rational, -self.radical)

    def __sub__(self, other: SqrtTwoNumber | int | Fraction) -> SqrtTwoNumber:
        return self + -self.coerce(other)

    def __mul__(self, other: SqrtTwoNumber | int | Fraction) -> SqrtTwoNumber:
        other = self.coerce(other)
        return SqrtTwoNumber(
            self.rational * other.rational + 2 * self.radical * other.radical,
            self.rational * other.radical + self.radical * other.rational,
        )

    __rmul__ = __mul__

    def __pow__(self, exponent: int) -> SqrtTwoNumber:
        if exponent < 0:
            raise ValueError("only nonnegative powers are supported")
        result = SqrtTwoNumber(1)
        factor = self
        remaining = exponent
        while remaining:
            if remaining & 1:
                result *= factor
            factor *= factor
            remaining //= 2
        return result

    def __float__(self) -> float:
        return float(self.rational) + float(self.radical) * sqrt(2)


SQRT_TWO = SqrtTwoNumber(radical=1)


def decimal_sqrt_two_square_residual(decimal_text: str) -> Fraction:
    """Return the exact residual ``decimal_text**2 - 2`` for a finite decimal."""
    approximation = Fraction(decimal_text)
    return approximation * approximation - 2


class SolutionMultiplicity(StrEnum):
    """Solution count class for equations of the form zero times x equals rhs."""

    NONE = "none"
    NON_UNIQUE = "non-unique"


def zero_product_solution_multiplicity(rhs: int | Fraction) -> SolutionMultiplicity:
    """Classify solutions to ``0 * x = rhs`` over the rational numbers."""
    return SolutionMultiplicity.NON_UNIQUE if Fraction(rhs) == 0 else SolutionMultiplicity.NONE


@dataclass(frozen=True)
class DimensionalMonomial:
    """A rational coefficient carrying an integer power of a length unit."""

    coefficient: Fraction
    length_power: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "coefficient", Fraction(self.coefficient))

    def __mul__(self, other: DimensionalMonomial) -> DimensionalMonomial:
        return DimensionalMonomial(
            self.coefficient * other.coefficient,
            self.length_power + other.length_power,
        )


@dataclass(frozen=True)
class TerryenWaveField:
    """A source-reported wave-field count and a candidate regular vertex model."""

    key: str
    display_name: str
    source_page: int
    bubble_count: int
    candidate_polytope: str
    candidate_dimension: int
    status: EvidenceStatus = EvidenceStatus.CANDIDATE_MAPPING


TERRYEN_WAVE_FIELDS = (
    TerryenWaveField("tetra_terryen", "Tetra-Terryen", 135, 4, "tetrahedron", 3),
    TerryenWaveField("huntyen", "Huntyen", 137, 8, "cube", 3),
    TerryenWaveField("mira", "Mira", 139, 6, "octahedron", 3),
    TerryenWaveField("aubreyen", "Aubreyen", 140, 12, "icosahedron", 3),
    TerryenWaveField("heavenly", "Heavenly", 141, 24, "24-cell", 4),
)


def terryen_wave_field(key: str) -> TerryenWaveField:
    """Return one candidate mapping by its stable key."""
    try:
        return next(field for field in TERRYEN_WAVE_FIELDS if field.key == key)
    except StopIteration as error:
        raise ValueError(f"unknown Terryen wave field: {key}") from error


def terryen_candidate_vertices(key: str) -> tuple[tuple[float, ...], ...]:
    """Return centered, equal-radius vertices for one candidate mapping."""
    field = terryen_wave_field(key)
    if field.candidate_polytope == "24-cell":
        vertices = TWENTY_FOUR_CELL_VERTICES
    else:
        vertices = platonic_solid(field.candidate_polytope).vertices
    return tuple(tuple(float(component) for component in vertex) for vertex in vertices)


@dataclass(frozen=True)
class SphericalCodeCertificate:
    """Directional separation certificate for equal spheres around a center."""

    point_count: int
    dimension: int
    maximum_pairwise_cosine: float
    minimum_angle_degrees: float
    supports_equal_sphere_kissing: bool


def terryen_spherical_code_certificate(key: str) -> SphericalCodeCertificate:
    """Audit a candidate as equal-radius directions on a unit sphere.

    Equal outer spheres tangent to an equal central sphere do not overlap when
    every pair of center directions is separated by at least 60 degrees, which
    is equivalent to a pairwise cosine no greater than one half.
    """
    vertices = terryen_candidate_vertices(key)
    dimension = len(vertices[0])
    norms = tuple(sqrt(sum(component * component for component in vertex)) for vertex in vertices)
    maximum_cosine = max(
        sum(a * b for a, b in zip(left, right, strict=True)) / (left_norm * right_norm)
        for (left, left_norm), (right, right_norm) in combinations(
            tuple(zip(vertices, norms, strict=True)), 2
        )
    )
    bounded_cosine = max(-1.0, min(1.0, maximum_cosine))
    return SphericalCodeCertificate(
        point_count=len(vertices),
        dimension=dimension,
        maximum_pairwise_cosine=maximum_cosine,
        minimum_angle_degrees=degrees(acos(bounded_cosine)),
        supports_equal_sphere_kissing=maximum_cosine <= 0.5 + 1e-12,
    )


KNOWN_KISSING_NUMBERS = {1: 2, 2: 6, 3: 12, 4: 24}


def within_known_kissing_bound(sphere_count: int, dimension: int) -> bool:
    """Compare a count with an exact known kissing number in dimensions 1 to 4."""
    if sphere_count < 0:
        raise ValueError("sphere_count must be nonnegative")
    try:
        return sphere_count <= KNOWN_KISSING_NUMBERS[dimension]
    except KeyError as error:
        raise ValueError("dimension must have a recorded exact kissing number") from error


def tetrahedral_mirror_completion() -> tuple[Coordinate, ...]:
    """Return the eight-point union of a tetrahedron and its central mirror."""
    return tuple(
        sorted(
            {*TETRAHEDRON_VERTICES, *MIRROR_TETRAHEDRON_VERTICES},
            key=lambda coordinate: tuple(float(component) for component in coordinate),
        )
    )


if tetrahedral_mirror_completion() != CUBE_VERTICES:
    raise RuntimeError("the tetrahedral mirror completion must equal the cube vertex set")
if tuple(field.bubble_count for field in TERRYEN_WAVE_FIELDS) != (4, 8, 6, 12, 24):
    raise RuntimeError("the Terryen source-count sequence changed")
