# Exact Static Vacuum Reciprocity Exterior v0.1

## Purpose

The reciprocity exponential metric was previously treated as a weak-field law
continued into the strong-field regime.

The self-consistent reciprocity action changes that status.

For a static vacuum exterior, the scalar field equation becomes exactly
Laplace's equation, so spherical symmetry fixes the exterior potential to
(mu/r).

Implementation:

`src/static_vacuum_reciprocity_exterior.py`

Tests:

`tests/test_static_vacuum_reciprocity_exterior.py`

## 1. Full geometry-scalar equation

The scalar action is

[
mathcal L_psi
=
rac{e^{4psi}}{2kappa}dotpsi^2
-
rac{|
ablapsi|^2}{2kappa}.
]

With matter source

[
S_m
=
rac{partialmathcal L_m}{partialpsi},
]

the scalar equation is

[
oxed{
e^{4psi}
left(
ddotpsi+2dotpsi^2
ight)
-

abla^2psi
=
kappa S_m.
}
]

## 2. Static vacuum reduction

In a static vacuum exterior,

[
dotpsi=0,
qquad
S_m=0.
]

Therefore

[
oxed{

abla^2psi=0.
}
]

This is exact for the proposed scalar action.

## 3. Spherical solution

For spherical symmetry,

[

abla^2psi
=
rac1{r^2}
rac{d}{dr}
left(
r^2rac{dpsi}{dr}
ight)
=
0.
]

Hence

[
psi(r)=A+rac{B}{r}.
]

Asymptotic flatness requires

[
A=0.
]

Writing

[
B=mu
]

gives

[
oxed{
psi(r)=rac{mu}{r}.
}
]

## 4. Source normalization

For (r>0),

[

abla^2rac{mu}{r}=0.
]

Distributionally,

[
-
abla^2rac{mu}{r}
=
4pimu,
delta^3(mathbf x).
]

Therefore a point source of total active energy (E_{m active}) satisfies

[
oxed{
mu
=
rac{
kappa E_{m active}
}{
4pi
}.
}
]

For stationary scalar matter on the virial shell,

[
E_{m active}=E.
]

## 5. Exact static exterior metric

The reciprocity metric is therefore

[
oxed{
ds^2
=
-e^{-2mu/r}c_*^2dt^2
+
e^{2mu/r}
left(
dr^2+r^2dOmega^2
ight)
}
]

for the exact static spherical vacuum solution of this scalar action.

## 6. Status change

The earlier description

> "point-source exponential continuation"

is now too weak **within this model**.

The more accurate statement is:

> Given the reciprocity metric assumptions and the self-consistent scalar
> action, the exponential (mu/r) exterior is the exact static spherical
> vacuum solution.

This is still not proof that nature uses this action.

## 7. Strong-field consequence

Because the exterior solution is exact within the model, its previously
derived strong-field predictions become genuine predictions of the proposed
action:

- no finite positive-radius lapse zero;
- areal-radius minimum;
- photon circular orbit differing from Schwarzschild;
- critical impact parameter

[
b_c=2emu.
]

Those predictions therefore become direct falsification targets for the action,
not optional choices of strong-field continuation.

## Status

The strong-field exterior geometry is now internally derived from the
reciprocity action under static spherical vacuum assumptions.
