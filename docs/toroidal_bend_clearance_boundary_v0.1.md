# Toroidal bend clearance boundary v0.1

## Purpose

The bend-spacing scan established two facts at once:

- the compact separated-shell reference still collides;
- the tested 25-point shell-gap/bend-margin grid contains at least one
  collision-free sample.

This checkpoint turns that finite scan into an explicit sampled frontier. It
does not change the graph, signed currents, annular junctions, Piola
connectors, or smooth-bend maps.

## Sampled frontier

For each tested positive bend-radius margin, the audit sorts shell gaps from
smallest to largest and records the first sampled collision-free gap.

When a smaller colliding sample exists on the same row, it is retained as the
lower bracket of the sampled transition.

A margin with no collision-free tested point is reported as unresolved.

This is a finite-grid boundary summary. The true continuous boundary may lie
between sampled gaps, may be nonmonotone between samples, or may change under
finer spatial collision sampling.

## Default grid

The default grid is the same grid already admitted by the spacing-scan
checkpoint:

- shell gaps: 0.25, 1.0, 3.0, 10.0, 30.0;
- bend margins: 0.005, 0.02, 0.05, 0.1, 0.25.

The audit records:

- total sampled points;
- colliding and collision-free counts;
- the first collision-free sampled gap for each resolved margin;
- the nearest lower colliding sampled gap when present;
- margins for which no free point has yet been found.

## Orientation check

The positive- and negative-current references are expected to have the same
collision/free mask because the collision geometry depends on active channel
volumes rather than current sign. The focused tests verify that equality on the
default sampled grid.

Zero current remains explicit and produces no active incident collision pairs.

## Evidence boundary

Established by this checkpoint:

- deterministic extraction of a sampled collision/no-collision frontier;
- explicit unresolved-margin reporting;
- current-orientation invariance of the sampled clearance mask;
- preservation of the existing finite spacing-scan evidence.

Not established:

- a continuous or globally monotone clearance boundary;
- an optimal compactness law;
- a scale-invariant clearance inequality;
- collision freedom across every Flower/Tree scale or recursive depth;
- a physical length scale;
- a dynamics law telling the geometry how to morph.

## Next gate

Use the sampled frontier to choose narrower shell-gap intervals around each
resolved margin, refine those intervals, and then test normalized clearance
ratios across Flower/Tree scales and recursive depths.

A separate-axis fan-out remains a fallback only if no compact,
scale-consistent clearance region survives.
