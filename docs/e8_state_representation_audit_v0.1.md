# E8 State Representation Audit v0.1

## Result

The current repository does not contain a physical Matrix state that has been
shown to carry a full E8 representation.

That negative result is important because the repository already contains
several uses of the number eight.

## SU(3) eight-component field

The SU(3) lattice Hamiltonian uses an electric field with eight components.

Those eight components exist because the Lie algebra su(3) has dimension
eight. They transform in the SU(3) adjoint through gauge conjugation.

They are therefore not relabelled as E8 coordinates.

Equal component count does not imply equal representation theory.

## Canonical 8 x 8 register

The 64-address register is an ordered pair of two choices from an eight-vertex
stella/cube set.

That means 8 x 8 choices.

It does not mean an eight-dimensional linear state vector.

The register therefore does not become an E8 representation merely because
the symbol eight occurs twice.

## Legitimate eight-dimensional object

The H4-derived E8 construction does produce a genuine eight-coordinate vector
space.

Those eight coordinates form the rank-eight root/Cartan space on which the E8
Weyl group acts by reflections.

The new E8CartanState type exposes that finite reflection action without
claiming the full E8 Lie algebra acts on eight physical components.

## Why this distinction matters

E8 has rank eight, but the E8 Lie algebra has dimension 248. Its smallest
nontrivial linear representation is the 248-dimensional adjoint
representation.

Therefore an eight-dimensional vector can naturally carry the E8 Weyl/root
space action, but it is not by itself a nontrivial representation of the full
E8 Lie algebra.

## Exact checks

The implementation verifies:

- no current Matrix state is classified as a full E8 representation;
- the SU(3) eight-component electric field is explicitly classified as a
  no-fit for E8;
- the H4-derived eight-coordinate space is classified as Weyl-space only;
- E8CartanState preserves norm under every E8 root reflection;
- its root reflections agree exactly with the existing E8 geometry module;
- central mirror remains an involution.

## Consequence for the engine

The next dynamics work should not attach E8 directly to SU(3), the 64-register,
or the canonical Z_108 core.

A defensible next experiment would instead introduce an optional internal
Cartan/Weyl coordinate carried alongside an existing Matrix state and then ask
whether any invariant coupling to the existing Hamiltonian can be derived.

Such a coupling must be introduced as a new candidate law and must preserve the
existing gauge symmetries.

## Next creator question

Can an optional E8 Cartan/Weyl coordinate be coupled to an already existing
Matrix observable through a scalar invariant, while leaving U(1), SU(2), and
SU(3) gauge covariance unchanged?

If no such invariant coupling can be derived, the E8 layer should remain a
mathematical symmetry and geometry module rather than a physical dynamics
sector.
