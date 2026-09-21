# SU(2) Classical Matter Doublet v0.1

## Purpose

The SU(2) Wilson sector is extended with a local matter field transforming in
the fundamental two-component representation.

Implementation:

`src/su2_matter_doublet.py`

Tests:

`tests/test_su2_matter_doublet.py`

## 1. Matter representation

At each lattice site,

[
Psi(x)
in
mathbb C^2.
]

Under a local SU(2) gauge transformation,

[
oxed{
Psi(x)
	o
G(x)Psi(x).
}
]

## 2. Covariant hopping

With link

[
U_i(x)in SU(2),
]

the forward covariant difference is

[
oxed{
D_iPsi(x)
=
U_i(x)Psi(x+hat i)
-
Psi(x).
}
]

Under local gauge transformation,

[
D_iPsi(x)
	o
G(x)D_iPsi(x).
]

The tests verify this covariance directly.

## 3. Gauge-invariant matter energy

The hopping energy is

[
E_{m hop}
=
sum_{x,i}
|D_iPsi(x)|^2.
]

The local invariant density is

[
ho(x)
=
Psi^daggerPsi.
]

The first implemented potential is

[
V(ho)
=
m^2ho
+
lambda_4ho^2.
]

Therefore

[
E_{m matter}
=
E_{m hop}
+
sum_xV(ho)
]

is locally SU(2) gauge invariant.

## 4. What this is not

This field is not yet identified as:

- a Higgs doublet;
- a left-handed fermion doublet;
- any Standard Model particle.

It is a classical fundamental-representation test field.

A physical electroweak identification would require additional structure.

## 5. Next non-Abelian steps

The immediate mathematical extensions are:

1. SU(2) real-time Hamiltonian dynamics;
2. non-Abelian electric Gauss law;
3. scalar-content coupling through (Psi^daggerPsi);
4. SU(3) Wilson sector;
5. representation and anomaly analysis before any Standard Model claim.

## Status

The project now has a locally gauge-covariant non-Abelian matter prototype.
