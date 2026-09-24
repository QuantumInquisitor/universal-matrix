from __future__ import annotations

import copy
import json
from dataclasses import replace
from decimal import Decimal

import pytest

from src.frequency_source_catalog import (
    REFERENCE_PATH,
    cycles_per_model_tick,
    frequency_in_hz,
    load_frequency_catalog,
)


@pytest.fixture(scope="module")
def catalog():
    return load_frequency_catalog()


@pytest.fixture
def catalog_data():
    return json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))


def _load_data(tmp_path, data):
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return load_frequency_catalog(path)


def test_milli_and_megahertz_are_distinct_exact_units():
    assert frequency_in_hz("3.3", "mHz") == Decimal("0.0033")
    assert frequency_in_hz("3.3", "MHz") == Decimal("3300000")
    assert frequency_in_hz("3.3", "MHz") / frequency_in_hz("3.3", "mHz") == Decimal("1e9")


@pytest.mark.parametrize("unit", ("kHz", "KHz", "Khz"))
def test_kilohertz_aliases_preserve_decimal_precision(unit):
    assert frequency_in_hz("21.275", unit) == Decimal("21275")
    assert frequency_in_hz("0.123456789012345678901234567890123", unit) == Decimal(
        "123.456789012345678901234567890123"
    )


def test_reported_megahertz_alias_is_explicitly_supported():
    assert frequency_in_hz("4.68", "Mhz") == Decimal("4680000")


@pytest.mark.parametrize("unit", ("", "mhz", "MHZ", "GHz", "cycles/tick", None))
def test_missing_or_unrecognized_units_are_not_guessed(unit):
    with pytest.raises(ValueError, match="unit"):
        frequency_in_hz("1200", unit)


@pytest.mark.parametrize("value", (0, -1, "NaN", "sNaN", "Infinity", "-Infinity", "unknown", None, True))
def test_frequency_requires_a_known_finite_positive_value(value):
    with pytest.raises(ValueError):
        frequency_in_hz(value, "Hz")


def test_role_is_required_before_selecting_or_indexing_frequencies(catalog):
    with pytest.raises(TypeError):
        catalog.records_for_role()
    with pytest.raises(TypeError):
        catalog.frequency_index()
    for role in (None, "all", "carrier,modulation"):
        with pytest.raises(ValueError, match="explicit frequency role"):
            catalog.frequency_index(role)
    modulation = catalog.records_for_role("modulation")
    carriers = catalog.records_for_role("carrier")
    assert {record.id for record in modulation}.isdisjoint(record.id for record in carriers)
    assert all(record.role == "modulation" for record in modulation)
    assert all(record.role == "carrier" for record in carriers)


def test_equal_normalized_frequencies_keep_both_source_records(tmp_path, catalog_data):
    original = catalog_data["frequencies"][0]
    alias = copy.deepcopy(original)
    alias.update(id="independent_same_value", source_id="scoon_machine",
                 source_location="Synthetic duplicate-value regression", reported_value="21.275",
                 reported_unit="kHz")
    catalog_data["frequencies"].append(alias)
    loaded = _load_data(tmp_path, catalog_data)
    ids = loaded.frequency_index("modulation")[Decimal("21275")]
    assert set(ids) == {original["id"], alias["id"]}
    selected = {record.id: record for record in loaded.records if record.id in ids}
    assert selected[original["id"]].source_id == "scoon_analysis"
    assert selected[alias["id"]].source_id == "scoon_machine"
    assert selected[original["id"]].reported_unit == "Hz"
    assert selected[alias["id"]].reported_unit == "kHz"


def test_model_tick_conversion_needs_an_explicit_clock_scale(catalog):
    record = next(record for record in catalog.records if record.id == "modulation_tetanus")
    with pytest.raises(TypeError):
        cycles_per_model_tick(record)
    with pytest.raises(TypeError):
        cycles_per_model_tick(record, "0.0005")
    assert cycles_per_model_tick(record, seconds_per_tick="0.0005") == Decimal("0.6")
    assert cycles_per_model_tick(record, seconds_per_tick="0.001") == Decimal("1.2")
    carrier = next(record for record in catalog.records if record.id == "analysis_carrier_812a_argon")
    assert cycles_per_model_tick(carrier, seconds_per_tick="0.000001") == Decimal("3.3")


@pytest.mark.parametrize("scale", (0, -1, "NaN", "Infinity", None, True))
def test_model_tick_scale_cannot_be_zero_unknown_or_nonfinite(catalog, scale):
    with pytest.raises(ValueError):
        cycles_per_model_tick(catalog.records[0], seconds_per_tick=scale)


