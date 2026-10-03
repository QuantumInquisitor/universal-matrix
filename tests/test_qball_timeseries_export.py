import hashlib
import json
from dataclasses import replace

import pytest

from src import qball_highres_timeseries_t2p5 as driver
from src import qball_timeseries_export as exporter
from src.qball_highres_timeseries import (
    HighResolutionTimeSeriesResult,
    TimeSeriesSample,
    summarize_channel,
)


def synthetic_result():
    direct = tuple(
        TimeSeriesSample(i, i * 0.125, i * 1e-9, -i * 1e-12, 1 - i * 0.01, 1 + i * 0.02)
        for i in range(3)
    )
    perturbed = tuple(replace(s, peak_ratio=s.peak_ratio + 0.0001234567890123) for s in direct)
    return HighResolutionTimeSeriesResult(
        direct=summarize_channel(direct),
        perturbed=summarize_channel(perturbed),
        steps=2,
        dt=0.125,
        sample_stride=1,
    )


def test_round_trip_preserves_all_samples_fields_and_explicit_metadata(tmp_path):
    result = synthetic_result()
    path = tmp_path / "samples" / "synthetic.json"
    exporter.write_timeseries_samples(
        result, path, configuration={"scope": "synthetic test only"}, provenance={"run_id": "stub"}
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    for name in ("direct", "perturbed"):
        restored = tuple(TimeSeriesSample(**record) for record in payload["channels"][name])
        assert restored == getattr(result, name).samples
    assert payload["sampling"] == {"steps": 2, "dt": 0.125, "sample_stride": 1}
    assert payload["configuration"] == {"scope": "synthetic test only"}
    assert payload["provenance"] == {"run_id": "stub"}
    assert "no physical seconds" in payload["columns"]["time"]
    assert "Cannot restart" in payload["scope"]


def test_nonfinite_sample_refused_before_output_written(tmp_path):
    result = synthetic_result()
    bad = replace(result.direct.samples[0], peak_ratio=float("nan"))
    result = replace(
        result, direct=replace(result.direct, samples=(bad,) + result.direct.samples[1:])
    )
    path = tmp_path / "bad.json"
    with pytest.raises(ValueError):
        exporter.write_timeseries_samples(result, path, configuration={}, provenance={})
    assert not path.exists()


@pytest.mark.parametrize("with_export", [False, True])
def test_cli_runs_once_preserves_report_and_exports_same_object(
    monkeypatch, capsys, tmp_path, with_export
):
    result = synthetic_result()
    run = driver.HighResolutionTimeSeriesT2p5(
        result, driver._extended(result.direct), driver._extended(result.perturbed)
    )
    calls = []
    exports = []

    def run_once():
        calls.append(True)
        return run

    monkeypatch.setattr(driver, "run_high_resolution_timeseries_t2p5", run_once)
    monkeypatch.setattr(
        exporter, "export_t2p5_samples", lambda existing, path: exports.append((existing, path))
    )
    path = str(tmp_path / "samples.json")
    driver.main(["--samples-json", path] if with_export else [])
    assert calls == [True]
    assert (
        capsys.readouterr().out == driver.format_high_resolution_timeseries_t2p5_report(run) + "\n"
    )
    assert len(exports) == int(with_export)
    if with_export:
        assert exports[0][0] is run
        assert exports[0][1] == path


def test_source_snapshot_hashes_normalized_bytes_with_relative_paths(tmp_path):
    source = tmp_path / "src"
    source.mkdir()
    (source / "example.py").write_bytes(b"value = 1\r\n")
    provenance = exporter.source_provenance(tmp_path)
    assert provenance["source_sha256"] == {
        "src/example.py": hashlib.sha256(b"value = 1\n").hexdigest()
    }
    assert provenance["git_head"] is None
    assert provenance["source_tree_dirty"] is None
