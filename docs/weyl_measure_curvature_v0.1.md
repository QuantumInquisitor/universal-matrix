# Weyl Subspace and Measure Curvature v0.1

## Purpose

This extension takes the repository's exact Ginsparg-Wilson projectors and
builds the first finite-lattice diagnostics needed for a chiral fermion measure.

Implementation:

`src/weyl_measure_curvature.py`

Tests:

`tests/test_weyl_measure_curvature.py`

The goal is not to claim anomaly cancellation. The goal is to expose the
geometry of the Weyl subspace over gauge-field configuration space in a form
that can be tested numerically.

## 1. Exact Weyl subspace

For the overlap operator (D), define

[
widehat{gamma}_5
=
gamma_5
left(
I-rac{D}{ho}
ight)
]

and

[
widehat P_pm
=
rac12
left(
Ipmwidehat{gamma}_5
ight).
]

A Weyl basis (V) is any orthonormal frame spanning one projector image,

[
V^dagger V=I,
qquad
VV^dagger=widehat P.
]

The basis is not unique. If (U) is unitary within the Weyl subspace,

[
Vightarrow VU
]

describes the same projector.

This internal frame freedom is exactly why anomaly analysis must distinguish
the projector geometry from arbitrary eigensolver basis phases.

## 2. Gauge transport of the Weyl subspace

For a compact U(1) gauge transformation,

[
D[A^g]
=
G D[A] G^dagger,
]

and therefore

[
oxed{
widehat P[A^g]
=
G
widehat P[A]
G^dagger.
}
]

The implementation verifies this directly.

For bases (V[A]) and (V[A^g]), the matrix

[
M
=
V[A^g]^dagger
G
V[A]
]

depends on the internal frame choices, but if the two subspaces agree exactly,
all singular values of (M) equal one.

The tests use this principal-angle criterion instead of incorrectly requiring
two independent eigensolvers to choose identical basis phases.

## 3. Projector-bundle curvature

Let (A(lambda^a)) be a smooth family of admissible gauge backgrounds.

The chiral projector then defines a vector bundle over gauge-field
configuration space.

Its basis-independent curvature is

[
oxed{
mathcal F_{ab}
=
i,operatorname{Tr}
left[
P
left(
partial_aP,partial_bP
-
partial_bP,partial_aP
ight)
ight].
}
]

The code evaluates the projector derivatives with symmetric finite
differences.

The test suite checks:

- antisymmetry,
- numerical reality,
- invariance under a fixed compact-U(1) gauge transformation.

## 4. Why this matters

A chiral fermion determinant is not merely the determinant of a square
Dirac matrix.

The Weyl subspace itself moves as the gauge background changes.

Therefore the fermion measure carries geometric information associated with
how its basis is transported over configuration space.

The projector curvature gives a basis-independent way to detect this geometry
before choosing a particular phase convention for a Weyl determinant.

## 5. What the curvature does not prove

A nonzero local value of

[
mathcal F_{ab}
]

does not by itself prove an uncancelled gauge anomaly.

Likewise, a zero value along one chosen pair of directions does not establish
anomaly cancellation.

A full anomaly statement requires, at minimum:

1. the full chiral representation content;
2. a globally consistent measure prescription;
3. the response of that measure under gauge transformations;
4. local and global anomaly constraints;
5. treatment of topologically nontrivial admissible gauge sectors.

## 6. Current U(1) status

The repository now has the following chain:

[
oxed{
D_{m overlap}
ightarrow
widehat{gamma}_5
ightarrow
widehat P_pm
ightarrow
	ext{Weyl basis}
ightarrow
mathcal F_{ab}.
}
]

Each arrow is implemented and tested on small admissible finite lattices.

This is now sufficient to begin measure-phase and determinant transport tests
without confusing arbitrary basis rotations with physical gauge response.

## 7. Next step

The next constrained problem is to define parallel transport between nearby
Weyl subspaces and compute a gauge-path measure phase or holonomy.

That will allow closed loops in gauge-field configuration space to be tested.

A nontrivial holonomy can then be compared with the projector curvature through
a discrete Stokes-type relation on sufficiently small loops.

Only after that should the repository attempt a local anomaly density or
representation-cancellation test.

## Status

The project now contains a basis-independent Weyl projector-bundle curvature
diagnostic and gauge-covariant Weyl subspace transport tests.

It remains a chiral-measure research framework, not a completed anomaly-free
chiral gauge theory.
