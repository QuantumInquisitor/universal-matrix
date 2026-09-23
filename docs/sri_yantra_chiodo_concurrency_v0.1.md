# Chiodo Sri Yantra Concurrency Contract v0.1

## Source

This checkpoint encodes the minimal planar concurrency conditions stated in
Alessandro Chiodo, "On the construction of the Sri Yantra", Comptes Rendus
Mathematique 359 (2021), 377-397, DOI 10.5802/crmath.163.

The paper proves a straightedge-and-compass construction for the family of
concurrent Sri Yantras satisfying these conditions.

## Triangle convention

Chiodo labels the nine maximal isosceles triangles t1 through t9 according to
the vertical position of their bases.

In this convention:

- t1 through t5 point downward;
- t6 through t9 point upward.

That matches the repository's existing five-down/four-up generator inventory.

## Condition (i)

Triangles t3 and t7 are inscribed in the same circumcircle.

## Condition (ii)

The apex of the first triangle is the base point of the second for these seven
ordered pairs:

(t8,t1)
(t6,t2)
(t9,t3)
(t1,t6)
(t5,t7)
(t4,t8)
(t2,t9)

## Condition (iii)

On each side of the symmetry axis, a leg of the downward triangle, the base of
the middle triangle, and a leg of the upward triangle concur for these twelve
ordered triples:

(t1,t2,t7)
(t2,t3,t7)
(t1,t3,t8)
(t1,t4,t6)
(t1,t5,t9)
(t4,t6,t9)
(t2,t7,t9)
(t3,t7,t8)
(t3,t8,t9)
(t4,t4,t8)
(t5,t5,t6)
(t2,t6,t6)

Repeated labels are meaningful because the same triangle can contribute both a
base and one of its legs.

## Four-parameter family

Up to rescaling and translation, Chiodo's construction is parametrized by four
ordered points P,Q,R,S on the normalized diameter OT=[0,1].

They are the base points of t3, t6, t7, and t9.

The paper then derives the remaining construction using straightedge operations
and one selected solution of a circle-line-point Apollonius problem.

For reproducibility, this module records the Huet values quoted by Chiodo:

P = 0.332
Q = 0.537
R = 0.602
S = 0.835

These values are an example inside the four-parameter family, not a claim that
one unique Sri Yantra is selected by the minimal concurrency conditions.

## What this adds to the engine

The repository now has a sourced constraint graph among all nine maximal
triangles.

This is stronger than the previous inventory-only model.

A concurrency relation among maximal triangles and a chamber contact are
different objects. The separate `src/sri_yantra_chambers.py` now derives the
Huet planar chamber graph numerically from the reconstructed coordinates.

## Subsequent checkpoints

The Huet coordinate solver reconstructs the concurrent reference
algebraically, without replaying every compass-and-straightedge operation.
The chamber extractor now derives the 43 selected triangles and their
circuits. See `docs/sri_yantra_huet_planar_v0.1.md` and
`docs/sri_yantra_chambers_v0.1.md`. General parameter-family and historical
spherical/Meru incidence equivalence remain open.
