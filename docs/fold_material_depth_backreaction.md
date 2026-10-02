# Recursive return-backreaction audit

The preceding transport checkpoint established that a root perturbation reaches physical level 3
by 0.011 seconds under the unchanged recursive material equations. Yet the incremental effect of
adding level 3 remains below the 1e-12 root-state reporting floor through 0.1 seconds.

This checkpoint isolates the causal contribution of each depth without changing the number of
physical modules.

## Fixed 15-module state dimension

Every case contains the same complete 15-module binary tree state. Only the set of active
parent-child connectors changes:

| Connected through child level | Active edges | Interpretation |
| --- | ---: | --- |
| 0 | 0 | root plus 14 isolated equilibrium modules |
| 1 | 2 | level-1 coupling only |
| 2 | 6 | levels 1 and 2 coupled; level 3 isolated |
| 3 | 14 | full depth-three tree |

The incremental root contribution of physical level d is therefore the absolute root-state
difference between the case connected through level d and the case connected through level d-1.
This removes the change in module count that occurs when comparing separate depth-2 and depth-3
trees.

## Energy transfer across each edge level

For the full tree, edge groups are classified by the physical level of their child endpoint.
At each sampled time the report keeps:

- connector potential change from the initial state;
- cumulative parent-endpoint work;
- cumulative child-endpoint work;
- the identity residual delta-U + W-parent + W-child;
- the magnitude of child work relative to parent-endpoint work.

This exposes whether parent work is transferred into child mechanical motion or remains stored
primarily as connector potential.

## Scope

The audit uses the existing connector, constitutive, damping, inertia, scale and initial-state
laws without coefficient changes. It does not introduce a new recursive interaction.

Passing establishes only causal attribution and energy accounting inside the tested 15-module
synthetic model. It does not establish a spatial recursive construction, arbitrary depth,
infinite-depth convergence, powered recursive operation, or correspondence with the 69-component
toroidal flow assembly.
