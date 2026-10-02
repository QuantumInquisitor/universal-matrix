"""Schedule saved timing signals; never rerun the historical Floquet study."""

# ruff: noqa: E402
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.timing_delivery_contract import endpoint_availability, endpoint_resources, timing_delivery


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    fixture = ROOT / "tests/fixtures/timing_delivery_signals.json"
    fixture_text = fixture.read_text(encoding="utf-8")
    assert (
        hashlib.sha256(fixture_text.encode("utf-8")).hexdigest()
        == "0753b9b41e1d959a060fc29ad6762c26fb13f5de98dfca1013a939aa231db255"
    )
    inputs = json.loads(fixture_text)
    assert sorted(c["case_id"] for c in inputs["cases"]) == sorted(
        f"base-N{n}-g0.97-seed{seed}-interactions-true" for n in (6, 8) for seed in range(8)
    )
    configs = {
        "ideal_replay": dict(
            acquisition="hypothetical_instantaneous",
            service=0.0,
            deadline=0.0,
            capacity=None,
            load=[],
        ),
        "cold_start_unloaded": dict(
            acquisition="cold_start", service=0.1, deadline=1.0, capacity=None, load=[]
        ),
        "cold_start_contention": dict(
            acquisition="cold_start",
            service=0.1,
            deadline=1.0,
            capacity=None,
            load=[(n, 0.9) for n in range(257)],
        ),
        "cold_start_finite_queue": dict(
            acquisition="cold_start",
            service=0.1,
            deadline=0.25,
            capacity=1,
            load=[(n, 1.5) for n in range(0, 257, 4)],
        ),
    }
    cases = []
    for case in inputs["cases"]:
        parameters = case["parameters"]
        cycles = parameters["cycles"]
        signal = case["finite_shot_signal"]
        ready = endpoint_availability(
            cycles=cycles,
            shots=parameters["shots"],
            lanes=256,
            preparation_periods=0.25,
            readout_periods=0.25,
        )
        divider = [(-1.0) ** n for n in range(cycles + 1)]
        for label, config in configs.items():
            options = dict(
                receiver_service_periods=config["service"],
                deadline_periods=config["deadline"],
                queue_capacity=config["capacity"],
                competing_jobs=config["load"],
            )
            outputs = {
                "candidate": timing_delivery(
                    signal, ready_times=None if label == "ideal_replay" else ready, **options
                ),
                "divider": timing_delivery(divider, **options),
            }
            metrics = {}
            for name, result in outputs.items():
                metrics[name] = {
                    key: result[key]
                    for key in (
                        "dropped_source_samples",
                        "late_source_samples",
                        "peak_unfinished_receiver_jobs",
                        "energy_joules",
                    )
                }
                metrics[name].update(
                    intrinsic_ticks=result["intrinsic_receiver"]["detected_ticks"],
                    on_time_ticks=result["on_time_receiver"]["detected_ticks"],
                    perfect_on_time_delivery=result["on_time_receiver"]["perfect_tick_delivery"],
                    maximum_delivered_tick_latency_periods=max(
                        (t["latency_periods"] for t in result["delivered_ticks"]), default=None
                    ),
                )
            if label == "ideal_replay":
                assert (
                    outputs["candidate"]["on_time_receiver"]
                    == outputs["candidate"]["intrinsic_receiver"]
                )
                assert outputs["divider"]["on_time_receiver"]["perfect_tick_delivery"]
            cases.append(dict(case_id=case["case_id"], configuration=label, metrics=metrics))
    paths = [
        Path(__file__),
        ROOT / "src/timing_delivery_contract.py",
        ROOT / "src/time_crystal_clock_subsystem.py",
        fixture,
    ]
    report = dict(
        parent_artifact_raw_sha256=inputs["parent_artifact_raw_sha256"],
        parent_source_sha256=inputs["parent_source_sha256"],
        input_case_ids=[c["case_id"] for c in inputs["cases"]],
        normalized_utf8_lf_sha256={
            p.relative_to(ROOT).as_posix(): hashlib.sha256(
                p.read_text(encoding="utf-8").encode("utf-8")
            ).hexdigest()
            for p in paths
        },
        configurations=configs,
        acquisition=dict(
            lanes=256,
            preparation_periods=0.25,
            readout_periods=0.25,
            contract="Fresh endpoint shots requested at their endpoint index; no speculative preparation.",
        ),
        cold_start_acquisition_resources_by_qubits={
            str(n): endpoint_resources(cycles=256, shots=256, qubits=n) for n in (6, 8)
        },
        cases=cases,
        energy_joules=None,
        comparison_contract="Only downstream service, competing load and deadline are matched. Divider availability at cycle n is an ideal assumption; cold-start endpoint acquisition is source-specific, not matched hardware cost.",
        ideal_replay_resources="Counterfactual prerecorded playback: no endpoint acquisition jobs are scheduled in ideal_replay. Cold-start resource counts do not apply to this positive control.",
        scope="Conditional cold-start backend plus common downstream FIFO. Existing source traces; no physical continuous-readout, hardware advantage, new reliability estimate or energy claim.",
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for label in configs:
        rows = [c for c in cases if c["configuration"] == label]
        print(
            label,
            {
                name: sorted({r["metrics"][name]["on_time_ticks"] for r in rows})
                for name in ("candidate", "divider")
            },
        )


if __name__ == "__main__":
    main()
