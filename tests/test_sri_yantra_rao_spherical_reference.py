from __future__ import annotations

import math

from src.sri_yantra_rao_spherical_reference import (
    RAO_TABLE1_REFERENCE_DERIVED,
    RAO_TABLE1_REFERENCE_PARAMETERS,
    RAO_TABLE1_REFERENCE_RESIDUALS,
    derive_rao_spherical,
    selected_constraint_residuals,
)


def test_published_table1_reference_row_is_encoded_verbatim():
    parameters = RAO_TABLE1_REFERENCE_PARAMETERS

    assert parameters.b == 0.231687
    assert parameters.c == 0.120012
    assert parameters.d == 0.146680
    assert parameters.e == 0.230471
    assert parameters.g == 0.053009
    assert parameters.h == 1.076084


def test_spherical_axis_partitions_close_rao_equation_2_2():
    parameters = RAO_TABLE1_REFERENCE_PARAMETERS

    assert math.isclose(parameters.r + parameters.h, math.pi / 2, abs_tol=1e-15)
    assert math.isclose(
        parameters.a + parameters.b + parameters.c,
        parameters.r,
        abs_tol=1e-15,
    )
    assert math.isclose(
        parameters.d + parameters.e + parameters.f,
        parameters.r,
        abs_tol=1e-15,
    )
    assert parameters.a > 0.0
    assert parameters.f > 0.0


def test_reference_derived_arcs_use_the_acute_published_branch():
    derived = RAO_TABLE1_REFERENCE_DERIVED

    values = (
        derived.x1,
        derived.x2,
        derived.x3,
        derived.x4,
        derived.x5,
        derived.x6,
        derived.x7,
        derived.x8,
        derived.x9,
        derived.x10,
        derived.x11,
        derived.x12,
        derived.x13,
        derived.x14,
        derived.x16,
        derived.x17,
        derived.x18,
        derived.x19,
    )
    assert all(0.0 < value < math.pi / 2 for value in values)


def test_selected_published_constraints_close_from_six_decimal_input():
    residuals = RAO_TABLE1_REFERENCE_RESIDUALS

    assert residuals.selected_indices == (1, 2, 4, 5, 10, 19)
    assert residuals.maximum_absolute < 1e-6


def test_each_reference_constraint_residual_is_small_individually():
    residuals = RAO_TABLE1_REFERENCE_RESIDUALS

    assert abs(residuals.f1) < 4e-7
    assert abs(residuals.f2) < 1e-7
    assert abs(residuals.f4) < 2e-8
    assert abs(residuals.f5) < 1e-7
    assert abs(residuals.f10) < 3e-7
    assert abs(residuals.f19) < 3e-7


def test_public_derivation_is_reproducible():
    derived = derive_rao_spherical(RAO_TABLE1_REFERENCE_PARAMETERS)
    residuals = selected_constraint_residuals(derived)

    assert derived == RAO_TABLE1_REFERENCE_DERIVED
    assert residuals == RAO_TABLE1_REFERENCE_RESIDUALS
