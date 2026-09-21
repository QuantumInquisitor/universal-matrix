# Fully Coupled Compact U(1) Fields v0.1

## Purpose

The first fully coupled matter-content-gauge system used the quadratic weak
gauge energy

[
rac{eta}{2}sum F_{ij}^2.
]

This extension upgrades the gauge sector to compact U(1) Wilson dynamics while
retaining the same action-derived matter and content couplings.

Implementation:

`src/fully_coupled_compact_fields.py`

Tests:

`tests/test_fully_coupled_compact_fields.py`

## 1. Compact gauge energy

The gauge potential energy is

[
oxed{
V_{m gauge}
=
eta
sum_p
left(
1-cos F_p
ight).
}
]

This is invariant under

[
F_p	o F_p+2pi n.
]

## 2. Compact gauge force

The canonical electric field evolves through

[
dot E_i
=
-rac{
partial H
}{
partial A_i
}.
]

For the Wilson action the plaquette contribution enters through

[
sin F_p
]

rather than the weak-field approximation (F_p).

The implementation verifies the compact gauge force against a direct numerical
finite-difference derivative of the Wilson energy.

## 3. Matter coupling

Matter remains transported by the compact link phase

[
e^{iA_i(x)}.
]

Therefore the matter sector was already naturally compatible with the compact
gauge interpretation.

The matter-link derivative is unchanged:

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

## 4. Link wrapping

After each gauge-coordinate drift,

[
A_i
	o
A_i+Delta t,E_i,
]

the link phase is wrapped to the principal interval

[
[-pi,pi).
]

This changes coordinate representation but not the compact link transporter.

## 5. Coupled invariants

The compact coupled system monitors:

- total energy;
- global U(1) matter charge;
- lattice Gauss residual.

Small-field tests verify approximate energy conservation and tight charge /
Gauss preservation.

## 6. Weak-field limit

For

[
|F|ll1,
]

[
1-cos F
=
rac12F^2
+
O(F^4).
]

Therefore the compact system reduces continuously to the previously tested weak
fully coupled model.

## 7. Why this matters

The fully coupled model now supports:

- nonlinear matter self-interaction;
- reciprocal matter-content scalar coupling;
- dynamic gauge backreaction;
- compact U(1) topology.

That is the strongest internally unified classical field system currently in
the repository.

## 8. Remaining major gaps

The next large theoretical gaps are no longer basic U(1) backreaction. They are:

- self-consistent reciprocity geometry in the same action;
- non-Abelian gauge structure;
- fermionic/spinor matter;
- quantum probability and entanglement;
- robust nonlinear soliton branch continuation;
- experimental calibration or derivation of the remaining dimensional scales.

## Status

The project now has an executable fully coupled classical matter + content +
compact U(1) Hamiltonian system.
