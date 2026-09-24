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

## Collision-free existence point

A deliberately wider shell spacing with a tighter positive-Jacobian bend,

shell gap = 3.0,

bend margin = 0.05,

produces no sampled incident bend/straight collision in the Vesica reference
at the higher-resolution audit used by the test suite.

The same candidate remains collision-free when the signed graph current is
reversed.

This is an existence result. It does not establish that these numerical values
are optimal, physically meaningful, or compact.

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
- existence of at least one collision-free Vesica spacing/bend candidate;
- current-reversal invariance of that existence result;
- deterministic finite parameter-grid scanning.

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
