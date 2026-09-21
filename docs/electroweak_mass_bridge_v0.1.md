# Electroweak Mass Bridge v0.1

## Purpose

The repository now contains mathematical U(1) and SU(2) gauge sectors.

This bridge records the standard tree-level SU(2)_L x U(1)_Y symmetry-breaking
mass algebra that any future Matrix-derived electroweak model would have to
reproduce.

Implementation:

`src/electroweak_mass_bridge.py`

Tests:

`tests/test_electroweak_mass_bridge.py`

## 1. Reference doublet vacuum

Using one complex scalar doublet with

[
Y=rac12
]

and

[
langlePhiangle
=
egin{pmatrix}
0\
v/sqrt2
end{pmatrix},
]

the charged SU(2) modes have

[
oxed{
m_W=rac{gv}{2}.
}
]

## 2. Neutral mass matrix

In the basis

[
(W^3,B),
]

the tree-level mass-squared matrix is

[
oxed{
M^2
=
rac{v^2}{4}
egin{pmatrix}
g^2 & -gg'\
-gg' & g'^2
end{pmatrix}.
}
]

Its determinant is zero.

## 3. Mixing angle

Define

[
sin	heta_W
=
rac{g'}{sqrt{g^2+g'^2}},
]

[
cos	heta_W
=
rac{g}{sqrt{g^2+g'^2}}.
]

Then the massless direction is

[
oxed{
A
=
sin	heta_W W^3
+
cos	heta_W B
}
]

and the orthogonal massive mode is

[
oxed{
Z
=
cos	heta_W W^3
-
sin	heta_W B.
}
]

## 4. Z mass

[
oxed{
m_Z
=
rac{v}{2}
sqrt{g^2+g'^2}.
}
]

Therefore

[
oxed{
m_W
=
m_Zcos	heta_W.
}
]

## 5. Electric coupling

The unbroken U(1) coupling is

[
oxed{
e
=
rac{gg'}{sqrt{g^2+g'^2}}
=
gsin	heta_W
=
g'cos	heta_W.
}
]

## 6. What this means for the Matrix project

This module is a **correspondence target**.

It does not derive:

- (g);
- (g');
- (v);
- the Higgs potential;
- chiral fermions;
- hypercharge assignments.

A real Matrix electroweak sector must explain why this structure emerges rather
than merely importing it.

## Status

The repository now has a precise algebraic target for future SU(2)xU(1)
symmetry-breaking correspondence.
