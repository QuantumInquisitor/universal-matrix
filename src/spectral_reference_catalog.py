"""Separate anecdotal frequency lists from evaluated atomic wavelengths.

No catalog establishes treatment efficacy or a resonance of the Matrix model.
Unknown wavelength medium cannot be converted; air conversion needs an explicit
phase refractive index at that wavelength and the intended environmental state.
"""

from __future__ import annotations

import json
import re
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path

REFERENCE_DIR = Path(__file__).parent / "reference_data"
LIGHT_SPEED_M_PER_S = Decimal("299792458")


def _positive(value, label: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be finite and positive")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"{label} must be numeric") from error
    if not result.is_finite() or result <= 0:
        raise ValueError(f"{label} must be finite and positive")
    return result


def wavelength_frequency_hz(wavelength_A, *, medium: str,
                            phase_refractive_index=None) -> Decimal:
    """Return c/(n*lambda); never silently treat an air wavelength as vacuum.

An air caller supplies its own wavelength-specific phase index, including its
temperature, pressure and composition assumptions. This function is only the
unit conversion, not an air-dispersion or uncertainty model.
    """
    wavelength = _positive(wavelength_A, "wavelength")
    if medium == "vacuum":
        if phase_refractive_index is not None:
            raise ValueError("a vacuum wavelength must not supply an air index")
        index = Decimal(1)
    elif medium == "air":
        if phase_refractive_index is None:
            raise ValueError("air wavelength requires an explicit phase refractive index")
        index = _positive(phase_refractive_index, "phase refractive index")
        if index <= 1:
            raise ValueError("this air conversion requires a phase index greater than one")
    else:
        raise ValueError("wavelength medium must be explicitly air or vacuum")
    with localcontext() as context:
        context.prec = max(28, len(wavelength.as_tuple().digits) + len(index.as_tuple().digits) + 8)
        return LIGHT_SPEED_M_PER_S / (index * wavelength * Decimal("1e-10"))


def parse_cafl_entries(numbered_lines: list[tuple[int, str]]) -> list[dict]:
    """Extract only explicit numeric fields from the supplied CAFL entry block.

Callers must delimit the entry block, excluding the header and footer. Balanced
parenthetical annotations can span lines; all their contents are omitted before
locating a separator or interpreting numbers. Unsupported syntax fails closed.
This parser does not interpret references, advice, durations or disease claims.
    """
    records = []
    depth = 0
    start = None
    outside = []
    annotated = False
    previous_line = -1
    for line_number, text in numbered_lines:
        if type(line_number) is not int or line_number <= previous_line or not isinstance(text, str):
            raise ValueError("source lines must be strings with increasing integer positions")
        previous_line = line_number
        if not text.strip():
            continue
        if start is None:
            start = line_number
        elif depth:
            outside.append(" ")
        for char in text:
            if char == "(":
                if depth == 0:
                    # Never join numeric fragments across a removed annotation.
                    outside.append(" ")
                depth += 1
                annotated = True
            elif char == ")":
                depth -= 1
                if depth < 0:
                    raise ValueError("unbalanced source annotation")
            elif depth == 0:
                outside.append(char)
        if depth:
            continue
        cleaned = "".join(outside).strip()
        parts = re.split(r"\s+-+\s*", cleaned, maxsplit=1)
        label = parts[0].strip()
        if len(parts) == 1 and re.search(r"-\s+\d", label):
            raise ValueError("unsupported source separator")
        if not re.fullmatch(r"[A-Za-z0-9_ .,'/+-]+", label) or not label:
            raise ValueError("unsupported source label")
        field = parts[1].strip() if len(parts) == 2 else ""
        values = [value.strip() for value in field.split(",")] if field else []
        for value in values:
            if not re.fullmatch(r"(?:\d+(?:\.\d*)?|\.\d+)", value):
                raise ValueError("unsupported explicit frequency field")
            _positive(value, "CAFL frequency")
        records.append({
            "id": f"cafl-{start}", "label": label,
            "source_lines": [start, line_number], "values_hz": values,
            "annotations_omitted": annotated,
            "status": "explicit_values" if values else "no_explicit_values",
        })
        start = None
        outside = []
        annotated = False
    if depth or start is not None:
        raise ValueError("unfinished source annotation")
    return records


def _load(path: str | Path, scope: str, evidence: str) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if (type(data.get("schema_version")) is not int or data["schema_version"] != 1
            or data.get("scope") != scope or data.get("evidence_class") != evidence):
        raise ValueError("unsupported catalog scope or evidence class")
    if not isinstance(data.get("source_url"), str) or not data["source_url"].startswith("https://"):
        raise ValueError("catalog requires a source URL")
    return data


def load_cafl_catalog(path: str | Path = REFERENCE_DIR / "cafl_explicit_catalog.json") -> dict:
    data = _load(path, "unverified_frequency_compilation", "anecdotal_compilation")
    if (data.get("unit") != "Hz" or data.get("frequency_role") != "unspecified_by_compilation"
            or data.get("measurement_uncertainty_hz") is not None):
        raise ValueError("CAFL units, role and unknown uncertainty must remain explicit")
    records = data["records"]
    ids = set()
    for record in records:
        if not isinstance(record.get("id"), str) or record["id"] in ids:
            raise ValueError("CAFL record ids must be unique strings")
        ids.add(record["id"])
        if not isinstance(record.get("label"), str) or not record["label"].strip():
            raise ValueError("CAFL source label is required")
        if not isinstance(record.get("values_hz"), list):
            raise ValueError("CAFL values must be a list")
        for value in record["values_hz"]:
            if not isinstance(value, str):
                raise ValueError("source precision requires decimal strings")
            _positive(value, "CAFL frequency")
        expected_status = "explicit_values" if record["values_hz"] else "no_explicit_values"
        if record.get("status") != expected_status:
            raise ValueError("CAFL extraction status disagrees with its values")
    expected = {"entries": len(records),
                "entries_with_values": sum(bool(r["values_hz"]) for r in records),
                "entries_without_explicit_values": sum(not r["values_hz"] for r in records),
                "frequency_occurrences": sum(len(r["values_hz"]) for r in records)}
    if any(data["coverage"].get(key) != value for key, value in expected.items()):
        raise ValueError("CAFL coverage does not match records")
    return data


def load_hydrogen_catalog(path: str | Path = REFERENCE_DIR / "nist_hydrogen_lines.json") -> dict:
    data = _load(path, "evaluated_atomic_spectrum", "evaluated_reference_data")
    ids = set()
    for row in data["rows"]:
        if not isinstance(row.get("id"), str) or row["id"] in ids:
            raise ValueError("spectral row ids must be unique strings")
        ids.add(row["id"])
        if row.get("isotope") != "1H" or row.get("spectrum") != "H I":
            raise ValueError("this catalog is restricted to neutral hydrogen-1")
        if not isinstance(row.get("wavelength_A"), str):
            raise ValueError("source precision requires a decimal wavelength string")
        _positive(row["wavelength_A"], "wavelength")
        if row.get("medium") not in ("vacuum", "air"):
            raise ValueError("spectral medium must be explicit")
        if row.get("wavelength_type") not in ("Ritz_resolved_fine_structure", "unresolved_multiplet_weighted_average_energies"):
            raise ValueError("wavelength derivation must be explicit")
        if row.get("wavelength_uncertainty_A") is not None:
            raise ValueError("this source does not supply per-row uncertainties")
        if row.get("line_reference") not in data["references"]:
            raise ValueError("spectral row needs its source reference")
        _positive(row["relative_intensity"], "relative intensity")
        if not isinstance(row.get("flags"), list) or any(flag not in ("P", "c") for flag in row["flags"]):
            raise ValueError("unsupported source flag")
    expected = {"rows": len(data["rows"]),
                "vacuum": sum(r["medium"] == "vacuum" for r in data["rows"]),
                "air": sum(r["medium"] == "air" for r in data["rows"]),
                "persistent": sum("P" in r["flags"] for r in data["rows"])}
    if data["coverage"] != expected:
        raise ValueError("spectral coverage does not match rows")
    return data


def main() -> None:
    cafl = load_cafl_catalog()
    hydrogen = load_hydrogen_catalog()
    print(json.dumps({"anecdotal_compilation": cafl["coverage"],
                      "evaluated_hydrogen_spectrum": hydrogen["coverage"],
                      "air_hz_conversion": "requires explicit refractive model",
                      "historical_instrument_catalog": "separate frequency_source_catalog module",
                      "russell_numeric_leads": "historical hypotheses; not calibration"}, indent=2))


if __name__ == "__main__":
    main()
