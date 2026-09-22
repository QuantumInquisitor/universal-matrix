# Q-Ball High-Resolution In-Run Time Series v0.1

## Purpose

The first four high-resolution persistence stages used endpoint diagnostics.
Those results established that the threshold-preserving (91^3) state remains
coherent through (t=0.5), but endpoint data alone cannot distinguish:

- monotonic relaxation;
- breathing-mode oscillation;
- damped oscillation;
- a transient overshoot followed by recovery.

This layer samples the same direct and perturbed evolution during the run.

Implementation:

- `src/qball_highres_timeseries.py`

Tests:

- `tests/test_qball_highres_timeseries.py`

## Sampling schedule

The evolution remains

[
91^3,qquad h=0.175,qquad dt=0.001,
]

through

[
500 {m steps},qquad t=0.5.
]

Diagnostics are sampled every 25 steps, producing 21 snapshots including
(t=0).

Each snapshot records:

- relative energy drift;
- relative charge drift;
- peak-amplitude ratio;
- RMS-radius ratio.

## Shape classification diagnostics

For both direct and perturbed channels, the report also records:

- peak turning-point count;
- radius turning-point count;
- whether the peak is monotonically nonincreasing;
- whether the radius is monotonically nondecreasing;
- maximum peak deviation;
- maximum radius deviation;
- endpoint deviation;
- endpoint-to-maximum deviation ratio.

An endpoint-to-maximum ratio near one means the largest excursion occurs at the
end of the observed window.

A substantially smaller ratio means the field reached a larger excursion
earlier and then returned toward its initial state, which is evidence of
turning or oscillatory behavior.

## Interpretation boundary

This diagnostic does not by itself determine a normal-mode frequency.

If turning points appear, the next build should record a longer sampled trace
and estimate oscillation periods directly.

If the channels remain monotonic through (t=0.5), the next step should be a
controlled extension of the sampled window rather than assuming oscillation.
