"""Independent accounting, failure-detection and report controls."""

import copy

import pytest

from scripts.report_phase_current_contract import report, split_power, validate


@pytest.mark.parametrize(
    "parent,child,transport,storage",
    [
        (-3, 3, 3, 0),
        (-2, -2, 0, 4),
        (0, 2, 1, -2),
        (0, 0, 0, 0),
    ],
)
def test_known_transport_and_storage_cases(parent, child, transport, storage):
    assert split_power(parent, child) == {"transport_w": transport, "storage_rate_w": storage}


def test_endpoint_exchange_reverses_transport_but_preserves_storage():
    forward = split_power(-7, 3)
    backward = split_power(3, -7)
    assert backward["transport_w"] == -forward["transport_w"]
    assert backward["storage_rate_w"] == forward["storage_rate_w"]


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_endpoint_powers_rejected(value):
    with pytest.raises(ValueError):
        split_power(value, 0)
    with pytest.raises(ValueError):
        split_power(0, value)


@pytest.fixture(scope="module")
def result():
    return report()


def test_finite_difference_storage_and_gauge_controls(result):
    validate(result)


def test_omitting_storage_fails_on_same_signed_endpoint_powers(result):
    rows = [row for row in result["mechanical_cases"] if row["case"] == "both_moving"]
    assert len(rows) == 3
    for row in rows:
        assert row["parent_power_w"] < 0 and row["child_power_w"] < 0
        assert abs(row["parent_power_w"] + row["child_power_w"]) > 1e-10


def test_report_detects_corrupted_balance(result):
    corrupted = copy.deepcopy(result)
    corrupted["mechanical_cases"][0]["storage_derivatives"][0]["balance_residual_w"] = 1
    with pytest.raises(AssertionError):
        validate(corrupted)


def test_report_detects_changed_provenance(result):
    corrupted = copy.deepcopy(result)
    corrupted["sources"]["src/gauge_matter.py"] = "wrong"
    with pytest.raises(ValueError, match="source hash"):
        validate(corrupted)
