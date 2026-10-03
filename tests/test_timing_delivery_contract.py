import numpy as np
import pytest

from src.time_crystal_clock_subsystem import clock_receiver
from src.timing_delivery_contract import endpoint_availability, endpoint_resources, timing_delivery


def test_one_lane_acquisition_matches_hand_schedule():
    # Two fresh shots each: endpoint0 completes2; endpoint1 completes6; endpoint2 completes12.
    assert endpoint_availability(
        cycles=2, shots=2, lanes=1, preparation_periods=0.5, readout_periods=0.5
    ) == [2, 6, 12]
    assert endpoint_availability(
        cycles=2, shots=2, lanes=2, preparation_periods=0.5, readout_periods=0.5
    ) == [1, 3, 6]


def test_resource_counts_match_existing_documented_totals():
    result = endpoint_resources(cycles=256, shots=256, qubits=6)
    assert result["state_preparations"] == 65792
    assert result["floquet_periods"] == 8421376
    assert result["single_spin_rotations"] == 12 * 8421376
    assert result["interaction_rotations"] == 5 * 8421376
    assert result["energy_joules"] is None


def test_free_playback_and_identical_availability_are_identical():
    signal = (-1.0) ** np.arange(9)
    result = timing_delivery(signal)
    assert result["on_time_receiver"] == clock_receiver(signal)
    assert result == timing_delivery(signal, ready_times=list(range(9)))


def test_fifo_closed_form_and_deadline_inclusive():
    result = timing_delivery([1, -1, 1], receiver_service_periods=2, deadline_periods=4)
    assert [s["completion_periods"] for s in result["samples"]] == [2, 4, 6]
    assert result["on_time_receiver"]["detected_ticks"] == 1
    late = timing_delivery([1, -1, 1], receiver_service_periods=2, deadline_periods=3.999)
    assert late["on_time_receiver"]["detected_ticks"] == 0
    assert late["late_source_samples"] == 1


def test_completion_before_arrival_and_competing_priority():
    # The source at0 loses to the competing job; source1 arrives exactly when it finishes.
    result = timing_delivery([1, -1, 1], competing_jobs=[(0, 1)], queue_capacity=1)
    assert [s["accepted"] for s in result["samples"]] == [False, True, True]
    assert result["on_time_receiver"]["detected_ticks"] == 1


def test_dropped_sample_breaks_original_adjacency_without_parity_fill():
    signal = (-1.0) ** np.arange(7)
    result = timing_delivery(signal, competing_jobs=[(2, 0.5)], queue_capacity=1)
    assert result["on_time_receiver"]["edge_cycles"] == [4, 6]
    assert result["on_time_receiver"]["missing_tick_cycles"] == [2]
    assert result["intrinsic_receiver"] == clock_receiver(signal)
    assert result["dropped_source_samples"] == 1


def test_late_jobs_still_consume_receiver_service():
    result = timing_delivery([1, -1, 1], receiver_service_periods=2, deadline_periods=0)
    assert result["late_source_samples"] == 3
    assert result["dropped_source_samples"] == 0
    assert result["samples"][-1]["completion_periods"] == 6
    assert result["on_time_receiver"]["detected_ticks"] == 0


@pytest.mark.parametrize(
    "options",
    [
        {"receiver_service_periods": True},
        {"deadline_periods": complex(1)},
        {"queue_capacity": 0},
        {"ready_times": [0, 2, 1]},
        {"ready_times": [0, 0, 2]},
        {"ready_times": [0, float("nan"), 2]},
        {"competing_jobs": [(0, -1)]},
        {"ready_times": 1},
        {"competing_jobs": 1},
        {"competing_jobs": [None]},
        {"competing_jobs": [1]},
        {"receiver_service_periods": [1]},
    ],
)
def test_invalid_delivery(options):
    with pytest.raises(ValueError):
        timing_delivery([1, -1, 1], **options)


@pytest.mark.parametrize(
    "options",
    [
        {"shots": True},
        {"lanes": 0},
        {"preparation_periods": -1},
        {"readout_periods": np.complex128(1)},
        {"cycles": 1},
    ],
)
def test_invalid_acquisition(options):
    params = dict(cycles=2, shots=1, lanes=1)
    params.update(options)
    with pytest.raises(ValueError):
        endpoint_availability(**params)


def test_immediate_completions_are_not_unfinished_and_boolean_samples_rejected():
    assert timing_delivery([1, -1, 1])["peak_unfinished_receiver_jobs"] == 0
    with pytest.raises(ValueError):
        timing_delivery([True, False, True])


def test_zero_service_jobs_wait_behind_prior_work():
    result = timing_delivery([1, -1, 1], competing_jobs=[(0, 2)], deadline_periods=2)
    assert [s["completion_periods"] for s in result["samples"]] == [2, 2, 2]
    assert result["peak_unfinished_receiver_jobs"] == 3
    assert result["on_time_receiver"]["detected_ticks"] == 1
