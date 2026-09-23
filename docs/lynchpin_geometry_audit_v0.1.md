# Lynchpin geometry audit v0.1

## Decision

The Howard Lynchpin corpus is admitted to the engine as an **experimental
geometry audit**, not as a verified physical law.

Three layers are kept separate:

1. exact incidence and symmetry that can be reconstructed from the patent
   claims;
2. metric embeddings that depend on lengths, angles, curvature, or material
   deformation;
3. propulsion, electromagnetic, acoustic, biological, cosmological, and
   arithmetic interpretations that require independent equations and evidence.

This separation preserves the useful geometry without promoting a patent,
drawing, or metaphor into physical proof.

## Primary source corpus

| Source | Geometric content used here |
|---|---|
| US9192875B2 | four circular faces, inscribed triangles, six tetrahedral-edge flanges, and a tetrahedral inner space |
| US9168465B2 | All-Shape applications and connected tetrahedral blocks |
| US9259660B2 | curved three-, four-, and six-surface blocks plus tetrahedral “un-shape” assemblies |
| US10556189B2 | seventeen numbered enhanced-block configurations, including the four-panel curvilinear tetrahedral “Whirl Maker” |
| US9339736B2 / US9731215B2 | collapsible pentagon modules, exact six-panel claim incidence, tetrahedral supports, converters, joints, and couplings |
| US11117065B2 | twenty-four Lynchpin figures, lateral pairs, propulsion layouts, and four- or five-module modified dodecahedra |
| Howard, Howard, and Seely, *Curvilinear Hyperbolic Space and Lynchpin Geometry* | proposed curved-space reinterpretation of multiplication |

Primary links:

- https://patents.google.com/patent/US9192875B2/en
- https://patents.google.com/patent/US9168465B2/en
- https://patents.google.com/patent/US9259660B2/en
- https://patents.google.com/patent/US10556189B2/en
- https://patents.google.com/patent/US9731215B2/en
- https://patents.google.com/patent/US11117065B2/en
- https://grey-finch-fe7e.squarespace.com/s/Title_Curvilinea.pdf

The code also inventories 24 named United States design patents. Design-patent
drawings are useful visual references, but normally do not supply the dimensions
or analytic surface equations required for a unique computational solid.

## Exact six-panel incidence

Examples 1 and 19 of US9731215B2 give enough information to recover a clean
combinatorial object.

Label the vertices of an abstract tetrahedron `0, 1, 2, 3`. Associate one
pentagonal panel with every tetrahedron edge:

`01, 02, 03, 12, 13, 23`.

At each tetrahedron vertex, the three incident edge-panels share a common
hinge. The four triple hinges are therefore:

| Tetrahedron vertex | Lynchpin panels at the hinge |
|---:|---|
| 0 | 01, 02, 03 |
| 1 | 01, 12, 13 |
| 2 | 02, 12, 23 |
| 3 | 03, 13, 23 |

Consequences derived by the engine:

- six panels;
- four triple hinges;
- every panel belongs to two hinges;
- every panel is adjacent to four other panels;
- twelve pairwise panel adjacencies;
- three opposite panel pairs;
- the panel-adjacency graph is exactly the octahedral graph;
- the full incidence automorphism group has 24 elements, with 12 proper
  tetrahedral rotations and 12 orientation-reversing actions.

This is the rigorous connection among the Lynchpin, tetrahedron, and
octahedron. It is stronger than a visual analogy.

The object is not a conventional closed polyhedral surface. Three panels share
each hinge edge, so its hinge complex is non-manifold. The octahedral result is
an adjacency result, not a claim that the pentagonal panels themselves become
the eight triangular faces of an octahedron.

## Dimensional closure test

The drawings collocate the four hinge rays at a common central vertex. Every
pair of rays bounds one of the six panels. If every panel is a rigid regular
pentagon, each ray pair must therefore make the regular-pentagon interior angle

`theta_5 = 108 degrees`,

with exact cosine

`c_5 = cos(theta_5) = (1 - phi) / 2`.

For four unit rays with one common pairwise cosine `c`, their Gram matrix is

`G = (1 - c) I + c J`.

Its eigenvalues are `1 - c` with multiplicity three and `1 + 3c` with
multiplicity one, so

`det(G) = (1 - c)^3 (1 + 3c)`.

At the regular-pentagon value, the engine derives:

| Quantity | Result |
|---|---:|
| pairwise ray angle | 108 degrees |
| Gram determinant | 0.16362712429686843 |
| Gram rank | 4 |
| local separation of the other three panels around one ray | 116.56505117707799 degrees |

