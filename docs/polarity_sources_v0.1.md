# Polarity-to-Source Mapping v0.1

## Purpose

This extension maps the Matrix polarity variables into a conserved source sector without directly identifying signed charge with (sigma A).

Implementation:

`src/polarity_sources.py`

Tests:

`tests/test_polarity_sources.py`

## 1. Why direct signed amplitude was rejected

A tempting source map is

[
hopropto sigma A.
]

That is not generally conservative under amplitude transfer between opposite-polarity states. If amplitude moves from a (+) state to a (-) state, the signed sum can change even when total amplitude is conserved.

Therefore a direct identification of (sigma A) with conserved charge is not used.

## 2. Polarization map

Instead define a vector polarization-like field

[
oxed{
P(x)=A(x)sigma(x),hat u(x)
}
]

where

[
hat u(x)in{hat x,hat y,hat z}
]

is selected from the three canonical boundary-axis pairs.

Polarity (sigma=pm1) supplies orientation along the selected axis.

## 3. Induced source density

Define

[
oxed{
ho_P(x)
=
-
abla_{m lat}cdot P(x)
}
]

using the backward-difference lattice divergence.

This has several immediate consequences.

### Uniform polarization

If (P) is spatially uniform on the periodic lattice,

[

ablacdot P=0,
]

so

[
ho_P=0.
]

### Localized polarization

A localized oriented polarization creates equal and opposite induced source regions at its discrete boundaries.

Thus a single polarized object naturally generates a source-sink pair without adding net charge.

### Polarity reversal

Under

[
sigmaightarrow-sigma,
]

we have

[
Pightarrow-P
]

and therefore

[
oxed{
ho_Pightarrow-ho_P.
}
]

The source geometry remains the same while its signs reverse.

## 4. Exact global neutrality

On a periodic lattice,

[
sum_x 
abla_{m lat}cdot P(x)=0
]

by telescoping.

Therefore

[
oxed{
sum_x ho_P(x)=0
}
]

for every polarization configuration.

This is not a numerical approximation. It is an identity of the periodic discrete divergence.

## 5. Polarization current

For two polarization configurations separated by a time step (Delta t), define

[
oxed{
J_P
=
rac{P^{n+1}-P^n}{Delta t}.
}
]

Then

[
ho_P^n=-
ablacdot P^n
]

and

[
ho_P^{n+1}=-
ablacdot P^{n+1}.
]

Therefore

[
rac{ho_P^{n+1}-ho_P^n}{Delta t}
=
-
ablacdot
rac{P^{n+1}-P^n}{Delta t},
]

which gives the exact discrete continuity identity

[
oxed{
rac{Deltaho_P}{Delta t}
+

abla_{m lat}cdot J_P
=
0.
}
]

Thus conservation follows from the source definition itself.

## 6. Relation to the six-gate architecture

The canonical boundary already supplies

[
{pm X,pm Y,pm Z}.
]

The polarization map uses exactly this structure:

- axis selection chooses (X,Y,Z);
- polarity chooses (+) or (-);
- amplitude sets the magnitude.

So the source orientation is not an unrelated external three-vector added to the theory. It is an adapter built directly from the six signed boundary directions.

## 7. Interaction consequence

The previously implemented source-interaction solver derives attraction/repulsion from the minimum-energy gauge field satisfying Gauss law.

The polarization map now supplies a principled route

[
oxed{
(A,sigma,hat u)
longrightarrow
P
longrightarrow
ho_P
longrightarrow
E
longrightarrow
U_{m int}.
}
]

A polarity flip reverses (ho_P), which reverses the sign of its interaction cross-term with a fixed external source distribution.

This gives the engine a concrete mechanism by which polarity reversal can switch an interaction from one sign to the other.

## 8. Relation to Russell-inspired dynamics

The nested polarity model already evolves:

- amplitude,
- polarity,
- phase,
- micro-to-macro exchange.

The polarization source map supplies the missing spatial bridge.

A future adapter can take a nested state, assign its active boundary-axis orientation, and deposit

[
P_ell(x)=A_ellsigma_ellhat u_ell
]

into the 3D gauge lattice.

Then polarity reversal

[
Q:(n,sigma)mapsto(n+54,-sigma)
]

automatically produces

[
Pightarrow-P
]

and hence

[
ho_Pightarrow-ho_P.
]

This is a direct mathematical route from the canonical (P=T_{54}) involution to reversal of the induced source field.

## 9. Tests

The regression suite verifies:

1. uniform polarization produces zero induced source;
2. localized polarization generates an equal-and-opposite source pair;
3. polarity reversal reverses every induced source sign;
4. polarization current satisfies the discrete continuity equation identically;
5. total periodic induced charge is always zero.

## 10. Current limitation

This construction naturally describes **bound/polarization-like sources**. It does not yet explain isolated nonzero net charge in a closed periodic cell.

That would require either:

- boundary flux through a non-periodic domain;
- topological charge;
- a separate free-charge degree of freedom;
- or a source/sink connection to the external boundary sector.

This distinction should be preserved rather than hidden.

## Status

The polarity dynamics now has a mathematically conservative path into the gauge source sector:

[
oxed{
	ext{polarity}
ightarrow
	ext{polarization}
ightarrow
	ext{induced charge}
ightarrow
	ext{gauge interaction}
}
]

without assuming a direct (ho=sigma A) law.
