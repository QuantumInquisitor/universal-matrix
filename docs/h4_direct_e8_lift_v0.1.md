# Direct H4 to E8 Lift v0.1

## Result

The repository now derives an E8 root system directly from the already
implemented H4 / 600-cell coordinates.

The input is not the standard 240-root E8 coordinate list.

The input is only the existing 120 H4 roots in Q(phi)^4.

From those roots the engine forms two exact copies:

H4

and

phi H4.

Their union has 240 distinct elements.

## Reduced inner product

Following Dechant's icosahedral construction, an inner product in Q(phi) is
written as

a + b phi.

The reduced inner product keeps only the rational coefficient:

(a + b phi)_red = a.

With this metric the 240 roots have equal unit norm and close under every root
reflection.

## Why the eight coordinates are not inserted by hand

Every existing H4 coordinate already has the form

a + b phi.

A four-component H4 vector therefore contains eight rational coefficients:

(a1, a2, a3, a4, b1, b2, b3, b4).

The implementation exposes that coefficient vector directly.

For two golden-field coordinates,

(a + b phi)(c + d phi)

has rational coefficient

ac + bd.

Therefore the reduced inner product on Q(phi)^4 is exactly the ordinary
Euclidean dot product of the eight rational coefficient vectors.

This means the eight-dimensional representation is already latent in the
four-dimensional golden-field coordinates. The code does not append four
arbitrary spatial axes.

## Exact checks

The implementation verifies:

- 120 roots in the existing H4 layer;
- 120 roots in phi H4;
- 240 distinct roots total;
- exact rational rank 8 after coefficient expansion;
- equal unit norm under the reduced metric;
- pairwise inner products only in {-1, -1/2, 0, 1/2, 1};
- closure under every one of the 240 x 240 root reflections;
- 120 antipodal pairs;
- 56 nearest neighbors at every root-polytope vertex.

These are the expected simply-laced E8 root-polytope invariants.

## Interpretation boundary

This establishes an exact mathematical H4-to-E8 lift from the engine's
existing 600-cell coordinates.

It does not establish eight physical spatial dimensions.

The eight rational coordinates are, at this stage, representation coordinates
obtained by resolving the quadratic field Q(phi) into its two rational
coefficients.

Any claim that they correspond to physical dimensions requires a separate
state law and an observable prediction.

## Next creator question

The direct lift and the independently constructed standard E8 root system now
exist in the same repository.

The next exact gate is:

Can we construct an explicit orthogonal equivalence between the coefficient-
lifted H4-derived E8 roots and the standard integer-scaled E8 roots, then verify
that the equivalence intertwines root reflections, the embedded D4 subsystem,
and central mirror?

If yes, the engine will have two independently generated E8 constructions and
a tested map between them.

## Sources

Pierre-Philippe Dechant, "The Birth of E8 out of the Spinors of the
Icosahedron," Proceedings of the Royal Society A 472 (2016), 20150504.

Pierre-Philippe Dechant, "The E8 geometry from a Clifford perspective,"
Advances in Applied Clifford Algebras 27 (2017), 397-421.
