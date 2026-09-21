# Wilson-Dirac Fermion Reference v0.1

## Purpose

A naive lattice spinor produces extra fermion species.

This extension adds the standard free Wilson-Dirac reference Hamiltonian so any
future Matrix fermion sector must confront fermion doubling explicitly.

Implementation:

`src/wilson_dirac_reference.py`

Tests:

`tests/test_wilson_dirac_reference.py`

## 1. Spatial lattice Hamiltonian

With continuous time and three discrete spatial directions,

[
H(mathbf p)
=
sum_i
alpha_isin p_i
+
eta_D
M_W(mathbf p),
]

where (eta_D) is the Dirac matrix and

[
M_W(mathbf p)
=
m
+
r
sum_i
(1-cos p_i).
]

## 2. Spectrum

[
oxed{
E(mathbf p)
=
pm
sqrt{
sum_isin^2p_i
+
M_W^2
}.
}
]

Each sign is doubly degenerate.

## 3. Naive doubling

For

[
m=0,
qquad
r=0,
]

the energy vanishes whenever every momentum component is either

[
0
]

or

[
pi.
]

In three spatial dimensions this gives

[
oxed{
2^3=8
}
]

zero-energy species.

The tests enumerate all eight explicitly.

## 4. Wilson term

For

[
r>0,
]

a corner containing (n_pi) momentum components equal to (pi) receives

[
oxed{
M_W
=
2rn_pi
}
]

when (m=0).

Thus only

[
(0,0,0)
]

remains massless.

## 5. Continuum limit

At small momentum,

[
sin p_i
approx
p_i,
]

so the naive kinetic part approaches the continuum Dirac dispersion.

The Wilson correction is higher order near the origin but large at doubler
corners.

## 6. Why this matters

Any claim that a discrete Matrix lattice contains physical fermions must address:

- fermion doubling;
- chiral symmetry;
- gauge coupling;
- anomaly structure;
- continuum limit.

A naive four-component spinor field is insufficient.

## 7. Physical interpretation warning

This module is a standard lattice-fermion reference.

It is not a derivation of electrons, quarks, neutrinos, or spin from the
canonical 108-state kernel.

## Status

The repository now has an explicit lattice-fermion correctness target before
any physical fermion identification is attempted.
