# Huet Reference Sri Yantra Planar Coordinates v0.1

## Purpose

The sourced Chiodo concurrency contract specifies how the nine maximal
triangles must meet. This checkpoint turns those relations into executable
planar coordinates for the Huet parameter choice quoted by Chiodo.

## Coordinate convention

Following Chiodo's construction figures, the right half of the Sri Yantra is
rotated anticlockwise by ninety degrees.

The common symmetry axis becomes the normalized diameter

OT = [0,1].

Each maximal isosceles triangle is represented by:

- an apex coordinate on OT;
- a base-point coordinate on OT;
- the slope of its upper leg.

Reflection across OT supplies the lower half.

## Input parameters

The input is the Huet choice quoted in Chiodo's footnote 20:

P = 0.332
Q = 0.537
R = 0.602
S = 0.835.

These are the base points of t3, t6, t7, and t9.

## Reconstruction

Triangles t3 and t7 are first placed on the common circle having OT as
diameter.

The remaining apex positions follow Chiodo condition (ii).

The twelve condition-(iii) concurrencies then determine the remaining slopes
and base positions.

The admissible branch is selected by the condition that the base of t1 lies
between O and the base of t3. For the Huet reference this branch is unique.

## Recovered base coordinates

The numerical reconstruction gives approximately:

t1  0.1130433243

t2  0.2308072497

t3  0.3320000000

t4  0.3961210639

t5  0.4487673715

t6  0.5370000000

t7  0.6020000000

t8  0.7351531571

t9  0.8350000000

The ordering agrees with Chiodo's t1-through-t9 base convention.

## Verification

The implementation checks:

- all nine triangles have positive half-height;
- all seven apex-to-base incidences close;
- all twelve three-line concurrencies close to better than 1e-11;
- t3 and t7 lie on the same normalized circumcircle;
- all 27 finite maximal-triangle edge segments are generated.

## Evidence boundary

This is an algebraic numerical reconstruction of Chiodo's published
concurrency conditions for the Huet parameter choice.

It is not yet a literal software replay of every straightedge-and-compass step
or the nested Apollonius construction.

It also does not identify every one of the traditional 43 subsidiary
triangles.

## Next gate

Use these 27 exact-concurrency edge segments to reconstruct Huet's concentric
triangle circuits and derive the traditional ring counts

14 + 10 + 10 + 8 + 1 = 43

from geometry rather than from stored metadata.

A generic polygonization of every line segment is not an acceptable substitute,
because the traditional 43 circuits are a selected concentric triangle
structure rather than simply the set of all planar faces.
