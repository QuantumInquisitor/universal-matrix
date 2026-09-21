# Second-Order Light Deflection in the Reciprocity Exterior v0.1

## Purpose

The reciprocity exterior and Schwarzschild agree at leading weak-field light
deflection,

[
alpha
=
4mu/b
+
cdots,
]

but differ at the next order.

This note derives the reciprocity coefficient analytically from the exact null
orbit equation.

Implementation:

`src/reciprocity_second_order_light_deflection.py`

Tests:

`tests/test_reciprocity_second_order_light_deflection.py`

## 1. Exact null orbit equation

For the reciprocity exterior,

[
ds^2
=
-e^{-2mu/r}dt^2
+
e^{2mu/r}
left(
dr^2+r^2dphi^2
ight)
]

in the equatorial plane.

Using conserved

[
E,
qquad
L,
qquad
b=L/E,
]

and defining

[
x=rac{b}{r},
qquad
epsilon=rac{mu}{b},
]

the null first integral reduces to

[
oxed{
left(
rac{dx}{dphi}
ight)^2
=
e^{4epsilon x}
-
x^2.
}
]

Differentiating gives

[
oxed{
x''+x
=
2epsilon e^{4epsilon x}.
}
]

## 2. Perturbative expansion

Write

[
x
=
x_0
+
epsilon x_1
+
epsilon^2x_2
+
cdots.
]

At zeroth order,

[
x_0''+x_0=0,
]

so

[
x_0=cosphi.
]

At first order,

[
x_1''+x_1=2,
]

and symmetry about closest approach gives

[
x_1=2.
]

At second order,

[
x_2''+x_2
=
8cosphi.
]

Using the turning-point expansion,

[
x_t
=
1
+
2epsilon
+
6epsilon^2
+cdots,
]

the symmetric solution is

[
oxed{
x_2
=
6cosphi
+
4phisinphi.
}
]

## 3. Asymptotic angle

The outgoing asymptote occurs where

[
x=0.
]

Write

[
phi
=
rac{pi}{2}
+
s.
]

The one-sided shift is

[
oxed{
s
=
2epsilon
+
2piepsilon^2
+
O(epsilon^3).
}
]

The total deflection is twice this shift:

[
oxed{
alpha_{m reciprocity}
=
4epsilon
+
4piepsilon^2
+
O(epsilon^3).
}
]

Therefore

[
oxed{
alpha_{m reciprocity}
=
4rac{mu}{b}
+
4pi
left(
rac{mu}{b}
ight)^2
+
Oleft(
(mu/b)^3
ight).
}
]

## 4. Schwarzschild comparison

For Schwarzschild/GR,

[
oxed{
alpha_{m GR}
=
4rac{mu}{b}
+
rac{15pi}{4}
left(
rac{mu}{b}
ight)^2
+
Oleft(
(mu/b)^3
ight).
}
]

Thus

[
oxed{
alpha_{m reciprocity}
-
alpha_{m GR}
=
rac{pi}{4}
left(
rac{mu}{b}
ight)^2
+
Oleft(
(mu/b)^3
ight).
}
]

## 5. Significance

The leading coefficient is identical,

[
4mu/b,
]

so first-order light-bending agreement is preserved.

The second-order coefficient is different:

[
4pi
]

versus

[
15pi/4.
]

That gives a coordinate-invariant observable distinction before entering the
strong-field regime.

## 6. Interpretation

This result follows from the exact reciprocity exterior and therefore is a
prediction of the proposed scalar-geometry action.

It does not establish that current data favor the reciprocity coefficient.

That requires a dedicated observational comparison.

## Status

The reciprocity model now has an explicit second-order lensing prediction
distinct from Schwarzschild/GR.
