# Powered material restart persistence and hierarchy-depth control

This checkpoint tests whether the complete powered material state can be saved, restored and
continued without silently resetting energy ledgers. It also distinguishes deeper hierarchy
bookkeeping from actual recursive physical replication.

## Restart state

The powered unequal-size model has 48 state components:

- four modules with generalized coordinates, rates, reserve energy, delivered work and three
  loss ledgers,
- four connector work pairs, and
- four external-input energy ledgers.

A 0.4 second powered run is serialized as finite JSON, restored and continued for another
0.4 seconds. Its final state is compared with a single 0.8 second run from the same initial
state and numerical tolerances. The same segmented-versus-continuous control is repeated with
the external source disabled.

Every segment is audited relative to its own starting state. Mechanical energy, reserve energy,
connector potential/work, losses, external input and hierarchy totals therefore remain valid
across a restart instead of being implicitly rebased to zero.

## Hierarchy depth is not physical recursion

The existing hierarchy compiler can nest bookkeeping groups. This report intentionally wraps the
same four physical modules in progressively deeper unary group layers and verifies that the root
energy, input and edge ownership do not change.

That result means only that regrouping is invariant. It does not establish a recursively
replicated material structure, new cross-scale forces or self-similar physical degrees of
freedom. The current hierarchy implementation also has an explicit depth-8 software guard.

## Next gate

After restart persistence passes, physical recursive replication should be introduced separately:
generate additional material modules at declared scale ratios, define parent-child spatial
connections and energy ownership, and test convergence as physical depth increases. Only then
should the replicated material hierarchy be compared with the 69-domain toroidal flow assembly.
