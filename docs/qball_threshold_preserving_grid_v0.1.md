# Q-Ball Threshold-Preserving Grid Confirmation v0.1

## Purpose

The joint spacing-and-volume extrapolation restores the refined radial
above-threshold classification in the (h\to0), (L\to\infty) limit.

Before running an expensive high-resolution persistence simulation, this layer
checks one finite Cartesian grid predicted to preserve the same energetic
threshold side.

Implementation:

- `src/qball_threshold_preserving_grid.py`

Tests:

- `tests/test_qball_threshold_preserving_grid.py`

## Target grid

The selected target is

[
h=0.175,
qquad
L=7.875,
]

which gives the centered grid

[
91^3.
]

The joint fit predicts that this grid should place the mapped refined radial
point slightly above

[
E/Q=1.
]

The predicted margin is intentionally larger than the maximum residual observed
in the joint fit.

## Confirmation outputs

The executable report records:

- radial (E/Q);
- actual Cartesian (E/Q);
- mapping relative difference;
- radial threshold side;
- Cartesian threshold side;
- whether the side is preserved;
- joint-fit prediction for the target grid;
- absolute prediction error.

## Next step

Only if the finite grid actually preserves the above-threshold classification
should it be used for the expensive direct and perturbed 3D persistence run.

This prevents extrapolation alone from being substituted for a finite-grid
calculation.
