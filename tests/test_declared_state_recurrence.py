import copy
import math

import numpy as np
import pytest

from src.declared_state_recurrence import clock_phase_history, compare, dumps, loads, snapshot

UNITS = {
    "position": "m",
    "velocity": "m/s",
    "orientation": "radian",
    "phase": "radian",
    "internal.mode": "dimensionless",
}
LIMITS = {k: 1e-10 for k in UNITS}


def specimen(tick=0):
    return snapshot(
        [
            {
                "id": "body",
                "position": [1, 0, 0],
                "velocity": [0, 1, 0],
                "orientation": np.eye(3),
                **clock_phase_history(tick),
                "internal": {"mode": 0},
            }
        ],
        model_id="test-model-v1",
        units=UNITS,
    )


@pytest.mark.parametrize("channel", ["velocity", "orientation", "phase", "internal"])
def test_same_position_does_not_hide_other_state_changes(channel):
    first = specimen()
    other = copy.deepcopy(first)
    row = other["components"][0]
    if channel == "velocity":
        row[channel] = [0, -1, 0]
    elif channel == "orientation":
        row[channel] = np.diag([-1, -1, 1]).tolist()
    elif channel == "phase":
        row[channel] = math.pi
    else:
        row[channel]["mode"] = 1
    result = compare(first, other, tolerances=LIMITS, winding_is_state=False)
    assert result["position_return"] and not result["declared_state_return"]
    assert result["changed_components"][0]["failed_channels"] == [
        "internal.mode" if channel == "internal" else channel
    ]


def test_clock_full_turn_keeps_cyclic_state_and_explicit_history():
    first, last = specimen(0), specimen(36)
    physical = compare(first, last, tolerances=LIMITS, winding_is_state=False)
    historical = compare(first, last, tolerances=LIMITS, winding_is_state=True)
    assert physical["declared_state_return"] and not physical["history_return"]
    assert not historical["declared_state_return"]
    assert physical["history_changes"] == [{"id": "body", "winding_delta": "1"}]


@pytest.mark.parametrize("tick", [-37, -36, -1, 0, 35, 36, 37, 36 * 10**30 + 7])
def test_exact_history_survives_save_resume_and_reverse_path(tick):
    saved = loads(dumps(specimen(tick)))
    assert saved == specimen(tick)
    phase = saved["components"][0]["phase"]
    turns = int(saved["components"][0]["winding"])
    recovered_tick = turns * 36 + round(phase / (math.pi / 18))
    assert recovered_tick == tick
    for increment in (-73, -1, 0, 1, 73):
        assert clock_phase_history(recovered_tick + increment) == clock_phase_history(
            tick + increment
        )
    assert compare(saved, specimen(recovered_tick), tolerances=LIMITS, winding_is_state=True)[
        "declared_state_return"
    ]


def test_wrapped_phase_comparison_handles_cut_without_erasing_history():
    a, b = specimen(), specimen()
    b["components"][0]["phase"] = math.tau - 1e-12
    assert compare(a, b, tolerances=LIMITS, winding_is_state=False)["declared_state_return"]


@pytest.mark.parametrize("channel", ["position", "velocity", "orientation"])
def test_zero_tolerance_detects_tiny_resolved_changes(channel):
    a, b = specimen(), specimen()
    tiny = 1e-200
    if channel == "orientation":
        b["components"][0][channel] = [[1, -tiny, 0], [tiny, 1, 0], [0, 0, 1]]
    else:
        a["components"][0][channel] = [0, 0, 0]
        b["components"][0][channel] = [tiny, 0, 0]
    result = compare(a, b, tolerances={k: 0 for k in UNITS}, winding_is_state=False)
    assert not result["declared_state_return"]
    assert result["maximum_errors"][channel] > 0


@pytest.mark.parametrize(
    "defect",
    [
        "missing_component",
        "different_model",
        "different_units",
        "missing_tolerance",
        "nan",
        "duplicate",
        "reflection",
        "fractional_winding",
        "negative_tolerance",
    ],
)
def test_incompatible_or_corrupt_state_cannot_silently_pass(defect):
    a, b, limits = specimen(), specimen(), dict(LIMITS)
    if defect == "missing_component":
        b["components"] = []
    elif defect == "different_model":
        b["model_id"] = "other"
    elif defect == "different_units":
        b["units"]["position"] = "mm"
    elif defect == "missing_tolerance":
        limits.pop("velocity")
    elif defect == "nan":
        b["components"][0]["velocity"][0] = float("nan")
    elif defect == "duplicate":
        b["components"] *= 2
    elif defect == "reflection":
        b["components"][0]["orientation"] = np.diag([1, 1, -1]).tolist()
    elif defect == "fractional_winding":
        b["components"][0]["winding"] = "0.5"
    else:
        limits["phase"] = -1
    with pytest.raises(ValueError):
        compare(a, b, tolerances=limits, winding_is_state=False)
