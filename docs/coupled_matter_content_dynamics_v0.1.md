# Reciprocal Matter-Content Dynamics v0.1

## Purpose

Earlier modules allowed matter to source a content field and separately allowed
a content potential to influence clocks or trajectories.

This extension derives both directions of interaction from one classical
Lagrangian coupling.

Implementation:

`src/coupled_matter_content_dynamics.py`

Tests:

`tests/test_coupled_matter_content_dynamics.py`

## 1. Classical fields

The dynamical fields are:

[
Phi(mathbf x,t)inmathbb C
]

for matter, and

[
chi(mathbf x,t)inmathbb R
]

for the neutral content scalar.

Spatial compact U(1) link phases remain fixed in this first coupled version.

## 2. Coupled Lagrangian

The flat-background classical Lagrangian density is

[
mathcal L
=
|D_tPhi|^2
-
|D_iPhi|^2
-
U(|Phi|^2)
+
g_chichi|Phi|^2
+
rac{
(partial_tchi)^2
}{
2kappa_chi c_chi^2
}
-
rac{
|
ablachi|^2
}{
2kappa_chi
}.
]

## 3. Matter equation

Variation with respect to (Phi^*) gives

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

Thus positive (chi) modifies the local effective matter potential.

## 4. Content equation

Variation with respect to (chi) gives

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

Therefore matter amplitude sources the content field.

## 5. Reciprocity

The same coupling constant

[
g_chi
]

appears in both equations.

This is important.

Matter does not source one field with one coefficient and then respond through
an unrelated second coefficient.

The action ties both directions together.

## 6. Total energy

The implemented total energy is

[
E
=
int
left[
|Pi|^2
+
|D_iPhi|^2
+
U(|Phi|^2)
-
g_chichi|Phi|^2
+
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
d^3x.
]

The tests verify approximate energy conservation for a small coupled
configuration.

## 7. U(1) charge

Because the scalar coupling depends only on

[
|Phi|^2,
]

the global U(1) phase symmetry remains intact.

Therefore the classical matter charge

[
Q
=
2,mathrm{Im}
int
Phi^*Pi,d^3x
]

remains conserved in the coupled dynamics.

## 8. Gauge invariance

The combined energy remains invariant under local spatial U(1) gauge
transformations of the matter field and fixed link variables.

## 9. What is still incomplete

The gauge field itself is not yet dynamically backreacting in this combined
matter-content system.

The next fully coupled classical action would need simultaneous evolution of:

- matter field (Phi);
- scalar content field (chi);
- U(1) gauge links (A_i);
- gauge electric momenta (E_i).

That system must preserve:

- U(1) gauge symmetry;
- Gauss constraint;
- matter charge continuity;
- total energy exchange among all sectors.

## Status

The repository now contains a reciprocal action-derived matter↔content field
system rather than two independent one-way couplings.