The nonzero determinant proves that four exactly equiangular 108-degree rays
require four Euclidean dimensions. They cannot all lie in 3D.

For exact 3D tetrahedral closure, the simple Gram eigenvalue must vanish:

`1 + 3c = 0`, so `c = -1/3`.

That produces:

| Quantity | Result |
|---|---:|
| pairwise ray angle | 109.47122063449069 degrees |
| Gram determinant | 0 |
| Gram rank | 3 |
| local separation of the other three panels around one ray | 120 degrees |

Therefore the disclosed assembly has two coherent mathematical readings:

- an exact 3D tetrahedral scaffold with the central panel corners deformed from
  108 degrees to about 109.471 degrees;
- an exact 4D regular-pentagon ray incidence, whose local panel separation is
  about 116.565 degrees rather than 120 degrees.

It cannot preserve both exact regular-pentagon 108-degree corners and exact
120-degree three-panel separation in 3D. The patent uses “substantially” and
“approximately,” so this is a quantified tolerance/deformation requirement,
not a conclusion that a physical model cannot be built.

## All connected six-face dodecahedral configurations

The engine enumerates every choice of six connected faces on the exact regular
dodecahedron. Face adjacency is represented by the dual icosahedral graph, and
the complete H3 symmetry group is derived from the existing H3 roots.

- `924` total six-face subsets exist;
- `812` are connected;
- the `812` connected subsets form `14` classes under all `120` rotations and
  reflections;
- they form `20` classes under the `60` proper rotations;
- `6` of the 14 full-symmetry classes split into distinct mirror partners when
  reflections are excluded.

| Class | Orbit size | Internal adjacencies | Degree sequence | Boundary edges | Complement components | Mirror pair |
|---:|---:|---:|---|---:|---|:---:|
| 1 | 12 | 10 | 3,3,3,3,3,5 | 10 | 6 | no |
| 2 | 20 | 9 | 2,2,2,4,4,4 | 12 | 6 | no |
| 3 | 60 | 9 | 2,2,3,3,4,4 | 12 | 6 | yes |
| 4 | 120 | 8 | 1,2,3,3,3,4 | 14 | 6 | yes |
| 5 | 30 | 7 | 1,1,3,3,3,3 | 16 | 6 | no |
| 6 | 120 | 7 | 1,2,2,3,3,3 | 16 | 6 | yes |
| 7 | 20 | 6 | 1,1,1,3,3,3 | 18 | 6 | no |
| 8 | 60 | 7 | 2,2,2,2,3,3 | 16 | 1+5 | no |
| 9 | 120 | 6 | 1,1,2,2,3,3 | 18 | 6 | yes |
| 10 | 30 | 7 | 2,2,2,2,3,3 | 16 | 6 | no |
| 11 | 120 | 6 | 1,2,2,2,2,3 | 18 | 6 | yes |
| 12 | 60 | 5 | 1,1,2,2,2,2 | 20 | 6 | yes |
| 13 | 30 | 6 | 2,2,2,2,2,2 | 18 | 2+4 | no |
| 14 | 10 | 6 | 2,2,2,2,2,2 | 18 | 3+3 | no |

No six-face dodecahedral patch has the Lynchpin’s octahedral degree sequence
`4,4,4,4,4,4`: a Lynchpin has 12 internal panel adjacencies, while the densest
six-face dodecahedral patch has 10. A Lynchpin is therefore not literally a
six-face subset of a regular dodecahedron. It is a different non-manifold
module that can participate in a larger modified-dodecahedron assembly.

## Modified-dodecahedron accounting

A regular dodecahedral shell has 12 faces. The disclosed module counts imply:

| Assembly | Panel instances | Shell faces | Instances not uniquely mapped to shell |
|---|---:|---:|---:|
| four Lynchpins | 24 | 12 | at least 12 |
| five Lynchpins | 30 | 12 | at least 18 |

The last column can represent protruding flanges, internal panels, or overlaps.
The patent explicitly shows surfaces extending beyond the twelve-face shell,
but it does not provide a complete panel-to-shell incidence map. The engine
therefore records these figures as underspecified rather than inventing that
map.

## Configuration coverage

The executable registry covers every figure in US11117065B2:

- different-edge triplet;
- common-edge triplet;
- six-panel Lynchpin;
- tetrahedral block, extended scaffold, and supported Lynchpin;
- lateral, reinforced, and propulsion-equipped two-module compounds;
- three four-module modified-dodecahedron orientations;
- three five-module modified-dodecahedron orientations;
- four-surface-plus-one-internal compound;
- supported four-module modified dodecahedron.

