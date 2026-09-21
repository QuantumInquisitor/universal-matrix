# Charged U(1) Weyl Gauge-Orbit Holonomy v0.1

## Purpose

This extension closes a missing conceptual loop between:

- charged overlap fermions,
- Weyl projector geometry,
- basis-independent parallel transport,
- and gauge-equivalent endpoints.

Implementation:

`src/u1_weyl_gauge_orbit.py`

Tests:

`tests/test_u1_weyl_gauge_orbit.py`

The goal is to measure how the finite-lattice Weyl measure twists along a gauge
orbit without confusing that effect with arbitrary eigensolver basis phases.

## 1. Gauge path

For an underlying compact U(1) gauge potential,

[
A_mu(x),
]

and gauge parameter

[
alpha(x),
]

the endpoint is

[
A_mu^g(x)
=
A_mu(x)
+
alpha(x)
-
alpha(x+hatmu).
]

A simple path along the gauge orbit is

[
A_mu(t)
=
A_mu
+
t
left[
alpha(x)-alpha(x+hatmu)
ight],
qquad
0le tle1.
]

The implementation discretizes this path into a configurable number of
segments.

## 2. Charge-q fermion

A fermion of charge (q) sees the link phase

[
qA_mu.
]

The exact site gauge transformation is therefore

[
oxed{
G_q(alpha)
=
e^{iqalpha(x)}.
}
]

At the projector level,

[
oxed{
widehat P_q[A^g]
=
G_q
widehat P_q[A]
G_q^dagger.
}
]

The tests verify this endpoint identity numerically.

## 3. Open Weyl transport

Let

[
V_0,V_1,ldots,V_N
]

be Weyl frames along the gauge path.

Between neighboring frames the repository uses the unitary polar factor of the
frame overlap to define discrete parallel transport.

The ordered open transport is

[
oxed{
H_{m open}
=
Q_{N,N-1}
cdots
Q_{2,1}
Q_{1,0}.
}
]

This maps Weyl coefficients at the initial frame to coefficients at the
endpoint frame.

## 4. Exact gauge identification

Because the endpoint is gauge equivalent to the start, the exact charge-q
gauge transformation supplies a second coefficient map,

[
oxed{
Q_g
=
operatorname{polar}
left(
V_N^dagger
G_q
V_0
ight).
}
]

This is the exact gauge identification of the initial Weyl subspace with the
endpoint Weyl subspace.

## 5. Quotient-space holonomy

The closed loop in gauge-orbit space is then

[
oxed{
H_{m gauge}
=
Q_g^dagger
H_{m open}.
}
]

Under arbitrary internal basis changes

[
V_kightarrow V_k U_k,
]

the closed holonomy transforms only by conjugation at the base point.

Therefore

[
oxed{
argdet H_{m gauge}
}
]

is independent of all arbitrary internal Weyl-frame conventions.

The test suite explicitly applies unrelated random unitary rotations at every
path point and verifies that the determinant phase does not change.

## 6. Neutral fermion check

For

[
q=0,
]

the fermion does not couple to the U(1) gauge field.

Then

[
G_q=I
]

and the charged overlap background is independent of (A).

The implementation correctly gives zero gauge-orbit measure phase in this
limit.

## 7. Infinitesimal response

The module defines a symmetric small-gauge-parameter derivative

[
oxed{
mathcal R_alpha
=
left.
rac{d}{depsilon}
Theta_{m gauge}[epsilonalpha]
ight|_{epsilon=0},
}
]

where

[
Theta_{m gauge}
=
argdet H_{m gauge}.
]

This quantity is a basis-independent infinitesimal measure-response diagnostic.

It is the natural object to compare next with the local overlap
index/anomaly-density candidate.

## 8. What this does not yet prove

The gauge-orbit phase is not automatically the complete consistent anomaly.

A full identification still requires:

1. a precise fermion measure convention;
2. a continuum-limit normalization;
3. the relation between covariant and consistent anomaly forms;
4. comparison with the local charged overlap index density;
5. cancellation across complete chiral representations;
6. treatment of topologically nontrivial sectors and global anomalies.

## 9. Current chain

The chiral U(1) program now contains

[
oxed{
D_q[A]
ightarrow
widehat P_q[A]
ightarrow
V_q[A]
ightarrow
H_{m open}
ightarrow
H_{m gauge}
ightarrow
Theta_{m gauge}.
}
]

Separately, the local overlap topology path is

[
oxed{
D_q[A]
ightarrow
q_{m index}(x)
ightarrow
	ext{anomaly ledger}.
}
]

The next meaningful test is to connect these two paths quantitatively.

## Status

The project now has a basis-independent charged Weyl measure holonomy defined
on closed loops in gauge-orbit space, together with an infinitesimal
gauge-response diagnostic.

It remains a controlled anomaly-research framework rather than a completed
anomaly-free chiral gauge theory.
