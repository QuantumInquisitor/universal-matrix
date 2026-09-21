# Yang-Mills Gauge Fields on the Reciprocity Geometry v0.1

## Purpose

The U(1) reciprocity-gauge calculation extends directly to classical Yang-Mills
fields because the spacetime tensor structure of the gauge action is the same.

Implementation:

`src/reciprocity_yang_mills_geometry.py`

Tests:

`tests/test_reciprocity_yang_mills_geometry.py`

## 1. Gauge action

For adjoint index (a),

[
S_{m YM}
=
-rac14
int d^4x,
sqrt{-g}
F^a_{mu
u}F^{amu
u}.
]

On the reciprocity metric,

[
oxed{
mathcal L_{m YM}
=
rac12e^{2psi}
sum_amathbf E_a^2
-
rac12e^{-2psi}
sum_amathbf B_a^2.
}
]

## 2. Canonical displacement

For every adjoint component,

[
oxed{
mathbf D_a
=
e^{2psi}mathbf E_a.
}
]

## 3. Hamiltonian

[
oxed{
mathcal H_{m YM}
=
rac12e^{-2psi}
sum_a
left(
mathbf D_a^2+mathbf B_a^2
ight).
}
]

For SU(2),

[
a=1,2,3.
]

For SU(3),

[
a=1,ldots,8.
]

## 4. Geometry source

Variation with respect to (psi) gives

[
oxed{
S_{m YM}
=
e^{-2psi}
sum_a
left(
mathbf D_a^2+mathbf B_a^2
ight)
=
2mathcal H_{m YM}.
}
]

This is the local active-source relation expected for a traceless classical
Yang-Mills stress tensor.

## 5. Common causal cone

The principal gauge-wave speed is

[
oxed{
c_{m YM}
=
e^{-2psi}.
}
]

Therefore

[
oxed{
c_{m SU(2)}
=
c_{m SU(3)}
=
c_{m U(1)}
=
c_psi
=
c_{m null}.
}
]

At the continuum principal-part level, all current bosonic sectors share the
same reciprocity null cone.

## 6. Stationary composite source universality

A free gauge field alone has local active source twice its energy density.

A stationary isolated bound composite must include all binding and confining
stresses.

For the complete conserved stress tensor, the von Laue condition gives

[
int T^{ij}d^3x=0,
]

and therefore

[
oxed{
M_{m active}=E_{m total}.
}
]

## 7. What remains to implement

This module handles the metric dependence and source algebra.

The explicit non-Abelian dynamical implementation still needs:

- Lie-algebra electric variables;
- covariant lattice Gauss law;
- non-Abelian Hamilton equations;
- matter current backreaction;
- coupling to the evolving (psi) field.

## Status

The reciprocity geometry now has a common continuum coupling structure for
U(1), SU(2), and SU(3) gauge fields.
