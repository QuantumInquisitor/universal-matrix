# Toroidal sampling reliability v0.1

## Purpose and scope

The existing collision sampler checks nonzero, same-face incident bends
against neighboring straight annular volumes. A positive penetration gives a
collision witness. Zero detections on a finite grid do not prove clearance,
and this audit does not cover every possible pair of network volumes.

This checkpoint varies sampling only. Geometry, routing, signed currents,
connector maps, and flux laws remain unchanged.

## Grid provenance and offsets

Every evaluated spacing and similarity result records its grid. The reliability
report compares `(phi, q, theta)` counts `(13, 5, 24)`, `(21, 9, 48)`, and
`(33, 13, 64)`, each at offsets `(0, 0, 0)` and `(0.5, 0.5, 0.5)`.

Counts retain the original convention: phi uses indices 1 through N-1; radial
q uses 1 through N-2; periodic theta uses 0 through N-1. Phi and q subtract
their offsets before division by N-1; theta adds its offset before division by
N. Phi is then multiplied by pi/2 and theta by 2*pi. Offsets must be finite
and in `[0, 1)`. All sampled points stay in the declared bend parameter domain.
Zero offsets reproduce the original grid; positive offsets supplement it.

The grids are not nested. Neither collision counts nor maximum sampled
penetration need increase at every step. Any detected collision is retained
in the aggregate conclusion, even if another grid misses it. Agreement across
the tested grids is not labeled convergence or certified clearance.

## Reproduced measurements

For shell gap 3.0 and bend margin 0.05:

| Grid counts | Offsets | Detected collisions | Maximum sampled penetration |
| --- | --- | --- | --- |
| 13, 5, 24 | 0, 0, 0 | 0 | 0 |
| 13, 5, 24 | 0.5, 0.5, 0.5 | 2 | 0.193804783611 |
| 21, 9, 48 | 0, 0, 0 | 2 | 0.196083874454 |
| 21, 9, 48 | 0.5, 0.5, 0.5 | 2 | 0.191137010025 |
| 33, 13, 64 | 0, 0, 0 | 2 | 0.199165161707 |
| 33, 13, 64 | 0.5, 0.5, 0.5 | 2 | 0.199737812086 |

The coarse grid therefore misses an actual collision. Its uniform-similarity
classification can remain invariant while being wrong about continuous
clearance. Scale covariance and sampling reliability are different checks.

The wider candidates `(gap, margin) = (8.25, 0.005)` and `(30.0, 0.05)` have
no collision detected on any of these six grids. They remain candidates for
further investigation, not proven collision-free constructions.

Run `python -m src.toroidal_sampling_reliability` to reproduce the report.
Existing frontier, refinement, and similarity reports now expose sampling
provenance and the finite-sampling evidence boundary. Existing `collision_free`
API names remain compatibility labels meaning only no sampled detection.

## Next gate and inside-out candidate

Before optimizing a clearance frontier, check candidate endpoints under denser
and shifted sampling; a conservative geometric bound or certified intersection
method is still required for a continuous guarantee. Flower/Tree topology and
dormant-path semantics remain separate gates.

An inside-out deformation is a candidate for a later geometry experiment. Its
map, domain, and treatment of singularities must be stated first. Applying one
injective map to both intersecting volumes preserves their intersection;
removing a collision therefore requires a change of their relative geometry,
not merely a common coordinate inversion. Any proposed path rearrangement must
be checked along its deformation for collisions, valid Jacobians, and conserved
flux. This checkpoint introduces no such transformation or dynamics law.
