"""Independent modal continuation, switched forcing and checkpoint controls."""

import json
import math

import pytest

from scripts.report_material_restart import (
    Specimen,
    advance,
    balance,
    dumps,
    loads,
    owned_energy,
    report,
    start,
)


def test_restart_preserves_full_state_and_work_at_drive_boundary():
    for case in report()["cases"]:
        assert case["exact_replay"]
        assert case["off_interval_work_j"] == 0
        assert sum(case["final"]["owned_energy_j"]) < sum(case["cutoff"]["owned_energy_j"])
        assert case["final"]["loss_j"] > case["cutoff"]["loss_j"]


def test_input_off_matches_independent_damped_modes():
    model = Specimen()
    cutoff = advance(start(model, 0.01, 400), model, 400)
    final = advance(cutoff, model, 1200)
    x0, x1, v0, v1 = cutoff["state"][:4]
    modes = []
    for sign, stiffness, damping in ((1, 4, 0.1), (-1, 8, 0.5)):
        q, v = (x0 + sign * x1) / math.sqrt(2), (v0 + sign * v1) / math.sqrt(2)
        gamma = damping / 2
        w = math.sqrt(stiffness - gamma**2)
        a, b = q, (v + gamma * q) / w
        c, s = math.cos(w * 8), math.sin(w * 8)
        modes.append(
            (
                math.exp(-gamma * 8) * (a * c + b * s),
                math.exp(-gamma * 8) * (-gamma * (a * c + b * s) + w * (-a * s + b * c)),
            )
        )
    expected = [
        (modes[0][0] + modes[1][0]) / math.sqrt(2),
        (modes[0][0] - modes[1][0]) / math.sqrt(2),
        (modes[0][1] + modes[1][1]) / math.sqrt(2),
        (modes[0][1] - modes[1][1]) / math.sqrt(2),
    ]
    assert final["state"][:4] == pytest.approx(expected, abs=5e-9)


def test_each_energy_owner_balances_and_refines_without_double_storage():
    cases = report()["cases"]
    for owner in range(3):
        coarse = abs(cases[0]["final"]["ownership_residuals_j"][owner])
        fine = abs(cases[-1]["final"]["ownership_residuals_j"][owner])
        assert fine < coarse / 100
        assert fine < 1e-9
    model = Specimen()
    state = [0.2, -0.3, 0.4, -0.5]
    assert sum(owned_energy(model, state)) == pytest.approx(sum(model.energies(state)))
    record = advance(start(model), model, 1200)
    ledger = balance(model, record)
    assert sum(ledger["ownership_residuals_j"]) == pytest.approx(
        ledger["total_balance_residual_j"], abs=1e-16
    )


def test_zero_and_disconnected_controls():
    model = Specimen(drive_amplitude_n=0)
    record = advance(start(model, initial=(0, 0, 0, 0)), model, 100)
    assert record["state"] == [0] * 11
    model = Specimen(link_stiffness_n_per_m=0, link_damping_n_s_per_m=0)
    record = advance(start(model), model, 100)
    assert record["state"][1] == record["state"][3] == 0
    assert record["state"][8:] == [0] * 3


@pytest.mark.parametrize("field", ["state", "step", "time_s", "contract"])
def test_checksum_detects_payload_change(field):
    model = Specimen()
    env = json.loads(dumps(start(model)))
    env["payload"][field] = None
    with pytest.raises(ValueError, match="checksum"):
        loads(json.dumps(env), model, 0.01, 400)


@pytest.mark.parametrize("change", ["model", "dt", "cutoff", "source"])
def test_restart_rejects_changed_contract(change):
    model = Specimen()
    record = start(model)
    dt, cutoff = 0.01, 400
    if change == "model":
        model = Specimen(mass_kg=2)
    elif change == "dt":
        dt = 0.02
    elif change == "cutoff":
        cutoff = 401
    else:
        record["contract"]["sources"]["report_material_specimen.py"] = "changed"
    with pytest.raises(ValueError, match="mismatch"):
        loads(dumps(record), model, dt, cutoff)


@pytest.mark.parametrize("step", [-1, True, 1.5, 1_000_001])
def test_invalid_absolute_steps(step):
    with pytest.raises(ValueError):
        advance(start(Specimen()), Specimen(), step)


def test_rehashed_time_inconsistency_and_loss_inconsistency_rejected():
    model = Specimen()
    record = advance(start(model), model, 100)
    record["time_s"] += 0.01
    with pytest.raises(ValueError, match="time"):
        loads(dumps(record), model, 0.01, 400)
    record["time_s"] = 1
    record["state"][5] += 1
    with pytest.raises(ValueError, match="loss"):
        loads(dumps(record), model, 0.01, 400)


def test_boolean_schema_and_unknown_fields_rejected_even_when_rehashed():
    model = Specimen()
    record = start(model)
    record["contract"]["schema"] = True
    with pytest.raises(ValueError, match="mismatch"):
        loads(dumps(record), model, 0.01, 400)
    record = start(model)
    record["extra"] = 1
    with pytest.raises(ValueError, match="fields"):
        loads(dumps(record), model, 0.01, 400)
