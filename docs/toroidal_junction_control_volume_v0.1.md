# Toroidal junction control volumes v0.1

## Purpose

The graph-to-toroidal flux bundle assigns every directed graph edge an explicit
three-dimensional toroidal current domain. Its remaining incidence relation was
still stored separately as graph bookkeeping.

This checkpoint replaces node balance with an explicit connected
three-dimensional control volume for every conservative graph node.

## Boundary-port convention

For an incident directed edge with signed current J, the node's signed outward
flux contribution is

- +J at the edge source;
- -J at the edge target.

A positive contribution is an outlet port. A negative contribution is an inlet
port. A zero-current edge keeps a zero-flux port but requires no internal
stream lane.

A junction is admitted only when the sum of all signed outward port fluxes is
zero to the declared numerical tolerance.

## Connected internal flow

Every junction is one rectangular control volume.

Incoming and outgoing port magnitudes are paired by a deterministic transport
decomposition. Each transfer amount receives one nonoverlapping internal lane.

Inside one lane,

J = (f(y,z), 0, 0),

and the field is independent of x. Therefore

div J = 0

throughout the junction interior.

The normalized lane profile uses

b(s) = 6 s (1-s)

on 0<s<1. Since the integral of b over the unit interval is one, the two
dimensional product profile integrates exactly to the declared transfer flux.

The left-face outward flux of a lane is minus its transfer amount. The
right-face outward flux is plus that amount. Side-wall normal flux is zero.

Summing lanes associated with one graph edge reconstructs that edge's entire
junction-port flux even when a high-degree node requires the edge to split
among several internal transfers.

## Coupling to the toroidal edge domains

For every toroidal channel associated with edge e,

- the source junction port has outward flux +J_e;
- the toroidal channel cut has oriented flux +J_e;
- the target junction port has outward flux -J_e.

The implementation verifies this three-part interface for every edge.

Thus conservation no longer depends only on computing an incidence matrix
after the fact. Each conservative node owns a connected 3D control volume whose
actual boundary-port ledger sums to zero.

## What is established

The implementation verifies:

- deterministic inlet/outlet classification from signed graph currents;
- exact flux balance at every accepted junction;
- a constructive inlet-to-outlet transport plan;
- nonoverlapping internal lanes;
- analytic zero interior divergence;
- zero side-wall flux;
- numerical integration of the lane profile back to its transfer flux;
- source-port, toroidal-cut, and target-port agreement for every edge;
- complete Vesica and Flower/Tree junction networks;
- zero-current ports;
- rejection of nonconservative nodes and invalid geometry.

## Evidence boundary

This is still a dimensionless kinematic construction.

It does not establish:

- a smooth geometric pipe joining the rectangular port surface to the toroidal
  cut surface;
- a force or action principle;
- an evolution equation;
- propagation speed;
- physical content units;
- a material constitutive law;
- experimental identification of the content current.

The port and toroidal cuts have equal flux, but geometric connector fields
between those surfaces remain a separate construction problem.

## Next gate

The remaining purely geometric bridge is an explicit divergence-free connector
between each junction port and its matching toroidal cut, preserving the same
signed flux while avoiding new sources at the interface.

After that connector exists, the kinematic network will be spatially continuous
at the flux-domain level. Only then should an independent dynamics or physical
normalization gate be opened.
