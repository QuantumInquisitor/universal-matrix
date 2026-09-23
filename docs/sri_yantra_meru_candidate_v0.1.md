# Explicit Meru candidate: conical graph control v0.1

This engine candidate gives actual spatial vertices and complete edge paths to
the computed Huet complex. Its height profile is a stated modelling choice.
It does not claim to reconstruct a historical Meru metric or a solid volume.

## Surface and edge rule

For a planar point (x,y), choose center c, radius R, horizontal scale s>0,
and height H>=0. With rho = sqrt((x-c)^2+y^2)/R, use

`L(x,y) = (s*(x-c), s*y, H*(1-rho))`.

The default Huet disk has c=0.5, R=0.5, s=1 and H=1. Every arrangement
vertex lies in this disk. H=0 recovers the flat control. Each edge is the
image of its complete planar segment under L. Each face is the image of its
planar region, including its boundary. Faces need not be flat Euclidean
triangles in three dimensions.

Horizontal projection followed by division by s and translation by c is a
continuous inverse. Consequently this graph surface is injective: no new edge
crossing, collapsed chamber, or lost incidence can occur for these admissible
metrics. The conical apex is not differentiable, but this does not invalidate
the continuous inverse. The horizontal area factor is s^2>0; the surface
cannot collapse a positive-area planar face. Zero horizontal scale is rejected.

Reflection of the original drawing, (x,y)->(x,-y), becomes (X,Y,Z)->(X,-Y,Z).
This is the drawing's axial mirror; it is not a claim of central inversion
symmetry of the raised cone.

## A detected failure of a different edge rule

Lifting only the 27 root corners and joining each root with straight spatial
segments changes the construction. At every projected arrangement vertex, the
audit interpolates height independently along each incident root chord. Any
nonzero spread means those chords fail to meet in space despite meeting in
projection.

At default height H=1, 53 of the 69 projected vertices fail this concurrency
check. The maximum height spread is 0.796 in the candidate's dimensionless
height units. The spread scales linearly with H; at H=0 every spread is zero.
Thus a visually correct projection is insufficient evidence for spatial
incidence. Even straight chords between consecutive lifted arrangement nodes
generally depart from the cone, though their shared endpoint IDs remain shared.

## Computed contract and verification

The surface lift retains all 69 vertices, 142 atomic edges, 74 bounded faces,
and 43 selected chambers. The outer-to-inner circuits remain 14,10,10,8,1.
Tests recover every vertex and samples of every edge, check mirror action,
and re-extract the projected generators to compare all edges, face boundaries,
and chamber contacts. They cover four height/scale choices, the root-chord
failure audit, invalid inputs, and off-surface points.

```sh
python -m src.sri_yantra_meru_candidate
python -m pytest -q tests/test_sri_yantra_meru_candidate.py
```

The projection identity establishes topology for this explicit family; finite
numerical tests check implementation. It does not settle incidence for stepped,
polyhedral, historically sourced, or other independently constrained Meru forms.
A model requiring planar triangular facets must supply compatible heights and
shared subdivisions instead of silently replacing the edge rule.

## Next gate

Use an explicitly chosen spatial domain for the toroidal field. Specify its
flux measure, conservation law, and mirror action before coupling it to the
Yantra graph. The geometry alone assigns no physical content or energy units.
