# Edge-specific separated toroidal channel shells v0.1

## Purpose

The incident-overlap audit shows that same-face junction connectors cannot all
terminate on one common annular channel without spatial overlap.

This checkpoint tests the minimal correction: assign every graph edge its own
radially separated annular channel shell while preserving the existing
edge-index ordering used by junction port bands.

## Shell allocation

For edge index i, choose

inner_i = R_0 + i (w + g),

outer_i = inner_i + w,

with shell width w>0 and shell gap g>=0.

The shells are therefore globally ordered and pairwise disjoint.

Each edge receives its own purely poloidal toroidal field with

major radius = outer_i,

minor radius = w.

Its canonical inner poloidal cut is exactly the assigned annulus

[inner_i, outer_i].

The signed graph current remains the poloidal cut flux.

## Order-preserving connector interpolation

On every junction face, annular port bands are already ordered by edge index.

For two same-face edges e_i < e_j,

port_outer_i <= port_inner_j

at the junction face, and

shell_outer_i < shell_inner_j

at the channel end.

The Piola transition interpolates its radial boundaries with the same smoothstep
weight. A convex combination of two ordered endpoint inequalities stays
ordered.

Therefore the two connector annuli remain disjoint for the entire transition.

The implementation also samples the complete connector interval directly as a
numerical cross-check.

## What is established

The implementation verifies:

- deterministic globally ordered edge shells;
- pairwise shell gaps;
- one edge-specific toroidal cut annulus per graph current;
- unchanged signed poloidal cut flux;
- compatibility with the existing annular junction and framed-edge builders;
- zero same-face nonzero connector overlap in positive and negative Vesica
  references;
- zero same-face connector overlap in the Flower/Tree reference;
- preserved framed-edge internal vector and flux-chain residuals;
- explicit zero-current edge assemblies;
- rejection of invalid shell geometry.

## Evidence boundary

This fixes the connector-overlap obstruction only.

The later global routing and bend geometry were originally designed around
common channel radii and intentionally excluded incident-edge collision pairs.
Distinct radial shells remove overlap while the connectors remain coaxial, but
the full routed bends of incident edges still require a new collision audit.

The edge-specific toroidal radii are a geometric existence construction, not a
derived physical scale law.

## Next gate

Rebuild the global routing and smooth bends using the separated framed-edge
network, then audit actual incident-edge geometry as well as nonincident
geometry.

If incident bend volumes still collide, an explicit separate-axis fan-out is
required. If they remain disjoint, the separated-shell construction can replace
the common-channel candidate for whole-network field sampling.
