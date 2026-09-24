import copy
import json
from decimal import Decimal

import pytest

from src.spectral_reference_catalog import (
    REFERENCE_DIR,
    load_cafl_catalog,
    load_hydrogen_catalog,
    parse_cafl_entries,
    wavelength_frequency_hz,
)


def test_vacuum_conversion_and_explicit_air_correction():
    assert wavelength_frequency_hz("5000", medium="vacuum") == Decimal("599584916000000")
    air = wavelength_frequency_hz("5000", medium="air", phase_refractive_index="1.0003")
    assert abs(air * Decimal("1.0003") - Decimal("599584916000000")) < Decimal("1e-12")
    assert air < wavelength_frequency_hz("5000", medium="vacuum")


@pytest.mark.parametrize("medium,index", [("air", None), (None, None), ("unknown", None),
                                           ("air", 1), ("air", "NaN"), ("vacuum", 1.0003)])
def test_conversion_does_not_invent_medium_or_index(medium, index):
    with pytest.raises(ValueError):
        wavelength_frequency_hz("5000", medium=medium, phase_refractive_index=index)


@pytest.mark.parametrize("value", [0, -1, True, "NaN", "Infinity", "missing", None])
def test_nonphysical_wavelengths_rejected(value):
    with pytest.raises(ValueError):
        wavelength_frequency_hz(value, medium="vacuum")


def test_parser_excludes_annotation_numbers_and_preserves_duplicates():
    result = parse_cafl_entries([(41, "Example (annotation 600, duration 5; nested (99)) - 10, 2.5, 10")])
    assert result == [{"id": "cafl-41", "label": "Example", "source_lines": [41, 41],
                       "values_hz": ["10", "2.5", "10"], "annotations_omitted": True,
                       "status": "explicit_values"}]


def test_multiline_annotation_and_embedded_separator_do_not_leak():
    result = parse_cafl_entries([(1, "Example (first 99 - 6,"),
                                (2, "second 500) - 1000, 1.2"),
                                (3, "Alias (see Example, 700)"), (4, "Empty - (no field)")])
    assert result[0]["values_hz"] == ["1000", "1.2"]
    assert result[0]["source_lines"] == [1, 2]
    assert result[1]["values_hz"] == []
    assert result[2]["label"] == "Empty"
    assert result[2]["status"] == "no_explicit_values"


@pytest.mark.parametrize("line", ["Example (unfinished - 50", "Example ) - 50",
                                   "Example - 50, 2 minutes", "Example - 5-9", "Example - 1,,2",
                                   "Example - 0", "Example - 2e3", "Example - 12(annotation)34",
                                   "Example- 100, 200"])
def test_unsupported_source_syntax_fails_closed(line):
    with pytest.raises(ValueError):
        parse_cafl_entries([(1, line)])


def test_parser_rejects_reordered_source_positions():
    with pytest.raises(ValueError):
        parse_cafl_entries([(2, "A - 10"), (1, "B - 20")])


def test_cafl_source_coverage_and_selected_original_values():
    catalog = load_cafl_catalog()
    assert catalog["source_version"] == "v2023_05_25"
    assert len(catalog["records"]) == 1557
    assert catalog["coverage"]["frequency_occurrences"] == 11668
    labels = {r["label"]: r for r in catalog["records"]}
    assert labels["Acute_pain"]["values_hz"] == ["3000", "95", "10000", "1550", "802", "880", "787", "727", "690", "666"]
    assert labels["Zearalenone_HC"]["values_hz"] == ["4978.71", "247.88"]
    assert labels["Actinomycosis"]["values_hz"] == []
    assert labels["Cancer"]["source_lines"] == [390, 391]
    assert "11780000" not in labels["Cancer"]["values_hz"]
    assert labels["Enterobiasis"]["values_hz"] == []


def test_hydrogen_source_precision_medium_and_derivation():
    catalog = load_hydrogen_catalog()
    assert catalog["coverage"] == {"rows": 30, "vacuum": 8, "air": 22, "persistent": 14}
    rows = {row["wavelength_A"]: row for row in catalog["rows"]}
    assert rows["1215.66824"]["wavelength_type"] == "Ritz_resolved_fine_structure"
    assert rows["949.7430"]["wavelength_type"] == "unresolved_multiplet_weighted_average_energies"
    assert rows["123685"]["medium"] == "air"  # Handbook IR convention, not an assumed cutoff.
    assert rows["18751.01"]["flags"] == ["P", "c"]
    assert all(row["wavelength_uncertainty_A"] is None for row in rows.values())


def test_catalogs_cannot_be_silently_reclassified(tmp_path):
    cases = [(load_cafl_catalog(), load_cafl_catalog), (load_hydrogen_catalog(), load_hydrogen_catalog)]
    for data, loader in cases:
        data["evidence_class"] = "measured_biological_resonance"
        path = tmp_path / "bad.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        with pytest.raises(ValueError, match="evidence"):
            loader(path)


@pytest.mark.parametrize("kind", ["duplicate", "counts", "unit", "uncertainty", "missing_reference"])
def test_changed_source_contracts_rejected(tmp_path, kind):
    data = copy.deepcopy(load_hydrogen_catalog())
    if kind == "duplicate":
        data["rows"][1]["id"] = data["rows"][0]["id"]
    elif kind == "counts":
        data["coverage"]["rows"] -= 1
    elif kind == "unit":
        data["rows"][0]["medium"] = None
    elif kind == "uncertainty":
        data["rows"][0]["wavelength_uncertainty_A"] = "0"
    else:
        data["rows"][0]["line_reference"] = "unknown"
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        load_hydrogen_catalog(path)


def test_russell_leads_remain_hypotheses_and_unknown_units():
    data = json.loads((REFERENCE_DIR / "universal_one_numeric_leads.json").read_text(encoding="utf-8"))
    assert data["evidence_class"] == "historical_author_proposal"
    assert len(data["records"]) == 5
    assert all(r["usable_as_measured_frequency"] is False for r in data["records"])
    unresolved = [r for r in data["records"] if r["evidence"] == "unresolved_units"]
    assert [r["value"] for r in unresolved] == ["7817.2", "7392.3", "6944.8"]
    assert all(r["unit"] is None and r["medium"] is None for r in unresolved)
