# Toroidal incident-bend spacing scan v0.1

## Purpose

The incident-bend audit found strict collisions for one separated-shell
geometry. Before replacing the junction architecture, this checkpoint asks
whether the existing geometry can remove that collision by changing only two
continuous parameters:

- radial gap between edge-specific channel shells;
- positive bend-radius margin above the annular outer radius.

The graph, signed currents, annular junction logic, Piola transitions, and
smooth-bend field remain unchanged.

## Baseline

The earlier reference uses approximately

shell gap = 0.25,

bend margin = 0.25.

The scan reproduces the known incident bend/straight collision at that point.

## First widened candidate is still a no-fit

The first deliberately widened test point,

shell gap = 3.0,

bend margin = 0.05,

still produces two sampled incident bend/straight collisions in the Vesica
reference. The maximum penetration is approximately 0.196 in the current
dimensionless geometry, and reversing the signed graph current does not remove
the obstruction.

Therefore moderate radial widening plus a tighter bend is not sufficient.

The completed regression scan expands the search to shell gaps

`(0.25, 1.0, 3.0, 10.0, 30.0)`

and positive bend margins

`(0.005, 0.02, 0.05, 0.1, 0.25)`.

Across that deterministic 25-point grid, at least one parameter point has no
collision detected by the finite sampler. This does not establish existence
of a continuously collision-free geometry. In particular, the default coarse
scan misses the known gap-3 collision detected by the denser single-point
test above; see `toroidal_sampling_reliability_v0.1.md`.

The current test intentionally establishes existence rather than claiming an
optimal point or a complete clearance boundary.

## Interpretation

The previous incident-bend result is therefore a no-fit for the tested compact
geometry, not yet a topology theorem forbidding the separated-shell approach.

The current network can morph its radial spacing and curvature while preserving
the same discrete incidence, signed fluxes, connector profiles, and bend maps.

That makes spacing and curvature legitimate geometric state variables for a
later adaptive or recursive routing law.

## Evidence boundary

Established here:

- reproduction of the earlier colliding reference;
- persistence of the collision at shell gap 3.0 and bend margin 0.05;
- orientation independence of that failed candidate;
- deterministic finite parameter-grid scanning;
- existence of at least one point with no collision detected on the tested grid.

Not established here:

- a globally minimal or optimal spacing law;
- collision freedom for every Flower/Tree scale and recursion depth;
- a physical length scale;
- a dynamical equation telling the geometry how to morph;
- a biological or consciousness interpretation of adaptive geometry.

## Next gate

The next geometric question should be optimization before redesign:

1. map the collision/no-collision boundary in the shell-gap/bend-margin plane;
2. test the same dimensionless ratios across Flower/Tree scales and recursive
   universe depths;
3. identify a conservative inequality or scaling law that guarantees
   clearance.

Only if no compact scale-consistent region exists should the engine move to an
off-axis multi-port junction or separate-axis fan-out.
