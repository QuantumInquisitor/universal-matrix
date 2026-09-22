# Q-Ball High-Resolution In-Run Time Series to t=2.0 v0.1

## Purpose

The sampled trace through (t=1.5) retained only one perturbed peak turning
event, a minimum near (t=0.925), while the perturbed radius remained
monotonic.

This extension changes only the observation duration:

[
t=2.0.
]

The grid, timestep, perturbation, and 25-step sampling cadence remain unchanged.

Implementation:

- `src/qball_highres_timeseries_t2.py`

Tests:

- `tests/test_qball_highres_timeseries_t2.py`

## Sampling

[
91^3,qquad h=0.175,qquad dt=0.001,
]

for

[
2000 {m steps}
]

with one sample every 25 steps.

This produces 81 snapshots including the initial state.

## Half-cycle candidate

If the perturbed peak develops a second turning event of the opposite kind, the
time between the first two events is reported as a sampled half-cycle candidate.

This is not yet a full oscillation period.

A full period requires either:

- two repeated same-kind perturbed peak events, or
- two consistent opposite-kind half cycles.

## Radius channel

The RMS-radius turning events remain independent evidence.

If the radius acquires its first turning point by (t=2.0), the next analysis
should compare its timing with the peak-amplitude reversal to study their phase
relationship.

## Decision rule

If the second perturbed peak turning event appears, use its interval only as a
half-cycle estimate and extend far enough to obtain an independent repeat.

If no second turning event appears, the peak recovery timescale exceeds this
window and should not be forced into a periodic interpretation.
