# Recursive Omniverse Contract v0.1

## Purpose

The intended Omniverse Engine is not merely a container holding unrelated
simulated universes. It is intended to test a stronger structural hypothesis:
the same generative code recurs through nested scales, with inner and outer
domains related reciprocally and each completed spiral becoming the seed of an
adjacent scale.

This first contract implements only the dimensionless structure needed to test
that idea. It does not claim that the contract has already been identified with
physical universes, multiverses, DNA, length, time, matter, or consciousness.

## Address

Each address contains one of three canonical routing channels, one of 36 phase
positions in a complete routing turn, and an integer scale level extending
inward and outward from level zero. The three channels and 36 phases cover all
108 canonical core states exactly.

## Spiral-cone transition

The unwrapped coordinate is

\[
u = 36s + p,
\]

where `s` is scale level and `p` is phase position. Local evolution adds an
integer number of steps to `u`. Every 36 steps returns to the same local code
while moving to the adjacent scale:

\[
(s,p) \mapsto (s+1,p).
\]

The path therefore closes in phase but not in scale. It is a spiral recurrence,
not a flat circular return.

## Inner and outer correspondence

The reciprocal mirror is `u -> -u`. It is an involution and reverses spiral
evolution:

\[
M(M(x))=x,
\qquad
M(A_k(x))=A_{-k}(M(x)).
\]

This is the first exact software contract for the proposed correspondence of
inner with outer and inward development with outward development.

The Sevenfold Seed contract now adds a separate recursive spatial mirror. A
half-turn fixes the center, exchanges opposite ring positions, and mirrors
each Vesica index at every depth of a nested universe address. It obeys

\[
M(M(a))=a,
\qquad
M(a.\mathrm{child}(i))=M(a).\mathrm{child}(M(i)).
\]

The spiral mirror and Seed mirror are compatible expressions of reciprocity,
but they act on different state spaces. No physical identity between them is
assumed without a future coupling law.

## DNA-like inheritance

A complete turn preserves routing channel and phase position. Those two values
form the current inheritance signature. The implementation therefore tests the
minimal proposition that a new scale inherits the same local organizing code.

It does not yet implement mutation, recombination, scale-dependent expression,
or biological DNA. Those require separate laws and evidence.

## Status

Exact software properties:

- 108-state coverage;
- full-turn inheritance;
- reversible inward and outward advancement;
- reciprocal-mirror involution;
- mirror/evolution conjugacy;
- recursive Seed-mirror involution and parent/child compatibility.

Open physical questions:

- what establishes a physical scale boundary;
- whether the 36-step turn has a dimensional duration;
- how scale radius, density, or coupling changes across a turn;
- how many universe or multiverse layers exist;
- whether this recursion corresponds to observed physical structure.
