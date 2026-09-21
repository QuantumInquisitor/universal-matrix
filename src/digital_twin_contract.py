"""Typed digital-twin telemetry contract.

The contract separates directly measured values from derived estimates and
carries units, source, timestamp, and quality metadata. This avoids presenting
computed values as if they were physical sensor measurements.

The module is transport-neutral and can be serialized for APIs, WebSocket
streams, databases, or customer adapters.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
import json
import math
import time
from typing import Any, Mapping


class TelemetryKind(StrEnum):
    MEASURED = "measured"
    DERIVED = "derived"
    COMMAND_STATE = "command_state"
    SYSTEM_STATE = "system_state"


class QualityLevel(StrEnum):
    GOOD = "good"
    DEGRADED = "degraded"
    INVALID = "invalid"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class TelemetryValue:
    name: str
    value: float | int | str | bool
    unit: str
    kind: TelemetryKind
    source: str
    timestamp_ns: int
    quality: QualityLevel = QualityLevel.UNKNOWN
    calibration_id: str | None = None
    uncertainty: float | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name must be non-empty")
        if not self.source.strip():
            raise ValueError("source must be non-empty")
        if self.timestamp_ns < 0:
            raise ValueError("timestamp_ns must be non-negative")
        if isinstance(self.value, float) and not math.isfinite(self.value):
            raise ValueError("numeric telemetry values must be finite")
        if self.uncertainty is not None:
            if not math.isfinite(self.uncertainty) or self.uncertainty < 0:
                raise ValueError("uncertainty must be finite and non-negative")


@dataclass(frozen=True)
class DigitalTwinSnapshot:
    twin_id: str
    asset_id: str
    timestamp_ns: int
    values: tuple[TelemetryValue, ...]
    schema_version: str = "0.1"

    def __post_init__(self) -> None:
        if not self.twin_id.strip():
            raise ValueError("twin_id must be non-empty")
        if not self.asset_id.strip():
            raise ValueError("asset_id must be non-empty")
        if self.timestamp_ns < 0:
            raise ValueError("timestamp_ns must be non-negative")
        if self.schema_version != "0.1":
            raise ValueError("unsupported digital-twin schema version")

    @property
    def measured_values(self) -> tuple[TelemetryValue, ...]:
        return tuple(
            value
            for value in self.values
            if value.kind is TelemetryKind.MEASURED
        )

    @property
    def derived_values(self) -> tuple[TelemetryValue, ...]:
        return tuple(
            value
            for value in self.values
            if value.kind is TelemetryKind.DERIVED
        )

    def to_dict(self) -> dict[str, Any]:
        values = []
        for value in self.values:
            item = asdict(value)
            item["kind"] = value.kind.value
            item["quality"] = value.quality.value
            values.append(item)
        return {
            "twin_id": self.twin_id,
            "asset_id": self.asset_id,
            "timestamp_ns": self.timestamp_ns,
            "schema_version": self.schema_version,
            "values": values,
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
        )


def measured_value(
    *,
    name: str,
    value: float | int | str | bool,
    unit: str,
    source: str,
    quality: QualityLevel = QualityLevel.GOOD,
    calibration_id: str | None = None,
    uncertainty: float | None = None,
    timestamp_ns: int | None = None,
) -> TelemetryValue:
    return TelemetryValue(
        name=name,
        value=value,
        unit=unit,
        kind=TelemetryKind.MEASURED,
        source=source,
        timestamp_ns=time.time_ns() if timestamp_ns is None else timestamp_ns,
        quality=quality,
        calibration_id=calibration_id,
        uncertainty=uncertainty,
    )


def derived_value(
    *,
    name: str,
    value: float | int | str | bool,
    unit: str,
    source: str,
    quality: QualityLevel = QualityLevel.UNKNOWN,
    uncertainty: float | None = None,
    timestamp_ns: int | None = None,
) -> TelemetryValue:
    return TelemetryValue(
        name=name,
        value=value,
        unit=unit,
        kind=TelemetryKind.DERIVED,
        source=source,
        timestamp_ns=time.time_ns() if timestamp_ns is None else timestamp_ns,
        quality=quality,
        uncertainty=uncertainty,
    )


def snapshot_from_mapping(
    *,
    twin_id: str,
    asset_id: str,
    measured: Mapping[str, tuple[float | int | str | bool, str, str]],
    derived: Mapping[str, tuple[float | int | str | bool, str, str]] | None = None,
    timestamp_ns: int | None = None,
) -> DigitalTwinSnapshot:
    ts = time.time_ns() if timestamp_ns is None else timestamp_ns

    values: list[TelemetryValue] = []
    for name, (value, unit, source) in measured.items():
        values.append(
            measured_value(
                name=name,
                value=value,
                unit=unit,
                source=source,
                timestamp_ns=ts,
            )
        )

    for name, (value, unit, source) in (derived or {}).items():
        values.append(
            derived_value(
                name=name,
                value=value,
                unit=unit,
                source=source,
                timestamp_ns=ts,
            )
        )

    return DigitalTwinSnapshot(
        twin_id=twin_id,
        asset_id=asset_id,
        timestamp_ns=ts,
        values=tuple(values),
    )
