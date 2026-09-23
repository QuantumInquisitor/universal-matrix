# Rao Spherical Sri Yantra Reference v0.1

## Purpose

The repository now has two very different spherical concepts:

1. a homeomorphic topology-control lift of the derived Huet planar chambers;
2. C. S. Rao's historically published spherical triangular construction.

They must not be conflated.

This checkpoint begins the second path by reproducing one of Rao's published
spherical parameter solutions directly from the paper's equations.

## Rao's spherical construction

Rao places the triangular complex on a sphere and uses great-circle arcs rather
than taking a finished planar drawing and bending it onto a curved carrier.

The formulation uses six independent angular variables in radians:

b, c, d, e, g, h.

If r is the angular radius of the base circle, Rao gives

r + h = pi/2

and

r = a + b + c = d + e + f.

The remaining intersection arcs are derived through spherical right-triangle
relations.

The code implements the chain needed by Rao equations 2.3 through 2.44 for the
selected reference constraints.

## Published Table 1 checkpoint

Rao Table 1 publishes several constrained spherical figures.

This implementation uses the row whose selected constraints are

1, 2, 4, 5, 10, 19.

The six printed basic variables are:

| variable | radians |
| --- | ---: |
| b | 0.231687 |
| c | 0.120012 |
| d | 0.146680 |
| e | 0.230471 |
| g | 0.053009 |
| h | 1.076084 |

Those values are encoded exactly as printed to six decimal places.

No nonlinear solve is performed to improve them before the validation.

## Implemented constraint residuals

The checkpoint evaluates the following sourced conditions.

### F1: concurrency closure

The two constructions of point 11 must agree:

F1 = x11 - x11a.

### F2: concentricity

The incircle of the innermost secondary triangle must be concentric with the
circumscribing circle:

F2 = d - U7 - rT.

### F4: equilateral root triangle at P2

The spherical equilateral condition is evaluated using Rao equation 3.4.

### F5: equal base arcs

F5 = x10 - x13.

### F10: equal intercepts

F10 = b + c - d - 2g - v8.

### F19: equal radial distances

F19 = r17 - r19.

## Numerical result

Using only the rounded values printed in Rao's table, the implementation
recovers all six selected residuals below 1e-6.

The largest residual is about 3.2e-7.

That is consistent with the loss of precision expected when a nonlinear
solution is published only to six decimal places.

The checkpoint therefore reproduces a sourced spherical solution rather than a
visual approximation.

## Relationship to the topology control

The topology-control sphere and Rao sphere answer different questions.

The topology control asks:

Can the complete planar 43-chamber graph be placed on a sphere without changing
its topology?

Yes. A homeomorphism guarantees that.

Rao asks:

What spherical triangular complexes arise when the generators themselves are
great-circle arcs constrained by spherical trigonometry?

That is a new metric construction. Its chamber incidence must be derived
rather than assumed.

## Scope of the original parameter checkpoint

The following limits describe the original parameter-only checkpoint. The
subsequent `sri_yantra_rao_great_circles_v0.1.md` derives explicit coordinates,
great-circle edges, and the complete graph for this reference row. It records
a corrected transcription of equation 2.41 and a geometric correction to
printed equation 2.22. Literal `x16` remains available for the source audit.

## Original evidence boundary

This checkpoint verifies one published six-constraint spherical parameter row.

It does not yet:

- build Cartesian unit-sphere coordinates for every Rao point;
- reconstruct every great-circle root-triangle arc;
- derive the spherical 43-chamber graph;
- prove topological equivalence with the Huet planar construction;
- implement all twenty Rao constraint functions;
- reproduce every row in Rao Tables 1 and 2.

Those are later gates.

## Next gate

Convert the sourced arc variables into explicit unit-sphere point and
great-circle representations.

The next implementation should reconstruct the nine spherical root triangles
for this reference row, then derive their intersection graph directly.

Only after that graph exists should it be compared against:

- the Huet planar 43-chamber complex;
- the homeomorphic spherical topology control.

## Primary source

C. S. Rao, "Sriyantra - A Study of Spherical and Plane Forms",
Indian Journal of History of Science 33(3), 1998, 203-227.
