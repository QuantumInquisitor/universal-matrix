# Q-Ball High-Resolution In-Run Time Series to t=2.5 v0.1

## Purpose

The sampled trace through (t=2.0) produced several perturbed peak reversals
and the first RMS-radius turning point.

However, closely spaced peak turns near (t=1.6) to (1.8) make it unsafe to
treat every sign change as the dominant breathing period.

This extension changes only the observation duration:

[
t=2.5.
]

The grid, timestep, perturbation, and 25-step sampling cadence remain unchanged.

Implementation:

- `src/qball_highres_timeseries_t2p5.py`

Tests:

- `tests/test_qball_highres_timeseries_t2p5.py`

## Sampling

[
91^3,qquad h=0.175,qquad dt=0.001,
]

for

[
2500 {m steps}
]

with one sample every 25 steps.

This yields 101 snapshots including the initial state.

## Stronger turning diagnostics

Each turning event now records:

- event type, minimum or maximum;
- sampled event time;
- actual peak or radius ratio at that event.

The report also records:

- minimum-to-minimum intervals;
- maximum-to-maximum intervals;
- amplitude swing between adjacent turning events.

These values allow small local wiggles to be distinguished from larger,
repeatable extrema.

## Period rule

A full-period candidate requires a repeated same-kind perturbed peak extremum.

A single minimum-to-maximum interval remains only a half-cycle candidate.

Closely spaced low-amplitude turns are retained as evidence but are not assumed
to represent the dominant mode.

## Radius phase

Radius turning events remain independent. If repeated radius extrema appear, the
next analysis should compare their timing against the dominant peak extrema to
estimate phase relation.
