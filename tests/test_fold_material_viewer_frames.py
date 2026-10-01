"""Science-viewer adapter controls for computed material time series."""

import numpy as np
import pytest

from scripts.export_fold_material_viewer_frames import adapt
from scripts.report_fold_material_supply import simulate


@pytest.fixture(scope="module")
def payload():
    case = simulate(duration=0.05, max_step=0.002)
    report = {"schema": 1, "cases": {"powered": case}}
    return report, adapt(report)


def test_preserves_ordered_time_series_and_ledgers(payload):
    report, viewer = payload
    source = report["cases"]["powered"]
    assert viewer["frame_count"] == len(source["samples"])
    assert viewer["module_count"] == 4
    assert [frame["time_s"] for frame in viewer["frames"]] == [
        sample["time_s"] for sample in source["samples"]
    ]
    for frame, sample in zip(viewer["frames"], source["samples"], strict=True):
        for module, reserve, supplied in zip(
            frame["modules"], sample["reserve_j"], sample["input_j"], strict=True
        ):
            assert module["reserve_j"] == reserve
            assert module["input_j"] == supplied


def test_metres_are_preserved_and_display_coordinates_are_explicit(payload):
    _, viewer = payload
    frame = viewer["frames"][0]
    assert viewer["units"]["source_length"] == "metre"
    assert viewer["units"]["display_m_per_unit"] == 0.1
    for module in frame["modules"]:
        assert len(module["bodies"]) == 22
        assert len({body["id"] for body in module["bodies"]}) == 22
        for body in module["bodies"]:
            metres = np.asarray(body["vertices_m"])
            display = np.asarray(body["vertices_display"])
            np.testing.assert_allclose(display, metres / 0.1, rtol=0, atol=1e-15)


def test_equal_size_equal_state_modules_have_equal_local_geometry(payload):
    _, viewer = payload
    frame = viewer["frames"][0]
    a, b = frame["modules"][2], frame["modules"][3]
    assert a["size"] == b["size"] == 0.5
    assert a["q"] == b["q"]
    for body_a, body_b in zip(a["bodies"], b["bodies"], strict=True):
        np.testing.assert_allclose(body_a["vertices_m"], body_b["vertices_m"], rtol=0, atol=0)


def test_adapter_does_not_claim_existing_viewer_direct_compatibility(payload):
    _, viewer = payload
    compatibility = viewer["compatibility"]
    assert not compatibility["current_repository_visualizers_are_direct_consumers"]
    assert compatibility["adapter_exposes_one_ordered_frame_sequence"]
    assert compatibility["metre_geometry_preserved"]
    assert compatibility["normalized_display_coordinates_added"]
    assert "No unvalidated global spatial placement" in viewer["coordinate_policy"]


@pytest.mark.parametrize(
    "report,kwargs",
    [
        ({}, {}),
        ({"schema": 1, "cases": {}}, {}),
        ({"schema": 1, "cases": {"powered": {}}}, {}),
        ({"schema": 1, "cases": {"powered": {"settings": {"sizes": [1], "edges": []}, "samples": []}}}, {}),
        ({"schema": 1, "cases": {"powered": {"settings": {"sizes": [1], "edges": []}, "samples": [{"time_s": 0}]}}}, {}),
        ({"schema": 1, "cases": {"powered": {"settings": {"sizes": [1], "edges": []}, "samples": []}}}, {"display_m_per_unit": 0}),
    ],
)
def test_invalid_payloads_rejected(report, kwargs):
    with pytest.raises(ValueError):
        adapt(report, **kwargs)
