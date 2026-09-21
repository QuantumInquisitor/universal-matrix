# Unified Variational Matter-Gauge-Content Energy v0.1

## Purpose

The project previously had separate mathematical sectors for:

- a neutral scalar content field;
- compact U(1) gauge links;
- candidate matter amplitudes.

This extension places them in one classical gauge-invariant variational energy.

Implementation:

`src/unified_variational_action.py`

Tests:

`tests/test_unified_variational_action.py`

## 1. Fields

The present classical state contains:

[
chi(mathbf x)
]

a neutral scalar content potential,

[
Phi(mathbf x)inmathbb C
]

a classical complex matter amplitude, and

[
A_i(mathbf x)
]

compact U(1) link phases.

(Phi) is **not** identified with a quantum probability wavefunction.

## 2. Static energy

The implemented energy is

[
E
=
E_chi
+
E_{m matter}
+
E_{m gauge}
+
E_{m coupling}.
]

The scalar part is

[
E_chi
=
sum_x
rac{
|
ablachi|^2
}{
2kappa_chi
}.
]

The matter part contains

[
|D_iPhi|^2
+
m^2|Phi|^2
+
lambda_4|Phi|^4
+
lambda_6|Phi|^6.
]

The scalar-matter coupling is

[
E_{m coupling}
=
-g_chi
sum_x
chi|Phi|^2.
]

The compact gauge sector uses the Wilson plaquette energy.

## 3. Local U(1) symmetry

The matter field transforms as

[
Phi(x)
	o
e^{ialpha(x)}
Phi(x),
]

and the link phase as

[
A_i(x)
	o
A_i(x)
+
alpha(x)
-
alpha(x+hat i).
]

The complete implemented energy is invariant under that transformation.

The tests verify local gauge invariance numerically for random configurations.

## 4. Scalar variation

Varying the energy with respect to (chi) gives

[
oxed{
-rac1{kappa_chi}

abla^2chi
-
g_chi|Phi|^2
=
0
}
]

for the current sign convention.

Thus the matter amplitude itself supplies a source for the content field.

This is a significant step because source density is no longer an unrelated
external array.

## 5. Bounded nonlinear matter potential

The implemented polynomial is

[
U(|Phi|)
=
m^2|Phi|^2
+
lambda_4|Phi|^4
+
lambda_6|Phi|^6.
]

A positive sextic coefficient can keep the large-amplitude energy bounded even
when the quartic coefficient is negative.

This structure is useful for searching for localized classical finite-charge
configurations.

## 6. What is still missing

The present object is a static energy functional.

A complete action still requires time-dependent kinetic terms and a consistent
choice of independent variables in the reciprocity geometry.

Therefore this module is the first common **variational kernel**, not yet the
final covariant action.

## Status

The matter, content, and U(1) gauge sectors now share one gauge-invariant
classical variational energy.
