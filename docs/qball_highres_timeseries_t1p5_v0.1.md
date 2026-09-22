# Q-Ball High-Resolution In-Run Time Series to t=1.5 v0.1

## Purpose

The sampled trace through (t=1.0) found the first turning point in the
perturbed peak amplitude near (t=0.925), while the perturbed radius remained
monotonic.

This extension keeps every numerical and physical parameter fixed and extends
only the observation window to

[
t=1.5.
]

Implementation:

- `src/qball_highres_timeseries_t1p5.py`

Tests:

- `tests/test_qball_highres_timeseries_t1p5.py`

## Sampling

The run uses

[
91^3,qquad h=0.175,qquad dt=0.001,
]

for

[
1500 {m steps}
]

with diagnostics sampled every 25 steps.

This yields 61 snapshots including the initial state.

## Turning-time diagnostics

The report now records the sampled turning events themselves, including:

- minimum and maximum peak events;
- minimum and maximum radius events;
- intervals between consecutive peak turning events.

If the perturbed peak develops a second turning point, the time between the
first minimum and next maximum is a sampled half-cycle estimate.

A full oscillation period is not claimed from a single half-cycle.

## Decision rule

If a second perturbed peak turning point appears, the next task is to extend the
sampled window far enough to capture a repeated same-kind turning event and
estimate a full period.

If the radius also turns, the peak and radius phase relation becomes the next
diagnostic.

If neither occurs by (t=1.5), the evolution remains too slow for a meaningful
period estimate in this window.
