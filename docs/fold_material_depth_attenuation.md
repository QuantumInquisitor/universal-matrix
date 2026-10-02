# Recursive root-backreaction attenuation sweep

The depth-three material tree closes its explicit energy accounts, but the first depth-three
comparison found that adding the third level changed the root state by only about 5e-17 over
the tested interval. That result is below the declared 1e-12 resolution threshold.

This checkpoint asks whether that small result is only a short-time effect or whether influence
from deeper levels attenuates strongly under the current half-scale law.

## Fixed model

No connector strength, scale exponent, material coefficient or resolution threshold is changed.

The sweep reuses the existing passive material tree at depths 0, 1, 2 and 3. It evaluates the
root state after 0.005, 0.01, 0.02, 0.04 and 0.05 seconds. For each duration it compares:

- depth 0 to depth 1,
- depth 1 to depth 2,
- depth 2 to depth 3.

A transition is called resolved only when its maximum absolute root-state difference exceeds
the predeclared 1e-12 threshold. The report records the first duration, if any, at which each
transition becomes resolved and its maximum response over the duration grid.

A disconnected depth-three tree is compared with a single root at the longest duration as a
causal/control check. All connected and disconnected runs retain node, edge and subtree energy
audits.

## Interpretation

If depth 2 to 3 remains unresolved throughout this bounded duration grid, the correct result is
that the present experiment has not demonstrated resolved macroscopic backreaction from the
third level. That does not prove an infinite-depth limit or zero influence at every time.

If it becomes resolved only at a later duration, the result instead indicates delayed
transmission under the unchanged law.

Neither outcome justifies changing the coupling merely to obtain a preferred recursive effect.
A new coupling mechanism requires an independent geometric, physical or empirical reason.
