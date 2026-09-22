# Q-Ball High-Resolution Persistence Stage 4 v0.1

## Purpose

Stage 4 tests the first duration selected by the explicit time-scaling
diagnostic rather than by an arbitrary jump.

The evolution remains on the confirmed threshold-preserving grid

[
91^3,qquad h=0.175,qquad L=7.875,
]

with the same timestep and the same localized (0.5%) perturbation.

Implementation:

- `src/qball_highres_persistence_stage4.py`

Tests:

- `tests/test_qball_highres_persistence_stage4.py`

## Duration

[
500 {m steps},qquad dt=0.001,qquad t=0.5.
]

## Prediction check

Before Stage 4, the three completed stages produced local projections to
(t=0.5) for peak and radius deviations.

Stage 4 records both the measured deviations and their ratio to those prior
projections.

This turns Stage 4 into a direct test of whether the short-time scaling
diagnostic remains predictive.

## Interpretation

A measured-to-projected ratio near one means the local Stage-2 to Stage-3 trend
continued approximately as expected.

A large departure does not automatically imply instability. It means the
earlier local extrapolation has left its predictive regime and the time
dependence must be reconsidered.

## Stop condition

No duration beyond (t=0.5) is selected by this stage.

The next action is chosen only after comparing:

- conservation drift;
- direct and perturbed survival;
- measured peak and radius deviations;
- measured-to-projected ratios.
