# H3 to 600-cell bridge v0.1

## Decision

The 600-cell is admitted as an exact experimental geometry layer because it is
now generated bottom-up from the complete Platonic-solid contract rather than
inserted for its count or appearance.

This closes the mathematical test that previously held the 600-cell back. It
does not establish that physical spacetime or an Omniverse literally has
600-cell geometry.

## H3 roots from the icosahedron

The exact icosahedron has 30 edges. For every edge with endpoints `u` and `v`,
take its midpoint direction and normalize it:

`alpha = (u + v) / (2 phi)`.

The resulting 30 vectors:

- have exact unit norm in `Q(phi)`;
- occur in 15 antipodal pairs;
- are closed under reflection in every root hyperplane;
- form the H3 root system, geometrically the vertices of an
  icosidodecahedron.

Thus H3 is derived from the newly completed icosahedral layer. It is not
created by padding a list to 30 entries.

## Spinor induction

For every ordered root pair `u, v`, the even Clifford product is represented in
the engine's established convention as

`S(u, v) = (u cross v, u dot v)`.

Across all 900 ordered pairs there are exactly 120 distinct unit spinors. They
are closed under quaternion multiplication and form the binary icosahedral
group. Interpreted as points on the unit 3-sphere in four-dimensional Euclidean
space, they are the 120 vertices of the regular 600-cell.

## Derived boundary

No boundary counts are inserted as metadata. The edge distance is derived as

`edge_squared = 2 - phi = 1 / phi^2`.

The resulting exact incidence is:

| Element | Count |
|---|---:|
| vertices | 120 |
| edges | 720 |
| triangular faces | 1,200 |
| tetrahedral cells | 600 |

Each vertex has 12 incident edges and belongs to 20 tetrahedral cells. Every
triangle belongs to two cells, and five tetrahedra meet at every edge. The
boundary satisfies `V - E + F - C = 0`.

The 600 tetrahedral cells are not the underspecified “64 tetrahedron grid.”
Those constructions have different counts and require a separate incidence
definition.

## Recovery of earlier layers

The construction is not only upward:

- the 30 vertices with `W = 0` recover the original H3 roots exactly;
- the existing common-radius 24-cell, normalized to the unit 3-sphere, is an
  exact 24-vertex subgroup;
- removing that 24-cell leaves 96 vertices, the vertex set associated with
  the snub 24-cell;
- the coordinate shells split as `8 + 16 + 96 = 120`.

This connects the earlier 16-cell, tesseract, 24-cell, and Platonic work to the
600-cell without changing their contracts.

## Mirror law

Central inversion preserves the complete vertex, edge, triangular-face, and
tetrahedral-cell sets. Mirroring one input root mirrors its spinor product;
mirroring both input roots leaves the product unchanged. These are separately
tested laws, not a metaphorical use of “mirror.”

## Published mathematical context

Pierre-Philippe Dechant proves that the 30 H3 reflections generate 120 rotors
and that their four-dimensional interpretation is the 600-cell/H4 root
system. The implementation independently reconstructs those finite sets and
their incidence using the engine's exact `Q(phi)` coordinates.

Source: P.-P. Dechant, “Platonic solids generate their four-dimensional
analogues,” *Acta Crystallographica A* 69 (2013), 592–602,
DOI 10.1107/S0108767313021442.

## Evidence boundary

This contract proves a mathematical H3-to-H4 construction. It does not prove
that the 600-cell is a material atom, a universe, a consciousness structure,
or the outer architecture of reality. Those interpretations require distinct
observable predictions and empirical tests.
