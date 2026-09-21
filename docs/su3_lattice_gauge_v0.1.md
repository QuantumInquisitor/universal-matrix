# SU(3) Lattice Gauge Prototype v0.1

## Purpose

This extension adds a second exact non-Abelian lattice gauge sector based on
SU(3).

Implementation:

`src/su3_lattice_gauge.py`

Tests:

`tests/test_su3_lattice_gauge.py`

## 1. Link variables

Each oriented link carries

[
U_i(x)in SU(3).
]

The implementation verifies

[
U^dagger U=I,
qquad
det U=1.
]

## 2. Local transformation

At every site,

[
G(x)in SU(3),
]

and

[
oxed{
U_i(x)
	o
G(x)U_i(x)G^dagger(x+hat i).
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

Its trace is gauge invariant.

## 4. Wilson action

The implemented action is

[
oxed{
S_W
=
eta
sum_p
left[
1
-
rac13
mathrm{Re,Tr},P_p
ight].
}
]

Random local SU(3) transformations leave the action invariant in the test
suite.

## 5. Random SU(3) generation

Random complex matrices are projected to unitary matrices by QR decomposition
and then corrected to determinant one.

The resulting matrices are tested for special unitarity.

## 6. Physical interpretation warning

This sector is not yet identified with QCD.

A physical color interpretation would require:

- triplet matter representation;
- dynamical gauge Hamiltonian;
- confinement behavior;
- asymptotic scaling;
- measured coupling structure;
- appropriate fermionic matter.

## Status

The repository now contains exact U(1), SU(2), and SU(3) lattice gauge
prototypes at the mathematical level.
