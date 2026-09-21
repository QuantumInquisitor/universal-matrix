# Higher-Order Weak-Field Reciprocity vs Schwarzschild v0.1

## Purpose

The reciprocity metric matches the standard first post-Newtonian parameters

[
eta=gamma=1.
]

That does not mean it is identical to Schwarzschild.

This note identifies the first higher-order differences using the same isotropic
coordinate.

Implementation:

`src/reciprocity_higher_order_weak_field.py`

Tests:

`tests/test_reciprocity_higher_order_weak_field.py`

## 1. Dimensionless potential

Define

[
u=rac{mu}{r}.
]

## 2. Reciprocity exponential metric

[
g_{tt}^{m exp}
=
-e^{-2u},
]

[
g_{ij}^{m exp}
=
e^{2u}delta_{ij}.
]

Expanding,

[
oxed{
g_{tt}^{m exp}
=
-1
+
2u
-
2u^2
+
rac43u^3
-
rac23u^4
+cdots
}
]

and

[
oxed{
g_{ij}^{m exp}
=
left(
1
+
2u
+
2u^2
+
rac43u^3
+
rac23u^4
+cdots
ight)delta_{ij}.
}
]

## 3. Schwarzschild in isotropic coordinates

[
g_{tt}^{m Schw}
=
-
left(
rac{
1-u/2
}{
1+u/2
}
ight)^2,
]

[
g_{ij}^{m Schw}
=
left(
1+rac u2
ight)^4
delta_{ij}.
]

Therefore

[
oxed{
g_{tt}^{m Schw}
=
-1
+
2u
-
2u^2
+
rac32u^3
-
u^4
+cdots
}
]

and

[
oxed{
g_{ij}^{m Schw}
=
left(
1
+
2u
+
rac32u^2
+
rac12u^3
+
rac1{16}u^4
+cdots
ight)delta_{ij}.
}
]

## 4. First agreement

The temporal coefficients through

[
u^2
]

agree.

The spatial coefficient through

[
u
]

agrees.

Therefore the usual first post-Newtonian identification remains

[
oxed{
eta=gamma=1.
}
]

## 5. First spatial disagreement

The reciprocity spatial (u^2) coefficient is

[
2,
]

while Schwarzschild gives

[
rac32.
]

So

[
oxed{
Delta g_{m spatial}
=
rac12u^2
+
O(u^3).
}
]

Using the common isotropic 2PN convention

[
g_{ij}
=
left[
1
+
2gamma u
+
rac32delta u^2
+cdots
ight]
delta_{ij},
]

the reciprocity metric corresponds to

[
oxed{
delta_{m reciprocity}
=
rac43,
}
]

while Schwarzschild/GR gives

[
oxed{
delta_{m GR}=1.
}
]

## 6. First temporal disagreement

The first temporal difference appears at

[
u^3.
]

The coefficient difference is

[
rac43-rac32
=
-rac16.
]

Therefore

[
oxed{
g_{tt}^{m exp}
-
g_{tt}^{m Schw}
=
-rac16u^3
+
O(u^4).
}
]

## 7. Significance

The theories can agree with leading solar-system tests while still producing
different post-post-Newtonian observables.

This gives a weak-field discrimination program independent of black-hole
physics.

## 8. What is not claimed here

This note does not state that current observations already exclude

[
delta=rac43.
]

That requires a separate current experimental analysis with the exact
observable definitions and coordinate-invariant predictions.

## Status

The reciprocity action now has an explicit higher-order weak-field signature
distinct from Schwarzschild/GR.
