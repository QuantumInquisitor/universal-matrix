# SU(3) x SU(2) x U(1) Weyl Anomaly Ledger v0.1

## Purpose

This extension adds an explicit product-group anomaly bookkeeping layer for Weyl
fermion representations transforming under

[
SU(3)	imes SU(2)	imes U(1).
]

Implementation:

`src/product_group_anomaly_ledger.py`

Tests:

`tests/test_product_group_anomaly_ledger.py`

The module is a representation-theory ledger. It does not claim that the
Universal Matrix has derived Standard Model multiplets or hypercharges.

## 1. Supported multiplets

Each physical Weyl multiplet carries:

- an SU(3) representation;
- an SU(2) representation;
- a U(1) charge;
- a handedness sign;
- an optional multiplicity.

The first supported representation set is deliberately small:

[
SU(3):
quad
1,;3,;ar 3,
]

and

[
SU(2):
quad
1,;2.
]

This is enough to test the familiar fundamental product representations without
pretending the general representation problem is already solved.

## 2. Normalizations

The ledger uses

[
T(3)=T(ar3)=rac12
]

for the SU(3) quadratic Dynkin index and

[
A(3)=+1,
qquad
A(ar3)=-1
]

for the SU(3) cubic anomaly index.

For the SU(2) doublet,

[
T(2)=rac12.
]

The SU(2) fundamental is pseudoreal, so there is no local perturbative
(SU(2)^3) anomaly.

## 3. SU(3)^3 coefficient

For physical handedness

[
chi_i=pm1,
]

the cubic color coefficient is

[
oxed{
C_{SU(3)^3}
=
sum_i
chi_i
A_3(R_{3,i})
dim(R_{2,i}).
}
]

The spectator weak dimension is included explicitly.

## 4. SU(3)^2 U(1)

The mixed color-Abelian coefficient is

[
oxed{
C_{SU(3)^2U(1)}
=
sum_i
chi_i
Y_i
T_3(R_{3,i})
dim(R_{2,i}).
}
]

## 5. SU(2)^2 U(1)

The mixed weak-Abelian coefficient is

[
oxed{
C_{SU(2)^2U(1)}
=
sum_i
chi_i
Y_i
T_2(R_{2,i})
dim(R_{3,i}).
}
]

The spectator color dimension is included explicitly.

## 6. U(1)^3

The Abelian cubic coefficient is

[
oxed{
C_{U(1)^3}
=
sum_i
chi_i
Y_i^3
dim(R_{3,i})
dim(R_{2,i}).
}
]

## 7. Mixed gravitational-U(1)

The mixed gravitational coefficient is

[
oxed{
C_{mathrm{grav}^2U(1)}
=
sum_i
chi_i
Y_i
dim(R_{3,i})
dim(R_{2,i}).
}
]

## 8. SU(2) global condition

The perturbative coefficients above do not detect the mod-2 SU(2) global
obstruction.

For the fundamental doublets supported here, the ledger separately counts

[
N_2
=
sum_{	ext{doublets}}
	ext{multiplicity}	imes
dim(R_3).
]

The supported global condition is

[
oxed{
N_2
equiv
0
pmod2.
}
]

Handedness does not change this mod-2 count because the SU(2) fundamental is
pseudoreal.

The test suite includes a single neutral SU(2) doublet for which every local
perturbative coefficient vanishes while the global parity condition fails.

This prevents the two anomaly notions from being collapsed into one boolean.

## 9. Standard Model one-generation correspondence target

The module includes a convenience reference containing the familiar physical
one-generation multiplets:

[
Q_L:
(3,2)_{1/6},
]

[
u_R:
(3,1)_{2/3},
]

[
d_R:
(3,1)_{-1/3},
]

[
L_L:
(1,2)_{-1/2},
]

[
e_R:
(1,1)_{-1}.
]

An optional right-handed neutrino

[

u_R:
(1,1)_0
]

can also be included.

With physical handedness kept explicit, the supported ledger verifies

[
C_{SU(3)^3}=0,
]

[
C_{SU(3)^2U(1)}=0,
]

[
C_{SU(2)^2U(1)}=0,
]

[
C_{U(1)^3}=0,
]

and

[
C_{mathrm{grav}^2U(1)}=0.
]

The weak-doublet count is

[
3+1=4,
]

so the supported SU(2) mod-2 condition is also satisfied.

This is used strictly as a known consistency target.

It is **not** evidence that the Matrix has derived this spectrum.

## 10. What this closes

The repository can now keep separate ledgers for:

- Abelian anomaly coefficients;
- non-Abelian cubic color anomaly;
- mixed non-Abelian-Abelian anomalies;
- mixed gravitational-U(1);
- SU(2) global doublet parity.

This is substantially safer than declaring a representation "anomaly free"
based only on the cubic U(1) sum.

## 11. What remains open

The ledger does not yet derive:

1. the actual chiral multiplet spectrum from the finite kernel;
2. hypercharge quantization;
3. family replication;
4. non-Abelian local anomaly density from the overlap measure;
5. global anomalies beyond the supported SU(2) fundamental parity check;
6. second-quantized chiral dynamics;
7. continuum renormalization and running couplings.

## Status

The project now has an explicit product-group anomaly bookkeeping layer capable
of testing a candidate

[
SU(3)	imes SU(2)	imes U(1)
]

Weyl spectrum against the supported perturbative and SU(2) global consistency
conditions.

The Standard Model generation is a correspondence benchmark, not a derived
output of the Universal Matrix.
