# Ginsparg-Wilson Chirality and Index Diagnostics v0.1

## Purpose

This extension builds the next algebraic layer on top of the repository's
existing overlap-Dirac operators.

Implementation:

`src/ginsparg_wilson_chirality.py`

Tests:

`tests/test_ginsparg_wilson_chirality.py`

It adds exact modified chirality projectors and a finite-lattice overlap index
diagnostic without yet claiming a complete chiral gauge theory.

## 1. Ginsparg-Wilson relation

For a lattice Dirac operator (D) satisfying

[
gamma_5 D + Dgamma_5
=
rac{1}{ho}
Dgamma_5 D,
]

together with

[
D^dagger
=
gamma_5 Dgamma_5,
]

define

[
oxed{
widehat{gamma}_5
=
gamma_5
left(
I-rac{D}{ho}
ight).
}
]

The Ginsparg-Wilson algebra implies

[
widehat{gamma}_5^dagger
=
widehat{gamma}_5
]

and

[
oxed{
widehat{gamma}_5^2=I.
}
]

So the finite-lattice chiral decomposition is exact even though ordinary
continuum anticommutation with (gamma_5) is replaced by the GW relation.

## 2. Modified chiral projectors

The corresponding projectors are

[
oxed{
widehat P_pm
=
rac12
left(
Ipmwidehat{gamma}_5
ight).
}
]

They satisfy

[
widehat P_pm^2
=
widehat P_pm,
]

[
widehat P_+widehat P_-
=
0,
]

and

[
widehat P_+
+
widehat P_-
=
I.
]

The test suite verifies Hermiticity, idempotency, orthogonality, completeness,
and the (pm1) eigenspace property.

## 3. Finite-lattice overlap index

For finite matrices with vanishing trace of the unmodified lattice
(gamma_5),

[
operatorname{Tr}gamma_5=0,
]

the overlap index can be expressed as

[
oxed{
operatorname{index}(D)
=
operatorname{Tr}
left[
gamma_5
left(
I-rac{D}{2ho}
ight)
ight].
}
]

Equivalently,

[
oxed{
operatorname{index}(D)
=
rac12
operatorname{Tr}
widehat{gamma}_5.
}
]

The implementation computes both forms independently and exposes their
difference as a consistency diagnostic.

For an exact admissible overlap operator the result should be integer-valued up
to floating arithmetic.

## 4. Free-field result

The current free finite-lattice overlap operator has zero net index,

[
operatorname{index}(D_{m free})=0,
]

as expected for the topologically trivial free background.

This does not imply that all admissible gauge backgrounds have zero index.

## 5. U(1) gauge covariance

For a local gauge transformation

[
D'
=
G D G^dagger,
]

the U(1) gauge matrix commutes with the spin-space (gamma_5), so

[
oxed{
widehat{gamma}_5[D']
=
G
widehat{gamma}_5[D]
G^dagger.
}
]

The tests verify this covariance numerically on weak random compact-U(1)
backgrounds.

Therefore the modified chiral subspaces transform covariantly with the overlap
operator.

## 6. What this closes

The repository now has:

1. Wilson-Dirac doubler control;
2. free overlap/Ginsparg-Wilson reference;
3. compact-U(1) gauge-covariant overlap operator;
4. exact GW-modified chiral projectors;
5. finite-lattice overlap-index diagnostics.

This is a substantially firmer foundation for chiral lattice work than
projecting naive Wilson fermions with ordinary continuum projectors.

## 7. What remains open

This module does **not** yet provide:

- a Weyl fermion determinant;
- a globally smooth fermion measure over gauge-field configuration space;
- gauge-anomaly computation;
- anomaly-cancellation conditions;
- SU(2) or SU(3) overlap kernels;
- Standard Model hypercharge assignments;
- second quantization.

Those are the next mathematically meaningful steps.

## 8. Next constrained target

The next chiral question is not whether projectors exist. They now do.

The next target is to build a small-lattice Weyl subspace basis and determine
how its measure changes under gauge transformations.

That is where anomaly information enters.

## Status

The project now contains a gauge-covariant Ginsparg-Wilson chirality layer and
an overlap-index diagnostic, while explicitly stopping short of claiming a
complete anomaly-free chiral gauge theory.
