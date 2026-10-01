# Experimental 15-module depth-three material tree

The depth-2 recursion checkpoint validated 1, 3 and 7 independently evolving material modules,
but a half-scale binary tree reaches the production scale floor of 0.25 at that depth. The
separate one-eighth scale audit then verified numerical consistency of the underlying synthetic
laws at 0.125 without changing the production validators.

This checkpoint uses that audited 0.125 adapter to run a complete binary tree through depth 3.

## State size

Depth 3 contains 15 independent material modules and 14 parent-child mapped connectors. Module
scales are 1, 1/2, 1/4 and 1/8. Every module owns its own mechanical energy and damping loss.
Every parent-child edge owns one connector potential and two endpoint work ledgers.

The production `scale_value()` floor and 8-node topology guard remain unchanged. This is an
experimental solver, not a silent widening of global scope.

## Subtree accounting

Because the legacy hierarchy compiler intentionally uses the 8-node topology contract, this
experiment computes complete binary-tree subtree membership directly. Every subtree account
contains its descendant module energies and internal connector potentials exactly once, while
work across the subtree boundary is treated as boundary transfer.

Controls include:

- connected depth 2 and depth 3,
- a 15-module depth-3 tree with all connectors removed,
- a depth-3 tree with one reversed endpoint reaction,
- a half-timestep depth-3 refinement run, and
- a single-module reference.

The disconnected 15-module case must reproduce the single root trajectory. Connected depth 3
must measurably alter the root response relative to depth 2. The reversed reaction must create a
localized connector and whole-subtree energy defect.

## Claim boundary

Passing establishes bounded passive dynamics and explicit energy ownership for 15 material
modules through physical depth 3 under the audited synthetic scale laws.

It does not validate spatial parent-child placement, collision-free recursive geometry, powered
depth-3 operation, arbitrary depth, an infinite-depth limit or correspondence with the separate
69-domain toroidal flow assembly.
