# U(1) Gauge-Covariant Wilson-Dirac Lattice v0.1

## Purpose

The free Wilson-Dirac reference removes naive lattice doublers, but physical
fermion candidates must also couple consistently to gauge fields.

This extension adds the position-space U(1)-gauge-covariant Wilson-Dirac
Hamiltonian.

Implementation:

`src/u1_wilson_dirac_lattice.py`

Tests:

`tests/test_u1_wilson_dirac_lattice.py`

## 1. Spinor field

At each site,

[
psi(x)inmathbb C^4.
]

The compact U(1) transporter is

[
U_i(x)=e^{iA_i(x)}.
]

## 2. Local gauge transformation

[
psi(x)
	o
e^{ialpha(x)}psi(x),
]

[
A_i(x)
	o
A_i(x)
+
alpha(x)
-
alpha(x+hat i).
]

## 3. Gauge-covariant kinetic term

The lattice kinetic contribution is

[
rac{
U_i(x)psi(x+hat i)
-
U_i^dagger(x-hat i)psi(x-hat i)
}{
2i
}.
]

It multiplies the Dirac matrix (alpha_i).

## 4. Wilson term

The gauge-covariant Wilson correction is

[
rac r2
left[
2psi(x)
-
U_i(x)psi(x+hat i)
-
U_i^dagger(x-hat i)psi(x-hat i)
ight].
]

It multiplies the Dirac (eta) matrix.

## 5. Complete Hamiltonian

[
oxed{
Hpsi
=
sum_i
alpha_i
rac{
U_ipsi_{+i}
-
U_i^dagger{}_{-i}psi_{-i}
}{
2i
}
+
eta
left[
mpsi
+
rac r2
sum_i
left(
2psi
-
U_ipsi_{+i}
-
U_i^dagger{}_{-i}psi_{-i}
ight)
ight].
}
]

## 6. Verification

The tests verify:

- local U(1) covariance;
- gauge invariance of spinor density;
- Hermiticity of the position-space Hamiltonian;
- exact agreement with the momentum-space Wilson-Dirac reference when
  (A_i=0).

## 7. What this is not

This is a single-particle classical lattice spinor operator.

It is not yet:

- a second-quantized fermion field theory;
- chiral electroweak matter;
- an electron model;
- a quark model.

## Status

The repository now has a gauge-covariant lattice fermion correctness layer that
handles both local U(1) symmetry and Wilson doubler suppression.
