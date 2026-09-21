# Fully Coupled Classical Fields v0.1

## Purpose

This is the first repository layer in which all three current classical field
sectors exchange energy dynamically:

- complex matter field;
- neutral content scalar;
- weak U(1) gauge field.

Implementation:

`src/fully_coupled_classical_fields.py`

Tests:

`tests/test_fully_coupled_classical_fields.py`

## 1. Dynamical variables

Matter:

[
Phi,quad Pi.
]

Content scalar:

[
chi,quad v_chi.
]

Gauge field:

[
A_i,quad E_i.
]

## 2. Unified classical Hamiltonian

The implemented energy is

[
H
=
H_{m matter}
+
H_chi
+
H_{m gauge}
+
H_{m interactions}.
]

Explicitly,

[
H
=
sum_x
left[
|Pi|^2
+
sum_i|D_iPhi|^2
+
U(|Phi|^2)
-
g_chichi|Phi|^2
ight]
]

[
+
sum_x
left[
rac{
v_chi^2
}{
2kappa_chi c_chi^2
}
+
rac{
|
ablachi|^2
}{
2kappa_chi
}
ight]
]

[
+
rac12sum_{m links}E_i^2
+
rac{eta}{2}
sum_{m plaquettes}
F_{ij}^2.
]

The fully coupled layer currently uses the quadratic weak gauge curvature rather
than the compact Wilson cosine.

## 3. Matter equation

[
oxed{
Phi_{tt}
=
Delta_APhi
-
U'(|Phi|^2)Phi
+
g_chichiPhi.
}
]

## 4. Content equation

[
oxed{
chi_{tt}
=
c_chi^2
left[

abla^2chi
+
kappa_chi g_chi|Phi|^2
ight].
}
]

## 5. Gauge equation

The link coordinate evolves as

[
oxed{
dot A_i=E_i.
}
]

The electric momentum evolves according to

[
oxed{
dot E_i
=
-rac{partial H}{partial A_i}.
}
]

The matter contribution is derived from the covariant gradient energy:

[
rac{
partial H_{m matter}
}{
partial A_i(x)
}
=
2,mathrm{Im}
left[
Phi^*(x)
e^{iA_i(x)}
Phi(x+hat i)
ight].
]

The tests verify this derivative numerically against finite differences.

The pure gauge force is also checked against a finite-difference derivative of
the magnetic energy.

## 6. Gauss generator

With the repository's positive global U(1) charge convention,

[
ho_{U(1)}
=
2,mathrm{Im}
(Phi^*Pi),
]

the canonical lattice Gauss generator in this sign convention is

[
oxed{
G
=

ablacdot E
+
ho_{U(1)}.
}
]

The sign is stated explicitly because an alternate physical-charge convention
would flip the matter term.

The coupled numerical evolution monitors the maximum residual of (G).

## 7. Conserved quantities

The implementation tracks:

- total classical energy;
- global U(1) charge;
- Gauss residual.

Small-system tests verify approximate energy conservation and tight charge /
Gauss preservation.

## 8. Numerical integrator

All canonical momenta are half-kicked,

[
Pi,quad v_chi,quad E_i,
]

then all coordinates are drifted,

[
Phi,quadchi,quad A_i,
]

followed by the second half kick.

This is a common kick-drift-kick structure for the coupled Hamiltonian system.

## 9. What this accomplishes

The model no longer has to treat:

- matter response,
- scalar source,
- gauge current,

as independent phenomenological rules.

They are all derivatives of one classical energy.

## 10. Remaining gaps

This still is not the final action because:

- the gauge sector is weak/quadratic here rather than compact Wilson;
- the reciprocity geometry is not yet dynamically included in the same action;
- the scalar field still evolves on the fixed lattice rather than the geometry
  it defines;
- no fermionic field exists;
- no non-Abelian gauge field exists;
- no quantum probability structure exists.

## Status

The repository now contains one executable classical Hamiltonian framework for
matter + scalar content + U(1) gauge backreaction.
