# Recursive 22-body material placement envelope

The Seed/Vesica correspondence audit established three symmetry-related mirror-closed binary
container slices whose scales match the tested material tree. It did not establish that the
22-body material specimen physically fits inside those vessels or that the existing local-frame
connector can be used unchanged after spatial separation.

This checkpoint audits those questions without selecting an arbitrary physical size ratio.

## Vessel-to-module ratio

Let the root material module use its existing 0.1 m geometric length parameter. Let the root
Seed-axis vessel radius be k times that module length. Because both the module geometry and the
candidate vessel tree scale by one half at every material level, the same dimensionless k applies
at all depths.

The report evaluates the full declared fold-state grid:

- material scale coordinate 0.9, 1.0, 1.1;
- fold angle 0, pi/12, pi/6.

It solves for the minimum k required by:

1. planar containment of every source body vertex inside its local circular vessel;
2. a 3D spherical bound on every source vertex;
3. conservative sibling bounding-sphere non-overlap;
4. conservative non-overlap across all 15 simultaneous recursive modules.

The sphere tests are sufficient conservative separation conditions, not exact body collision
certificates. No physical value of k is selected by this audit.

## Recursive orientation

Within each parent vessel, the two children use opposite body orientations separated by pi about
the Seed-plane normal. The same rule is applied recursively. Corresponding sibling body vertices
must therefore be central mirrors in the Seed plane while retaining the same out-of-plane
coordinate.

All three Seed-axis candidates are rotated back to a common reference and compared body vertex by
body vertex. Equality establishes only rigid-rotation equivalence of the candidate placements; it
does not select a canonical physical axis.

## Spatial connector compatibility

The existing recursive connector was validated in module-local coordinates with no physical
translation between module origins.

After Seed-axis placement, every parent-child center separation is one half of the parent vessel
radius. Therefore a physical connector requires a nonzero geometric rest offset equal to

k/2 times the parent module length.

At the reference state the existing mapped port displacement is zero, so this translation is not
present in the current connector state.

There is a second issue. Mirror-closed placement rotates one child branch by pi relative to its
parent. For the co-oriented branch, the current local port delta and a rest-corrected spatial
delta agree. For the mirrored branch, the child port vector changes orientation. A physical
spatial adapter must therefore either transform the child attachment frame into the parent frame
or explicitly decouple connector attachment orientation from the body mirror orientation.

This is a geometry/attachment mapping problem, not evidence for a new recursive force law.

## Limits

The audit uses source midsurface vertices, bridge endpoints and hub markers. It does not include
body thickness or exact mesh-mesh contact. The conservative bounding-sphere test can certify
separation when satisfied but cannot prove collision when it fails.

No common vessel/module size ratio is selected, no Seed axis is made canonical, and no spatial
connector rest/attachment adapter is added in this checkpoint.
