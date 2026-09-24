# Toroidal bend-clearance refinement v0.1

## Purpose

The sampled clearance-frontier checkpoint identifies, for each tested bend
margin, the first collision-free shell gap on the coarse grid and the nearest
lower colliding sample when one exists.

This checkpoint refines only those finite collision/free brackets. It does not
assume that clearance is globally monotone in shell gap.

## Method

For each resolved coarse bracket,

$$
g_c < g_f,
$$

where $g_c$ is the nearest lower colliding sample and $g_f$ is the first
collision-free sample, the interval is divided into a fixed number of equal
subintervals.

The already-computed coarse endpoint results are reused. Only the interior
gaps are evaluated with the same Vesica graph, signed currents, annular
junctions, Piola connectors, bend construction, and collision sampler.

The refined report records:

- the coarse collision/free bracket;
- the narrower sampled collision/free bracket;
- the number of classification transitions across the refined row;
- whether any sampled collision reappears after a collision-free point.

That last diagnostic is important because the current evidence does not justify
assuming a monotone clearance law.

## Censored rows

A margin is left-censored when the smallest coarse shell gap is already
collision-free, because the lower transition lies outside the tested interval.

A margin remains unresolved when the coarse grid contains no collision-free
sample.

Neither case is converted into an invented boundary.

## Evidence boundary

Established here:

- deterministic interior refinement of resolved sampled brackets;
- reuse of coarse endpoint classifications;
- explicit detection of re-entrant collision samples;
- narrower finite sampled brackets without a monotonicity assumption.

Not established:

- a continuous boundary;
- monotonicity between samples;
- a globally minimal or optimal shell gap;
- a scale-invariant clearance inequality;
- collision freedom at every Flower/Tree scale or recursive depth;
- a physical length scale or adaptive geometry dynamics.

## Next gate

If the refined rows remain well behaved, compare dimensionless clearance ratios
across scaled Vesica and Flower/Tree constructions. If a row is re-entrant,
increase geometric sampling density and map that region before attempting a
scale law.

A separate-axis fan-out remains a fallback only if no compact,
scale-consistent collision-free region survives.
