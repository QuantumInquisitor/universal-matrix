# Consistent scaling of an unequal-sized connected pair

`scripts/report_fold_scaled_pair.py` combines the reconstructed body scaling
with the nonlinear mapped connector. The child remains half the parent's
linear size. Uniform parent scale lambda is 1, .75 or .5; absolute child scales
are .5, .375 and .25. Each module uses its own reconstructed mass and inertia,
restoring potential and damping law from `fold_scaling.md`.

This experiment is passive: no active reservoir is included. Node A starts
displaced and moving; node B starts at rest. It tests body/connector consistency
before introducing active reservoirs or more recursive levels.

## Energy and similarity

Both port lengths scale by lambda. Connector physical stiffness also scales by
lambda, so its stored energy and generalized forces scale by lambda cubed.
Module mass matrices scale to the fifth power. Corresponding time intervals
scale by lambda, rates inversely, and damping work cubically. Relative child
size is fixed throughout; changing that ratio is a different experiment.

Each module tracks mechanical energy plus damping loss minus received connector
work. The connector tracks potential plus both endpoint works. Global energy
contains both module energies, their losses and connector potential once.

| Case | Physical duration (s) | Maximum global balance residual (J) |
| --- | ---: | ---: |
| Reference parent scale 1 | 1 | 5.775e-17 |
| Parent scale .75 | .75 | 2.436e-17 |
| Parent scale .5 | .5 | 7.218e-18 |
| Parent scale .5, fixed connector stiffness | .5 | 2.376e-17 |

For consistently scaled stiffness, coordinates agree exactly in this run;
maximum rescaled rate difference is 2.776e-17 and rescaled energy difference
6.353e-22 J. Because the runs use matching reference-time integration grids,
this checks scaling consistency, not independent integration accuracy.

A separate half-timestep run reduces the half-scale energy residual to
1.254e-18 J. Endpoint component differences are below 1.821e-9 in their own
units. Scale, angle, scale rate and angle rate are listed separately. Two
steps establish agreement, not a measured convergence order.

## A conservative comparison that does not preserve similarity

Holding connector stiffness fixed still defines a valid conservative potential.
It therefore passes energy accounting, but does not obey the selected cubic
similarity law. Child scale-coordinate and angle differences reach .002935 and
.004220 rad relative to the resized reference. This is a different physical
assumption, not an intentionally broken force or energy calculation.

Tests independently differentiate the connector potential, verify acceleration
and work scaling, and confirm energy conservation for both stiffness laws.
Independent review found force-gradient error 2.45e-15 and global energy-rate
errors 3.71e-16 J/s (scaled stiffness) and 4.50e-16 J/s (fixed stiffness).
No blocking issue was found. Inputs to trajectory comparison require a unit-scale
reference, matching relative size and matching reference-time grids.

The source-hashed report is `experiments/fold-scaled-pair-summary.json`. It
includes initial states, separate accounts, samples and timestep comparison.

## Remaining scope

This is a finite passive two-module result under synthetic constant-density and
strain-energy assumptions. It does not validate calibrated materials, actual
attachment locations, intermodule collision, sustained breathing or full
recursive structure. Next: extend this consistent connector/body law to a
small network containing multiple absolute sizes, retaining one energy owner
per connection and checking boundary accounts at each hierarchy level.
