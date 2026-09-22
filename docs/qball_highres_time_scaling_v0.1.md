# Q-Ball High-Resolution Time-Scaling Diagnostic v0.1

## Purpose

Three completed high-resolution persistence stages now exist on the same
threshold-preserving (91^3) grid:

[
t=0.025,quad 0.1,quad 0.25.
]

This layer analyzes how conservation drift and structural deviations scale
across those completed observations before selecting a Stage-4 duration.

Implementation:

- `src/qball_highres_time_scaling.py`

Tests:

- `tests/test_qball_highres_time_scaling.py`

## Channels

The analysis treats six quantities independently:

- direct energy drift;
- perturbed energy drift;
- direct peak-amplitude deviation;
- perturbed peak-amplitude deviation;
- direct radius deviation;
- perturbed radius deviation.

For each channel it reports:

- early local power exponent from (t=0.025	o0.1);
- late local power exponent from (t=0.1	o0.25);
- global exponent from (t=0.025	o0.25);
- latest measured value;
- a local late-time projection to (t=0.5).

The extrapolation is only a duration-selection diagnostic. It is not treated as
an asymptotic law.

## Current pattern

The radius channels are close to quadratic in time over all three completed
stages.

Energy drift rises strongly at first but is nearly flat between Stage 2 and
Stage 3, suggesting the conservation error is not continuing to accelerate.

Peak-amplitude deviation grows more slowly than radius deviation at late time
for the direct state and more strongly for the perturbed state, but remains very
small in absolute magnitude.

## Stage-4 rule

The next candidate duration is restricted to

[
t=0.5
]

only when all projected peak and radius deviations remain below a conservative
one-percent structural limit.

With the current Stage-1 through Stage-3 observations, that criterion is met.

The rule does not authorize larger jumps such as (t=1) or beyond.
