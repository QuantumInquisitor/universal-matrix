# Micro-to-whole geometry contract v0.1

## Purpose

This contract makes the engine's scale construction explicit. It joins the
existing Seed, stella octangula, 16-cell, tesseract, and 24-cell bridges into
one tested dependency graph. Here **micro-to-whole** means that every larger
finite coordinate set is generated from smaller canonical inputs. It does not
mean that vertex count is physical size, and it does not establish a literal
map of the observable universe or an omniverse.

## Exact construction graph

| Source | Operation | Exact result |
|---|---|---|
| one shared center | retain center plus projected axial images | seven Seed centers |
| six axial gates | choose one signed gate on each of three axes | eight stella vertices |
| six axial gates | all ordered even Clifford products `(cross, dot)` | eight 16-cell vertices |
| 16-cell | lift every vertex into both tesseract parities | sixteen tesseract vertices |
| either stella tetrahedron | take its 12 directed edge roots and their spinor products | 24-cell vertices |
| tesseract plus radius-matched 16-cell | exact set union at squared radius four | the same 24-cell |

The last two rows are independent constructions of the same 24-point set.
That agreement is stronger than a numerical resemblance.

## Downward recovery

Dropping the fourth coordinate recovers the existing three-dimensional
layers with exact multiplicities:

| 4D source | XYZ shadow |
|---|---|
| 16-cell | six gates once each, shared center twice |
| tesseract | eight stella vertices twice each |
| 24-cell | eight stella vertices twice, six radius-two gates once, center twice |

Projecting the 16-cell XYZ shadow along the stella body diagonal gives one
center and a regular six-point ring. These are the centers of a normalized
Seed-of-Life circle layout. The contract establishes the center geometry, not
the claim that a physical Flower of Life is cast by a 4D object.

## Sri Yantra simplex bridge

The multidimensional Sri Yantra contract adds a dimension-open local bridge.
An oriented triangle is the two-dimensional member of the centered regular
simplex family. Its three-dimensional successor is a tetrahedron, and the two
centrally inverted orientations form an eight-vertex dual-tetrahedron
compound. This is an exact simplex-to-stella relation.

It is not an equality between the complete forms. The Sri Yantra retains nine
source generators with a four-upward/five-downward inventory, whereas one
stella octangula contains two tetrahedra. Placement and intersection of all
nine lifted generators remain an open construction problem. See
`docs/sri_yantra_multidimensional_v0.1.md`.

## Mirror law

Every layer is closed under the same central inversion `x -> -x`. Linear
downward projections commute with that inversion. For the bilinear spinor
generators, mirroring either one input mirrors the output; mirroring both
inputs leaves the product unchanged. Tests cover these separate laws rather
than treating the word *mirror* as an analogy.

## Evidence boundary

The contract proves finite coordinate identities, incidence-compatible
projections, and mirror equivariance. Interpretations involving elemental
substances, ether, nested universes, consciousness, or the actual structure
of an omniverse remain hypotheses until they yield independently measurable
predictions. The fourth coordinate is geometric and carries no assigned
physical identity in this version.
