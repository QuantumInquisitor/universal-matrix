# Incident bend collision audit v0.1

## Purpose

Edge-specific channel shells remove the coaxial overlap of same-face connector
transitions. The next question is whether those separated shells remain
spatially disjoint once one edge begins a smooth bend while another incident
edge is still traveling along the shared endpoint axis.

This checkpoint audits the actual smooth annular bend volume against the actual
trimmed annular straight segment of every other nonzero edge sharing that
junction face.

## Geometry under test

For a routed edge at one graph endpoint:

- the endpoint straight shell begins at the junction axis point;
- the straight shell ends where the first quarter bend begins;
- the quarter bend uses the edge-specific channel inner and outer radii;
- the neighboring same-face edge has its own separated annular straight shell
  around the same endpoint axis.

The audit samples points inside one bend and computes their exact axial/radial
coordinates relative to the neighboring finite straight segment.

A point is a collision witness only when it lies strictly inside both the bend
annulus and the neighboring straight annulus, with positive axial and radial
penetration margins.

## Result

For the separated-shell Vesica reference, both positive and negative current
orientations still produce incident bend/straight collisions.

The Flower/Tree separated-shell reference also produces collision witnesses.

Zero-current Vesica edges produce no nonzero incident collision because their
fields are excluded from the active-pair audit.

The obstruction is therefore later than the connector interpolation:

1. separated port-to-channel connectors remain radially ordered and disjoint;
2. the first curved edge begins moving its annular tube away from the shared
   axis;
3. another incident edge still occupies a straight annular shell on that axis;
4. the curved volume enters the neighboring shell before the routes have
   spatially separated.

## Evidence boundary

This is a numerical geometric collision audit.

It does not invalidate the individual bend map, the Piola current, the
separated connector proof, or graph flux conservation. It shows that the
current global routing order is insufficient for incident edges.

The nonincident collision certificate remains valid for the pairs it was
designed to cover.

## Follow-up gate

This audit establishes a no-fit for the tested compact separated-shell
parameters. It does not establish that every possible shell spacing and bend
radius must collide.

The follow-up scan in `src/toroidal_bend_spacing_scan.py` preserves the same
graph, signed fluxes, annular junctions, Piola connectors, and smooth-bend maps
while varying shell gap and bend-radius margin. Its deterministic 25-point
Vesica grid contains at least one collision-free sample.

The next gate is therefore optimization before redesign:

- map the collision/no-collision boundary;
- test dimensionless clearance ratios across Flower/Tree scales and recursive
  depths;
- derive a conservative scale-consistent clearance condition;
- retain separate-axis fan-out as the fallback if no compact scale-consistent
  region survives.

See `docs/toroidal_bend_spacing_scan_v0.1.md`.
