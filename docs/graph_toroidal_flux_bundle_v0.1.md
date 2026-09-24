# Graph-to-toroidal flux bundle v0.1

## Purpose

The conservative toroidal field provides one compact divergence-free
three-dimensional current with a measurable signed cut flux. The remaining
kinematic question is how a finite conservative graph current can be assigned
to explicit three-dimensional domains without losing the current carried by
each graph edge.

This checkpoint supplies a minimal one-to-one answer.

## Channel-to-volume map

For every directed graph edge

$$
e=(s,t,J_e),
$$

the engine assigns one translated solid ring torus.

All channel tori use the same major radius $R$ and minor radius $a$, but
their centers are translated along the common z axis far enough that their
supports are disjoint.

The local toroidal field is the existing `ToroidalContentCurrent` with

$$
I_e = J_e,
\qquad
T_e = 0.
$$

The canonical inner equatorial cut is declared to carry the graph edge
source-to-target orientation. Its measured surface flux is therefore exactly

$$
\Phi_e = J_e.
$$

No normalization factor is fitted after the fact.

## Why the volumes are disjoint

Neighboring torus centers are separated by

$$
2a+g,
$$

where $g\ge 0$ is an explicit gap. Their z-support intervals therefore do
not overlap.

Each translated field is divergence-free. Because the supports are disjoint,
the bundle sum is also divergence-free pointwise wherever a channel field is
nonzero.

This gives every graph edge its own spatially inspectable current domain.

## Incidence is retained separately

The map does not replace the graph incidence relation.

Each volume record keeps the original source node, target node, current, and
channel label. Applying the original incidence matrix to the mapped channel
fluxes therefore produces exactly the same node divergence as the graph model.

For the conservative Vesica and Tree circulations, the mapped flux ledger is
node-balanced to the same numerical tolerance as the original graph.

This separation matters. The current version is a flux-preserving volume
assignment, not yet a claim that several toroidal tubes physically merge at a
shared three-dimensional node junction.

## What is established

The implementation verifies:

- one assigned toroidal domain per directed graph edge;
- exact signed cut-flux equality for every edge;
- preservation of graph node divergence;
- pairwise-disjoint volume supports;
- divergence-free summed current inside every active tube;
- explicit domains even for zero-current graph edges;
- deterministic spacing and bundle centering;
- validation of invalid geometric parameters.

The numerical surface integral is repeated after translation to confirm that
the measured three-dimensional cut flux still equals the original graph
current.

## Evidence boundary

This is a dimensionless kinematic graph-to-volume bridge.

It does not yet establish:

- a shared physical junction geometry at graph nodes;
- exchange of current between neighboring toroidal supports;
- a force law or action;
- propagation speed;
- physical content units;
- a measured energy density;
- a physical identity for the conserved content scalar.

The disjoint-tube construction is deliberately conservative. It preserves the
current ledger before attempting a more restrictive connected embedding.

## Next gate

A stronger spatial coupling would replace the incidence ledger by explicit
three-dimensional junction control volumes while preserving the same signed
channel fluxes and zero net source at conservative graph nodes.

Only after such a junction construction should the project add an independent
dynamical law or physical normalization. A dynamics proposal must state its
action or transport equation, conserved quantity, characteristic scales, and
at least one observable capable of rejecting the model.
