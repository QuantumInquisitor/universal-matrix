"""Independent modal solution and connected energy controls."""

import math

import pytest

from scripts.report_material_specimen import Specimen, report, run


def test_conservative_matches_two_independent_normal_modes():
    model = Specimen(drive_amplitude_n=0, anchor_damping_n_s_per_m=0, link_damping_n_s_per_m=0)
    result = run(model, dt=0.01, duration=2)
    # x0(0)=0.1 splits equally into symmetric and antisymmetric modes.
    ws, wa = 2.0, math.sqrt(8)
    expected = [
        0.05 * (math.cos(ws * 2) + math.cos(wa * 2)),
        0.05 * (math.cos(ws * 2) - math.cos(wa * 2)),
        -0.05 * (ws * math.sin(ws * 2) + wa * math.sin(wa * 2)),
        -0.05 * (ws * math.sin(ws * 2) - wa * math.sin(wa * 2)),
    ]
    assert result["final_state"] == pytest.approx(expected, abs=1e-8)
    assert result["external_work_j"] == result["dissipated_j"] == 0
    assert abs(result["balance_residual_j"]) < 1e-9


def test_connection_transfers_motion_and_disconnection_prevents_it():
    connected = run(Specimen(drive_amplitude_n=0))
    disconnected = run(
        Specimen(drive_amplitude_n=0, link_stiffness_n_per_m=0, link_damping_n_s_per_m=0)
    )
    assert abs(connected["final_state"][1]) > 1e-4
    assert disconnected["final_state"][1] == disconnected["final_state"][3] == 0


def test_driven_and_relaxing_ledgers_refine():
    data = report()
    assert data["refinement"]["displacement_m"]["difference_ratio"] > 12
    assert data["refinement"]["velocity_m_per_s"]["difference_ratio"] > 12
    for cases in data["cases"].values():
        assert cases[-1]["max_abs_balance_residual_j"] < cases[0]["max_abs_balance_residual_j"] / 12
    fine = data["cases"]["driven_damped"][-1]
    assert fine["external_work_j"] > 0
    assert fine["dissipated_j"] > 0
    assert abs(fine["balance_residual_j"]) < 1e-8
    off = data["cases"]["drive_off"][-1]
    assert off["external_work_j"] == 0
    assert off["final_energy_j"] < off["initial_energy_j"]


def test_zero_state_stays_zero_without_drive():
    result = run(Specimen(drive_amplitude_n=0), initial=(0, 0, 0, 0))
    assert result["final_state"] == [0, 0, 0, 0]
    assert result["final_energy_j"] == result["dissipated_j"] == 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"mass_kg": 0},
        {"mass_kg": True},
        {"link_damping_n_s_per_m": -1},
        {"drive_omega_rad_per_s": float("nan")},
    ],
)
def test_invalid_parameters(kwargs):
    with pytest.raises(ValueError):
        Specimen(**kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [{"dt": 0}, {"duration": float("inf")}, {"dt": 0.3}, {"initial": (0, 0, 0, float("nan"))}],
)
def test_invalid_integration(kwargs):
    with pytest.raises(ValueError):
        run(Specimen(), **kwargs)
