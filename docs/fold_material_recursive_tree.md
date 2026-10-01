# Replicated material-module tree

This checkpoint is the first recursion test in this lane that increases the number of physical
dynamical degrees of freedom. It is intentionally separate from the earlier hierarchy-depth
control, which only regrouped the same four modules.

## Construction

A binary tree is generated through physical depth 2:

| Depth | Module count | Parent-child links | Smallest module scale |
| --- | ---: | ---: | ---: |
| 0 | 1 | 0 | 1 |
| 1 | 3 | 2 | 1/2 |
| 2 | 7 | 6 | 1/4 |

Every node is an independently integrated copy of the geometry-derived material module. Child
linear scale is one half of its parent. Every parent-child edge uses the existing mapped-port
connector with one owned connector potential and equal-and-opposite endpoint reactions.

Only the root is initially displaced and moving. Descendants begin at the material reference
state. This lets the test distinguish a response caused by actual coupling from one caused merely
by allocating more state variables.

## Controls

The report includes:

- connected trees at depths 0, 1 and 2,
- a seven-module depth-2 tree with every parent-child edge removed,
- a depth-2 tree with one deliberately reversed endpoint reaction, and
- a half-timestep depth-2 refinement run.

The disconnected tree must reproduce the single root module trajectory even though six extra
independent equilibrium modules exist. The connected trees are expected to alter the root
response because energy can move through the mapped connectors. The reversed-reaction control
must break its edge and whole-tree energy account.

## What this establishes

Passing this checkpoint establishes that the current equations can evolve multiple material
modules arranged in a repeated parent-child topology with explicit energy ownership. It is a real
increase in dynamical state dimension, not a bookkeeping nesting trick.

It does not establish arbitrary depth, a spatially realizable fractal assembly, a validated
mechanical joint, powered recursive operation, convergence to an infinite-depth limit, or a
stable recursive breathing cycle. The present repository-wide mixed-size configuration contract
supports at most eight modules, so the complete binary tree is deliberately stopped at seven.

The next recursion step should address physical-depth extension and convergence. That requires
either a reviewed expansion of the module-count contract or a sparse recursive solver, followed
by explicit parent-child spatial placement and collision/joint checks before correspondence with
the separate 69-domain toroidal flow assembly.
