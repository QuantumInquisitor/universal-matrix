# Reciprocity Newton Normalization v0.1

## Purpose

The self-consistent reciprocity action reduces the weak static source equation
to

[
-
abla^2psi
=
kappaho_{m active}.
]

For nonrelativistic rest matter,

[
ho_{m active}
approx
ho_{m rest-energy}.
]

This note fixes the normalization required to reproduce Newton's weak
inverse-square law.

Implementation:

`src/reciprocity_newton_normalization.py`

Tests:

`tests/test_reciprocity_newton_normalization.py`

## 1. Point-source solution

For total rest energy

[
E=Mc_*^2,
]

the static Green-function solution is

[
psi(r)
=
rac{
kappa Mc_*^2
}{
4pi r
}.
]

## 2. Weak acceleration

The reciprocity metric gives

[
|mathbf a|
=
c_*^2|
ablapsi|.
]

Therefore

[
|mathbf a|
=
rac{
kappa c_*^4
}{
4pi
}
rac{M}{r^2}.
]

Matching

[
|mathbf a|
=
rac{GM}{r^2}
]

requires

[
oxed{
kappa
=
rac{
4pi G
}{
c_*^4
}.
}
]

## 3. Relation to Einstein coupling

The conventional Einstein field-equation coupling is

[
kappa_E
=
rac{
8pi G
}{
c^4
}.
]

Hence, with the scalar-action/source normalization used here,

[
oxed{
kappa
=
rac12kappa_E.
}
]

The factor of two is a convention/result of the scalar field equation and
metric normalization. It must not be hidden by reusing the same symbol without
definition.

## 4. Potential normalization

With the matched (kappa),

[
oxed{
psi
=
rac{
GM
}{
c_*^2r
}
}
]

for a point source.

This is exactly the dimensionless weak potential used by the earlier
clock-space reciprocity bridge.

## 5. What has changed

The earlier phenomenological factorization was

[
G_{m eff}
=
rac{
c_*^2g_chikappa_{mathcal C}q_M
}{
4pi
}.
]

The self-consistent action removes the independent (q_M) source charge for
rest matter and absorbs the coupling into one geometry scalar normalization,

[
oxed{
G_{m eff}
=
rac{
kappa c_*^4
}{
4pi
}.
}
]

This is a cleaner theory.

## 6. What remains open

The measured numerical value of

[
G
]

has still not been derived from the dimensionless canonical kernel.

At present one can use measured (G) to determine (kappa).

A deeper completion would need to derive the dimensional scale from the finite
architecture or relate it to another independently measured microscopic scale.

## Status

The weak gravitational normalization now contains one coupling instead of an
arbitrary product of matter and scalar couplings.
