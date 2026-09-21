# Neutral-Crossing Scale Transfer v0.1

## Purpose

This experimental extension connects the phase-driven polarity oscillator to
reversible exchange between adjacent micro-to-macro scale layers.

Implementation:

`src/scale_transfer.py`

Tests:

`tests/test_scale_transfer.py`

## 1. Transfer activation

The polarity oscillator uses

[
p(phi)=cosphi
]

as the signed inward/outward carrier.

The inter-scale transfer carrier is chosen as its quadrature:

[
oxed{
s(phi)=sinphi.
}
]

Therefore:

- polarity extrema occur at (s=0), so no scale transfer occurs;
- neutral crossings occur at (|s|=1), so transfer activation is maximal.

This directly couples polarity reversal to micro/macro interchange.

## 2. Adjacent-scale state

Let

[
mathbf a=
egin{bmatrix}
a_ell\
a_{ell+1}
end{bmatrix}
]

be signed amplitudes at neighboring scale levels.

One transfer step applies

[
mathbf a'
=
R(delta)mathbf a
]

with

[
R(delta)=
egin{bmatrix}
cosdelta & -sindelta\
sindelta & cosdelta
end{bmatrix}
]

and

[
oxed{
delta=
kappasinphi,Delta t.
}
]

## 3. Exact conservation law

Because (R) is orthogonal,

[
R^TR=I.
]

Therefore

[
oxed{
a_ell'^2+a_{ell+1}'^2
=
a_ell^2+a_{ell+1}^2.
}
]

If physical energy is proportional to amplitude squared, the scale-transfer
step is exactly energy conserving at the pair level.

This avoids an arbitrary one-way transfer rule.

## 4. Direction convention

The implemented orientation convention is

[
sinphi>0
quadRightarrowquad
	ext{micro-to-macro}
]

and

[
sinphi<0
quadRightarrowquad
	ext{macro-to-micro}.
]

This sign convention is currently an adapter choice.

The important derived property is reversibility:

[
R(-delta)=R(delta)^{-1}.
]

A reversed transition phase exactly undoes the previous transfer in the ideal
pair system.

## 5. Relation to polarity

The combined cycle is now

[
	ext{outward extremum}
ightarrow
	ext{neutral / maximal upward transfer}
ightarrow
	ext{inward extremum}
ightarrow
	ext{neutral / maximal downward transfer}
ightarrow
	ext{outward extremum}.
]

This gives a precise candidate for the recurring expansion / contraction /
neutral interchange structure.

## 6. Multi-scale chain

For amplitudes

[
(a_0,a_1,dots,a_{L-1}),
]

each adjacent edge carries its own transition phase.

The implementation applies pairwise orthogonal rotations in a symmetric
forward/reverse sweep.

Since every local map preserves the Euclidean norm, the complete chain preserves

[
oxed{
sum_ell a_ell^2.
}
]

This gives a global inter-scale invariant.

## 7. Physical interpretation candidate

A possible interpretation is:

- (cosphi): local inward/outward field orientation;
- (sinphi): rate or channel of scale exchange;
- (a_ell^2): scale-localized conserved content;
- (sum a_ell^2): total conserved content across the nested hierarchy.

This is mathematically consistent, but the physical identity of the conserved
content is not yet established.

It could eventually correspond to:

- field energy,
- action amplitude,
- information norm,
- another conserved scalar.

That identification must come from experiment or a deeper derivation.

## 8. Strong next question

The next missing law is no longer whether transfer occurs at neutral crossings.

It is:

[
oxed{
	ext{What determines the coupling }kappa?
}
]

A physical theory needs (kappa) to be derived from the architecture or from
another independently measurable quantity.

Possible structural dependencies to investigate include:

- routing phase;
- local gauge curvature;
- polarity amplitude;
- scale index;
- topological sector;
- six-gate boundary state.

## Status

The model now contains a reversible conservative candidate for nested
micro-to-macro interchange:

[
oxed{
phi
ightarrow
sinphi
ightarrow
R(kappasinphi,Delta t)
}
]

with exact quadratic conservation.
