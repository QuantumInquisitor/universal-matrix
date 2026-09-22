# Q-Ball High-Resolution Persistence Stage 1 v0.1

## Purpose

This is the first dynamical test on the finite Cartesian grid that independently
preserves the refined radial above-threshold energetic classification.

The grid is

[
91^3,qquad h=0.175,qquad L=7.875.
]

The run is intentionally short. It is a numerical sanity stage before any
longer high-cost evolution.

Implementation:

- `src/qball_highres_persistence_stage1.py`

Tests:

- `tests/test_qball_highres_persistence_stage1.py`

## Stage-1 duration

The default stage uses

[
25 {m steps},qquad dt=0.001,
]

for a simulated duration of

[
t=0.025.
]

Both the unperturbed mapped state and the standard localized (0.5%)
amplitude perturbation are evolved.

## Recorded evidence

The report keeps separate:

- radial (E/Q);
- Cartesian (E/Q);
- confirmation that both remain above the free-mass threshold before evolution;
- direct finite-window survival;
- perturbed finite-window survival;
- relative energy drift;
- relative charge drift;
- peak-amplitude ratio;
- RMS-radius ratio.

## Interpretation boundary

Passing stage 1 means only that the state is numerically well behaved over this
short interval on the threshold-preserving grid.

It is not yet evidence for long-duration nonlinear stability.

## Stop condition

After the stage-1 CI report is available, the next duration should be selected
from the measured drift and structural changes rather than automatically
jumping to 1000 steps.
