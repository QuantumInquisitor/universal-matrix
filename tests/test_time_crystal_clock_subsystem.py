import math

import numpy as np
import pytest
from scipy.linalg import expm

from src.canonical_polarity_clock import clock_node
from src.time_crystal_clock_subsystem import clock_receiver, floquet_trace


@pytest.mark.parametrize("on", (False, True))
def test_perfect_pi_pulses_flip_every_state_and_keep_norm(on):
    result = floquet_trace(g=1, cycles=80, initial_bits=[1, 0, 1, 0, 0, 1], interactions=on)
    np.testing.assert_allclose(
        result["initial_sign_corrected_signal"], (-1.0) ** np.arange(81), atol=1e-13
    )
    assert result["maximum_norm_error"] < 1e-12
    receiver = clock_receiver(result["initial_sign_corrected_signal"])
    assert receiver["perfect_tick_delivery"]
    assert receiver["final_core_node"] == clock_node(0, 40)


def test_no_transverse_pulse_leaves_z_eigenstate_unchanged():
    result = floquet_trace(g=0, cycles=12)
    np.testing.assert_allclose(result["initial_sign_corrected_signal"], 1, atol=1e-14)
    assert clock_receiver(result["initial_sign_corrected_signal"])["detected_ticks"] == 0


def test_imperfect_pulse_candidate_drives_two_canonical_cycles():
    on = floquet_trace(qubits=6, cycles=144, g=0.97, seed=0)
    off = floquet_trace(qubits=6, cycles=144, g=0.97, seed=0, interactions=False)
    np.testing.assert_array_equal(on["fields"], off["fields"])
    np.testing.assert_array_equal(on["initial_bits"], off["initial_bits"])
    result = clock_receiver(on["finite_shot_signal"], base_node=17)
    assert result["perfect_tick_delivery"]
    assert result["detected_ticks"] == 72
    assert result["final_core_node"] == 17
    assert not clock_receiver(off["finite_shot_signal"])["perfect_tick_delivery"]


def test_factorized_evolution_matches_independent_dense_exponential():
    result = floquet_trace(qubits=3, cycles=12, g=0.93, seed=12, initial_bits=[1, 0, 1], shots=2)
    indices = np.arange(8)
    z = 1 - 2 * ((indices[:, None] >> np.arange(3)) & 1)
    generator = sum(np.eye(8)[indices ^ (1 << bit)] for bit in range(3))
    diagonal = 0.5 * z @ np.array(result["fields"]) + 0.25 * (z[:, :-1] * z[:, 1:]) @ np.array(
        result["coupling_angles"]
    )
    unitary = expm(-1j * np.diag(diagonal)) @ expm(-1j * math.pi * 0.93 / 2 * generator)
    state = np.eye(8, dtype=complex)[5]
    expected = []
    for _ in range(13):
        expected.append(np.abs(state) ** 2 @ z)
        state = unitary @ state
    np.testing.assert_allclose(result["local_polarizations"], expected, atol=1e-13)


def test_missing_or_weak_samples_do_not_get_ticks_filled_from_parity():
    signal = (-1.0) ** np.arange(73)
    assert clock_receiver(signal)["final_core_node"] == 0
    signal[10] = 0
    result = clock_receiver(signal)
    assert result["missing_tick_cycles"] == [10]
    assert result["detected_ticks"] == 35
    assert result["maximum_tick_count_error"] == 1
    assert result["final_core_node"] == clock_node(0, 35)


def test_wrong_phase_is_detected_even_if_total_tick_count_is_similar():
    result = clock_receiver(-((-1.0) ** np.arange(73)))
    assert result["extra_tick_cycles"]
    assert result["missing_tick_cycles"]
    assert not result["perfect_tick_delivery"]


def test_readout_and_pulse_errors_reproduce_with_same_seed():
    options = dict(qubits=3, cycles=12, readout_flip_probability=0.1, pulse_jitter=0.01)
    assert floquet_trace(**options) == floquet_trace(**options)


@pytest.mark.parametrize(
    "options",
    (
        {"qubits": 1},
        {"cycles": True},
        {"g": float("nan")},
        {"initial_bits": [0]},
        {"shots": 0},
        {"pulse_jitter": -0.01},
    ),
)
def test_invalid_trace_inputs(options):
    with pytest.raises(ValueError):
        floquet_trace(**options)
