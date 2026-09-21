# Static Reciprocity Dirac Operator v0.1

## Purpose

The constant-background Dirac bridge established the correct fermion redshift
and causal cone when (psi) is uniform.

This extension includes spatially varying static (psi(mathbf x)), where
tetrad gradients and the spin connection matter.

Implementation:

`src/reciprocity_dirac_static_background.py`

Tests:

`tests/test_reciprocity_dirac_static_background.py`

## 1. Exact static isotropic Hamiltonian

For a static isotropic metric

[
ds^2
=
-V(mathbf x)^2dt^2
+
W(mathbf x)^2dmathbf x^2,
]

the exact Hermitian Dirac Hamiltonian can be written

[
oxed{
H
=
eta_D mV
+
rac12
left{
oldsymbol{alpha}cdotmathbf p,
F
ight},
}
]

with

[
F=rac VW.
]

This form is standard in the curved-space Dirac literature, including work by
Obukhov, Silenko, and Teryaev.

## 2. Reciprocity specialization

For

[
V=e^{-psi},
qquad
W=e^psi,
]

we obtain

[
F=e^{-2psi}.
]

Therefore

[
oxed{
H
=
eta_D m e^{-psi}
+
rac12
left{
oldsymbol{alpha}cdotmathbf p,
e^{-2psi}
ight}.
}
]

## 3. Geometry-gradient term

Expanding the anticommutator gives

[
H
=
eta_D m e^{-psi}
-ioldsymbol{alpha}cdot
left[
F
abla
+
rac12
abla F
ight].
]

The

[
rac12
abla F
]

term is the static tetrad/spin-connection contribution in this Hermitian
representation.

It must not be dropped when (psi) varies in space.

## 4. Lattice implementation

The momentum operator uses the periodic central Hermitian difference

[
p_iPsi(x)
=
-i
rac{
Psi(x+hat i)-Psi(x-hat i)
}{
2a
}.
]

The code evaluates the operator as the discrete anticommutator itself:

[
rac12
left[
p_i(FPsi)
+
F p_iPsi
ight].
]

That ordering preserves Hermiticity much more cleanly than discretizing the
expanded derivative terms independently.

## 5. Verification

The tests verify:

- Hermiticity for random spatially varying (psi);
- exact constant-(psi) plane-wave lattice dispersion;
- reduction to the flat central Dirac operator at (psi=0);
- pointwise equality of the massless principal speed and reciprocity null
  speed,

[
oxed{
c_{m Dirac}
=
c_{m null}
=
e^{-2psi}.
}
]

## 6. Relation to Wilson fermions

This module isolates the curved-background Dirac/spin-connection structure.

It does not yet add a geometry-dependent Wilson doubler-suppression term.

The existing U(1) Wilson-Dirac module remains the lattice-doubling reference.

A later fully curved Wilson-Dirac construction must preserve:

- Hermiticity;
- local gauge covariance;
- correct curved-space continuum limit;
- doubler lifting.

## 7. Scope

The current result assumes

[
partial_tpsi=0.
]

A time-dependent reciprocity background requires the full spacetime spin
connection and is still open.

## Status

The fermion sector now has an exact static reciprocity-background Dirac
operator with the required geometry-gradient term and common causal cone.
