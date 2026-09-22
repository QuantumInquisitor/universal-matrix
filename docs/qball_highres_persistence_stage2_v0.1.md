# Q-Ball High-Resolution Persistence Stage 2 v0.1

## Purpose

Stage 2 extends the same threshold-preserving (91^3) direct and perturbed
evolution from 25 to 100 steps while holding all other parameters fixed.

Implementation:

- `src/qball_highres_persistence_stage2.py`

Tests:

- `tests/test_qball_highres_persistence_stage2.py`

## Duration scaling

The Stage-2 defaults are

[
100 {m steps},qquad dt=0.001,
]

for

[
t=0.1.
]

This is exactly four times the Stage-1 duration.

## Controlled comparison

The grid remains

[
91^3,qquad h=0.175,qquad L=7.875,
]

and the perturbation remains the standard localized (0.5%) amplitude
perturbation.

The report uses the same diagnostics as Stage 1 so that any change can be
attributed primarily to duration rather than a simultaneous parameter change.

## Decision rule

If Stage 2 remains clean, the next duration should be chosen from the measured
growth in:

- energy drift;
- charge drift;
- peak-amplitude deviation;
- RMS-radius deviation.

A longer stage should not be launched if those quantities show unexpected
superlinear growth.
