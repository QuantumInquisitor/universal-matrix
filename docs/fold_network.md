# Small fold network with connection ownership

`scripts/report_fold_network.py` extends the verified pair to a graph of up to
eight synthetic modules. The reported experiments use four. Each node retains
the existing nine-state reservoir model; each unique undirected connection
stores its spring potential once and integrates work delivered at both ends.
Duplicate connections, including reversed duplicates, self-connections, invalid
indices and nonpositive stiffness weights are rejected. Disconnected nodes
are allowed; omission of an edge represents no connection.

## Accounting

For each node, the change in mechanical energy equals reservoir work minus
damping loss plus the sum of work delivered by incident edges. For each edge,
its potential change plus both endpoint works is zero. The total includes
all node mechanical energies, reserves and losses, plus each edge potential
once. Integrated internal work is never added again to total energy.

The generalized spring law is inherited unchanged from `fold_coupling.md`.
An edge acts on scale and angle coordinates; it is not a calibrated Cartesian
joint. Node labels and edge orientations are bookkeeping choices. Tests show
that relabeling nodes or reversing edge orientation preserves dynamics, with
endpoint work entries permuted appropriately.

## Experiments

Six four-second cases cover a chain, star, cycle, disconnected nodes, a chain
with the second edge's reaction deliberately reversed, and a conservative
chain with no reservoir fuel or damping. A seventh run refines the fueled
chain from .02 to .01 seconds. Node 0 begins displaced and moving; other nodes
start at rest with empty reserves. Only node 0 receives fuel in fueled cases.
The complete initial states, edge list, settings, source hashes and sampled
results are recorded in `experiments/fold-network-summary.json`.

The deliberately broken second edge is initially unstretched. Its failure
develops after motion reaches it. Node work ledgers can still balance because
they record the applied forces honestly; the edge and global accounts identify
the nonconservative connection. This distinction tests the accounting rather
than assuming visible motion establishes correct physics.

| Four-second case | Maximum global residual (J) |
| --- | ---: |
| Chain | 1.883e-13 |
| Star | 4.605e-13 |
| Cycle | 2.924e-13 |
| Disconnected | 1.209e-13 |
| Conservative chain | 7.997e-14 |
| Deliberately broken chain | 3.955e-7 |

The broken chain's edge residuals are 5.30e-14, 3.95e-7 and 9.74e-16 J:
the second edge is correctly isolated. Chain refinement lowers the global
residual to 9.027e-15 J; per-node coordinate/rate differences are below
4.194e-9 in their respective units. These two steps show agreement, not a
measured convergence order. In the conservative run, downstream nodes 1, 2
and 3 end with 1.6174e-6, 1.8912e-7 and 5.2644e-9 J of mechanical energy.
This energy comes from the initially moving/displaced node and strained edges,
not from creation of energy by the graph.

Independent review found no blocking defect. A separate directional derivative
of total energy on a weighted cycle gave -3.73e-14 W; reversing an active
reaction produced -4.20e-6 W. Reversing all edge orientations left node
derivatives identical and swapped endpoint work exactly. Tests also reduce the
two-node graph to the previously verified pair and keep disconnected resting
nodes at rest. The linked network, pair and reservoir suites have 51 passing
tests. Reports are reproduced and checked in the experimental workflow.

## Limits and next step

These are finite runs of synthetic coordinate graphs. A cycle is a graph loop,
not proof of fractal geometry, physical folding closure or sustained breathing.
No intermodule placement, material calibration, Cartesian momentum proof or
continuous collision validation is implied. The graph has no recursive hierarchy
yet. Next: add explicit parent/child grouping and verify that regrouping the same
nodes and connections leaves energy totals and trajectories unchanged before
introducing any new cross-scale coupling law.
