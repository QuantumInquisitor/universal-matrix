# Optimized SU(2) Hamiltonian Dynamics v0.1

## Purpose

The SU(2) Hamiltonian reference uses group-direction finite differences to
compute the Wilson force. That is accurate but scales poorly.

This extension implements the analytic staple force and validates it against
the reference.

Implementation:

`src/su2_hamiltonian.py`

Tests:

`tests/test_su2_hamiltonian.py`

Reference oracle:

`src/su2_hamiltonian_reference.py`

## 1. Staple sum

For each link

[
U_mu(x),
]

the staple matrix is the sum over every

[

u
eqmu
]

of the forward and backward three-link paths that complete a plaquette through
the target link.

Denote that sum by

[
K_mu(x).
]

The Wilson contribution containing the link can be written

[
V_{m link}
=
	ext{constant}
-
rac{eta}{2}
operatorname{ReTr}
left[
U_mu(x)K_mu(x)
ight].
]

## 2. Analytic force

Under the left group variation

[
U_mu
	o
e^{iepsilon T_a}
U_mu,
]

the force is

[
oxed{
F_mu^a
=
-rac{eta}{2}
operatorname{ImTr}
left[
T_aU_mu K_mu
ight].
}
]

## 3. Reference validation

The test suite evaluates the same force with the slower symmetric group
finite-difference definition

[
F_mu^a
=
-
rac{
V(e^{+iepsilon T_a}U_mu)
-
V(e^{-iepsilon T_a}U_mu)
}{
2epsilon
}.
]

The analytic and reference forces are compared pointwise on random SU(2) link
configurations.

## 4. Gauss identity

Gauge invariance implies that the pure gauge force has zero covariant
divergence.

The implementation tests

[
oxed{
D_iF_i=0
}
]

numerically on random configurations.

This is the local identity responsible for source-free Gauss preservation
during Hamiltonian evolution.

## 5. Dynamics

The optimized engine uses:

1. analytic half-kick of (E_i^a);
2. exact group-valued link drift;
3. analytic second half-kick.

The link drift remains

[
U_i
	o
exp(iDelta t E_i)U_i.
]

## 6. Validation targets

Tests cover:

- analytic/reference force agreement;
- covariant force-divergence cancellation;
- Gauss preservation from a valid source-free initial state;
- small long-step energy drift.

## 7. Architecture

The project now has two SU(2) dynamics layers:

### Reference

`su2_hamiltonian_reference.py`

Slow, direct group derivative. Intended as a correctness oracle.

### Optimized

`su2_hamiltonian.py`

Analytic staple force. Intended for actual simulation.

Future changes to the optimized force should continue to be tested against the
reference on small lattices.

## Status

SU(2) now has an optimized non-Abelian electric Hamiltonian sector with exact
group drift and Gauss-compatible Wilson force.
