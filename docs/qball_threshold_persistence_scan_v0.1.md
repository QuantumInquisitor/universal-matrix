# Q-Ball Threshold Persistence Scan v0.1

## Purpose

This experiment compares finite-time nonlinear persistence on the two accepted
continued branch points that immediately straddle the refined energetic
condition

\[
E/Q=m_{\rm free}.
\]

Implementation:

- `src/qball_threshold_persistence_scan.py`

The scan is executed in CI on Python 3.12 after the critical verification suite.

## Procedure

1. Refine the energetic crossing with the accepted seeded continuation.
2. Select the two accepted neighboring points that bracket the crossing.
3. Map each radial solution onto the same spacing-consistent 3D lattice.
4. Compare radial and Cartesian \(E/Q\).
5. Evolve each unperturbed state.
6. Re-map each state, apply the same localized amplitude perturbation, and evolve again.
7. Apply the existing explicit finite-window survival criteria.
8. Print the crossing, bracket width, branch-point parameters, mapping error,
   conserved-quantity drift, peak ratio, radius ratio, and both survival
   booleans.

## Why both sides matter

The energetic criterion and the finite-time survival criterion are not assumed
to coincide.

A branch point with \(E/Q>m_{\rm free}\) can in principle remain localized
for the finite simulated window, while an energetically bound point could fail
a sufficiently strong dynamical perturbation.

The experiment therefore asks where the boundaries lie relative to one another
rather than assuming one diagnostic defines the others.

## Interpretation boundary

A passing direct or perturbed run establishes only survival under the specified
finite grid, timestep, duration, perturbation, and criteria.

It does not establish asymptotic stability, quantum stability, or experimental
particle identity.

## Next step

If both threshold-neighbor points survive, expand outward along the branch until
the first persistence failure is found. If they differ, refine directly between
the surviving and failing points to estimate the finite-time persistence
boundary.


## Mapping-side safeguard

The first scan showed why the radial and Cartesian energetic classifications
must be tracked separately near the threshold.

For the refined point with radial \(E/Q\) slightly above one, the finite 3D
mapping shifted Cartesian \(E/Q\) slightly below one even though the relative
mapping difference was below one percent.

The scan now therefore records:

- radial threshold side;
- Cartesian threshold side;
- whether the mapping preserves the side of the threshold;
- whether a radial-versus-persistence threshold comparison is valid after
  mapping.

A persistence result is not interpreted as evidence about the radial energetic
boundary when the mapping itself changes the energetic classification.
