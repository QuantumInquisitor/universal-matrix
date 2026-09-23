# Stella Octangula, 64 Register, and Hassium Correspondence v0.1

## Purpose and evidence boundary

This note separates four different kinds of statement:

1. exact geometry and software identities that can be proved in the repository;
2. published chemical or nuclear facts;
3. model-based scientific predictions;
4. proposed correspondences that are not evidence of a shared physical cause.

The separation is essential. A numerical or geometric match can justify a
testable adapter. It cannot by itself establish that the Universal Matrix is a
physical description of Hassium or of the Omniverse.

## Exact star-tetrahedron bridge

The unambiguous regular star tetrahedron, or stella octangula, is the compound
of two regular tetrahedra whose eight outer vertices are the eight vertices of
a cube. In coordinates, those vertices are all triples in `{−1, +1}^3`.
Coordinate-product parity divides them into two groups of four, and each group
is a regular tetrahedron.

The six edge midpoints of either tetrahedron are

`(+X, −X, +Y, −Y, +Z, −Z)`.

They are the vertices of the central octahedron and match the six canonical
boundary-gate directions exactly. This is a coordinate identity, not a visual
analogy.

The full signed-permutation symmetry of the three axes contains 48 frames.
Exactly 24 are proper rotations and 24 are reflected frames. This is the same
48-frame set already retained by the Sevenfold Seed bridge.

## Why the 64 register fits exactly

The star compound has eight outer vertices. An ordered pair of such vertices
has `8 × 8 = 64` possibilities. The current register can therefore be decoded
bijectively as a pair of three-bit stella vertices:

`address = 8 × first_vertex_index + second_vertex_index`.

This supplies a neutral mathematical carrier for the proposed eight light by
eight sound interpretation. Geometry establishes the 64 ordered pairs. It does
not establish that the first coordinate is physically light or that the second
is physically sound.

The 64 pairs have an exact relative-distance decomposition:

| Differing coordinate axes | Pair count |
| ---: | ---: |
| 0 | 8 |
| 1 | 24 |
| 2 | 24 |
| 3 | 8 |

Every one of the 48 signed frames induces a distinct permutation of the 64
addresses while preserving these distance shells. The existing projection
from 108 core states still has its established collision pattern: 44 register
addresses receive two core states and 20 receive one.

## One mirror tested across representations

For this contract, “mirror” has a precise meaning: central inversion through
the shared origin,

`M(x, y, z) = (−x, −y, −z)`.

This is a point reflection, not an arbitrary plane reflection. It has
determinant `−1`, exchanges the two tetrahedra, sends every boundary gate to
its opposite, and satisfies `M(M(v)) = v` exactly. With the canonical
three-bit vertex encoding, antipodal vertices have complementary indices.
Mirroring both vertices in a register pair therefore gives the exact address
law

`M64(a) = 63 − a`.

The mirror preserves every pair's relative signature and Hamming-distance
shell. Its 64-address permutation is also exactly the action of the
all-axis-reversing member of the 48 signed frames.

The same half-turn is now applied independently at every level of a nested
Vesica address. The Seed center remains fixed, ring positions `1, 2, 3` swap
with `4, 5, 6`, spoke overlaps remain spokes, and ring overlaps remain ring
overlaps. Mirroring a parent and then entering the mirrored child is identical
to entering a child and mirroring the resulting address. This is a testable
self-similarity rule rather than a visual resemblance.

This discrete mirror complements the existing spiral-cone reciprocal mirror
`u -> −u`. They are two defined actions on different state spaces and are not
silently treated as the same physical operation.

## Flower of Life as a projection hypothesis

There is an exact geometric result behind the proposed “shadow” idea. View the
stella octangula along the cube body diagonal `(1, 1, 1)` and orthographically
project onto the perpendicular plane. The two opposite tips on that viewing
axis coincide at the projected center. The other six tips form a regular
hexagon. After one uniform rescaling, the seven unique projected points are
exactly a center plus six equally spaced neighbors, the circle-center layout
of a Seed of Life.

The six vertices of the internal octahedron project to a second, aligned
regular hexagon at exactly half the outer radius. Thus the compound contains a
literal inner/outer two-scale hexagonal relation in this projection. Central
inversion commutes with projection: projecting a mirrored point gives the
planar opposite of the original projection.

What the projection proves is a seven-point center geometry. Circles do not
appear automatically. Drawing equal circles on those centers produces the
Seed construction, and continuing the same hexagonal circle lattice produces
a Flower of Life pattern. That continuation is a defined geometric
construction and a promising model hypothesis, not evidence that the Flower
is physically emitted as a shadow by an Omniverse structure.

## Sri Yantra relation after dimensional expansion

