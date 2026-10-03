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

## Typed point-model checkpoints

`checkpoint(state)` now packages the existing 48-component state with the
`material-point-powered-checkpoint-v1` schema, explicit inertia/state/ownership
identity, module sizes and ordered connector topology. `restore_checkpoint`
validates these before interpreting numeric slots. `advance` accepts that envelope
and returns a new envelope alongside its unchanged numerical arrays. The report's
powered JSON round-trip now exercises the typed envelope; solver equations,
tolerances and cumulative ledger indexing are unchanged.

Legacy raw 48-entry vectors remain supported by the existing point-only `advance`
API. They are not self-identifying saved models: choosing this legacy API asserts
point-powered semantics. Missing identity is rejected in a typed envelope, and
explicit foreign identities or topologies never fall back to raw-vector behavior.
A matching length alone does not make a distributed checkpoint compatible.

The identity tags describe body-point inertia, node9/edge2/input1 state layout and
separate powered node/edge/group ownership. They are model declarations rather
than authentication. No distributed powered persistence, field conversion, source
hardware or new recursive dynamics is introduced. A future distributed format
must define its own supported adapter and tests rather than relabel these slots.

The state-layout tag means ordered node blocks
`[q0,q1,v0,v1,reserve,delivered_work,damping_loss,conversion_loss,leakage_loss]`,
followed by two signed endpoint-work values per ordered edge, then one external
input-energy ledger per node. Connector potential is computed and owned once per
edge; it is not an extra state slot or part of each node's stored energy. Delivered
work remains transfer, not additional storage. The typed checkpoint fixes the
existing four-module topology and preserves all cumulative values exactly.
