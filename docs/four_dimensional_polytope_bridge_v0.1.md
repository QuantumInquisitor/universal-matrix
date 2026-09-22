# Four-Dimensional Polytope Bridge v0.1

## Decision

The regular 16-cell and its dual, the tesseract or 8-cell, are the strongest
first extension of the engine into four-dimensional geometry. They are added
as exact dimensionless coordinate structures. The fourth coordinate is named
`W`; it is not identified with time, Ether, consciousness, a hidden physical
dimension, or any other ontology in this contract.

## Why this pair fits

The current three-dimensional construction starts from the eight cube vertices
`{−1, +1}^3`. Product parity divides them into two regular tetrahedra, producing
the stella octangula.

The same construction continues one dimension higher. The sixteen tesseract
vertices are `{−1, +1}^4`. Product parity divides them into two eight-vertex
demitesseracts. A normalized order-four Hadamard transform maps each parity
class bijectively onto the vertices

`(±1, 0, 0, 0)` and permutations,

which are the regular 16-cell. The transform uniformly reduces all distances
by a factor of two. It is a similarity, and becomes an isometry after applying
that one global scale factor. No incidence or angular relation is changed.

Thus the exact ladder is:

| Dimension | Hypercube vertex set | Parity half | Compound carrier |
| ---: | --- | --- | --- |
| 3 | 8 cube vertices | 4-vertex tetrahedron | two tetrahedra |
| 4 | 16 tesseract vertices | 8-vertex 16-cell | two 16-cells |

Fixing `W = +1` or `W = −1` gives two opposite cubic cells of the tesseract.
Dropping W from either cell recovers the existing eight stella vertices
exactly. The present engine therefore becomes a literal three-dimensional
slice of the new structure rather than being replaced by it.

## Six gates, center, and the Seed projection

The 16-cell has four antipodal vertex pairs. Orthographically dropping W sends
three pairs to the six existing axial gate coordinates

`(+X, −X, +Y, −Y, +Z, −Z)`.

The remaining pair, `+W` and `−W`, projects twice onto the origin. Projecting
that XYZ image once more along `(1, 1, 1)` sends the six gates to a regular
hexagon. After uniform normalization, its seven unique image points are exactly
the same center-plus-six-neighbor Seed layout produced by the stella projection.

This supplies a commuting geometric chain:

`4D 16-cell -> 3D six gates plus doubled center -> 2D Seed centers`.

The double occupancy at the center is retained as projection multiplicity. It
is not counted as two visible Seed centers and is not assigned a physical
meaning without a later law.

## Construction from the local gates upward

The bridge is bidirectional. It does not require assuming the large form and
only projecting downward. Treat the six gate vectors as the axial roots
`±e1`, `±e2`, and `±e3`. The even Clifford product of any ordered pair splits
into its scalar and oriented bivector parts. In the implemented coordinate
convention this is

`gate_product(u, v) = (u cross v, u dot v)`.

The first three components are XYZ and the scalar component is W. Parallel or
antiparallel gate pairs therefore produce the two `±W` tips that project to the
center. Orthogonal gate pairs produce the six `±X`, `±Y`, and `±Z` tips.

Across all 36 ordered gate pairs, there are exactly eight distinct results:

`(±1, 0, 0, 0)` and permutations.

Those are all vertices of the 16-cell. Applying the inverse Hadamard map to
those eight local products at parity `+1` and parity `−1` reconstructs every
one of the sixteen tesseract vertices. The tested upward chain is therefore

`six local gates -> eight 16-cell vertices -> sixteen tesseract vertices`.

Together with the downward projection, this supplies a micro-to-whole and
whole-to-micro consistency loop. It is a finite geometric identity, not yet a
claim that physical scales literally grow by this operation.

## Register extension

Ordered pairs of the sixteen tesseract vertices form a 256-address experimental
hyper-register. It decomposes exactly into four 64-address sheets selected by
the W signs of the first and second vertices:

`256 = 64 × 2 × 2`.

No current 64-address information is changed. Each sheet is a bijective copy of
the existing register. The four-bit relative-distance shells are

| Differing axes | Pair count |
| ---: | ---: |
| 0 | 16 |
| 1 | 64 |
| 2 | 96 |
| 3 | 64 |
| 4 | 16 |

This is the next binomial shell pattern after the current three-bit
`8, 24, 24, 8` decomposition.

## Mirror behavior changes with dimension

Central inversion remains

`M(x, y, z, w) = (−x, −y, −z, −w)`.

It is still an involution and gives the exact hyper-address law

`M256(a) = 255 − a`.

It exchanges the two fixed-W cube slices while reducing to the existing 3D
central mirror on XYZ. It preserves each 16-cell parity class because four sign
changes leave coordinate-product parity unchanged.

There is an important dimensional distinction. The determinant of central
inversion is `−1` in three dimensions but `+1` in four dimensions. It reverses
orientation in 3D and preserves orientation in 4D. “Mirror” here therefore
means point inversion, not necessarily a handedness-reversing plane reflection.

The signed-permutation group grows from `2^3 × 3! = 48` spatial frames to
`2^4 × 4! = 384` four-dimensional frames, evenly divided into 192 proper and
192 orientation-reversing frames. All 48 existing frames embed exactly by
fixing W.

## Candidate grading

| Four-dimensional candidate | Exact relevant structure | Decision |
| --- | --- | --- |
| 16-cell plus tesseract | Six gates, doubled center, stella cube slices, parity compound, mirror, and 64-sheet extension | Implement now |
| 24-cell | Unique self-dual regular 4-polytope with 24 vertices and octahedral cells; closely related to D4 and F4 | Research next, no canonical engine address yet |
| 600-cell | 120 vertices and 600 tetrahedral cells; strong recursive tetrahedral geometry | Hold until an exact map to present state variables exists |
| 5-cell | Four-dimensional simplex with five vertices | No present Seed, gate, or register fit |
| 120-cell | Dual of the 600-cell with dodecahedral cells | No present exact bridge |

The 24-cell and 600-cell remain mathematically important. Their counts alone do
not justify adding state variables.

## Published mathematical context

H. S. M. Coxeter's classification provides the regular and semiregular polytope
framework. Pierre-Philippe Dechant gives a particularly relevant construction:
three-dimensional root systems generate four-dimensional root systems through
spinors. In the simplest case, the six vectors of the octahedral root system
generate eight spinors which become the vertices `(±1, 0, 0, 0)` and
permutations of the 16-cell. The same paper distinguishes the 24-cell/F4 and
600-cell/H4 extensions.

That published result is mathematical support for the dimensional bridge. It
does not establish that physical spacetime or the Omniverse has this geometry.

## Source ledger

1. H. S. M. Coxeter, “Regular and Semi-Regular Polytopes I,” *Mathematische
   Zeitschrift* 46, 380–407 (1940), DOI 10.1007/BF01181449.
2. Pierre-Philippe Dechant, “Platonic solids generate their four-dimensional
   analogues,” *Acta Crystallographica A* 69, 592–602 (2013),
   DOI 10.1107/S0108767313021442.
