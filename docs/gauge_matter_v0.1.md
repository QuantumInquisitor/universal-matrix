# Gauge-Covariant Matter and Current Extension v0.1

## Purpose

This extension couples the polarity/amplitude/phase sector to the three-dimensional U(1) gauge adapter through a locally gauge-invariant conserved current.

Implementation:

`src/gauge_matter.py`

Tests:

`tests/test_gauge_matter.py`

The goal is to connect the previously separate polarity/injection and gauge subsystems without violating local U(1) symmetry or charge conservation.

## 1. Matter state

Each lattice site carries

[
Psi(x)=left(A(x),sigma(x),phi(x)ight),
]

where

- (A(x)ge0) is modeled amplitude,
- (sigma(x)in{-1,+1}) is polarity,
- (phi(x)) is phase.

The local U(1) transformation acts on phase:

[
phi(x)ightarrowphi(x)+alpha(x).
]

Amplitude and polarity are unchanged.

## 2. Gauge-covariant link phase

For an oriented link from (x) to (y=x+hat i), define

[
Delta_i(x)
=
phi(y)-phi(x)+	heta_i(x).
]

Under

[
phi(x)ightarrowphi(x)+alpha(x),
]

[
	heta_i(x)
ightarrow
	heta_i(x)+alpha(x)-alpha(y),
]

the combination (Delta_i(x)) is exactly invariant.

## 3. Matter current

The current ansatz is

[
oxed{
J_i(x)
=
kappa
sqrt{A(x)A(y)}
,sigma(x)sigma(y),
sinDelta_i(x)
}
]

for (y=x+hat i).

This form has the following properties:

- local U(1) gauge invariance;
- oriented-current antisymmetry under link reversal;
- zero current for zero amplitude;
- polarity-sensitive sign;
- phase/link sensitivity through a gauge-invariant combination.

The equation remains an experimental microscopic ansatz. It is not claimed to be a standard electromagnetic matter current.

## 4. Exact continuity equation

The lattice divergence is

[
(
abla_{m lat}cdot J)(x)
=
sum_i
left[
J_i(x)-J_i(x-hat i)
ight].
]

Charge evolves by

[
oxed{
dotho(x)
=
-

abla_{m lat}cdot J(x)
}
]

or in one explicit step,

[
ho^{n+1}(x)
=
ho^n(x)
-
Delta t,

abla_{m lat}cdot J(x).
]

On the periodic lattice, summing the divergence over all sites telescopes to zero. Therefore

[
oxed{
sum_xho(x)
=
	ext{constant}
}
]

exactly up to floating-point arithmetic.

## 5. Source-coupled gauge equation

The weak-field gauge momentum equation is extended from

[
dot E
=
-rac{partial V}{partial A}
]

to

[
oxed{
dot E
=
-rac{partial V}{partial A}
-
J
}.
]

This is the lattice analogue of adding a source current to an Abelian gauge field.

The charge sector simultaneously obeys

[
dotho=-
ablacdot J.
]

Because the divergence of the gauge-curvature force vanishes identically, these two equations imply

[
rac{d}{dt}
left(

ablacdot E-ho
ight)
=
0.
]

Therefore, if the Gauss constraint

[

ablacdot E=ho
]

holds initially, the coupled evolution preserves it.

The implementation tests this directly.

## 6. Relation to the polarity/injection model

The previous nested polarity extension introduced amplitude, phase, polarity reversal, and conservative inter-layer exchange.

This gauge-matter extension uses the same conceptual variables to build a three-dimensional conserved current:

[
oxed{
(A,sigma,phi,	heta)
longrightarrow
J
}
]

followed by

[
oxed{
J
longrightarrow
dotho,dot E
}.
]

That provides the first explicit bridge between the Russell-inspired polarity dynamics and the Maxwell-like gauge sector.

The present 3D source model is not yet numerically wired to the nested-layer `NestedPolarityDynamics` object. Instead, it uses the same variable types and symmetry principles in a spatial lattice representation. A later adapter can transfer nested-layer state into spatial source fields.

## 7. Tests implemented

The regression suite checks:

1. link current is invariant under simultaneous matter and gauge transformation;
2. reversing link orientation reverses the current;
3. the lattice continuity update conserves total periodic charge;
4. source-coupled gauge evolution preserves the Gauss constraint when initialized consistently.

## 8. What this establishes

The engine now has a source sector satisfying

[
oxed{
dotho+
abla_{m lat}cdot J=0
}
]

and a gauge sector satisfying

[
oxed{

abla_{m lat}cdot E=ho
}
]

with source-coupled evolution preserving the constraint.

Together with the previous Bianchi identity,

[
oxed{

abla_{m lat}cdot B=0,
}
]

and transverse wave propagation, this is a substantially more complete Maxwell-like lattice structure.

## 9. What remains unresolved

The principal unresolved steps are:

- what measured physical quantity corresponds to (A);
- what physical property corresponds to polarity (sigma);
- whether the current normalization (kappa) can be fixed independently;
- whether matter phase (phi) corresponds to a physical charged field phase;
- how the nested micro-to-macro layers populate the 3D source lattice;
- whether the source-coupled model reproduces measured electromagnetic forces or wave interactions;
- the mapping from lattice units to SI charge, current, field strength, distance, and time.

## Status

The Universal Matrix engine now contains an internally conserved gauge-covariant source/current sector.

It should be described as a **Maxwell-like U(1) lattice gauge system with an experimental polarity/phase matter source**, not yet as a complete derivation of physical electromagnetism.
