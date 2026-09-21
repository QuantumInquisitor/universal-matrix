# Product-Group Overlap Fermions v0.1

## Purpose

This extension combines the repository's separate Abelian and non-Abelian
overlap building blocks into a single product-representation overlap operator
for Weyl multiplets transforming under

[
SU(3)	imes SU(2)	imes U(1).
]

Implementation:

`src/product_group_overlap_dirac.py`

Tests:

`tests/test_product_group_overlap_dirac.py`

The supplied representation spectrum remains external input. This module does
not claim that the Universal Matrix derives Standard Model multiplets.

## 1. Product representation link

For a multiplet with color representation (R_3), weak representation (R_2),
and Abelian charge (Y), the internal link is

[
oxed{
U_{mu}^{m rep}(x)
=
e^{iY A_mu(x)}
left[
R_3(U^{(3)}_mu(x))
otimes
R_2(U^{(2)}_mu(x))
ight].
}
]

This is the matrix seen by the fermion before the overlap construction is
applied.

## 2. Supported representations

The product operator uses the same first representation set as the anomaly
ledger:

[
SU(3):
quad
1,;3,;ar3,
]

and

[
SU(2):
quad
1,;2.
]

The representation maps are

[
R_3(3):Umapsto U,
]

[
R_3(ar3):Umapsto U^*,
]

[
R(1):Umapsto 1.
]

The weak doublet uses the fundamental SU(2) matrix directly.

## 3. Internal dimension

The internal representation dimension is

[
oxed{
d_{m int}
=
dim(R_3)dim(R_2).
}
]

Examples:

[
(3,2)
ightarrow
d_{m int}=6,
]

[
(3,1)
ightarrow
d_{m int}=3,
]

[
(1,2)
ightarrow
d_{m int}=2,
]

[
(1,1)
ightarrow
d_{m int}=1.
]

The tests verify all four cases.

## 4. Combined gauge transformation

The site transformation seen by the multiplet is

[
oxed{
G_{m rep}(x)
=
e^{iYalpha(x)}
left[
R_3(G_3(x))
otimes
R_2(G_2(x))
ight].
}
]

The full lattice spin-internal transformation is then

[
mathcal G
=
igoplus_x
left(
I_4
otimes
G_{m rep}(x)
ight).
]

The overlap operator must obey

[
oxed{
D[U^G]
=
mathcal G
D[U]
mathcal G^dagger.
}
]

The test suite verifies this simultaneously for all three gauge factors.

## 5. Q-like multiplet test

A correspondence multiplet with structure

[
(3,2)_{1/6}
]

is used as the strongest combined covariance test.

The internal link dimension is six and includes:

- a fundamental SU(3) link;
- a fundamental SU(2) link;
- an Abelian phase.

Independent local transformations are applied in all three factors.

The resulting overlap operator is verified to transform covariantly.

This is a mathematical representation test only.

## 6. Antifundamental color test

The module explicitly supports

[
ar3.
]

For the antifundamental representation,

[
U_{ar3}
=
U_3^*.
]

The test suite verifies local gauge covariance for an antifundamental color
multiplet independently of the fundamental case.

## 7. Pure U(1) singlet reduction

When both non-Abelian representations are singlets,

[
R_3=1,
qquad
R_2=1,
]

the internal dimension becomes one.

The implementation then reduces directly to the repository's existing
compact-U(1) overlap operator with effective phase

[
Y A_mu.
]

This avoids artificially wrapping the scalar Abelian representation in a fake
non-Abelian matrix structure.

## 8. Ginsparg-Wilson chirality

The combined product-representation operator retains the overlap relation

[
oxed{
Gamma_5D
+
DGamma_5
=
rac1ho
DGamma_5D.
}
]

The ((3,2)_Y) test verifies this on the full six-dimensional internal space.

## 9. Gamma5 Hermiticity

The combined operator also satisfies

[
oxed{
D^dagger
=
Gamma_5
D
Gamma_5.
}
]

This confirms that tensoring the gauge representations has not broken the
overlap chirality structure.

## 10. Relation to the anomaly ledger

The repository now has two complementary product-group layers.

The representation ledger asks:

[
	ext{Do the supplied Weyl multiplets cancel the supported anomalies?}
]

The overlap layer asks:

[
	ext{Can a supplied multiplet be represented by a gauge-covariant chiral
lattice Dirac operator?}
]

These are different questions and are intentionally kept separate.

## 11. What this closes

The project now has a direct computational path from a supplied product-group
multiplet

[
(R_3,R_2)_Y
]

to a finite-lattice overlap operator carrying all three gauge quantum numbers
simultaneously.

That closes the earlier gap where U(1), SU(2), and SU(3) overlap fermions
existed only as separate gauge-factor references.

## 12. What remains open

The current product operator still does not provide:

1. a Matrix-derived chiral multiplet spectrum;
2. a globally defined product-group Weyl measure;
3. non-Abelian local anomaly density;
4. non-Abelian measure holonomy;
5. electroweak symmetry breaking for chiral overlap multiplets;
6. Yukawa couplings;
7. family replication;
8. second quantization;
9. continuum renormalization.

## Status

The Universal Matrix repository now contains a gauge-covariant overlap-fermion
operator for supplied

[
SU(3)	imes SU(2)	imes U(1)
]

product representations, including fundamental, antifundamental, doublet, and
singlet cases.

This is a chiral lattice representation framework, not yet a complete quantum
Standard Model derivation.
