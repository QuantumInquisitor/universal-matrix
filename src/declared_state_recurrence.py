"""Return diagnostics for explicitly declared 3D component state.

History is reported separately: a completed turn need not change physical state
unless the model actually couples to winding. No hidden-state completeness is
inferred from this schema.
"""

import json
import math

import numpy as np

from .canonical_polarity_clock import ROUTING_TICKS_PER_CYCLE, polarity_phase_from_tick


def clock_phase_history(tick):
    if type(tick) is not int:
        raise ValueError("tick must be an integer")
    turns, _ = divmod(tick, ROUTING_TICKS_PER_CYCLE)
    return {"phase": polarity_phase_from_tick(tick), "winding": str(turns)}


def _finite(value):
    if isinstance(value, (bool, complex, str)):
        raise ValueError("finite real numeric state required")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("finite real numeric state required") from error
    if not math.isfinite(number):
        raise ValueError("finite real numeric state required")
    return number


def _array(value, shape):
    array = np.asarray(value)
    if (
        array.shape != shape
        or not np.issubdtype(array.dtype, np.number)
        or np.iscomplexobj(array)
        or not np.all(np.isfinite(array))
    ):
        raise ValueError("invalid finite state array")
    return array.astype(float)


def snapshot(components, *, model_id, units):
    if not isinstance(model_id, str) or not model_id or not components:
        raise ValueError("nonempty model identity and component inventory required")
    rows, names, internal_keys = [], set(), None
    fields = {"id", "position", "velocity", "orientation", "phase", "winding", "internal"}
    for item in components:
        if set(item) != fields:
            raise ValueError("component fields must match the declared schema")
        name = item["id"]
        if not isinstance(name, str) or not name or name in names:
            raise ValueError("component identities must be unique nonempty strings")
        names.add(name)
        orientation = _array(item["orientation"], (3, 3))
        if (
            not np.allclose(orientation.T @ orientation, np.eye(3), rtol=0, atol=1e-12)
            or abs(np.linalg.det(orientation) - 1) > 1e-12
        ):
            raise ValueError("orientation must be a proper 3D rotation")
        phase = _finite(item["phase"])
        if not 0 <= phase < math.tau:
            raise ValueError("phase must be canonical in [0,2pi)")
        winding = item["winding"]
        if type(winding) is int:
            winding = str(winding)
        if not isinstance(winding, str):
            raise ValueError("winding must be an exact integer or canonical integer string")
        try:
            if str(int(winding)) != winding:
                raise ValueError("noncanonical winding")
        except (ValueError, TypeError) as error:
            raise ValueError("invalid winding") from error
        internal = item["internal"]
        if not isinstance(internal, dict) or any(not isinstance(k, str) or not k for k in internal):
            raise ValueError("internal state requires named scalar variables")
        if internal_keys is None:
            internal_keys = set(internal)
        if set(internal) != internal_keys:
            raise ValueError("all components must share this declared internal schema")
        rows.append(
            {
                "id": name,
                "position": _array(item["position"], (3,)).tolist(),
                "velocity": _array(item["velocity"], (3,)).tolist(),
                "orientation": orientation.tolist(),
                "phase": phase,
                "winding": winding,
                "internal": {k: _finite(v) for k, v in sorted(internal.items())},
            }
        )
    expected_units = {"position", "velocity", "phase", "orientation"} | {
        f"internal.{k}" for k in internal_keys
    }
    if set(units) != expected_units or any(not isinstance(v, str) or not v for v in units.values()):
        raise ValueError("every numeric channel needs an explicit unit label")
    if units["phase"] != "radian" or units["orientation"] != "radian":
        raise ValueError("angular comparisons use radians")
    return {
        "schema": 1,
        "model_id": model_id,
        "units": dict(units),
        "components": sorted(rows, key=lambda r: r["id"]),
    }


def _validate(value):
    if (
        set(value) != {"schema", "model_id", "units", "components"}
        or type(value["schema"]) is not int
        or value["schema"] != 1
    ):
        raise ValueError("unsupported snapshot schema")
    return snapshot(value["components"], model_id=value["model_id"], units=value["units"])


def dumps(value):
    return json.dumps(_validate(value), sort_keys=True, allow_nan=False)


def loads(text):
    return _validate(json.loads(text))


def compare(left, right, *, tolerances, winding_is_state):
    left, right = _validate(left), _validate(right)
    if type(winding_is_state) is not bool:
        raise ValueError("winding policy must be explicit")
    if left["model_id"] != right["model_id"] or left["units"] != right["units"]:
        raise ValueError("comparison requires identical declared model and units")
    if [r["id"] for r in left["components"]] != [r["id"] for r in right["components"]]:
        raise ValueError("component inventory changed")
    if set(tolerances) != set(left["units"]):
        raise ValueError("each compared channel needs its own absolute tolerance")
    limits = {k: _finite(v) for k, v in tolerances.items()}
    if any(v < 0 for v in limits.values()):
        raise ValueError("tolerances must be nonnegative")
    maxima = {k: 0.0 for k in limits}
    changed, history = [], []
    for a, b in zip(left["components"], right["components"], strict=True):
        errors = {
            key: math.hypot(*(np.asarray(a[key]) - b[key])) for key in ("position", "velocity")
        }
        rotation = np.asarray(a["orientation"]).T @ b["orientation"]
        sine = math.hypot(*(rotation - rotation.T).flat) / (2 * math.sqrt(2))
        cosine = (np.trace(rotation) - 1) / 2
        errors["orientation"] = math.atan2(float(sine), float(cosine))
        errors["phase"] = abs(math.remainder(a["phase"] - b["phase"], math.tau))
        if set(a["internal"]) != set(b["internal"]):
            raise ValueError("internal schema changed")
        errors.update(
            {f"internal.{k}": abs(a["internal"][k] - b["internal"][k]) for k in a["internal"]}
        )
        if not all(math.isfinite(e) for e in errors.values()):
            raise ValueError("state difference exceeds finite numerical range")
        for key, error in errors.items():
            maxima[key] = max(maxima[key], error)
        failed = [k for k, error in errors.items() if error > limits[k]]
        turns = int(b["winding"]) - int(a["winding"])
        if turns:
            history.append({"id": a["id"], "winding_delta": str(turns)})
            if winding_is_state:
                failed.append("winding")
        if failed:
            changed.append({"id": a["id"], "failed_channels": failed})
    return {
        "component_count": len(left["components"]),
        "position_return": maxima["position"] <= limits["position"],
        "declared_state_return": not changed,
        "history_return": not history,
        "winding_is_state": winding_is_state,
        "maximum_errors": maxima,
        "tolerances": limits,
        "changed_components": changed,
        "history_changes": history,
        "scope": "Only declared variables and units; no claim that hidden physical state is complete",
    }
