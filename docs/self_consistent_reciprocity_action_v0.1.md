# Self-Consistent Reciprocity Action v0.1

## Purpose

Earlier gravity-like extensions used a content scalar to define an effective
reciprocity metric, but the scalar field equation was still specified
separately.

This extension places the scalar geometry variable and complex matter field in
one action.

Implementation:

`src/self_consistent_reciprocity_action.py`

Tests:

`tests/test_self_consistent_reciprocity_action.py`

## 1. Effective metric

In natural units (c_*=1),

[
g_{mu
u}
=
mathrm{diag}
left(
-e^{-2psi},
e^{2psi},
e^{2psi},
e^{2psi}
ight).
]

Therefore

[
sqrt{-g}=e^{2psi}.
]

## 2. Geometry-scalar action

Take

[
S_psi
=
-rac1{2kappa}
int
d^4x,
sqrt{-g},
g^{mu
u}
partial_mupsi
partial_
upsi.
]

For the reciprocity metric this becomes

[
oxed{
mathcal L_psi
=
rac{e^{4psi}}{2kappa}
dotpsi^2
-
rac{|
ablapsi|^2}{2kappa}.
}
]

The spatial factor cancels exactly.

## 3. Complex scalar matter

For a complex scalar,

[
S_m
=
-int d^4x,
sqrt{-g}
left[
g^{mu
u}
partial_muPhi^*
partial_
uPhi
+
U(|Phi|^2)
ight].
]

This reduces to

[
oxed{
mathcal L_m
=
e^{4psi}|dotPhi|^2
-
|
ablaPhi|^2
-
e^{2psi}U.
}
]

## 4. Matter source for the geometry scalar

Direct variation with respect to (psi) gives

[
oxed{
rac{partialmathcal L_m}{partialpsi}
=
4e^{4psi}|dotPhi|^2
-
2e^{2psi}U.
}
]

For the complex scalar stress tensor this equals

[
oxed{
sqrt{-g}
left(
ho+p_x+p_y+p_z
ight).
}
]

Therefore the scalar geometry is sourced by an active stress-energy combination
rather than by an independently assigned "content charge."

## 5. Static weak-field equation

For a static weak geometry,

[
dotpsi=0,
qquad
|psi|ll1,
]

the Euler-Lagrange equation becomes

[
oxed{
-
abla^2psi
=
kappa
left(
ho+p_x+p_y+p_z
ight).
}
]

This replaces the earlier phenomenological assumption

[
Q_{mathcal C}=q_M M
]

with a source derived from the matter action.

## 6. Rest harmonic identity

For a free spatially uniform rest mode

[
Phi=Ae^{-imt}
]

at (psi=0),

[
|dotPhi|^2
=
m^2|A|^2,
]

[
U=m^2|A|^2.
]

The active source is

[
4m^2|A|^2
-
2m^2|A|^2
=
2m^2|A|^2.
]

The matter energy density is

[
|dotPhi|^2+U
=
2m^2|A|^2.
]

Hence

[
oxed{
ho+p_x+p_y+p_z
=
ho_{m rest}
}
]

for this rest mode.

This gives a concrete route to universal source coupling through rest energy.

## 7. Common causal cone

The principal part of the scalar equation has local characteristic speed

[
oxed{
c_psi=e^{-2psi}
}
]

in coordinate units.

The null condition of the effective metric gives the same coordinate light
speed,

[
oxed{
c_{m null}=e^{-2psi}.
}
]

Thus the geometry scalar and metric null cone agree automatically in this
action.

## 8. Hamiltonian

Canonical momenta are

[
P_psi
=
rac{e^{4psi}}{kappa}dotpsi,
]

[
Pi=e^{4psi}dotPhi.
]

The Hamiltonian density is

[
oxed{
mathcal H
=
rac{kappa}{2}e^{-4psi}P_psi^2
+
rac{|
ablapsi|^2}{2kappa}
+
e^{-4psi}|Pi|^2
+
|
ablaPhi|^2
+
e^{2psi}U.
}
]

The implementation evolves this system with RK4 for research tests.

## 9. What this improves

The previous sequence was

[
	ext{matter}
	o
ho_{mathcal C}
	o
chi
	o
psi
	o
g_{mu
u}.
]

The new sequence is closer to

[
oxed{
S[psi,Phi]
	o
	ext{matter equation}
+
	ext{geometry-scalar equation}
+
g_{mu
u}(psi).
}
]

That removes one independent source-charge assumption.

## 10. Remaining limitation

The effective metric is still chosen by the reciprocity ansatz

[
g_{mu
u}(psi)
=
mathrm{diag}
(
-e^{-2psi},
e^{2psi},
e^{2psi},
e^{2psi}
).
]

The action does not yet derive that metric map from the finite
(mathbb Z_{108}sqcup B_6) kernel.

So the action is self-consistent **given the reciprocity metric ansatz**, not a
complete derivation of spacetime geometry from the canonical kernel.

## Status

The gravity-like sector now has a common matter + geometry-scalar action and a
derived stress-energy source.

This is a substantial reduction in phenomenological freedom, but it remains an
experimental scalar-geometry theory.
