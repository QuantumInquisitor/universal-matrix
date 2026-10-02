"""Controls for the dense governing-state recursive clearance audit."""

from scripts.report_fold_recursive_governing_clearance import (
    CORNER_Q,
    DENSE_Q,
    DENSE_SCALE_VALUES,
    DENSE_THETA_VALUES,
    is_corner_q,
)


def test_dense_grid_contains_declared_corner():
    assert CORNER_Q in DENSE_Q
    assert len(DENSE_Q) == len(DENSE_SCALE_VALUES) * len(DENSE_THETA_VALUES)


def test_dense_grid_stays_inside_declared_domain():
    assert min(DENSE_SCALE_VALUES) >= 0.9
    assert max(DENSE_SCALE_VALUES) <= 1.1
    assert min(DENSE_THETA_VALUES) >= 0
    assert max(DENSE_THETA_VALUES) <= 3.141592653589793 / 6


def test_corner_classifier_is_exact():
    assert is_corner_q((1.1, 0.0))
    assert not is_corner_q((1.095, 0.0))
    assert not is_corner_q((1.1, 0.0025))
