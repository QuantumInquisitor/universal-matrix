# Six-Gate Spatial Response v0.1

## Purpose

The weak-field light-bending audit showed that a clock-only scalar response is
insufficient.

This note asks what the canonical six-gate boundary symmetry can actually
derive about the missing spatial sector.

Implementation:

`src/six_gate_spatial_response.py`

Tests:

`tests/test_six_gate_spatial_response.py`

## 1. Boundary symmetry

The six canonical orientations are

[
B_6
=
{pm X,pm Y,pm Z}.
]

Their signed-permutation symmetry group has

[
2^3 3!=48
]

elements.

Represent these symmetries by signed permutation matrices

[
Gin O(3).
]

## 2. Linear spatial response

Let

[
R
]

be a linear infinitesimal spatial-response tensor produced by a scalar content
potential.

If the response preserves the full six-gate symmetry, then

[
RG=GR
]

for every signed permutation matrix (G).

Commutation with the independent axis sign flips removes off-diagonal terms.

Commutation with all axis permutations forces the three diagonal entries to be
equal.

Therefore

[
oxed{
R
=
gamma_M I.
}
]

This is a genuine symmetry restriction.

## 3. Group averaging

Any arbitrary (3	imes3) response tensor can be projected onto the
six-gate-invariant subspace by

[
ar R
=
rac1{48}
sum_G
G R G^T.
]

The result is

[
oxed{
ar R
=
rac{operatorname{tr}R}{3}I.
}
]

The implementation verifies this numerically for the complete 48-element group.

## 4. Nonlinear multiplicative completion

If the isotropic spatial scale response also satisfies additive composition in
the scalar potential,

[
S(psi_1+psi_2)
=
S(psi_1)S(psi_2),
]

with continuity and

[
S(0)=1,
]

then

[
oxed{
S(psi)
=
e^{gamma_Mpsi}.
}
]

The isotropic spatial metric factor is then

[
oxed{
h_{ij}
=
e^{2gamma_Mpsi}delta_{ij}.
}
]

At weak field,

[
h_{ij}
approx
left(
1+2gamma_Mpsi
ight)
delta_{ij}.
]

## 5. What symmetry fixes and what it does not

The six-gate architecture fixes:

[
oxed{
	ext{isotropy}
}
]

if the full boundary symmetry is preserved.

It does **not** fix:

[
oxed{
gamma_M.
}
]

Therefore setting

[
gamma_M=1
]

would still be an additional physical statement unless another Matrix principle
derives it.

## 6. Connection to experiment

The weak-field PPN bridge requires

[
gamma_Mapprox1
]

in the solar-system regime if this sector is to reproduce observed light
deflection and Shapiro delay.

That external requirement does not count as an internal derivation.

The open problem is therefore sharply defined:

[
oxed{
	ext{What Matrix principle fixes the invariant spatial-response coefficient?}
}
]

## Status

The spatial sector is now partially derived:

[
oxed{
B_6	ext{ symmetry}
Rightarrow
Rpropto I.
}
]

The coefficient remains a real unresolved physical parameter.
