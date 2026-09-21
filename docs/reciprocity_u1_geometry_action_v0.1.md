# U(1) Gauge Field on the Reciprocity Geometry v0.1

## Purpose

The earlier single-causal-cone bridge required the content/gravity-like field
and gauge sector to share one propagation speed.

This note derives that result from the U(1) gauge action on the reciprocity
metric.

Implementation:

`src/reciprocity_u1_geometry_action.py`

Tests:

`tests/test_reciprocity_u1_geometry_action.py`

## 1. Metric

In natural units,

[
ds^2
=
-e^{-2psi}dt^2
+
e^{2psi}dmathbf x^2.
]

## 2. Maxwell action

Start from

[
S_{m EM}
=
-rac14
int
d^4x
sqrt{-g}
F_{mu
u}F^{mu
u}.
]

For the reciprocity metric,

[
oxed{
mathcal L_{m EM}
=
rac12e^{2psi}mathbf E^2
-
rac12e^{-2psi}mathbf B^2.
}
]

## 3. Canonical electric displacement

The momentum conjugate to the gauge coordinate is

[
oxed{
mathbf D
=
e^{2psi}mathbf E.
}
]

Therefore

[
mathbf E
=
e^{-2psi}mathbf D.
]

## 4. Hamiltonian

The Legendre transform gives

[
oxed{
mathcal H_{m EM}
=
rac12
e^{-2psi}
left(
mathbf D^2+mathbf B^2
ight).
}
]

At

[
psi=0,
]

this reduces to the standard flat-space Maxwell energy density.

## 5. Geometry source

Variation of the gauge Lagrangian with respect to (psi) gives

[
rac{
partialmathcal L_{m EM}
}{
partialpsi
}
=
e^{2psi}mathbf E^2
+
e^{-2psi}mathbf B^2.
]

Using

[
mathbf D=e^{2psi}mathbf E,
]

[
oxed{
S_{m EM}
=
e^{-2psi}
left(
mathbf D^2+mathbf B^2
ight)
=
2mathcal H_{m EM}.
}
]

This is the local active source expected from a traceless gauge stress tensor.

## 6. Why the factor of two does not automatically violate universality

A free radiation/gauge field by itself is not a stationary localized isolated
object.

If radiation or gauge energy is confined in a stationary composite, the
binding/confining sector carries stress.

For the **complete stationary isolated system**, the von Laue condition gives

[
int T^{ij}d^3x=0.
]

Therefore the total integrated reciprocity source remains

[
oxed{
M_{m active}=E_{m total}.
}
]

The local gauge factor of two and global source universality are therefore not
contradictory.

## 7. Common causal cone

For a uniform (psi) background, Hamilton's equations give gauge-wave
coordinate speed

[
oxed{
c_{m gauge}=e^{-2psi}.
}
]

The reciprocity metric null condition gives

[
oxed{
c_{m null}=e^{-2psi}.
}
]

The self-consistent geometry-scalar action gives

[
oxed{
c_psi=e^{-2psi}.
}
]

Thus

[
oxed{
c_{m gauge}
=
c_psi
=
c_{m null}.
}
]

The common causal cone now follows from the shared geometry coupling rather than
being separately imposed.

## 8. Extension to Yang-Mills sectors

Classical SU(2) and SU(3) Yang-Mills actions have the same spacetime tensor
structure

[
-rac14
sqrt{-g}
F^a_{mu
u}F^{amu
u}.
]

Therefore the same metric factors and principal causal cone are expected
componentwise for the non-Abelian gauge fields.

The non-Abelian dynamical implementation still needs to be built explicitly.

## Status

The reciprocity geometry now couples consistently to the U(1) gauge action and
derives the same local causal cone for geometry-scalar, gauge, and null
propagation.
