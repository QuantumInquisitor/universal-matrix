# Per-level recursive material transport audit

The 0.05 second attenuation sweep and the 0.1 second duration extension show that depth-three
influence on the root is small but strongly time dependent. Root response alone cannot tell
whether the attenuation occurs because the signal fails to reach deeper descendants or because
energy reaches them but only weakly returns through the hierarchy.

This checkpoint therefore measures transport inside the same passive depth-three model without
changing any equation.

## Measurements

The complete 15-module tree is integrated through 0.1 seconds with the same timestep, material
law, scale ratio and mapped connector law as the preceding depth-three controls.

At 0, 0.005, 0.01, 0.02, 0.04, 0.05, 0.075 and 0.1 seconds the report records for each physical
level:

- maximum generalized-coordinate displacement from the material reference;
- maximum rate multiplied by local module scale, so corresponding-scale rates can be compared;
- total mechanical energy owned by modules on that level;
- cumulative damping loss.

For every set of edges whose children lie on levels 1, 2 or 3, it also records:

- total connector potential;
- signed cumulative work at parent endpoints;
- signed cumulative work at child endpoints;
- sum and maximum of absolute child-endpoint work.

The raw signed and absolute ledgers are retained because symmetric cancellation and physical
energy transfer are different questions.

## Causal control

Only the root begins displaced and moving. Every descendant begins at the exact material
reference state. Deeper connector potentials therefore begin at zero.

A separate depth-three tree with all parent-child edges removed uses the same extra state
variables. Its descendants must remain exactly at the reference state. This distinguishes actual
connector-mediated response from artifacts of allocating more modules.

## Numerical response marker

The existing 1e-12 dimensionless coordinate floor is retained only as a numerical reporting
marker for first visible response. It is not treated as a physical excitation threshold and is
not tuned to the result. Continuous response amplitudes and work ledgers remain the primary
evidence.

## Limits

This experiment does not supply a spatial parent-child embedding, validate collision-free
recursive geometry, establish arbitrary or infinite depth, or map the material tree onto the
separate 69-component toroidal flow assembly. It measures information and energy transport only
inside the declared synthetic recursive material equations.
