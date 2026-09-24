# Sevenfold Seed Contract v0.1

## Purpose

This contract formalizes the creator hypothesis that the Seed of Life is one
central mode with six surrounding modes. The book identifies Consciousness as
the seventh center, the source from which the other six stem and to which they
return. The present extension treats Ether as the proposed relational medium
through which that central Consciousness expresses across scales. This is an
ontology under test, not evidence that consciousness is a physical field or
that a historical mechanical ether has been recovered.

## Competing interpretations

All interpretations preserve Fire, Air, Water, and Earth on two opposite axes.
The third axis remains open and is evaluated three ways:

1. **Material:** Metal opposite Crystal.
2. **Polarity:** Positive opposite Negative.
3. **Dual aspect:** Metal expresses conductive outward polarity while Crystal
   expresses coherent inward polarity.

Metal and Crystal are called generative modes here. They are not asserted to be
chemical elements. Keeping the three models distinct prevents a symbolic
preference from silently becoming a physical law.

## Seed geometry

Positions 1 through 6 form a hexagonal ring around position 0. Opposite
positions form three reciprocal axes: `(1, 4)`, `(2, 5)`, and `(3, 6)`.

The local Seed contains twelve explicitly indexed Vesica relationships:

- six overlaps between Ether's center circle and the surrounding circles;
- six overlaps between adjacent circles on the surrounding ring.

Under the present creator hypothesis, every indexed Vesica is a universe
domain. A universe address is a path of Vesica indices. Appending an index
enters a child universe containing another complete Seed, so recursion is not
assigned an arbitrary maximum depth.

The recursive universe-port engine now gives this address an exact contained
geometry. If a parent vessel has radius (R), its complete Seed uses circles
of radius (R/2). The largest centered circle inside any resulting Vesica has
radius (R/4), remains inside the parent vessel, and contains the next complete
Seed. Thus the current planar containment convention gives

$$
R_d=R_0/4^d
$$

and (12^d) distinct addresses at exact depth (d). This is a software and
Euclidean-geometry result under the selected convention, not a measured
physical ratio between universes.

## Recursive central mirror

The Seed mirror is the half-turn through position 0. It fixes the center and
exchanges the three pairs `(1, 4)`, `(2, 5)`, and `(3, 6)`. The same action
maps each center-to-ring Vesica to an opposite center-to-ring Vesica and each
adjacent-ring Vesica to an opposite adjacent-ring Vesica.

At recursive depth, the mirror is applied to every Vesica index in the path.
It is exactly involutive, and it respects the parent/child relation: mirror
twice returns the original universe address, while mirroring after entering a
child gives the same address as entering the mirrored child of the mirrored
parent. This encodes “the pattern mirrors itself” as a test rather than an
ungraded visual claim.

## Relation to the larger architecture

The Seed is the first complete local neighborhood. Repetition of the Seed forms
the Flower of Life substrate. Tree of Life structures are proposed routing and
expression maps selected from that substrate. Toroidal structures describe
circulation through the substrate rather than replacing it.

That construction is now explicit in `src/universe_port_engine.py`. Equal-size
Flower growth has (1+3n(n+1)) circles and (9n^2+3n) neighboring Vesicas in
a radius-(n) hexagonal disk. Inner and outer Tree routes are opposite
orientations of Flower edges that cross successive rings. The negative,
neutral, and positive pillars are extracted from the same lattice and transform
under its central mirror.

## Exact software properties

- every interpretation contains exactly one center and six ring positions;
- Consciousness/Ether remains the dual-aspect center in all interpretations;
- the ring has exactly three opposite reciprocal axes;
- the local neighborhood has twelve unique Vesica relationships;
- every Vesica address can extend recursively by another valid child index;
- the same central mirror is involutive and parent/child compatible at every
  recursive depth.
- every contained Seed and Vesica child remains inside its parent vessel;
- equal-circle Flower growth is kept distinct from inward scale contraction;
- inner and outer Tree routes are exact reverses derived from Flower geometry.

## Open physical questions

- whether Consciousness and Ether are distinct, dual aspects, or different
  descriptions of one center;
- whether Ether corresponds to any measurable field or vacuum property;
- whether Metal and Crystal are fundamental modes or emergent expressions;
- whether the two modes encode polarity, material organization, or both;
- whether the current explicit port coupling to three routing channels and 36
  phases has physical meaning beyond exact 108-state coverage;
- what observable distinguishes these models from one another.

See `docs/universe_port_engine_v0.1.md` for the complete geometry and evidence
boundary.
