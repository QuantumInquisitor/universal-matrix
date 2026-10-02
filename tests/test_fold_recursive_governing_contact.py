"""Controls for the governing recursive continuous contact solver."""

import pytest

from scripts.report_fold_recursive_governing_contact import (
    monotonicity,
)


def test_monotonicity_classifies_non_decreasing_sequence():
    row = monotonicity((0, 1, 2), (0.0, 1.0, 2.0))
    assert row["nondecreasing"]
    assert not row["nonincreasing"]


def test_monotonicity_classifies_non_increasing_sequence():
    row = monotonicity((0, 1, 2), (2.0, 1.0, 0.0))
    assert not row["nondecreasing"]
    assert row["nonincreasing"]


def test_monotonicity_rejects_unsorted_axis():
    with pytest.raises(ValueError):
        monotonicity((0, 0, 1), (1, 2, 3))


def test_monotonicity_rejects_misaligned_values():
    with pytest.raises(ValueError):
        monotonicity((0, 1), (1,))
