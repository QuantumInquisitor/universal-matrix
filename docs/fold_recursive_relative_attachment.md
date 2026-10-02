# Recursive relative attachment-frame search

The single-marker correspondence search found many state-independent anisotropic linear readouts
of the abstract two-component connector port, but no literal scaled-orthogonal projection of any
single panel vertex, bridge endpoint or hub marker.

A physical attachment is more naturally represented by a structural vector between two material
markers. This checkpoint therefore searches every unordered pair of the 58 existing source
markers, for 1,653 candidate relative segments.

## Fixed geometry only

For candidate markers a and b, the source vector is

r(q) = x_b(q) - x_a(q).

The reference vector r(Q0) is subtracted before comparing with the abstract mapped-port
displacement. The Jacobian of the relative vector is likewise compared with the mapped-port
Jacobian.

One fixed 2x3 transform is fitted on an independent state grid and validated on separate state and
scale grids. No state-dependent transform is allowed.

## Acceptance hierarchy

Three levels are kept distinct:

1. fixed linear match: algebraically reproduces the port within the predeclared displacement and
   Jacobian tolerances;
2. scaled-orthogonal match: the fixed transform is also a uniform scale times an orthogonal
   two-dimensional projection;
3. unit-orthogonal match: the projection scale is one.

Only levels 2 and 3 count as candidate literal geometric attachment frames. An anisotropic linear
map remains a reduced-coordinate readout.

## Interpretation

If a scaled-orthogonal relative-marker candidate exists, it becomes a geometry-derived physical
attachment-frame candidate to test against the Seed-axis rest offset and mirrored branch
orientation.

If none exists, then the existing 22-body source geometry does not contain a literal connector
port under either single-marker or relative-marker rigid projection. The connector should remain
an abstract generalized port until a separately justified attachment geometry is introduced.

No candidate is selected solely because it has the smallest least-squares error.