It also records the distinct US9731215B2 assemblies:

- twelve-face dodecahedron from four three-panel units;
- nested tetrahedral pair and five-block tripod;
- four-block neutral converter;
- eight-block positive and negative universal joints;
- six-block turbine connector;
- eight-block flexible phase-capacitor coupling.

The explicit US9168465B2 All-Shape registry covers all eleven figures plus the
textual variants:

- four circular or elliptical faces around a tetrahedral inner space;
- one circumscribed-triangle face with three foldable flanges;
- four vertex and six flange locations for magnetic material;
- the six-flange open-to-closed folding sequence;
- a nested pair and the related nested tripod/column construction;
- a six-block hub ring and its arbitrary closed-chain generalization;
- partially collapsed and partially extended radial arrays;
- the four-block larger-tetrahedron construction.

The registry marks the literal 120-degree equilateral-triangle interior angle
and the literal 120-degree tetrahedral vertex-angle statements as inconsistent
in Euclidean geometry. The mechanisms remain parametric until their lengths,
hinge ranges, actuator travel, contact maps, and block poses are specified.

All seventeen numbered US10556189B2 enhanced configurations are inventoried.
Their disclosed panel counts and connection descriptions are testable, but
most surface equations, edge lengths, curvatures, and assembled coordinates
are absent. They remain parametric or underspecified models.

## All-Shape angle correction

US9192875B2 and related specifications describe an equilateral triangle as
having three 120-degree interior angles. In Euclidean geometry:

- an equilateral triangle has three 60-degree interior angles, totaling 180;
- its exterior turning angles are 120 degrees, totaling 360.

The construction can therefore be read consistently only if the 120-degree
labels mean exterior or projected angles. Read literally as interior angles,
the statement is inconsistent.

## Curvilinear multiplication test

The three-page *Curvilinear Hyperbolic Space and Lynchpin Geometry* document
does not specify a complete metric tensor or coordinate transformation, and
its visual sections still contain placeholder text.

Splitting a Euclidean unit square along a diagonal yields two triangles of area
`1/2`; their total remains `1`. Under a positive 2D metric `g`, the local area
element scales by `sqrt(det(g))`. Area doubles only when the chosen metric has
`det(g) = 4`. That result follows from the metric, not from the act of splitting
the square.

Thus `1 * 1 = 1` remains true for ordinary multiplication. A newly defined
curved-area operator can be studied, but it must be given a new operator name,
domain, identity, composition rule, and consistency axioms before claims about
its algebra can be tested.

## Physical test boundary

Patent grant means that patentability requirements were adjudicated. It does
not by itself validate propulsion efficiency, field behavior, resonance,
health effects, microscopic self-assembly, or a cosmological interpretation.

Before a physical claim enters the engine as more than a hypothesis, it needs:

1. dimensions and tolerances;
2. mass and material properties;
3. force, torque, field, and power equations;
4. boundary and initial conditions;
5. a baseline device for comparison;
6. measured data with uncertainty;
7. a falsification threshold.

## Implemented tests

The audit currently verifies:

- exact six-panel/tetrahedron-edge correspondence;
- four triple hinges and octahedral adjacency;
- non-manifold hinge status;
- proper and full tetrahedral symmetry;
- 108-degree rank-4 and 109.471-degree rank-3 closure results;
- 120-degree local hinge separation for the tetrahedral solution;
- all 812 connected six-face dodecahedral subsets;
- all 14 full and 20 proper symmetry classes;
- six mirror-paired classes;
- modified-dodecahedron panel accounting;
- complete US11117065 figure coverage;
- complete US9168465 figure coverage and its separately stated variants;
- seventeen enhanced configurations and 24 design-patent references;
- Euclidean triangle-angle and unit-area conservation checks;
- explicit metric determinant requirement for curved-area scaling.

## Next experimental gate

The next useful model is a paired CAD study:

1. a 3D tetrahedral-ray Lynchpin with the central panel corner set to
   `acos(-1/3)` and quantified pentagon deformation;
2. a 4D exact-108-degree model projected into 3D, with distortion and mirror
   behavior measured.

Collision-free folding, hinge travel, strain, surface self-intersection, and
manufacturing tolerances can then decide which configuration is mechanically
meaningful. CFD or electromagnetic simulation should wait until a specific
geometry, material, actuator, and power budget are supplied.
