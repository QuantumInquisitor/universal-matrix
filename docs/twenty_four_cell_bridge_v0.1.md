# 24-Cell Bridge v0.1

## Decision

The regular 24-cell earns a separate geometry layer because it is generated in
two independent exact ways from structures already present in the engine:

1. top-down, as the common-radius union of the tesseract and its dual 16-cell;
2. bottom-up, from the directed edge roots of either tetrahedron in the stella
   octangula.

It is not introduced as a new register and is not assigned a physical or
cosmological identity.

## Common-radius construction

Use integer coordinates at squared radius four. The tesseract contributes its
sixteen vertices

`(±1, ±1, ±1, ±1)`.

The radius-matched 16-cell contributes eight vertices

`(±2, 0, 0, 0)` and permutations.

The two sets are disjoint and their union contains exactly 24 points. This is a
standard coordinate realization of the regular 24-cell. It makes the 24-cell
an integration carrier for the dual 4D pair already accepted by the previous
bridge, rather than an unrelated form selected for its number.

## Micro-to-whole construction from one tetrahedron

Either parity tetrahedron in the stella has six undirected edges and twelve
directed edge roots. After dividing cube-coordinate differences by two, those
roots are exactly the permutations of

`(±1, ±1, 0)`.

They form the twelve-vertex cuboctahedral A3 root system. Both tetrahedra
produce the same root set, so the construction does not privilege one member
of the mirrored compound.

Every root has squared norm two. For every ordered pair `u, v`, take the
unnormalized even Clifford product

`E(u, v) = (u cross v, u dot v)`.

Across all 144 ordered pairs, the distinct results are exactly the 24 vertices
above. The local directed relationships of either tetrahedron therefore
generate the complete four-dimensional carrier.

## Incidence contract

The implemented vertex set derives the full boundary counts rather than
inserting them as metadata:

| Element | Count |
| --- | ---: |
| vertices | 24 |
| edges | 96 |
| triangular faces | 96 |
| octahedral cells | 24 |

Each vertex has eight incident edges and belongs to six octahedral cells. Each
cell has six vertices, twelve edges, and eight triangular faces. The boundary
satisfies the four-polytope Euler relation

`V − E + F − C = 24 − 96 + 96 − 24 = 0`.

The 24 facet normals are the signed coordinate permutations of
`(1, 1, 0, 0)`, the D4 root system. Each supporting equation `normal dot x = 2`
selects one six-vertex octahedral cell. This vertex/facet pairing is the
coordinate expression behind the 24-cell's self-duality.

## Projection into the existing engine

Dropping W produces fifteen unique XYZ positions:

- the eight stella cube vertices, each with multiplicity two from `±W`;
- the six axial gate directions at radius two, each with multiplicity one;
- the center, with multiplicity two from the `±W` 16-cell tips.

The projection therefore contains the existing cube/stella, gate octahedron,
and center in one exact image. Multiplicity is retained and is not silently
converted into a new physical state count.

## Mirror and triality

Four-dimensional central inversion preserves the full vertex, edge, face, and
cell structure and exchanges each facet with its opposite.

The 24-cell also has an extra Hadamard involution not contained in the 384
signed axis frames. It exchanges the radius-matched 16-cell with one
demitesseract parity class while preserving the other class as a set. Together
with signed axis operations, this triality transformation generates exactly
1,152 vertex symmetries, the full 24-cell symmetry order.

This is a precise form of three-way structural interchange among three
eight-vertex 16-cell subsets. It is not identified with a physical trinity
without a separate observable law.

## Why the 600-cell still waits

The same published spinor framework continues from the A3 roots and 24
spinors to H3 and 120 spinors, producing the 600-cell. The 600-cell is therefore
a legitimate mathematical continuation. It is not yet an engine layer because
no current local structure has been shown to supply the required H3 root set
without inserting an icosahedral assumption.

## Source ledger

1. H. S. M. Coxeter, “Regular and Semi-Regular Polytopes I,” *Mathematische
   Zeitschrift* 46, 380–407 (1940), DOI 10.1007/BF01181449.
2. Pierre-Philippe Dechant, “Platonic solids generate their four-dimensional
   analogues,” *Acta Crystallographica A* 69, 592–602 (2013),
   DOI 10.1107/S0108767313021442. The paper derives 24 spinors from the A3
   root system and identifies them with the 24-cell/D4 root system.
