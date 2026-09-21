# Gauge Hamiltonian Extension v0.1

## Purpose

This extension adds an explicit evolution coordinate to the routing-by-scale U(1) gauge lattice.

Implementation:

`src/gauge_hamiltonian.py`

Tests:

`tests/test_gauge_hamiltonian.py`

The goal is to determine whether the Universal Matrix can support a source-free gauge dynamics with a Gauss constraint and a weak-field wave sector before assigning any physical spacetime interpretation.

## 1. Canonical variables

The link angles are generalized coordinates:

[
	heta_ell
]

and the corresponding real link variables

[
E_ell
]

are their conjugate momenta.

The Hamiltonian is

[
H
=
rac12sum_{	ext{links}}E^2
+
etasum_{	ext{plaquettes}}
left(1-cos Fight).
]

The first term is electric-like kinetic energy. The second term is magnetic-like gauge-curvature energy.

These names are provisional until a physical spacetime and electromagnetic interpretation is justified.

## 2. Hamilton equations

The evolution law is

[
dot	heta=E
]

and

[
dot E=-rac{partial V}{partial	heta}.
]

The potential derivative is supplied by the exact Wilson-action Euler-Lagrange residuals already implemented in `gauge_dynamics.py`.

Numerical evolution uses a second-order symplectic leapfrog update:

1. half momentum kick;
2. full link-angle drift;
3. half momentum kick.

This is chosen because long-term Hamiltonian evolution should approximately conserve energy rather than introducing systematic numerical damping.

## 3. Discrete Gauss quantity

At each lattice site the discrete divergence of link momenta is

[
G_{ell,k}
=
E^r_{ell,k}-E^r_{ell,k-1}
+
E^s_{ell,k}
-
E^s_{ell-1,k},
]

with the inter-layer terms omitted where no link exists.

With a charge variable (ho_{ell,k}), the constraint residual is

[
mathcal G_{ell,k}
=
G_{ell,k}-ho_{ell,k}.
]

The source-free sector is

[
oxed{G_{ell,k}=0}.
]

Because the gauge potential energy is locally gauge invariant, the exact Hamiltonian flow preserves the associated Gauss generator. Numerical evolution should preserve it up to floating-point/integration error.

## 4. Weak-field limit

For small plaquette angle,

[
1-cos F
=
rac12F^2+O(F^4),
]

so

[
H
approx
rac12sum E^2
+
rac{eta}{2}sum F^2.
]

This is the standard quadratic electric-plus-magnetic structure expected of an Abelian lattice gauge field.

The implementation exposes both the compact and weak-field Hamiltonians so their agreement can be tested quantitatively.

## 5. Tests implemented

The regression suite checks:

- zero field is stationary;
- total discrete divergence sums to zero;
- source-free Gauss constraint is preserved under evolution;
- leapfrog evolution has small energy drift for sufficiently small timestep;
- weak-field Hamiltonian agrees with compact energy at small field amplitude;
- a supplied charge distribution satisfies (G-ho=0) when matched to the link-momentum divergence;
- magnetic-like field equals gauge-invariant plaquette curvature.

## 6. What this establishes

The Matrix gauge extension now has:

[
oxed{	ext{local U(1) gauge invariance}}
]

[
oxed{	ext{gauge-invariant curvature}}
]

[
oxed{	ext{Hamiltonian evolution}}
]

[
oxed{	ext{electric-like conjugate variables}}
]

[
oxed{	ext{source-free Gauss constraint}}
]

[
oxed{	ext{weak-field }E^2+F^2	ext{ energy}}
]

This is substantially closer to a Maxwell-like lattice system than the earlier static gauge action.

## 7. What is still missing for physical Maxwell theory

The present gauge lattice coordinates are:

[
(ell,k)
]

where (ell) is nested scale and (k) is routing position.

They have not yet been identified with physical spatial coordinates.

Therefore the current equations should not yet be written as physical

[

ablacdotmathbf E=ho
]

or

[

abla	imesmathbf B-partial_tmathbf E=mathbf J
]

in three-dimensional space.

To justify that step the model still needs:

1. a physical spatial embedding;
2. at least the appropriate independent spatial directions;
3. a dimensional lattice spacing;
4. current/source evolution;
5. a continuum-limit analysis;
6. wave dispersion and propagation-speed calculations.

## 8. Next test

The immediate next test is the weak-field normal-mode dispersion relation.

Linearizing the Hamiltonian equations should give a discrete wave equation. The resulting numerical/analytic dispersion relation can then be derived from the Matrix lattice itself.

That is the next point where a propagation speed can emerge as a dimensionless lattice quantity before any SI calibration.

## Status

This extension establishes a source-free Hamiltonian U(1) gauge sector on the Matrix routing-by-scale cylinder.

It does not yet establish that the sector is physical electromagnetism, nor that its propagation speed equals the measured speed of light.
