# Spatially Varying Non-Abelian Reciprocity Geometry v0.1

## Purpose

The constant-(psi) bridge shows that SU(2) and SU(3) Hamiltonian evolution
shares the reciprocity causal factor

[
e^{-2psi}.
]

This extension allows

[
psi=psi(mathbf x)
]

while preserving exact local gauge invariance.

Implementation:

`src/reciprocity_nonabelian_spatial_geometry.py`

Tests:

`tests/test_reciprocity_nonabelian_spatial_geometry.py`

## 1. Link-centered geometry weight

For a link from (x) to (x+hat i), define

[
arpsi_ell
=
rac12
left[
psi(x)+psi(x+hat i)
ight].
]

Then

[
oxed{
w_ell
=
e^{-2arpsi_ell}.
}
]

The electric contribution is

[
H_E
=
rac12
sum_{ell,a}
w_ell
(E_ell^a)^2.
]

## 2. Plaquette-centered geometry weight

For the four corners of a plaquette,

[
arpsi_p
=
rac14
left(
psi_1+psi_2+psi_3+psi_4
ight).
]

Define

[
oxed{
w_p=e^{-2arpsi_p}.
}
]

The magnetic Wilson contribution for SU((N)) is

[
H_B
=
eta
sum_p
w_p
left[
1-rac1Noperatorname{ReTr}U_p
ight].
]

## 3. Gauge invariance

The geometry weights contain no group indices and do not transform under local
SU((N)) gauge rotations.

Each electric norm

[
E^aE^a
]

and each plaquette trace remains gauge invariant.

Therefore

[
oxed{
H_{m YM}[U,E,psi]
}
]

is locally gauge invariant for arbitrary spatial (psi).

The tests verify this directly for SU(2) and SU(3).

## 4. Local geometry source

Define

[
S_psi(x)
=
-rac{partial H}{partialpsi(x)}.
]

For a link energy contribution

[
h_ell
=
rac12w_ell E_ell^2,
]

each endpoint receives

[
h_ell.
]

For a plaquette contribution

[
h_p
=
eta w_p
left[
1-rac1Noperatorname{ReTr}U_p
ight],
]

each of the four corners receives

[
rac12h_p.
]

## 5. Exact source-sum identity

Each link has two endpoints, so its total deposited source is

[
2h_ell.
]

Each plaquette has four corners, each receiving (h_p/2), so its total
deposited source is

[
2h_p.
]

Therefore

[
oxed{
sum_xS_psi(x)
=
2H_{m YM}.
}
]

The implementation verifies this identity for random spatially varying
(psi) fields in both SU(2) and SU(3).

## 6. Finite-difference verification

The local source at an individual lattice site is also compared against a
direct numerical derivative

[
-rac{
H(psi_x+epsilon)
-
H(psi_x-epsilon)
}{
2epsilon
}.
]

This verifies the deposition rule independently of the global sum identity.

## 7. Uniform-background limit

When

[
psi(x)=psi_0,
]

every link and plaquette weight becomes

[
e^{-2psi_0}.
]

Hence

[
oxed{
H_{m YM}[psi_0]
=
e^{-2psi_0}
H_{m YM}[0],
}
]

recovering the constant-background bridge exactly.

## 8. Discretization warning

Using arithmetic means of (psi) over endpoints and plaquette corners is a
specific midpoint-style lattice discretization.

It is:

- gauge invariant;
- symmetric under reversal/permutation of the geometric cell;
- second-order natural for smooth fields.

It is **not** uniquely dictated by the canonical 108-state kernel.

Alternative consistent discretizations should be compared by convergence to
the same continuum limit.

## Status

The non-Abelian gauge sectors now have an explicit, locally gauge-invariant
coupling to spatially varying reciprocity geometry together with an exact
geometry-source deposition rule.
