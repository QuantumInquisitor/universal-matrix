# Q-Ball High-Resolution In-Run Time Series to t=1.0 v0.1

## Purpose

The first sampled high-resolution trace showed no turning in the perturbed
channel through (t=0.5), while the direct peak displayed small reversals.

This extension keeps the same grid, timestep, perturbation, and sampling cadence
and doubles the observed window to

[
t=1.0.
]

Implementation:

- `src/qball_highres_timeseries_t1.py`

Tests:

- `tests/test_qball_highres_timeseries_t1.py`

## Sampling

The run uses:

[
91^3,qquad h=0.175,qquad dt=0.001,
]

with

[
1000 {m steps}
]

and sampling every 25 steps.

This produces 41 snapshots including the initial state.

## Additional diagnostics

The extension retains the turning-point and monotonicity metrics from the
(t=0.5) trace and adds the sampled times of:

- minimum peak ratio;
- maximum peak ratio;
- minimum radius ratio;
- maximum radius ratio.

These extrema times help distinguish continuing monotonic drift from a resolved
turnaround.

## Decision rule

If the perturbed peak or radius develops a turning point before (t=1.0), the
next task is oscillation-period estimation from a longer trace.

If the perturbed channel remains monotonic, the next step is to characterize
the long-timescale relaxation law rather than assume a breathing mode.
