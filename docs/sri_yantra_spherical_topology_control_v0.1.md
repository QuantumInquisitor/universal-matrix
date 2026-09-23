# Sri Yantra Spherical Topology Control v0.1

## Purpose

The repository now has a derived forty-three-chamber planar incidence complex.

Before comparing that complex with a historically sourced spherical Sri Yantra,
we need a control experiment:

What happens if the exact planar complex is lifted onto a sphere by a known
homeomorphism?

This checkpoint supplies that control.

It is deliberately not presented as C. S. Rao's spherical Sri Yantra.

## Construction

The selected Huet chamber vertices are first translated along the planar
symmetry axis and uniformly scaled so they lie strictly inside an open disk of
radius 0.9.

The normalized planar point

(u,v)

is then sent to the unit sphere by inverse stereographic projection:

\[
X=\frac{2u}{1+u^2+v^2},
\]

\[
Y=\frac{2v}{1+u^2+v^2},
\]

\[
Z=\frac{1-u^2-v^2}{1+u^2+v^2}.
\]

Because the selected chamber vertices remain inside the unit disk, all selected
vertices lie in the open northern hemisphere.

The inverse chart is

\[
u=\frac{X}{1+Z},
\qquad
v=\frac{Y}{1+Z}.
\]

## Edges are lifted as complete paths

A chamber edge is not replaced by a straight three-dimensional chord or by a
great-circle arc.

Every point of the original planar line segment is mapped through the same
inverse-stereographic chart.

This matters because inverse stereographic projection is a homeomorphism. It
therefore preserves:

- distinct vertices;
- edge incidence;
- edge intersections and non-intersections;
- chamber boundaries;
- cyclic enclosure order;
- the complete 43-chamber adjacency structure.

The control answers a topology question, not a metric one.

## Mirror law

The Huet reconstruction is reflected in the rotated planar coordinate by

\[
(x,y)\mapsto(x,-y).
\]

The normalization does not translate the y coordinate. Under the spherical
control this becomes

\[
(X,Y,Z)\mapsto(X,-Y,Z).
\]

The implementation verifies this equivariance at every arrangement node.

## Verified invariants

The spherical control preserves:

- 43 selected chambers;
- enclosure counts 1, 8, 10, 10, and 14;
- enclosure vertex counts 3, 16, 20, 20, and 28;
- 129 distinct chamber edges;
- all chamber-to-vertex incidence IDs;
- all four noncentral ring-cycle member sets;
- the planar mirror involution.

Every spherical node also roundtrips through the inverse chart to the original
planar coordinate.

No topology change is detected.

## Why this is not Rao's spherical form

C. S. Rao's 1998 construction does not take an existing planar drawing and
homeomorphically bend it onto a sphere.

Rao formulates a new spherical triangular complex using great-circle arcs and
spherical trigonometry. The construction uses six basic angular variables

b, c, d, e, g, h

and derives the remaining intersection geometry from spherical right-triangle
relations. Rao then imposes selected sets of nonlinear geometric constraints,
including concurrency, concentricity, equilateral root/secondary triangles,
equal base arcs, midpoint conditions, and radial equalities.

That is a different mathematical problem.

## Why both models are useful

The topology control establishes a baseline:

If a later Rao implementation changes chamber incidence, that change is not
caused merely by embedding the same planar graph in three dimensions or on a
curved surface.

It is caused by rebuilding the geometry with different spherical metric and
great-circle constraints.

This gives the engine a meaningful A/B comparison:

1. homeomorphic spherical lift, topology forced to remain unchanged;
2. sourced spherical reconstruction, topology determined by the spherical
   equations themselves.

## Evidence boundary

This control is an exact topological construction up to ordinary floating-point
evaluation of a closed-form homeomorphism.

It does not claim:

- historical authenticity;
- great-circle chamber edges;
- Rao's parameter values;
- a Sri Meru metric;
- physical curvature;
- extra physical dimensions.

## Next gate

Implement Rao's sourced spherical geometry as its own subsystem.

The implementation should begin with one published parameter row and reproduce:

- the nine root-triangle base points;
- the derived transverse intersections;
- the selected six nonlinear constraint residuals;
- the circumcircle and symmetry-arc geometry.

Only after Rao's own spherical root complex closes numerically should its
derived chamber incidence be compared with the forty-three-chamber Huet planar
complex and the homeomorphic topology control.

## Primary source

C. S. Rao, "Sriyantra - A Study of Spherical and Plane Forms",
Indian Journal of History of Science 33(3), 1998, 203-227.
