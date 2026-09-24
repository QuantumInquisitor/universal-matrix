"""Provenance-preserving frequency data for optional numerical experiments.

Historical instrument observations are inputs, not biological resonances or
validated material properties. Carrier, modulation, spectral observations and
unresolved dial settings remain distinct. No hardware or canonical state is
changed by this module.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path

_UNIT_EXPONENTS = {"mHz": -3, "Hz": 0, "kHz": 3, "KHz": 3, "Khz": 3, "MHz": 6, "Mhz": 6}
FREQUENCY_ROLES = frozenset(("modulation", "carrier", "reported_spectral_component", "mains_modulation", "bandwidth"))
REFERENCE_PATH = Path(__file__).parent / "reference_data" / "rife_scoon_catalog.json"


def _positive_decimal(value, name: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be finite and positive")
    try:
        result = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError(f"{name} must be a decimal number") from error
    if not result.is_finite() or result <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return result


def frequency_in_hz(value, unit: str) -> Decimal:
    """Normalize explicit units without conflating milli- and megahertz."""
    if unit not in _UNIT_EXPONENTS:
        raise ValueError("frequency unit must be explicit and supported")
    value = _positive_decimal(value, "frequency")
    with localcontext() as context:
        context.prec = max(28, len(value.as_tuple().digits) + 8)
        return value.scaleb(_UNIT_EXPONENTS[unit])


@dataclass(frozen=True)
class FrequencyRecord:
    id: str
    source_id: str
    source_location: str
    historical_label: str
    reported_value: str
    reported_unit: str
    role: str
    approximate: bool
    measurement_uncertainty_hz: str | None
    band: int | None
    dial: str | None
    configuration: str

    def __post_init__(self) -> None:
        if any(not isinstance(value, str) or not value.strip() for value in (
                self.id, self.source_id, self.source_location, self.historical_label, self.configuration)):
            raise ValueError("frequency records require identifiers and source context")
        if self.role not in FREQUENCY_ROLES or not isinstance(self.approximate, bool):
            raise ValueError("frequency role and approximation status must be explicit")
        frequency_in_hz(self.reported_value, self.reported_unit)
        if self.measurement_uncertainty_hz is not None:
            _positive_decimal(self.measurement_uncertainty_hz, "measurement uncertainty")
        if self.band is not None and (type(self.band) is not int or self.band not in (1, 2, 3, 4)):
            raise ValueError("band must be a reported setting from 1 through 4")
        if self.dial is not None:
            # Zero is a possible dial position, unlike a frequency.
            try:
                dial = Decimal(str(self.dial))
            except InvalidOperation as error:
                raise ValueError("dial must be a number in [0,100]") from error
            if not dial.is_finite() or not 0 <= dial <= 100:
                raise ValueError("dial must be a number in [0,100]")

    @property
    def hz(self) -> Decimal:
        return frequency_in_hz(self.reported_value, self.reported_unit)


@dataclass(frozen=True)
class FrequencyCatalog:
    metadata: dict
    records: tuple[FrequencyRecord, ...]
    sources: tuple[dict, ...]
    ranges: tuple[dict, ...]
    unresolved_settings: tuple[dict, ...]

    def records_for_role(self, role: str) -> tuple[FrequencyRecord, ...]:
        if role not in FREQUENCY_ROLES:
            raise ValueError("choose an explicit frequency role")
        return tuple(record for record in self.records if record.role == role)

    def frequency_index(self, role: str) -> dict[Decimal, tuple[str, ...]]:
        """Index one role while preserving every source record at each value."""
        values = {}
        for record in self.records_for_role(role):
            values.setdefault(record.hz, []).append(record.id)
        return {value: tuple(values[value]) for value in sorted(values)}


def load_frequency_catalog(path: str | Path = REFERENCE_PATH) -> FrequencyCatalog:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if (type(data.get("schema_version")) is not int or data["schema_version"] != 1
            or data.get("scope") != "historical_instrument_data_only"):
        raise ValueError("unsupported frequency catalog schema or scope")
    sources = tuple(data["sources"])
    source_ids = {source["id"] for source in sources}
    if len(source_ids) != len(sources) or not source_ids:
        raise ValueError("catalog source identifiers must be unique and nonempty")
    for source in sources:
        if any(not isinstance(source.get(key), str) or not source[key].strip()
               for key in ("id", "url", "author", "source_kind", "uncertainty_note")):
            raise ValueError("sources must declare provenance and uncertainty")
    records = tuple(FrequencyRecord(**row) for row in data["frequencies"])
    ranges, unresolved = tuple(data["ranges"]), tuple(data["unresolved_settings"])
    identifiers = [record.id for record in records] + [row["id"] for row in (*ranges, *unresolved)]
    if any(not isinstance(identifier, str) or not identifier.strip() for identifier in identifiers):
        raise ValueError("catalog record identifiers must be nonempty strings")
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("catalog record identifiers must be unique")
    if any(source not in source_ids for source in (
            *(record.source_id for record in records), *(row["source_id"] for row in (*ranges, *unresolved)))):
        raise ValueError("every record must reference a declared source")
    for row in ranges:
        low = frequency_in_hz(row["lower_value"], row["lower_unit"])
        high = frequency_in_hz(row["upper_value"], row["upper_unit"])
        if low >= high or (row["band"] is not None and (
                type(row["band"]) is not int or row["band"] not in (1, 2, 3, 4))):
            raise ValueError("reported ranges require ordered endpoints and a valid band")
        if not isinstance(row.get("approximate"), bool):
            raise ValueError("reported ranges require explicit approximation status")
    for row in unresolved:
        if any(not isinstance(row.get(key), str) or not row[key].strip()
               for key in ("historical_label", "setting_as_reported", "reason")):
            raise ValueError("unresolved settings must retain their original context")
        if any(key in row for key in ("frequency_hz", "reported_value", "normalized_hz")):
            raise ValueError("unresolved settings cannot silently acquire a frequency")
    metadata = {key: data[key] for key in ("schema_version", "catalog_id", "retrieved_on", "scope")}
    return FrequencyCatalog(metadata, records, sources, ranges, unresolved)


def cycles_per_model_tick(record: FrequencyRecord, *, seconds_per_tick) -> Decimal:
    """Unit conversion only; the physical clock scale must be supplied.

    This does not derive a Matrix clock scale, drive a field, predict a
    resonance, or simulate a piezoelectric response.
    """
    seconds = _positive_decimal(seconds_per_tick, "seconds_per_tick")
    with localcontext() as context:
        context.prec = max(28, len(record.hz.as_tuple().digits) + len(seconds.as_tuple().digits) + 8)
        return record.hz * seconds


def main() -> None:
    catalog = load_frequency_catalog()
    print("SOURCE-TRACKED HISTORICAL FREQUENCY CATALOG")
    print(f"catalog={catalog.metadata['catalog_id']}; records={len(catalog.records)}")
    for role in sorted(FREQUENCY_ROLES):
        records = catalog.records_for_role(role)
        print(f"role={role}; records={len(records)}; unique_hz={len(catalog.frequency_index(role))}")
    print(f"reported_ranges={len(catalog.ranges)}; unresolved_settings={len(catalog.unresolved_settings)}")
    print("uncertainty=unknown_unless_explicitly_reported; source_precision_is_not_measurement_accuracy")
    print("scope=optional_experimental_inputs; no_biological_resonance_or_therapeutic_validation")
    print("physical_response_requires=clock_scale,material_tensors,geometry,damping,boundaries,measured_validation")


if __name__ == "__main__":
    main()
