# Space-Time Dependent Reciprocity Dirac Evolution v0.1

## Purpose

The repository previously treated two complementary curved-spinor limits:

- static spatially varying (psi(mathbf x));
- homogeneous time-varying (psi(t)).

This extension combines both into prescribed

[
psi=psi(t,mathbf x).
]

Implementation:

`src/reciprocity_dirac_spacetime_background.py`

Tests:

`tests/test_reciprocity_dirac_spacetime_background.py`

## 1. Geometry

[
ds^2
=
-e^{-2psi(t,mathbf x)}dt^2
+
e^{2psi(t,mathbf x)}dmathbf x^2.
]

## 2. Local volume rescaling

Define

[
oxed{
chi
=
e^{3psi/2}Psi.
}
]

Then the ordinary flat lattice norm of (chi) equals the curved spatial norm
of the original spinor:

[
oxed{
int chi^daggerchi,d^3x
=
int e^{3psi}Psi^daggerPsi,d^3x.
}
]

This removes the explicit temporal volume-dilution term from the rescaled
equation.

## 3. Instantaneous Hermitian Hamiltonian

The rescaled spinor evolves with

[
oxed{
H(t)
=
eta m e^{-psi}
+
rac12
left{
oldsymbolalphacdotmathbf p,
e^{-2psi}
ight}.
}
]

The spatial geometry-gradient/spin-connection term is contained exactly in the
anticommutator.

Expanding the kinetic part gives

[
rac12{alpha_i p_i,F}
=
-ialpha_i
left[
Fpartial_i
+
rac12(partial_iF)
ight],
]

where

[
F=e^{-2psi}.
]

## 4. Time dependence

The Hamiltonian is evaluated on each time slice using the current
(psi(t,mathbf x)).

The explicit (dotpsi) connection term that appears in the unrescaled spinor
has already been absorbed by

[
chi=e^{3psi/2}Psi.
]

Therefore

[
oxed{
ipartial_tchi
=
H(t)chi.
}
]

## 5. Hermiticity

For every fixed time slice,

[
H(t)^dagger=H(t)
]

under the periodic lattice inner product.

The tests verify this numerically for random spatially varying geometry.

## 6. Norm conservation

Because the instantaneous Hamiltonian is Hermitian,

[
rac{d}{dt}
langlechi|chiangle
=
0.
]

The test suite evolves a geometry containing both time dependence and spatial
variation and verifies conservation of the rescaled norm.

The reconstructed original spinor satisfies the equivalent curved norm
identity.

## 7. Relation to earlier modules

This module contains both previous limits:

### Static spatial limit

If

[
partial_tpsi=0,
]

it reduces to the existing static reciprocity Dirac operator.

### Homogeneous temporal limit

If

[

ablapsi=0,
]

the anticommutator reduces to

[
e^{-2psi}oldsymbolalphacdotmathbf p,
]

matching the homogeneous time-dependent Dirac bridge.

## 8. Remaining spinor gap

This solves propagation on a **prescribed** reciprocity geometry.

The next deeper step is backreaction:

[
oxed{
	ext{Dirac stress-energy}
ightarrow
psi
}
]

inside the same action.

After that, the central fermion problem becomes chirality and anomaly
consistency rather than the spin connection itself.

## Status

The repository now contains a Hermitian lattice Dirac evolution for prescribed
time- and space-dependent reciprocity geometry.
