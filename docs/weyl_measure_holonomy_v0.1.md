# Weyl Measure Holonomy v0.1

## Purpose

This extension adds discrete parallel transport for finite-lattice Weyl
subspaces and a closed-loop measure-phase diagnostic.

Implementation:

`src/weyl_measure_holonomy.py`

Tests:

`tests/test_weyl_measure_holonomy.py`

It builds on the already verified Ginsparg-Wilson projectors and projector-bundle
curvature.

## 1. Neighboring Weyl frames

Let

[
V_a,qquad V_b
]

be orthonormal Weyl frames spanning neighboring chiral subspaces.

The frame overlap is

[
M_{ba}
=
V_b^dagger V_a.
]

For sufficiently close admissible backgrounds this matrix is nonsingular.

Its unitary polar factor is

[
oxed{
Q_{ba}
=
operatorname{polar}(M_{ba}).
}
]

This supplies a discrete parallel-transport map between Weyl coefficient
spaces.

## 2. Internal basis covariance

The physical Weyl subspace does not depend on the particular orthonormal frame.

Under

[
V_aightarrow V_a U_a,
qquad
V_bightarrow V_b U_b,
]

with unitary (U_a,U_b),

[
oxed{
Q_{ba}
ightarrow
U_b^dagger
Q_{ba}
U_a.
}
]

Therefore the transport itself is frame covariant rather than frame invariant.

That is the correct behavior.

## 3. Closed-loop holonomy

For a loop of Weyl frames,

[
V_0ightarrow
V_1ightarrow
cdots
ightarrow
V_{N-1}ightarrow
V_0,
]

the ordered transport product is

[
oxed{
mathcal H
=
Q_{0,N-1}
cdots
Q_{2,1}
Q_{1,0}.
}
]

Under arbitrary internal frame changes at every vertex, the closed holonomy
changes only by conjugation at the base point,

[
mathcal H
ightarrow
U_0^dagger
mathcal H
U_0.
]

Its eigenvalues and determinant are therefore basis independent.

## 4. Chiral measure phase

The determinant defines a U(1) phase,

[
oxed{
Theta_{m loop}
=
argdetmathcal H.
}
]

This is the discrete finite-lattice Weyl measure holonomy diagnostic.

The code reports the principal phase in

[
(-pi,pi].
]

The tests verify that this phase is unchanged by independent random unitary
rotations of every Weyl basis on the loop.

That rules out arbitrary eigensolver phase conventions as the source of the
measured loop phase.

## 5. Orientation reversal

Reversing the loop orientation reverses the holonomy,

[
mathcal H_{m reverse}
=
mathcal H^{-1},
]

up to the expected basis conjugation.

Therefore

[
oxed{
Theta_{m reverse}
=
-Theta_{m forward}
pmod{2pi}.
}
]

The finite-lattice tests verify this behavior.

## 6. Contractible-loop limit

For a family of sufficiently small contractible loops in gauge-field
configuration space,

[
mathcal Hightarrow I
]

as the loop area shrinks.

Consequently

[
Theta_{m loop}ightarrow 0.
]

The test suite verifies this numerically for weak compact-U(1) rectangular
loops.

## 7. Relation to projector curvature

The preceding module defines the local projector-bundle curvature

[
mathcal F_{ab}
=
i,operatorname{Tr}
left[
P[partial_aP,partial_bP]
ight].
]

For sufficiently small loops, the holonomy phase should approach the curvature
flux through the loop,

[
Theta_{m loop}
sim
mathcal F_{ab}
Deltalambda^a
Deltalambda^b
]

up to the orientation/sign convention chosen for the discrete transport.

This relation is the next numerical consistency target.

## 8. What this does not establish

A nontrivial closed-loop phase is not by itself an anomaly proof.

A full gauge-anomaly statement still requires:

- the complete chiral representation content;
- a globally defined fermion measure;
- gauge variation of that measure;
- local anomaly coefficients;
- global/topological anomaly analysis;
- cancellation across all chiral species.

## Status

The repository now contains:

[
oxed{
D_{m overlap}
ightarrow
widehat P_pm
ightarrow
	ext{Weyl frames}
ightarrow
	ext{parallel transport}
ightarrow
mathcal H
ightarrow
argdetmathcal H.
}
]

This supplies a basis-independent closed-loop chiral-measure diagnostic on
small admissible finite lattices.