The multidimensional Sri Yantra contract supplies another exact local bridge:
a regular triangle is the two-dimensional centered-simplex template, a regular
tetrahedron is its three-dimensional successor, and the positive/negative
three-dimensional templates form an eight-vertex stella compound under
central inversion.

This explains how triangular orientation can expand into a star-tetrahedral
volume without treating a flat image as fundamental. It does not identify the
complete Sri Yantra with one stella. The former retains nine source triangles
in a four-upward/five-downward inventory; the latter contains two tetrahedra.
An exact placement and incidence law for all nine lifted generators is still
required. See `docs/sri_yantra_multidimensional_v0.1.md`.

## The phrase “64 tetrahedron grid” remains underspecified

Online diagrams called a “64 tetrahedron grid” do not provide one universally
standardized mathematical object. Different presentations can count solid
tetrahedra, star compounds, visible cells, or projected triangles differently.
The engine should not silently choose one.

To add a literal 64-tetrahedra complex, the next input must specify an exact
vertex set, 64 tetrahedral cells as four-vertex incidence tuples, shared-face
adjacency, orientation, boundary, and scale rule. Until then, the implemented
claim is the exact `8 × 8 = 64` stella-vertex register bridge.

## Hassium facts and correspondences

### Established or conventionally tabulated

Hassium has atomic number 108, lies in group 8 and period 7, and is commonly
listed with electron configuration `[Rn] 5f14 6d6 7s2`. Only very small numbers
of atoms have been produced, so a bulk elemental crystal shape is not an
experimental basis for this bridge.

Chemical experiments formed and detected Hassium tetroxide, `HsO4`, supporting
Hassium's placement with the group 8 elements. The tetrahedral molecular
geometry of `HsO4` is a theoretical molecular result. It is not the shape of a
Hassium atom, its nucleus, or a macroscopic Hassium crystal.

### Exact arithmetic within published models

The conventional principal-shell population is listed as
`2, 8, 18, 32, 32, 14, 2`.

Therefore:

* the seven shell populations sum to 108;
* the two consecutive 32-electron populations sum to 64.

For the especially studied isotope `270Hs`, `Z = 108` and `N = 162`, giving:

* `162 = 108 + 54`;
* `270 = 108 + 162 = 2 × 108 + 54`.

A relativistic mean-field study describes `270Hs` as a candidate deformed
doubly magic nucleus at `Z = 108` and `N = 162`. Among the higher-order terms
examined, its `beta_6` deformation had the greatest calculated effect. Nuclear
physics calls a rank-six deformation hexacontatetrapole, or 64-pole. A 64-pole
spherical-harmonic term is not a structure made from 64 tetrahedra.

## What is genuinely notable

The correspondences are unusually layered:

* 108 is both the canonical core size and Hassium's proton number;
* 64 is both the projection-register size and the sum of two listed 32-electron
  shell populations;
* `270Hs` introduces the already canonical 54 through `162 = 108 + 54`;
* a rank-six, 64-pole deformation is especially important in published models
  near `270Hs`;
* predicted `HsO4` molecular geometry is tetrahedral;
* the exact star-tetrahedron symmetry has the same 48 signed frames as the
  Seed-to-gate bridge.

That makes Hassium a disciplined candidate for a future correspondence study.
It does not yet make Hassium a validation of the engine.

## Falsifiable next step

Any physical Hassium adapter must predict an observable not inserted from the
same source used to build it. Candidate targets include an independently
calculated level ordering, isotope shift, transition amplitude, molecular bond
property, or deformation-sensitive quantity. The prediction must be compared
with conventional nuclear or relativistic electronic calculations and, where
available, experiment.

## Source ledger

1. Royal Society of Chemistry, Hassium fact box and chemistry overview,
   atomic number 108, group 8, period 7, and electron configuration.
2. Düllmann and collaborators, “Chemical investigation of hassium (element
   108),” Nature 418, 859–862 (2002), DOI 10.1038/nature00980.
3. Malli, “Dramatic relativistic effects in atomization energy and volatility
   of the superheavy Hassium tetroxide and OsO4,” Journal of Chemical Physics
   117, 10441–10443 (2002), DOI 10.1063/1.1527057.
4. Wang, Sun, and Zhou, “Microscopic study of higher-order deformation effects
   on the ground states of superheavy nuclei around 270Hs,” Chinese Physics C
   46 (2022), DOI 10.1088/1674-1137/ac3904.
5. Morton and collaborators, “Influence of higher-order deformations in the
   34S + 168Er fusion reaction,” Physical Review C 64, 034604 (2001), DOI
   10.1103/PhysRevC.64.034604, for the beta_6/hexacontatetrapole terminology.
