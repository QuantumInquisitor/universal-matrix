# Reciprocity Exterior Curvature v0.1

## Purpose

The exact static spherical reciprocity exterior is

[
ds^2
=
-e^{-2mu/r}dt^2
+
e^{2mu/r}
left(
dr^2+r^2dOmega^2
ight).
]

This note computes its exact curvature invariants and identifies the precise
geometric difference from a General Relativistic vacuum exterior.

Implementation:

`src/reciprocity_exterior_curvature.py`

Tests:

`tests/test_reciprocity_exterior_curvature.py`

## 1. Ricci tensor

For finite

[
r>0,
]

the only nonzero diagonal coordinate component of the Ricci tensor is

[
oxed{
R_{rr}
=
-rac{2mu^2}{r^4}.
}
]

Therefore the geometry is not Ricci-flat for

[
mu
eq0.
]

## 2. Ricci scalar

[
oxed{
R
=
-rac{
2mu^2
}{
r^4
}
e^{-2mu/r}.
}
]

A Schwarzschild vacuum exterior instead satisfies

[
R=0.
]

## 3. Ricci-tensor square

[
oxed{
R_{mu
u}R^{mu
u}
=
rac{
4mu^4
}{
r^8
}
e^{-4mu/r}.
}
]

## 4. Kretschmann scalar

[
oxed{
R_{alphaetagammadelta}
R^{alphaetagammadelta}
=
rac{
4mu^2
left(
7mu^2
-
16mu r
+
12r^2
ight)
}{
r^8
}
e^{-4mu/r}.
}
]

## 5. Large-radius behavior

For

[
rggmu,
]

the leading Kretschmann behavior is

[
oxed{
K
sim
rac{
48mu^2
}{
r^6
}.
}
]

This has the same leading inverse-radius scaling and coefficient as the
Schwarzschild Kretschmann invariant when radii coincide asymptotically.

However,

[
R
sim
-rac{
2mu^2
}{
r^4
}
+cdots,
]

so the geometries already differ at higher weak-field order.

## 6. Small isotropic-radius behavior

As

[
r	o0^+,
]

the factors

[
e^{-2mu/r},
qquad
e^{-4mu/r}
]

dominate the inverse powers.

Therefore the scalar curvature invariants implemented here tend toward zero
rather than diverging.

This does not by itself establish geodesic completeness or a traversable
wormhole. Those require separate global causal analysis.

## 7. Einstein tensor

The coordinate-diagonal Einstein tensor is nonzero:

[
G_{tt}
=
-rac{
mu^2
}{
r^4
}
e^{-4mu/r},
]

[
G_{rr}
=
-rac{
mu^2
}{
r^4
},
]

[
G_{	heta	heta}
=
rac{
mu^2
}{
r^2
},
]

[
G_{phiphi}
=
rac{
mu^2
sin^2	heta
}{
r^2
}.
]

Therefore

[
oxed{
G_{mu
u}
eq0
}
]

in the scalar-vacuum exterior.

## 8. Interpretation

This is not an inconsistency inside the reciprocity scalar theory.

Its vacuum equation is

[

abla^2psi=0,
]

not

[
G_{mu
u}=0.
]

The result instead provides a precise discriminator:

[
oxed{
	ext{reciprocity scalar vacuum}

eq
	ext{Einstein vacuum}.
}
]

Thus agreement with first-post-Newtonian tests does not make the theories
identical.

## Status

The exact reciprocity exterior now has explicit curvature invariants suitable
for higher-order weak-field and strong-field comparisons.
