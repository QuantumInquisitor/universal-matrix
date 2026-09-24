# Incident connector overlap audit v0.1

## Purpose

The annular-junction checkpoint gives every incident edge a disjoint annular
band on the junction face. The framed-edge checkpoint then transitions each
band toward the same cut-open toroidal channel annulus.

The global routing and smooth-bend checkpoints deliberately audit only
nonincident edge volumes. Before a unified whole-network field can be admitted,
incident edges sharing one junction face must also be checked.

## Normalized outward progress

For each connector, define progress p from the junction face to the channel:

p = 0 at the annular junction port,

p = 1 at the common channel annulus.

For a source endpoint this is the inlet transition parameter directly. For a
target endpoint the outlet transition is traversed in reverse.

At every p the connector has an annular interval

[r_inner(p), r_outer(p)].

## No-fit result

Two edges sharing one junction face begin in disjoint radial bands. Therefore
their overlap width is zero at p=0.

In the current framed-edge construction every edge uses the same channel
annulus. Therefore at p=1 the two radial intervals are identical and their
overlap width equals the channel annulus width.

The transition is continuous, so every nonzero same-face pair must begin
overlapping at some p in (0,1).

The implementation locates that first overlap by bisection and records the
terminal overlap width.

## What is verified

For the Vesica reference circulation:

- two same-face nonzero connector pairs are present;
- both begin disjoint at the junction surface;
- both overlap before reaching the channel end;
- positive and negative current orientations have the same geometric
  obstruction;
- a zero-current circulation produces no nonzero-current overlap pairs.

The Flower/Tree reference also contains affected nodes and same-face overlap
pairs.

## Interpretation

This is a geometric no-fit, not a failure of flux conservation.

The annular Piola transitions remain individually divergence-free and preserve
their edge flux. The problem is that two independently valid connector domains
occupy the same spatial region, so a whole-network field sampler would become
multi-valued there.

The global nonincident collision certificate therefore cannot be promoted to a
complete network collision certificate.

## Next gate

A corrected construction must keep same-face incident edges disjoint after they
leave the junction.

Two candidate routes are admissible for further testing:

1. assign edge-specific, radially separated channel annuli while preserving
   port ordering through each Piola transition;
2. construct an explicit divergence-free spatial fan-out that moves each
   annular connector onto a separate axis before the channel expansion.

The next implementation should choose the minimal construction, prove
disjointness throughout the transition, then rerun both incident and
nonincident collision audits before attempting a unified field sampler.
