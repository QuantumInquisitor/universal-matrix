# Q-Ball High-Resolution Persistence Stage 3 v0.1

## Purpose

Stage 3 extends the same threshold-preserving direct and perturbed evolution to
250 steps while holding the grid, timestep, and perturbation fixed.

Implementation:

- `src/qball_highres_persistence_stage3.py`

Tests:

- `tests/test_qball_highres_persistence_stage3.py`

## Duration

[
250 {m steps},qquad dt=0.001,qquad t=0.25.
]

This is ten times Stage 1 and 2.5 times Stage 2.

## Controlled comparison

The same (91^3) grid at (h=0.175) and the same localized (0.5%)
perturbation are reused without modification.

The report again records:

- energy drift;
- charge drift;
- peak-amplitude ratio;
- RMS-radius ratio;
- direct survival;
- perturbed survival;
- threshold-side preservation.

## Decision rule

If Stage 3 remains within the same qualitative regime, the next duration can be
chosen from the observed scaling of structural deviations.

If the peak or radius changes accelerate sharply, the next task becomes fitting
their time dependence rather than simply extending duration.
