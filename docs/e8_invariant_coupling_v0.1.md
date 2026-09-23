# E8 Gauge-Compatible Scalar Coupling v0.1

## Purpose

The E8 state audit found no existing Matrix field that should be reinterpreted
as a full E8 representation.

The next question was therefore narrower:

Can the optional E8 Cartan/Weyl coordinate couple to existing dynamics without
breaking their established gauge symmetries?

## Minimal candidate

The first allowed E8 quantity is the quadratic Cartan invariant

I_E8 = ||h||^2.

Every E8 Weyl reflection preserves this quantity.

Let O be any scalar observable that is already invariant under the gauge group
of its own sector.

The candidate interaction is

E_int = g I_E8 O.

The E8 coordinate does not transform the U(1), SU(2), or SU(3) field.

The gauge field does not transform the E8 Cartan coordinate.

The two sectors meet only through scalar invariants.

## Verification

The implementation verifies:

- the coupling is unchanged under every E8 root reflection;
- a U(1) local phase transformation leaves the selected matter norm and the
  E8 coupling unchanged;
- an SU(2) unitary transformation leaves the selected doublet norm and the
  E8 coupling unchanged;
- an SU(3) unitary transformation leaves the selected triplet norm and the
  E8 coupling unchanged;
- setting g = 0 decouples the E8 layer exactly.

## What this establishes

This proves that a scalar-singlet coupling can be written without algebraically
conflicting with the tested U(1), SU(2), or SU(3) gauge transformations.

It does not establish that nature contains this coupling.

It does not determine the value or sign of g.

It does not turn the eight Cartan coordinates into physical spatial
dimensions.

It does not enlarge SU(3) into E8.

## Why the coupling is deliberately weak in structure

A direct component-by-component coupling between the E8 eight-vector and the
SU(3) eight-component electric field would depend on a chosen basis and would
not follow from the current gauge structure.

The quadratic invariant avoids that unjustified identification.

## Next creator question

Which already existing scalar observable is the best candidate for O?

Candidates that can be tested without violating gauge covariance include:

- U(1) matter norm;
- SU(2) matter norm;
- SU(3) matter norm;
- a gauge-invariant local energy density;
- the existing neutral reciprocity/content scalar.

The next step should compare these candidates by dimensional consistency,
locality, conservation properties, and whether the coupling produces a
distinct falsifiable effect rather than merely renormalizing an existing
parameter.