@pytest.mark.parametrize("section", ("frequencies", "ranges", "unresolved_settings"))
def test_record_identifiers_are_unique_across_catalog_sections(tmp_path, catalog_data, section):
    if section == "frequencies":
        catalog_data[section].append(copy.deepcopy(catalog_data[section][0]))
    else:
        catalog_data[section][0]["id"] = catalog_data["frequencies"][0]["id"]
    with pytest.raises(ValueError, match="record identifiers must be unique"):
        _load_data(tmp_path, catalog_data)


def test_source_identifiers_cannot_be_duplicated(tmp_path, catalog_data):
    catalog_data["sources"].append(copy.deepcopy(catalog_data["sources"][0]))
    with pytest.raises(ValueError, match="source identifiers must be unique"):
        _load_data(tmp_path, catalog_data)


@pytest.mark.parametrize("section", ("frequencies", "ranges", "unresolved_settings"))
def test_every_kind_of_record_requires_a_declared_source(tmp_path, catalog_data, section):
    catalog_data[section][0]["source_id"] = "missing_source"
    with pytest.raises(ValueError, match="declared source"):
        _load_data(tmp_path, catalog_data)


def test_source_without_retrievable_provenance_is_rejected(tmp_path, catalog_data):
    del catalog_data["sources"][0]["url"]
    with pytest.raises(ValueError, match="provenance and uncertainty"):
        _load_data(tmp_path, catalog_data)


def test_boolean_true_is_not_a_catalog_schema_version(tmp_path, catalog_data):
    catalog_data["schema_version"] = True
    with pytest.raises(ValueError, match="schema"):
        _load_data(tmp_path, catalog_data)


@pytest.mark.parametrize("section", ("frequencies", "ranges", "unresolved_settings"))
def test_all_record_kinds_require_nonblank_identifiers(tmp_path, catalog_data, section):
    catalog_data[section][0]["id"] = " "
    with pytest.raises(ValueError):
        _load_data(tmp_path, catalog_data)


@pytest.mark.parametrize("approximate", (1, "true", None))
def test_range_approximation_status_must_be_a_boolean(tmp_path, catalog_data, approximate):
    catalog_data["ranges"][0]["approximate"] = approximate
    with pytest.raises(ValueError):
        _load_data(tmp_path, catalog_data)


def test_unknown_measurement_uncertainty_remains_unknown(catalog):
    assert all(record.measurement_uncertainty_hz is None for record in catalog.records)
    precise_looking = next(record for record in catalog.records if record.id == "modulation_bx")
    assert precise_looking.reported_value == "21275"
    assert precise_looking.approximate is False
    assert precise_looking.measurement_uncertainty_hz is None
    known = replace(precise_looking, measurement_uncertainty_hz="0.5")
    assert known.measurement_uncertainty_hz == "0.5"
    for uncertainty in ("0", "-1", "NaN", "unknown"):
        with pytest.raises(ValueError):
            replace(precise_looking, measurement_uncertainty_hz=uncertainty)


@pytest.mark.parametrize("field", ("frequency_hz", "reported_value", "normalized_hz"))
def test_unresolved_dial_settings_cannot_silently_acquire_a_frequency(tmp_path, catalog_data, field):
    catalog_data["unresolved_settings"][0][field] = "1200"
    with pytest.raises(ValueError, match="cannot silently acquire a frequency"):
        _load_data(tmp_path, catalog_data)


def test_complete_source_table_retains_critical_values_and_setting_labels(catalog):
    assert len(catalog.records) == 24
    modulation = catalog.records_for_role("modulation")
    assert len(modulation) == 16
    assert sum(record.source_location.startswith("Treatment Settings table, row ")
               for record in modulation) == 15
    assert len(catalog.ranges) == 5
    assert len(catalog.unresolved_settings) == 12
    records = {record.id: record for record in catalog.records}
    for identifier, label, hz, band, dial in (
        ("modulation_bx", "BX", "21275", 4, "10"),
        ("modulation_tetanus", "Tetanus", "1200", 2, "78.5"),
        ("modulation_tb_rod", "TB Rod", "8300", 3, "63"),
    ):
        record = records[identifier]
        assert (record.historical_label, record.reported_value, record.reported_unit, record.band, record.dial) == (
            label, hz, "Hz", band, dial
        )
        assert record.hz == Decimal(hz)
        assert record.source_id == "scoon_analysis"
        assert record.source_location.startswith("Treatment Settings table, row ")
    assert records["modulation_gc_typhoid_uncertain"].historical_label == "GC+Typhoid?"


