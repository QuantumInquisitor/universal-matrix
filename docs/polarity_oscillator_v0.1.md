# Phase-Driven Polarity Dynamics v0.1

## Purpose

This extension formalizes the hypothesis that polarity is an oscillatory
transition state rather than a permanently attached binary label.

Implementation:

`src/polarity_oscillator.py`

Tests:

`tests/test_polarity_oscillator.py`

## 1. Canonical half-cycle rule

Let (phi) be an unwrapped phase and define

[
h(phi)=
leftlfloorrac{phi}{pi}ightfloor
mod 2.
]

Then define

[
n(phi)
=
n_0+54h(phi)
pmod{108}
]

and

[
sigma(phi)
=
sigma_0(-1)^{h(phi)}.
]

Therefore every half-cycle applies

[
oxed{
Q(n,sigma)
=
(n+54,-sigma)
}
]

which is exactly the canonical polarity involution.

Since

[
54+54=108equiv0pmod{108},
]

we have

[
oxed{
Q^2=I.
}
]

A full phase cycle therefore returns the same discrete node/polarity pair.

## 2. Continuous inward/outward carrier

The underlying signed carrier is

[
oxed{
p(phi)=cosphi.
}
]

Interpretation at the adapter level:

- (p>0): outward-like orientation;
- (p<0): inward-like orientation;
- (p=0): neutral transition.

The discrete polarity label is therefore a coarse classification of a continuous
oscillation, not an instantaneous physical jump.

The transition carrier

[
s(phi)=sinphi
]

has maximum magnitude at the neutral crossings.

That makes the neutral state dynamically important rather than merely the
absence of polarity.

## 3. Physical interpretation candidate

One complete oscillation can be read as

[
	ext{outward}
ightarrow
	ext{neutral}
ightarrow
	ext{inward}
ightarrow
	ext{neutral}
ightarrow
	ext{outward}.
]

This provides a mathematical candidate for the recurring expansion/contraction
structure discussed elsewhere in the project.

It does not yet prove that physical toroidal fields oscillate this way.

## 4. Nested coupling

Adjacent oscillators can exchange phase through the gauge-covariant combination

[
Delta_{ij}
=
phi_j-phi_i+	heta_{ij}.
]

The implemented phase drive is

[
oxed{
D_{ij}
=
kappasinDelta_{ij}.
}
]

For an internal link,

[
D_iightarrow D_i+D_{ij}
]

and

[
D_jightarrow D_j-D_{ij},
]

so the total internal phase drive sums to zero.

This gives a conservative synchronization mechanism between neighboring
micro-to-macro layers while preserving the gauge-link phase.

## 5. Observable consequences

If this polarity law becomes physical, it predicts several structural effects.

### Alternating source sign

For

[
P=A,p(phi),hat u,
]

the induced polarization source becomes

[
ho_P
=
-
ablacdot
left[
Acosphi,hat u
ight].
]

A half-cycle reverses the sign of the oriented polarization.

### Interaction modulation

If the source interaction energy depends bilinearly on the induced source,
then relative phase controls whether two oscillators reinforce or oppose one
another.

The interaction therefore becomes phase dependent rather than permanently
attractive or repulsive.

### Neutral crossings

At

[
phi=rac{pi}{2}+mpi,
]

the signed carrier vanishes while its rate of change is maximal.

If physical transfer or boundary injection is concentrated near these crossings,
that provides a testable distinction from a static-polarity theory.

## 6. Important unresolved choice

The current implementation uses continuous free phase evolution

[
dotphi=omega+D.
]

It does not yet decide what determines the intrinsic angular rate (omega).

Possible future derivations include dependence on:

- local field energy;
- routing state;
- scale level;
- amplitude;
- topological sector;
- neighboring oscillators;
- a universal base frequency.

The angular rate should eventually be derived rather than chosen.

## 7. Strong next question

The most important next structural issue is whether the outward/inward
oscillation also changes the **scale coordinate**.

If a half-cycle does only

[
(n,sigma)	o(n+54,-sigma),
]

the oscillation remains local.

If the neutral crossing also transfers state between adjacent scale layers,

[
ell	oellpm1,
]

then the same oscillation could generate the micro-to-macro injection/extraction
behavior envisioned for the nested architecture.

That requires a separate scale-transition law and conservation rule.

## Status

The model now has an exact canonical mechanism for phase-driven polarity
reversal:

[
oxed{
phi	ophi+pi
quadLongleftrightarrowquad
Q=(T_{54},sigma	o-sigma)
}
]

with full-cycle closure

[
oxed{
phi	ophi+2pi
quadLongleftrightarrowquad
Q^2=I.
}
]

This is mathematically consistent with the v0.4 kernel and is currently an
experimental dynamical hypothesis.
