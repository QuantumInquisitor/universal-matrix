# Coupled SU(2) Matter-Gauge Dynamics v0.1

## Purpose

The repository had:

- a dynamical SU(2) gauge field;
- a static SU(2) classical matter doublet.

This extension couples them through one classical Hamiltonian.

Implementation:

`src/su2_matter_gauge_dynamics.py`

Tests:

`tests/test_su2_matter_gauge_dynamics.py`

## 1. Fields

Matter:

[
Psi(x)inmathbb C^2,
qquad
Pi(x)inmathbb C^2.
]

Gauge:

[
U_i(x)in SU(2),
qquad
E_i^a(x)inmathbb R^3.
]

## 2. Hamiltonian

[
H
=
sum_x|Pi|^2
+
sum_{x,i}
left|
U_i(x)Psi(x+hat i)-Psi(x)
ight|^2
]

[
+
sum_x
left[
m^2ho+lambda_4ho^2
ight]
+
rac12sum E^2
+
S_W[U],
]

with

[
ho=Psi^daggerPsi.
]

## 3. Matter equation

The covariant lattice Laplacian is

[
Delta_UPsi(x)
=
sum_i
left[
U_i(x)Psi(x+hat i)
+
U_i^dagger(x-hat i)Psi(x-hat i)
-
2Psi(x)
ight].
]

Then

[
oxed{
dotPsi=Pi
}
]

and

[
oxed{
dotPi
=
Delta_UPsi
-
left(
m^2+2lambda_4ho
ight)Psi.
}
]

## 4. Matter current

The matter contribution to the link force is derived from the covariant
hopping energy:

[
oxed{
J_i^a(x)
=
2,mathrm{Im}
left[
Psi^dagger(x)
T_a
U_i(x)
Psi(x+hat i)
ight].
}
]

The electric equation is

[
oxed{
dot E_i^a
=
F_{W,i}^a
-
J_i^a.
}
]

The test suite verifies the current against a finite-difference derivative of
the hopping energy under an exact SU(2) group perturbation.

## 5. Matter charge

The local non-Abelian charge density is

[
oxed{
ho^a(x)
=
2,mathrm{Im}
left[
Psi^dagger(x)
T_a
Pi(x)
ight].
}
]

## 6. Coupled Gauss law

With the left-electric convention,

[
(D_iE_i)^a
=
	ext{outgoing electric}
-
	ext{parallel-transported incoming electric}.
]

The coupled Gauss generator is

[
oxed{
G^a(x)
=
(D_iE_i)^a
+
ho^a(x).
}
]

The sign follows the same canonical convention already used in the U(1)
coupled engine.

## 7. Gauge invariance

A local transformation acts as

[
Psi(x)	o G(x)Psi(x),
]

[
Pi(x)	o G(x)Pi(x),
]

[
U_i(x)
	o
G(x)
U_i(x)
G^dagger(x+hat i),
]

and

[
E_i(x)
	o
G(x)E_i(x)G^dagger(x).
]

The complete energy is numerically invariant under arbitrary random local
SU(2) transformations.

## 8. Conservation tests

The initial coupled test configuration has zero Gauss charge.

During evolution the tests monitor:

- total Hamiltonian energy;
- coupled Gauss residual.

The matter field can develop nonzero local color/isospin-like charge while the
electric field responds so that the total Gauss generator remains constrained.

## 9. Interpretation warning

This is a classical SU(2) scalar doublet gauge theory.

It is not yet the electroweak Standard Model because it lacks:

- chiral fermions;
- hypercharge coupling;
- Higgs vacuum selection;
- symmetry breaking in the dynamical engine;
- measured couplings.

## Status

SU(2) now has fully coupled matter and gauge backreaction rather than separate
static sectors.
