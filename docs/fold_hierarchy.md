# Regrouping the fold network without changing its physics

`scripts/report_fold_hierarchy.py` adds a validated parent/child hierarchy over
the existing graph. Leaves must cover every node exactly once. Empty groups,
duplicate or missing leaves, invalid indices and depth beyond eight reject.
Each connection is assigned to the lowest common ancestor of its endpoints.
The recursive force traversal visits each leaf and applies each connection once,
then solves the unchanged module acceleration equations.

This hierarchy groups existing degrees of freedom. It introduces no new force
law, coarse-graining approximation, physical scale or material parameter.

## Ownership and boundary accounting

Exclusive connection ownership controls where its forces are evaluated.
An independent inclusive account for each group contains descendant mechanical
energy, reserves, losses and every connection wholly inside that group. Its
change must equal the work entering through connections crossing the boundary.
Reservoir-delivered work is internal transfer and is not added to total energy.

Inclusive accounts overlap across hierarchy levels: a parent includes its
children. **Do not sum parent and child totals.** The root's total counts each
node and connection once. A child may gain or lose energy through its boundary
while the root remains balanced.

## Reproduction and results

Four layouts—flat, balanced, deeply nested and reordered—run the same four-node
weighted cycle for two seconds at .02-second steps. An independent flat force
traversal is integrated as the reference. All accepted states are compared,
with coordinate/rate differences separated from energy-state differences.

In this run all four layouts match the flat trajectory exactly, including
energy states. The maximum inclusive-group ledger residual is 1.342e-13 J.
This is an observed floating-point result for the specified case, not a promise
of bitwise equality on every platform or larger graph. Automated checks allow
small rounding differences. Source hashes, initial state, ownership tables,
initial/final group accounts and differences are in
`experiments/fold-hierarchy-summary.json`.

An accounting negative control counts edge 0 a second time. It overcounts
initial total by 1.05e-6 J and introduces a spurious energy change of
-7.36997e-7 J over the interval. This checks double-counting, not a defective
force law; force-sign negative controls remain in the network study.

Independent review found no blocking defect. Separately differentiating each
subgroup's inclusive energy and subtracting boundary power gave errors below
1.15e-14 J/s. Tests verify exact edge ownership, subgroup boundary work, recursive
versus flat derivatives and short trajectories, disconnected single-node
hierarchies, invalid layouts and timestep rejection.

## What this establishes

Grouping is a consistent representation of the existing synthetic mechanics.
It does not yet validate new cross-scale interactions, fractal material geometry,
spatial joints, collision clearance, sustained breathing or the XR mapping.
Next: specify a cross-scale connection using explicit coordinate mappings and
derive its forces from one potential, then test its energy account before
applying it across the whole structure.
