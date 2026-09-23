"""Direct H4-to-E8 lift from the existing 600-cell coordinates.

The repository H4 roots live in Q(phi)^4. Following the published
icosahedral spinor construction, the 240 candidate E8 roots are the disjoint
union H4 U phi*H4 equipped with the reduced inner product: take the rational
coefficient of the Q(phi) dot product.

Writing each coordinate as a + b*phi turns one 4D golden-field vector into an
8-component rational vector. Under that coefficient lift, the reduced inner
product is exactly the ordinary Euclidean dot product in Q^8.

This module proves an exact mathematical bridge only. It does not identify
those eight rational coordinates with eight physical spatial dimensions.
"""

from __future__ import annotations

from fractions import Fraction
from functools import cache

from .h3_600_cell_bridge import SIX_HUNDRED_CELL_VERTICES, dot4
from .platonic_solid_bridge import PHI, PhiNumber

GoldenCoordinate4D = tuple[PhiNumber, PhiNumber, PhiNumber, PhiNumber]
RationalCoordinate8D = tuple[
    Fraction, Fraction, Fraction, Fraction,
    Fraction, Fraction, Fraction, Fraction,
]


def phi_scale(root: GoldenCoordinate4D) -> GoldenCoordinate4D:
    """Multiply one H4 root by the golden ratio exactly."""
    return tuple(PHI * component for component in root)


H4_ROOTS = tuple(SIX_HUNDRED_CELL_VERTICES)
PHI_H4_ROOTS = tuple(phi_scale(root) for root in H4_ROOTS)
DIRECT_E8_ROOTS = tuple(
    sorted(
        {*H4_ROOTS, *PHI_H4_ROOTS},
        key=lambda root: tuple(
            coefficient
            for component in root
            for coefficient in (component.rational, component.golden)
        ),
    )
)
_DIRECT_E8_ROOT_SET = frozenset(DIRECT_E8_ROOTS)


def reduced_inner_product(
    left: GoldenCoordinate4D,
    right: GoldenCoordinate4D,
) -> Fraction:
    """Return the rational coefficient of the Q(phi) inner product."""
    return dot4(left, right).rational


def coefficient_lift_8d(root: GoldenCoordinate4D) -> RationalCoordinate8D:
    """Expand four a+b*phi entries into eight rational coefficients."""
    if len(root) != 4:
        raise ValueError("root must have exactly four Q(phi) coordinates")
    rationals = tuple(component.rational for component in root)
    goldens = tuple(component.golden for component in root)
    return rationals + goldens


def rational_dot_8d(
    left: RationalCoordinate8D,
    right: RationalCoordinate8D,
) -> Fraction:
    """Return the ordinary Euclidean dot product in rational 8-space."""
    if len(left) != 8 or len(right) != 8:
        raise ValueError("both coefficient vectors must have eight entries")
    return sum((a * b for a, b in zip(left, right, strict=True)), Fraction(0))


def direct_e8_reflect(
    vector: GoldenCoordinate4D,
    root: GoldenCoordinate4D,
) -> GoldenCoordinate4D:
    """Reflect one direct-lift root using the reduced E8 inner product."""
    if vector not in _DIRECT_E8_ROOT_SET or root not in _DIRECT_E8_ROOT_SET:
        raise ValueError("vector and root must both belong to the direct E8 lift")
    denominator = reduced_inner_product(root, root)
    coefficient = 2 * reduced_inner_product(vector, root) / denominator
    reflected = tuple(
        component - PhiNumber(coefficient) * root_component
        for component, root_component in zip(vector, root, strict=True)
    )
    if reflected not in _DIRECT_E8_ROOT_SET:
        raise RuntimeError("reduced reflection escaped the direct E8 root set")
    return reflected


def direct_e8_antipodal_pair_count() -> int:
    """Count unordered central-mirror root pairs."""
    unseen = set(DIRECT_E8_ROOTS)
    count = 0
    while unseen:
        root = unseen.pop()
        mirror = tuple(-component for component in root)
        if mirror not in unseen:
            raise RuntimeError("direct E8 root set lost central-mirror closure")
        unseen.remove(mirror)
        count += 1
    return count


def direct_e8_inner_product_spectrum() -> tuple[Fraction, ...]:
    """Return all distinct reduced pairwise inner products."""
    return tuple(
        sorted(
            {
                reduced_inner_product(left, right)
                for left in DIRECT_E8_ROOTS
                for right in DIRECT_E8_ROOTS
            }
        )
    )


@cache
def direct_e8_neighbor_counts() -> tuple[int, ...]:
    """Return nearest-neighbor counts for every coefficient-lifted E8 root."""
    lifted = tuple(coefficient_lift_8d(root) for root in DIRECT_E8_ROOTS)
    counts = []
    for index, root in enumerate(lifted):
        distances = []
        for other_index, other in enumerate(lifted):
            if other_index == index:
                continue
            difference = tuple(a - b for a, b in zip(root, other, strict=True))
            distances.append(rational_dot_8d(difference, difference))
        nearest = min(distances)
        counts.append(sum(distance == nearest for distance in distances))
    return tuple(counts)


def coefficient_rank_8d() -> int:
    """Return the exact rational rank of the 240 coefficient-lifted roots."""
    rows = [list(coefficient_lift_8d(root)) for root in DIRECT_E8_ROOTS]
    row_count = len(rows)
    column_count = 8
    pivot_row = 0

    for column in range(column_count):
        pivot = next(
            (row for row in range(pivot_row, row_count) if rows[row][column] != 0),
            None,
        )
        if pivot is None:
            continue

        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        pivot_value = rows[pivot_row][column]
        rows[pivot_row] = [value / pivot_value for value in rows[pivot_row]]

        for row in range(row_count):
            if row == pivot_row or rows[row][column] == 0:
                continue
            factor = rows[row][column]
            rows[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(rows[row], rows[pivot_row], strict=True)
            ]

        pivot_row += 1
        if pivot_row == column_count:
            break

    return pivot_row


if len(H4_ROOTS) != 120:
    raise RuntimeError("the existing 600-cell layer must supply exactly 120 H4 roots")
if len(DIRECT_E8_ROOTS) != 240:
    raise RuntimeError("H4 union phi*H4 must contain exactly 240 distinct roots")
if set(H4_ROOTS) & set(PHI_H4_ROOTS):
    raise RuntimeError("the two H4 copies must be disjoint")
if {reduced_inner_product(root, root) for root in DIRECT_E8_ROOTS} != {Fraction(1)}:
    raise RuntimeError("all direct E8 roots must have unit reduced norm")
if coefficient_rank_8d() != 8:
    raise RuntimeError("the coefficient lift must span all eight rational dimensions")
