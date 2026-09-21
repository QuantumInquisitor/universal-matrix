# Weyl Determinant and Basis-Phase Diagnostics v0.1

## Purpose

This extension constructs the finite-lattice Weyl operator associated with the
repository's overlap-Dirac and Ginsparg-Wilson chiral structures.

Implementation:

`src/weyl_determinant.py`

Tests:

`tests/test_weyl_determinant.py`

The purpose is to make the determinant's basis dependence explicit before any
attempt is made to interpret its phase as a physical gauge response.

## 1. Weyl block

Let

[
V
]

span a Ginsparg-Wilson modified chiral subspace,

[
widehat P_chi V=V,
]

and let

[
overline V
]

span the ordinary barred chiral subspace with opposite chirality,

[
P_{-chi}overline V=overline V.
]

The finite Weyl operator is

[
oxed{
M
=
overline V^dagger D V.
}
]

In a topologically trivial sector with equal chiral ranks, (M) is square and
its determinant exists.

## 2. Internal basis freedom

The physical chiral subspaces do not fix unique bases.

For unitary internal rotations,

[
Vightarrow VU,
qquad
overline Vightarrowoverline Voverline U,
]

the Weyl block transforms as

[
oxed{
M
ightarrow
overline U^dagger M U.
}
]

Therefore

[
oxed{
det M
ightarrow
det(overline U)^*
det M
det(U).
}
]

The tests verify this transformation law numerically.

## 3. Determinant magnitude

Because internal rotations are unitary,

[
|det U|
=
|detoverline U|
=
1.
]

Hence

[
oxed{
|det M|
}
]

is independent of the arbitrary chiral frame convention.

The test suite verifies this directly.

## 4. Determinant phase

The phase does not share that property.

Instead,

[
argdet M
ightarrow
argdet M
+
argdet U
-
argdetoverline U.
]

So the raw determinant phase is not yet a physical observable.

This is not a defect in the implementation. It is the central measure problem
of a chiral fermion theory.

A measure prescription must determine how chiral frames are transported over
gauge-field configuration space before a gauge variation of the determinant
phase can be meaningfully interpreted.

## 5. Relation to the preceding holonomy layer

The repository now has two complementary objects:

1. the finite Weyl determinant on a chosen chiral frame;
2. the basis-independent closed-loop holonomy of the Weyl subspace.

The holonomy layer tracks how the chiral subspace twists geometrically.

The determinant layer shows how an explicit fermion amplitude depends on the
choice of local frame.

A consistent fermion measure must connect these two.

## 6. Topological rank mismatch

If the modified and barred chiral subspaces have unequal dimensions, the Weyl
block becomes rectangular.

The implementation refuses to assign an ordinary determinant in that case.

That rank mismatch is potentially meaningful and must be treated with index
theory rather than hidden by padding or arbitrary truncation.

## 7. What remains open

The repository still does not contain:

- a globally smooth measure section;
- a lattice Weyl determinant with a physically fixed phase;
- a local gauge-anomaly density;
- representation anomaly coefficients;
- anomaly cancellation across a complete chiral matter spectrum;
- global anomaly analysis.

## Status

The project now has an explicit finite-lattice Weyl determinant together with
tests proving its exact internal-basis covariance.

This advances the chiral program from projector geometry into the actual
fermion determinant problem while preserving the distinction between a
basis-dependent determinant phase and a physical anomaly.
