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

## Geometric universe-port realization

The recursive address now has an explicit planar containment model in
`src/universe_port_engine.py`.

One parent circle is treated as the vessel. A complete seven-circle Seed is
inscribed using circles of half the parent radius. Every one of the Seed's
twelve adjacent equal-circle pairs defines an addressed Vesica universe
domain. The largest circle centered in that lens is the vessel that carries
the domain's next Seed and has half the generating-circle radius. Its contained
radius is therefore

\[
R_{d+1}=R_d/4.
\]

This does not replace the integer spiral scale. It supplies one exact
dimensionless geometric realization under a declared containment convention.
The absolute physical size of (R_0), and whether observed nature uses this
ratio, remain open.

The construction also separates two operations that had previously been easy
to blur:

- Flower expansion grows outward with equal-radius circles;
- recursive universe containment contracts inward by one quarter per depth.

The Flower adjacency graph supplies both Tree orientations: the outer Tree
directs routes away from the center and the inner Tree reverses them. No
independent Tree diagram is inserted.

## Status

Exact software properties:

- 108-state coverage;
- full-turn inheritance;
- reversible inward and outward advancement;
- reciprocal-mirror involution;
- mirror/evolution conjugacy;
- recursive Seed-mirror involution and parent/child compatibility.
- contained Seed, Vesica, and child-circle geometry at every tested depth;
- (R_d=R_0/4^d) and (12^d) address growth under the planar convention;
- equal-radius Flower counts and reciprocal inner/outer Tree routes;
- active port states coupled to all 108 canonical routing positions;
- explicit Terryen-candidate cavity activation without silently selecting a
  preferred candidate.

Open physical questions:

- what establishes a physical scale boundary;
- whether the 36-step turn has a dimensional duration;
- whether the geometric one-quarter containment ratio maps to any physical
  scale transition;
- how density, coupling, or clock rate changes across a turn;
- how many universe or multiverse layers exist;
- whether this recursion corresponds to observed physical structure.

See `docs/universe_port_engine_v0.1.md` for formulas, tests, and the scientific
claim boundary.
