# SU(3) Classical Matter Triplet v0.1

## Purpose

The SU(3) Wilson gauge prototype is extended with a classical fundamental
three-component matter representation.

Implementation:

`src/su3_matter_triplet.py`

Tests:

`tests/test_su3_matter_triplet.py`

## 1. Matter field

At each lattice site,

[
Psi(x)inmathbb C^3.
]

Under local SU(3),

[
oxed{
Psi(x)	o G(x)Psi(x).
}
]

## 2. Covariant derivative

With

[
U_i(x)in SU(3),
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

The tests verify

[
D_iPsi
	o
G(x)D_iPsi.
]

## 3. Gauge-invariant energy

The local norm

[
ho
=
Psi^daggerPsi
]

is gauge invariant.

The prototype matter energy is

[
E
=
sum_{x,i}
|D_iPsi|^2
+
sum_x
left[
m^2ho+lambda_4ho^2
ight].
]

The complete energy is invariant under arbitrary local SU(3) transformations.

## 4. Physical interpretation warning

This is not yet a quark model.

A QCD interpretation would require substantially more structure:

- fermionic matter;
- chiral/flavor structure;
- color-singlet observables;
- running coupling;
- confinement evidence;
- continuum-limit scaling;
- hadron spectrum.

## Status

The project now contains locally gauge-covariant classical matter
representations for both SU(2) and SU(3).
