"""Finite-record stroboscopic diagnostics, never a time-crystal classifier."""

import numpy as np


def stroboscopic_diagnostics(states, *, signal_floor=1e-8):
    """States must be sampled once per external drive period at fixed phase.

    Include conjugate coordinates when possible: displacement alone can vanish
    at a sampling node. Units/scales of columns must be declared by the caller.
    No drive inference, stationarity proof or many-body classification is made.
    """
    if np.iscomplexobj(states):
        raise ValueError("real states required")
    values = np.asarray(states, dtype=float)
    if values.ndim == 1:
        values = values[:, None]
    if (
        values.ndim != 2
        or len(values) < 16
        or values.shape[1] == 0
        or not np.isfinite(values).all()
    ):
        raise ValueError("at least 16 finite, nonempty state vectors required")
    if (
        isinstance(signal_floor, (bool, complex))
        or not np.isfinite(signal_floor)
        or signal_floor <= 0
    ):
        raise ValueError("positive finite signal floor required")
    # Equal even-length halves avoid parity and sample-count bias.
    values = values[-(len(values) // 4) * 4 :]
    centered = values - values.mean(axis=0)
    rms = float(np.sqrt(np.mean(np.sum(centered**2, axis=1))))
    half = len(values) // 2
    amplitudes = [
        float(np.sqrt(np.mean(np.sum((part - part.mean(axis=0)) ** 2, axis=1))))
        for part in (values[:half], values[half:])
    ]
    active = rms > signal_floor
    alternating = ((-1.0) ** np.arange(len(values)))[:, None]
    return dict(
        sample_count=len(values),
        centered_state_rms=rms,
        signal_resolved=active,
        one_cycle_error=float(np.sqrt(np.mean(np.sum(np.diff(values, axis=0) ** 2, axis=1))) / rms)
        if active
        else None,
        two_cycle_error=float(
            np.sqrt(np.mean(np.sum((values[2:] - values[:-2]) ** 2, axis=1))) / rms
        )
        if active
        else None,
        alternating_coherence=float(np.linalg.norm(np.mean(alternating * centered, axis=0)) / rms)
        if active
        else None,
        late_to_early_rms=amplitudes[1] / amplitudes[0] if amplitudes[0] > signal_floor else None,
        classification="finite-record diagnostic only; not evidence sufficient for a time crystal",
    )
