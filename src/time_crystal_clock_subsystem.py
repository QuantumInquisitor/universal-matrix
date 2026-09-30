"""Finite Floquet-Ising timing candidate and optional canonical clock receiver.

Mi et al., Nature, doi:10.1038/s41586-021-04257-w, Eq.1 supplies the model.
This small exact simulation is not hardware or a many-body phase replication.
Receiver playback of ensemble expectations excludes physical readout backaction.
"""

import math

import numpy as np

from .canonical_polarity_clock import clock_node, polarity_phase_from_tick


def _integer(value, name, minimum, maximum):
    if (
        isinstance(value, (bool, np.bool_))
        or not isinstance(value, (int, np.integer))
        or not minimum <= value <= maximum
    ):
        raise ValueError(f"{name} must be integer in [{minimum},{maximum}]")
    return int(value)


def floquet_trace(
    *,
    qubits=6,
    cycles=256,
    g=0.97,
    seed=0,
    interactions=True,
    initial_bits=None,
    shots=256,
    readout_flip_probability=0.0,
    pulse_jitter=0.0,
):
    """U = exp(-i sum h Z/2) exp(-i sum phi ZZ/4) exp(-i pi g sum X/2).

    h~Uniform[-pi,pi], phi~Uniform[-1.5pi,-.5pi], open chain. Gate angles are
    dimensionless. Each finite-shot readout represents separately prepared
    end-of-circuit ensembles; it does not collapse the evolving state below.
    """
    qubits = _integer(qubits, "qubits", 2, 12)
    cycles = _integer(cycles, "cycles", 2, 4096)
    seed = _integer(seed, "seed", 0, 2**32 - 1)
    shots = _integer(shots, "shots", 1, 100000)
    for name, value in (
        ("g", g),
        ("readout_flip_probability", readout_flip_probability),
        ("pulse_jitter", pulse_jitter),
    ):
        if isinstance(value, (bool, complex)) or not np.isfinite(value):
            raise ValueError(f"{name} must be finite and real")
    if not 0 <= g <= 1 or not 0 <= readout_flip_probability <= 0.5 or not 0 <= pulse_jitter <= 0.1:
        raise ValueError("g in [0,1], readout flip in [0,.5], jitter in [0,.1] required")
    if not isinstance(interactions, bool):
        raise ValueError("interactions must be boolean")
    rng = np.random.default_rng(seed)
    fields = rng.uniform(-math.pi, math.pi, qubits)
    couplings = rng.uniform(-1.5 * math.pi, -0.5 * math.pi, qubits - 1)
    if initial_bits is None:
        initial_bits = rng.integers(0, 2, qubits)
    bits = np.asarray(initial_bits)
    if bits.shape != (qubits,) or not np.all((bits == 0) | (bits == 1)):
        raise ValueError("one binary initial value per qubit required")
    initial_sign = 1 - 2 * bits.astype(int)
    indices = np.arange(2**qubits)
    z = 1 - 2 * ((indices[:, None] >> np.arange(qubits)) & 1)
    effective_couplings = couplings if interactions else np.zeros_like(couplings)
    phases = np.exp(
        -1j * (0.5 * (z @ fields) + 0.25 * ((z[:, :-1] * z[:, 1:]) @ effective_couplings))
    )
    state = np.zeros(2**qubits, dtype=complex)
    state[int(np.sum(bits.astype(int) * (1 << np.arange(qubits))))] = 1
    pulse_rng = np.random.default_rng(seed + 100000)
    readout_rng = np.random.default_rng(seed + 200000)
    polarizations, readouts, norm_errors = [], [], []
    for cycle in range(cycles + 1):
        probability = np.abs(state) ** 2
        norm_errors.append(abs(float(probability.sum()) - 1))
        probability = probability / probability.sum()
        polarizations.append(probability @ z)
        samples = z[readout_rng.choice(len(state), shots, p=probability)].copy()
        flips = readout_rng.random(samples.shape) < readout_flip_probability
        samples[flips] *= -1
        readouts.append(float(np.mean(samples * initial_sign)))
        if cycle == cycles:
            break
        angle = math.pi * (g + pulse_jitter * pulse_rng.normal()) / 2
        for qubit in range(qubits):
            state = math.cos(angle) * state - 1j * math.sin(angle) * state[indices ^ (1 << qubit)]
        state *= phases
    local = np.array(polarizations)
    correlation = np.mean(local * initial_sign, axis=1)
    return dict(
        parameters=dict(
            qubits=qubits,
            cycles=cycles,
            g=g,
            seed=seed,
            interactions=interactions,
            shots=shots,
            pulse_jitter=pulse_jitter,
            readout_flip_probability=readout_flip_probability,
        ),
        fields=fields.tolist(),
        coupling_angles=effective_couplings.tolist(),
        initial_bits=bits.tolist(),
        initial_sign_corrected_signal=correlation.tolist(),
        finite_shot_signal=readouts,
        local_polarizations=local.tolist(),
        maximum_norm_error=max(norm_errors),
        late_alternating_correlation=float(
            np.mean(correlation[-128:] * (-1.0) ** np.arange(cycles + 1)[-128:])
        ),
        readout_scope="independent endpoint ensembles; no continuous sensor or backaction model",
    )


def clock_receiver(signal, *, threshold=0.2, base_node=0):
    """One tick for each observed negative-to-positive transition.

    Uses adjacent samples only. Missing-confidence samples break the edge;
    the receiver never fills missing ticks from expected parity. Mapping one
    complete source oscillation to one engine tick is an explicit adapter choice.
    """
    if np.iscomplexobj(signal):
        raise ValueError("real signal required")
    values = np.asarray(signal, dtype=float)
    if values.ndim != 1 or len(values) < 3 or not np.isfinite(values).all():
        raise ValueError("at least three finite scalar samples required")
    if isinstance(threshold, bool) or not np.isfinite(threshold) or not 0 < threshold < 1:
        raise ValueError("threshold must lie in (0,1)")
    base_node = _integer(base_node, "base_node", 0, 107)
    signs = np.where(values > threshold, 1, np.where(values < -threshold, -1, 0))
    edges = np.flatnonzero((signs[:-1] == -1) & (signs[1:] == 1)) + 1
    expected = np.arange(2, len(values), 2)
    missing = np.setdiff1d(expected, edges)
    extra = np.setdiff1d(edges, expected)
    cumulative = np.cumsum(np.isin(np.arange(len(values)), edges))
    reference = np.arange(len(values)) // 2
    return dict(
        edge_cycles=edges.tolist(),
        detected_ticks=len(edges),
        expected_ticks=len(expected),
        missing_tick_cycles=missing.tolist(),
        extra_tick_cycles=extra.tolist(),
        maximum_tick_count_error=int(np.max(np.abs(cumulative - reference))),
        unresolved_sample_fraction=float(np.mean(signs == 0)),
        final_tick=int(cumulative[-1]),
        final_core_node=clock_node(base_node, int(cumulative[-1])),
        final_clock_phase=polarity_phase_from_tick(int(cumulative[-1])),
        perfect_tick_delivery=bool(len(missing) == 0 and len(extra) == 0),
        phase_resolution="drive-period sampling only; no within-period jitter claim",
    )
