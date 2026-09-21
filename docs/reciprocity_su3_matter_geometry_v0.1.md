# SU(3) Matter + Gauge + Reciprocity Geometry v0.1

## Purpose

The repository previously had:

- SU(3) matter + gauge dynamics;
- SU(3) gauge + reciprocity-geometry dynamics.

This extension combines those into one Hamiltonian system.

Implementation:

`src/reciprocity_su3_matter_geometry.py`

Tests:

`tests/test_reciprocity_su3_matter_geometry.py`

## 1. Fields

Matter:

[
Psi(x)inmathbb C^3,
qquad
Pi(x)inmathbb C^3.
]

Geometry:

[
psi(x),
qquad
P_psi(x).
]

Gauge:

[
U_i(x)in SU(3),
qquad
E_i^a(x),quad a=1,ldots,8.
]

## 2. Hamiltonian

[
H
=
H_psi
+
H_{m matter}
+
H_{SU(3)}.
]

Geometry:

[
H_psi
=
sum_x
left[
rac{kappa}{2}
e^{-4psi}
P_psi^2
+
rac{|
ablapsi|^2}{2kappa}
ight].
]

Matter:

[
oxed{
H_{m matter}
=
sum_x
left[
e^{-4psi}|Pi|^2
+
e^{2psi}V(Psi^daggerPsi)
ight]
+
sum_{ell}
|D_ellPsi|^2.
}
]

The spatial gauge-covariant hopping term is unweighted because

[
sqrt{-g},g^{ij}
=
delta^{ij}
]

for the reciprocity metric.

Gauge:

[
H_{SU(3)}
=
rac12
sum_ell
w_ell E_ell^aE_ell^a
+
eta
sum_p
w_p
left[
1-rac13operatorname{ReTr}U_p
ight].
]

## 3. Matter geometry source

The matter contribution is

[
oxed{
S_psi^{m matter}
=
4e^{-4psi}|Pi|^2
-
2e^{2psi}V.
}
]

This is the canonical form of the same stress-energy source derived in the
self-consistent reciprocity action.

## 4. Gauge geometry source

The SU(3) contribution remains

[
oxed{
S_psi^{SU(3)}
=
-rac{partial H_{SU(3)}}{partialpsi}.
}
]

The full geometry source is

[
oxed{
S_psi^{m total}
=
S_psi^{m matter}
+
S_psi^{SU(3)}.
}
]

The test suite verifies this against a direct finite-difference derivative of
the complete non-geometry Hamiltonian.

## 5. Matter dynamics

[
dotPsi
=
e^{-4psi}Pi.
]

[
dotPi
=
Delta_UPsi
-
e^{2psi}
V'(Psi^daggerPsi)Psi.
]

## 6. Gauge dynamics

The link drift is geometry weighted:

[
U_ell
ightarrow
exp
left[
iDelta t,
w_ell E_ell^aT_a
ight]
U_ell.
]

The electric force contains:

[
oxed{
dot E
=
F_{m Wilson}^{(psi)}
-
J_{m matter}.
}
]

The matter current is unchanged by the geometry scalar because the spatial
hopping term is unweighted.

## 7. Geometry dynamics

[
dotpsi
=
kappa e^{-4psi}P_psi.
]

[
dot P_psi
=
rac{
abla^2psi}{kappa}
+
2kappa e^{-4psi}P_psi^2
+
S_psi^{m matter}
+
S_psi^{SU(3)}.
]

## 8. Verification

The tests check:

- local SU(3) gauge invariance of the full Hamiltonian;
- exact geometry-source derivative against finite differences;
- free-rest matter source equals rest-energy density;
- controlled small-step total-energy drift;
- finite coupled Gauss residual.

## 9. Significance

The SU(3) sector now contains one classical engine in which:

[
oxed{
	ext{matter}
leftrightarrow
SU(3)	ext{ gauge field}
leftrightarrow
	ext{reciprocity geometry}
}
]

all backreact dynamically.

This closes one of the main gaps identified in the previous status map.

## 10. Remaining gaps

The next major gaps are:

1. time-dependent curved-space Dirac/spin connection;
2. chiral lattice fermions and anomaly constraints;
3. second quantization and genuine quantum states;
4. dimensional-scale derivation;
5. strong-field observational confrontation.

## Status

The SU(3) matter, gauge, and reciprocity-geometry sectors now share one
executable classical Hamiltonian framework.
