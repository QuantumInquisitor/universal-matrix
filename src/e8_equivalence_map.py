"""Exact equivalence between the two independently generated E8 root systems.

One root system is obtained from the existing H4 / 600-cell coordinates by the
direct Q(phi) coefficient lift.  The other is the standard integer-scaled E8
construction in higher_dimensional_geometry.

This module finds a simple-root basis independently inside each root set,
matches their E8 Dynkin Gram matrices, and derives the unique rational linear
map carrying one selected basis to the other.  The resulting map is then tested
against all 240 roots.

Coordinates in the standard set have squared norm eight while the coefficient
lift has squared norm one, so the exact similarity relation is M^T M = 8 I.
"""

from __future__ import annotations

from fractions import Fraction
from functools import cache

from .h4_direct_e8_lift import (
    DIRECT_E8_ROOTS,
    coefficient_lift_8d,
    direct_e8_reflect,
    rational_dot_8d,
)
from .higher_dimensional_geometry import e8_reflect, e8_roots_scaled

RationalVector = tuple[Fraction, ...]
RationalMatrix = tuple[tuple[Fraction, ...], ...]
IntegerVector = tuple[int, ...]

# E8 Dynkin tree in the selected ordering:
#
# 0 - 1 - 2 - 3 - 4 - 5 - 6
#         |
#         7
_E8_EDGES = frozenset(
    {
        frozenset((0, 1)),
        frozenset((1, 2)),
        frozenset((2, 3)),
        frozenset((3, 4)),
        frozenset((4, 5)),
        frozenset((5, 6)),
        frozenset((2, 7)),
    }
)


def _fraction_vector(values) -> RationalVector:
    return tuple(Fraction(value) for value in values)


DIRECT_COEFFICIENT_ROOTS = tuple(coefficient_lift_8d(root) for root in DIRECT_E8_ROOTS)
STANDARD_E8_ROOTS = tuple(e8_roots_scaled())


def _direct_inner(left: RationalVector, right: RationalVector) -> Fraction:
    return rational_dot_8d(left, right)


def _standard_inner(left: IntegerVector, right: IntegerVector) -> int:
    return sum(a * b for a, b in zip(left, right, strict=True))


def _required_inner(selected_index: int, candidate_index: int, squared_norm) -> Fraction:
    if selected_index == candidate_index:
        return Fraction(squared_norm)
    if frozenset((selected_index, candidate_index)) in _E8_EDGES:
        return Fraction(-squared_norm, 2)
    return Fraction(0)


def _simple_root_basis(roots, inner, squared_norm) -> tuple:
    """Find one deterministic E8 simple-root basis inside a root set."""
    ordered = tuple(sorted(roots))
    first = ordered[0]
    selected = [first]

    def compatible(candidate, position: int) -> bool:
        return all(
            Fraction(inner(candidate, root))
            == _required_inner(position, prior_position, squared_norm)
            for prior_position, root in enumerate(selected)
        )

    def search(position: int):
        if position == 8:
            return tuple(selected)

        for candidate in ordered:
            if candidate in selected:
                continue
            if compatible(candidate, position):
                selected.append(candidate)
                result = search(position + 1)
                if result is not None:
                    return result
                selected.pop()
        return None

    result = search(1)
    if result is None:
        raise RuntimeError("failed to find an E8 simple-root basis")
    return result


@cache
def direct_simple_roots() -> tuple[RationalVector, ...]:
    return _simple_root_basis(DIRECT_COEFFICIENT_ROOTS, _direct_inner, Fraction(1))


@cache
def standard_simple_roots() -> tuple[IntegerVector, ...]:
    return _simple_root_basis(STANDARD_E8_ROOTS, _standard_inner, 8)


def _transpose(matrix) -> tuple[tuple, ...]:
    return tuple(tuple(row[column] for row in matrix) for column in range(len(matrix[0])))


def _matrix_from_columns(columns) -> RationalMatrix:
    return tuple(
        tuple(Fraction(columns[column][row]) for column in range(len(columns)))
        for row in range(len(columns[0]))
    )


def _identity(size: int) -> RationalMatrix:
    return tuple(
        tuple(Fraction(int(row == column)) for column in range(size))
        for row in range(size)
    )