def test_carrier_configurations_and_report_sources_remain_distinct(catalog):
    carriers = {record.id: record for record in catalog.records_for_role("carrier")}
    expected = {
        "analysis_carrier_812a_argon": ("3.3", "MHz", "3300000", "scoon_analysis"),
        "analysis_carrier_809_helium": ("4.68", "Mhz", "4680000", "scoon_analysis"),
        "machine_resting_carrier": ("3.33", "MHz", "3330000", "scoon_machine"),
    }
    assert set(carriers) == set(expected)
    for identifier, (value, unit, hz, source) in expected.items():
        record = carriers[identifier]
        assert (record.reported_value, record.reported_unit, record.source_id) == (value, unit, source)
        assert record.hz == Decimal(hz)
    assert len({record.configuration for record in carriers.values()}) == 3
    sources = {source["id"]: source for source in catalog.sources}
    assert sources["scoon_analysis"]["url"] != sources["scoon_machine"]["url"]
    assert all(record.source_location and sources[record.source_id]["uncertainty_note"]
               for record in carriers.values())


def test_reported_band_ranges_retain_raw_units_without_filling_unresolved_settings(catalog):
    expected = (("20", "200"), ("200", "2000"), ("2000", "20000"), ("20000", "200000"))
    bands = sorted((row for row in catalog.ranges if row["band"] is not None), key=lambda row: row["band"])
    assert [row["band"] for row in bands] == [1, 2, 3, 4]
    for row, (lower, upper) in zip(bands, expected, strict=True):
        assert frequency_in_hz(row["lower_value"], row["lower_unit"]) == Decimal(lower)
        assert frequency_in_hz(row["upper_value"], row["upper_unit"]) == Decimal(upper)
    assert bands[1]["upper_unit"] == "KHz"
    assert bands[2]["lower_unit"] == "KHz"
    unresolved = {row["historical_label"]: row for row in catalog.unresolved_settings}
    assert unresolved["V"]["setting_as_reported"] == "band 3, dial 39"
    assert unresolved["Radiation"]["setting_as_reported"] == "2-17-3"
    assert all(row["reason"] and not {"frequency_hz", "reported_value", "normalized_hz"}.intersection(row)
               for row in catalog.unresolved_settings)


def test_uncalibrated_waveform_example_is_separate_from_the_historical_setting_table(catalog):
    example = next(record for record in catalog.records if record.id == "machine_modulation_example")
    assert example.role == "modulation"
    assert example.reported_value == "1430"
    assert example.reported_unit == "Hz"
    assert example.hz == Decimal("1430")
    assert example.source_id == "scoon_machine"
    assert example.band is None and example.dial is None
    assert example.measurement_uncertainty_hz is None
    assert "uncalibrated" in example.configuration.lower()
    assert not example.source_location.startswith("Treatment Settings table, row ")
    assert "modulation" in example.historical_label.lower()


def test_later_booster_bandwidth_is_not_selected_as_a_carrier_or_modulation(catalog):
    bandwidths = catalog.records_for_role("bandwidth")
    assert len(bandwidths) == 1
    bandwidth = bandwidths[0]
    assert bandwidth.id == "machine_booster_bandwidth"
    assert (bandwidth.reported_value, bandwidth.reported_unit) == ("800", "KHz")
    assert bandwidth.hz == Decimal("800000")
    assert bandwidth.approximate is True
    assert bandwidth.source_id == "scoon_machine"
    assert "booster" in bandwidth.configuration.lower()
    assert bandwidth.band is None and bandwidth.dial is None
    assert bandwidth.id not in {record.id for record in catalog.records_for_role("carrier")}
    assert bandwidth.id not in {record.id for record in catalog.records_for_role("modulation")}
    assert catalog.frequency_index("bandwidth") == {Decimal("800000"): (bandwidth.id,)}


def test_overall_booster_input_range_is_distinct_from_numbered_oscillator_bands(catalog):
    overall = [row for row in catalog.ranges if row["band"] is None]
    assert len(overall) == 1
    row = overall[0]
    assert row["id"] == "machine_booster_input_range"
    assert row["source_id"] == "scoon_machine"
    assert (row["lower_value"], row["lower_unit"]) == ("20", "Hz")
    assert (row["upper_value"], row["upper_unit"]) == ("200", "Khz")
    assert frequency_in_hz(row["lower_value"], row["lower_unit"]) == Decimal("20")
    assert frequency_in_hz(row["upper_value"], row["upper_unit"]) == Decimal("200000")
    assert row["approximate"] is False
    source = next(source for source in catalog.sources if source["id"] == row["source_id"])
    assert source["url"].endswith("scoon_1939_beam_ray_machine.html")
