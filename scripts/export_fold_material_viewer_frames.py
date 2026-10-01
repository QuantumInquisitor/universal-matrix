"""Adapt computed material time-series states into an explicit science-viewer contract."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .report_fold_constitutive import geometry
    from .report_fold_kinematics import scalar
except ImportError:
    from report_fold_constitutive import geometry
    from report_fold_kinematics import scalar


def _vector_list(value, length, name):
    if not isinstance(value, list) or len(value) != length:
        raise ValueError(f"{name} must contain one entry per module")
    return value


def adapt(report, *, case="powered", display_m_per_unit=0.1):
    """Preserve metre geometry while adding normalized display coordinates."""
    display_m_per_unit = scalar(display_m_per_unit, "display_m_per_unit")
    if not 1e-9 <= display_m_per_unit <= 1e9:
        raise ValueError("display_m_per_unit outside supported range")
    if not isinstance(report, dict) or report.get("schema") != 1:
        raise ValueError("powered material report schema 1 required")
    cases = report.get("cases")
    if not isinstance(cases, dict) or case not in cases:
        raise ValueError("requested powered material case is unavailable")
    source = cases[case]
    settings = source.get("settings", {})
    sizes = settings.get("sizes")
    edges = settings.get("edges")
    if not isinstance(sizes, (list, tuple)) or not sizes:
        raise ValueError("source case must declare module sizes")
    module_count = len(sizes)
    if not isinstance(edges, (list, tuple)):
        raise ValueError("source case must declare network edges")
    samples = source.get("samples")
    if not isinstance(samples, list) or not samples:
        raise ValueError("source case must contain time-series samples")

    frames = []
    previous_time = None
    for frame_index, sample in enumerate(samples):
        time_s = scalar(sample.get("time_s"), "time_s")
        if previous_time is not None and time_s <= previous_time:
            raise ValueError("sample times must increase strictly")
        previous_time = time_s
        q = _vector_list(sample.get("q"), module_count, "q")
        rates = _vector_list(sample.get("rates"), module_count, "rates")
        reserve = _vector_list(sample.get("reserve_j"), module_count, "reserve_j")
        delivered = _vector_list(
            sample.get("delivered_work_j"), module_count, "delivered_work_j"
        )
        damping = _vector_list(
            sample.get("damping_loss_j"), module_count, "damping_loss_j"
        )
        conversion = _vector_list(
            sample.get("conversion_loss_j"), module_count, "conversion_loss_j"
        )
        leakage = _vector_list(
            sample.get("leakage_loss_j"), module_count, "leakage_loss_j"
        )
        supplied = _vector_list(sample.get("input_j"), module_count, "input_j")

        modules = []
        for module_index, size in enumerate(sizes):
            size = scalar(size, "module size")
            rows = geometry(q[module_index], length_m=0.1 * size)
            bodies = []
            for body in rows:
                vertices_m = np.asarray(body["vertices_m"], dtype=float)
                if vertices_m.ndim != 2 or vertices_m.shape[1] != 3:
                    raise ValueError("geometry body vertices must be Nx3")
                bodies.append(
                    dict(
                        id=f"module-{module_index}/{body['id']}",
                        source_body_id=body["id"],
                        vertices_m=vertices_m.tolist(),
                        vertices_display=(vertices_m / display_m_per_unit).tolist(),
                    )
                )
            modules.append(
                dict(
                    id=f"module-{module_index}",
                    size=float(size),
                    q=[scalar(v, "q") for v in q[module_index]],
                    rates=[scalar(v, "rates") for v in rates[module_index]],
                    reserve_j=scalar(reserve[module_index], "reserve_j"),
                    delivered_work_j=scalar(
                        delivered[module_index], "delivered_work_j"
                    ),
                    losses_j=dict(
                        damping=scalar(damping[module_index], "damping_loss_j"),
                        conversion=scalar(
                            conversion[module_index], "conversion_loss_j"
                        ),
                        leakage=scalar(leakage[module_index], "leakage_loss_j"),
                    ),
                    input_j=scalar(supplied[module_index], "input_j"),
                    bodies=bodies,
                )
            )
        frames.append(
            dict(
                index=frame_index,
                time_s=time_s,
                modules=modules,
                edge_potential_j=sample.get("edge_potential_j"),
                edge_work_j=sample.get("edge_work_j"),
            )
        )

    return dict(
        schema="matrix-science-viewer-timeseries-v1",
        case=case,
        frame_count=len(frames),
        module_count=module_count,
        network_edges=edges,
        units=dict(
            source_length="metre",
            time="second",
            energy="joule",
            angle="radian",
            display_length="normalized viewer unit",
            display_m_per_unit=display_m_per_unit,
        ),
        coordinate_policy=(
            "Each module remains in its own verified local material frame. "
            "No unvalidated global spatial placement is invented."
        ),
        compatibility=dict(
            current_repository_visualizers_are_direct_consumers=False,
            adapter_exposes_one_ordered_frame_sequence=True,
            metre_geometry_preserved=True,
            normalized_display_coordinates_added=True,
        ),
        frames=frames,
    )


def export(report_path, *, case="powered", display_m_per_unit=0.1):
    path = Path(report_path)
    raw = path.read_text(encoding="utf-8")
    result = adapt(
        json.loads(raw), case=case, display_m_per_unit=display_m_per_unit
    )
    result["source_report"] = dict(
        path=str(path),
        sha256_normalized_text=hashlib.sha256(raw.encode()).hexdigest(),
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--case", default="powered")
    parser.add_argument("--display-m-per-unit", type=float, default=0.1)
    args = parser.parse_args()
    result = export(
        args.input,
        case=args.case,
        display_m_per_unit=args.display_m_per_unit,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