def _inverse(matrix: RationalMatrix) -> RationalMatrix:
    size = len(matrix)
    augmented = [
        list(matrix[row]) + list(_identity(size)[row])
        for row in range(size)
    ]

    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if augmented[row][column] != 0),
            None,
        )
        if pivot is None:
            raise RuntimeError("simple-root basis matrix is singular")

        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_value = augmented[column][column]
        augmented[column] = [value / pivot_value for value in augmented[column]]

        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor == 0:
                continue
            augmented[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(
                    augmented[row],
                    augmented[column],
                    strict=True,
                )
            ]

    return tuple(tuple(row[size:]) for row in augmented)


def _matrix_multiply(left: RationalMatrix, right: RationalMatrix) -> RationalMatrix:
    rows = len(left)
    shared = len(right)
    columns = len(right[0])
    if len(left[0]) != shared:
        raise ValueError("matrix dimensions are incompatible")
    return tuple(
        tuple(
            sum(
                (left[row][index] * right[index][column] for index in range(shared)),
                Fraction(0),
            )
            for column in range(columns)
        )
        for row in range(rows)
    )


def _matrix_vector_multiply(matrix: RationalMatrix, vector) -> RationalVector:
    return tuple(
        sum(
            (coefficient * Fraction(component) for coefficient, component in zip(row, vector, strict=True)),
            Fraction(0),
        )
        for row in matrix
    )


@cache
def h4_to_standard_e8_matrix() -> RationalMatrix:
    direct_basis = _matrix_from_columns(direct_simple_roots())
    standard_basis = _matrix_from_columns(standard_simple_roots())
    return _matrix_multiply(standard_basis, _inverse(direct_basis))


def map_direct_root_to_standard(root: RationalVector) -> IntegerVector:
    """Map one coefficient-lifted H4-derived root into the standard E8 set."""
    if root not in frozenset(DIRECT_COEFFICIENT_ROOTS):
        raise ValueError("root must belong to the H4-derived E8 coefficient set")
    mapped = _matrix_vector_multiply(h4_to_standard_e8_matrix(), root)
    if any(component.denominator != 1 for component in mapped):
        raise RuntimeError("equivalence map produced a nonintegral standard root")
    integer = tuple(int(component) for component in mapped)
    if integer not in frozenset(STANDARD_E8_ROOTS):
        raise RuntimeError("equivalence map escaped the standard E8 root set")
    return integer


def similarity_gram() -> RationalMatrix:
    """Return M^T M for the exact equivalence map."""
    matrix = h4_to_standard_e8_matrix()
    return _matrix_multiply(_transpose(matrix), matrix)


def expected_similarity_gram() -> RationalMatrix:
    return tuple(
        tuple(Fraction(8 if row == column else 0) for column in range(8))
        for row in range(8)
    )


def map_is_bijection() -> bool:
    return {
        map_direct_root_to_standard(root) for root in DIRECT_COEFFICIENT_ROOTS
    } == set(STANDARD_E8_ROOTS)


def mirror_commutes(root: RationalVector) -> bool:
    mapped_mirror = map_direct_root_to_standard(tuple(-component for component in root))
    mapped = map_direct_root_to_standard(root)
    return mapped_mirror == tuple(-component for component in mapped)


def reflection_commutes(vector_index: int, root_index: int) -> bool:
    """Check one reflection square across the two E8 realizations."""
    golden_vector = DIRECT_E8_ROOTS[vector_index]
    golden_root = DIRECT_E8_ROOTS[root_index]
    reflected_golden = direct_e8_reflect(golden_vector, golden_root)
    reflected_coefficients = coefficient_lift_8d(reflected_golden)

    standard_vector = map_direct_root_to_standard(
        coefficient_lift_8d(golden_vector)
    )
    standard_root = map_direct_root_to_standard(
        coefficient_lift_8d(golden_root)
    )
    reflected_standard = e8_reflect(standard_vector, standard_root)

    return map_direct_root_to_standard(reflected_coefficients) == reflected_standard


if similarity_gram() != expected_similarity_gram():
    raise RuntimeError("the H4-to-standard-E8 map must be an exact scale-sqrt(8) orthogonal map")
if not map_is_bijection():
    raise RuntimeError("the H4-derived E8 roots must map bijectively to the standard E8 roots")
