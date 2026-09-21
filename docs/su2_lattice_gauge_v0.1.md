# SU(2) Lattice Gauge Prototype v0.1

## Purpose

The project previously contained only an Abelian U(1) gauge sector.

This extension adds a mathematically exact non-Abelian SU(2) lattice Wilson
sector.

Implementation:

`src/su2_lattice_gauge.py`

Tests:

`tests/test_su2_lattice_gauge.py`

## 1. Link variables

Each oriented link carries

[
U_i(x)in SU(2).
]

The implementation represents each link as a (2	imes2) complex matrix with

[
U^dagger U=I,
qquad
det U=1.
]

## 2. Local gauge transformation

At every lattice site,

[
G(x)in SU(2).
]

Links transform as

[
oxed{
U_i(x)
	o
G(x)
U_i(x)
G^dagger(x+hat i).
}
]

## 3. Plaquette

The oriented plaquette is

[
P_{ij}(x)
=
U_i(x)
U_j(x+hat i)
U_i^dagger(x+hat j)
U_j^dagger(x).
]

Under local gauge transformation,

[
P_{ij}(x)
	o
G(x)
P_{ij}(x)
G^dagger(x).
]

Therefore its trace is gauge invariant.

## 4. Wilson action

The implemented SU(2) Wilson action is

[
oxed{
S_W
=
eta
sum_p
left[
1
-
rac12
mathrm{Re,Tr},P_p
ight].
}
]

The tests verify invariance under arbitrary independent random gauge
transformations at every site.

## 5. Pure gauge configurations

Starting with identity links and applying an arbitrary local gauge
transformation creates a pure-gauge link configuration.

Its Wilson action remains numerically zero.

## 6. Why SU(2)

SU(2) is the smallest non-Abelian compact Lie group and is therefore the
natural next mathematical test after U(1).

The existence of this module does **not** establish that this SU(2) sector is
the Standard Model electroweak SU(2).

That identification would require:

- chiral fermion representations;
- hypercharge U(1);
- symmetry breaking;
- W/Z mass generation;
- measured coupling structure;
- anomaly consistency.

## Status

The repository now contains exact Abelian and non-Abelian lattice gauge
prototypes.

The SU(2) sector is currently a mathematical gauge extension only.
