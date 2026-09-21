# Coupled SU(3) Matter-Gauge Dynamics v0.1

## Purpose

The repository now has:

- dynamical SU(3) Wilson gauge fields;
- classical SU(3) triplet matter.

This extension couples those sectors through one Hamiltonian.

Implementation:

`src/su3_matter_gauge_dynamics.py`

Tests:

`tests/test_su3_matter_gauge_dynamics.py`

## 1. Fields

Matter:

[
Psi(x)inmathbb C^3,
qquad
Pi(x)inmathbb C^3.
]

Gauge:

[
U_i(x)in SU(3),
qquad
E_i^a(x),quad a=1,dots,8.
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
S_W^{SU(3)}[U],
]

where

[
ho=Psi^daggerPsi.
]

## 3. Matter equation

The SU(3)-covariant lattice Laplacian is

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
dotPsi=Pi,
]

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

The link current is derived from the same covariant hopping energy:

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

The electric equation becomes

[
oxed{
dot E_i^a
=
F_{W,i}^a
-
J_i^a.
}
]

The current is tested against a direct SU(3) group-direction derivative of the
hopping energy.

## 5. Matter charge

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

The pure-gauge covariant divergence is combined with matter charge:

[
oxed{
G^a(x)
=
(D_iE_i)^a
+
ho^a(x).
}
]

The test evolution starts on the constrained surface and monitors the full
Gauss residual during coupled matter-gauge evolution.

## 7. Local gauge invariance

Under

[
Psi	o GPsi,
qquad
Pi	o GPi,
]

[
U_i(x)
	o
G(x)
U_i(x)
G^dagger(x+hat i),
]

[
E_i(x)
	o
G(x)E_i(x)G^dagger(x),
]

the total Hamiltonian is invariant.

The tests verify this with random local SU(3) transformations.

## 8. Interpretation warning

This remains a classical triplet gauge theory.

It is not yet QCD because it lacks:

- fermionic quarks;
- flavor structure;
- chiral symmetry;
- continuum running;
- confinement measurements;
- hadron spectrum.

## Status

Both SU(2) and SU(3) now have fully coupled classical matter-gauge Hamiltonian
engines with non-Abelian Gauss constraints.
