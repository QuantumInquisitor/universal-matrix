# Integrated Nested Oscillatory Hierarchy v0.1

## Purpose

This layer combines the reconstructed pieces into one experimental nested
micro-to-macro dynamics without collapsing distinct phase roles.

Implementation:

`src/nested_oscillatory_hierarchy.py`

Tests:

`tests/test_nested_oscillatory_hierarchy.py`

## 1. Layer state

Each layer carries

[
X_ell=
(n_{ell,0},
phi_{P,ell},
phi_{G,ell},
a_ell,
omega_ell).
]

Here:

- (n_{ell,0}) is the canonical base node;
- (phi_P) is the physical polarity clock;
- (phi_G) is the U(1) gauge phase;
- (a_ell) is a signed scale amplitude;
- (omega_ell) is the intrinsic polarity-clock rate.

The canonical discrete state is derived from (phi_P), not stored as an
independent evolving variable.

## 2. Canonical polarity state

For

[
h_ell=
leftlfloor
rac{phi_{P,ell}}{pi}
ightfloor
mod2,
]

the state is

[
n_ell
=
n_{ell,0}+54h_ell
pmod{108},
]

[
sigma_ell
=
sigma_{ell,0}(-1)^{h_ell}.
]

Therefore every polarity half-cycle remains tied to the exact canonical
(T_{54}) involution.

## 3. Observable polarity and transfer carriers

The local polarity carrier is

[
p_ell
=
cosphi_{P,ell},
]

and the scale-transfer carrier is

[
s_ell
=
sinphi_{P,ell}.
]

The two are in quadrature.

That gives:

[
p=pm1
Rightarrow
s=0,
]

so polarity extrema have no scale transfer, while

[
p=0
Rightarrow
|s|=1,
]

so neutral crossings have maximal transfer activation.

## 4. Gauge sector remains separate

Gauge interaction uses

[
Delta_{G,ij}
=
phi_{G,j}
-
phi_{G,i}
+
	heta_{ij}.
]

A representative link energy is

[
E_{G,ij}
=
-kappa_G
cosDelta_{G,ij}.
]

Advancing only the polarity clocks leaves the gauge phases unchanged and
therefore leaves this gauge-link energy unchanged.

That prevents absolute polarity phase from becoming a gauge-dependent
observable.

## 5. Inter-scale exchange

Adjacent scale amplitudes undergo the conservative rotation

[
egin{bmatrix}
a_ell'\
a_{ell+1}'
end{bmatrix}
=
R(delta_ell)
egin{bmatrix}
a_ell\
a_{ell+1}
end{bmatrix}
]

with

[
delta_ell
=
kappa_T
sinphi_{P,ell}
Delta t.
]

Thus transfer direction follows the physical polarity-transition phase.

## 6. Conserved global content

Every pairwise map is orthogonal, so

[
a_ell'^2+a_{ell+1}'^2
=
a_ell^2+a_{ell+1}^2.
]

The complete hierarchy therefore preserves

[
oxed{
mathcal C
=
sum_ell a_ell^2
}
]

up to floating-point error.

The tests verify this over hundreds of steps.

## 7. Current evolution law

At present,

[
dotphi_{P,ell}
=
omega_ell.
]

This is intentionally minimal.

No gauge field currently drives the physical polarity clock, and no polarity
clock directly shifts the U(1) gauge phase.

That separation is deliberate until a gauge-invariant coupling law is derived.

## 8. What this achieves

The architecture now has one coherent nested cycle:

[
oxed{
	ext{canonical node}
leftrightarrow
	ext{physical polarity clock}
leftrightarrow
	ext{neutral crossing}
leftrightarrow
	ext{conservative scale transfer}
}
]

while the U(1) gauge phase remains a separate redundant coordinate used only
through gauge-invariant combinations.

## 9. Next missing law

The next deep question is:

[
oxed{
	ext{What determines }omega_ell
	ext{ and }kappa_T
	ext{ from the architecture?}
}
]

Until those are derived, the hierarchy is structurally coherent but not a
parameter-free physical theory.

Candidate sources for (omega_ell) and (kappa_T) include:

- local quadratic content (a_ell^2);
- canonical routing state;
- six-gate boundary orientation;
- topological winding;
- scale index;
- gauge-invariant field strength.

The correct dependence should be selected by symmetry, conservation, and
experimental falsifiability rather than numerical convenience.
