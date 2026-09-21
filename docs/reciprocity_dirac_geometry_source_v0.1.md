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

## 3. Reference implementation

The current implementation evaluates the local derivative by symmetric finite
differences in (psi(x)).

This is intentionally a correctness oracle for small lattices.

A future analytic source can be derived and compared against this oracle.

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

## 8. Next step

The immediate next improvement is an analytic lattice expression for

[
S_psi(x)
]

that can be verified against the finite-difference oracle and used efficiently
inside dynamical geometry evolution.

## Status

The Dirac sector now has an action-derived reciprocity geometry source at the
small-lattice semiclassical level.
