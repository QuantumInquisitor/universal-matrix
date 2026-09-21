# Dirac Geometry Backreaction Source v0.1

## Purpose

The reciprocity Dirac sector previously described spinor propagation on a
prescribed geometry.

This extension defines how the spinor energy would source the reciprocity
geometry scalar at the single-particle / semiclassical level.

Implementation:

`src/reciprocity_dirac_geometry_source.py`

Tests:

`tests/test_reciprocity_dirac_geometry_source.py`

## 1. Dirac energy functional

For the Hermitian reciprocity Dirac Hamiltonian,

[
H_D[psi]
=
eta m e^{-psi}
+
rac12
left{
oldsymbolalphacdotmathbf p,
e^{-2psi}
ight},
]

define

[
oxed{
E_D[psi,chi]
=
operatorname{Re}
langlechi|H_D[psi]|chiangle.
}
]

## 2. Geometry source

The geometry source is defined by the Hamiltonian derivative

[
oxed{
S_psi(x)
=
-rac{partial E_D}{partialpsi(x)}.
}
]

This follows the same action/Hamiltonian principle used for scalar matter and
gauge fields.

No independent "fermion gravitational charge" is introduced.

## 3. Analytic lattice source and reference oracle

The local derivative now has an explicit analytic lattice form.

For

[
V=e^{-psi},
qquad
F=e^{-2psi},
]

and the discrete Hermitian central momentum operator (p_i),

[
H_D
=
eta m V
+
rac12sum_i{alpha_i p_i,F},
]

the local geometry source is

[
oxed{
S_psi(x)
=
mV(x),operatorname{Re}
left[
chi^dagger(x)etachi(x)
ight]
+
2F(x)sum_i
operatorname{Re}
left[
chi^dagger(x)alpha_i p_ichi(x)
ight].
}
]

The finite-difference implementation is retained as an independent correctness
oracle for small lattices.

The test suite verifies pointwise agreement between the analytic expression and
the finite-difference derivative on nonuniform random geometries.

## 4. Source-sum identity

A uniform variation

[
psi(x)	opsi(x)+epsilon
]

changes all lattice sites simultaneously.

Therefore

[
oxed{
sum_x S_psi(x)
=
-rac{dE_D}{depsilon}
}
]

for that uniform shift.

The test suite verifies that the sum of the local finite-difference derivatives
matches the independent uniform derivative.

## 5. Rest spinor

For a positive-energy zero-momentum rest spinor,

[
E
=
m e^{-psi}|A|^2.
]

Therefore

[
-rac{dE}{dpsi}
=
E.
]

Hence

[
oxed{
S_psi^{m rest}
=
E_{m rest}.
}
]

The tests verify this identity.

## 6. Significance for source universality

The scalar, gauge, and now Dirac sectors all have source definitions derived
from the same principle:

[
oxed{
S_psi
=
-rac{delta H_{m nongeometry}}{deltapsi}.
}
]

This removes the need to assign composition-specific geometry charges to
fermions.

For a complete stationary isolated composite, the earlier von Laue theorem
still governs the integrated total source.

## 7. What this is not

This is not yet a second-quantized fermion stress tensor.

It is a single-particle / semiclassical backreaction reference based on the
curved Dirac Hamiltonian.

A quantum field theory treatment would require the expectation value of the
renormalized stress-energy operator.

## 8. Coupled backreaction dynamics

The analytic source is now used in

`src/reciprocity_dirac_backreaction.py`

with tests in

`tests/test_reciprocity_dirac_backreaction.py`.

The coupled Hamiltonian is

[
H_{m total}
=
H_{m geometry}
+
operatorname{Re}
langle
chi|H_D[psi]|chi
angle,
]

with

[
H_{m geometry}
=
sum_x
left[
rac{kappa}{2}e^{-4psi}P_psi^2
+
rac{|
ablapsi|^2}{2kappa}
ight].
]

The spinor evolves through

[
ipartial_tchi
=
H_D[psi]chi,
]

while the geometry momentum evolves with the same analytic source,

[
dot P_psi
=
rac{
abla^2psi}{kappa}
+
2kappa e^{-4psi}P_psi^2
+
S_psi.
]

This is an Ehrenfest-type semiclassical backreaction system generated from one
shared Hamiltonian. The tests check short-time spinor-norm conservation and
small total-energy drift.

## 9. Remaining limitation

This still does not constitute second-quantized fermion backreaction.

A quantum field treatment requires a renormalized expectation value of the
stress-energy operator and a consistent vacuum prescription.

## Status

The Dirac sector now has both an analytic action-derived reciprocity geometry
source and a dynamically coupled one-particle / semiclassical backreaction
prototype.
