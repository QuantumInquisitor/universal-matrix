# Global toroidal routing v0.1

## Purpose

The framed-edge checkpoint proves local flux and vector continuity for one
complete graph edge at a time.  It does not place all edges and junctions in a
single Euclidean network.

This checkpoint supplies the first deterministic global placement and collision
audit.

## Global junction frames

Every annular junction keeps its local axis parallel to global +z.  The global
placement is therefore a rigid translation, not a deformation.

Junction centers are placed along the global x axis.  Their spacing is chosen
from the largest routed-edge envelope radius and the largest junction bounding
radius, plus an explicit nonnegative node gap.

This deliberately uses more space than necessary.  The purpose is to establish
a collision-free existence construction before optimizing compactness.

## Routed edge centerlines

Every framed edge receives a unique positive y corridor and a unique symmetric
high/low z level.

For source axis point S and target axis point T, the seven route points are

1. S;
2. directly above S at +H_e;
3. sideways to the unique y corridor at +H_e;
4. vertically down to -H_e;
5. across x to the target x coordinate at -H_e;
6. sideways back to y=0 at -H_e;
7. T.

The first and final segments follow the framed assembly's signed axial rule:
+z for positive or zero current and -z for negative current. Therefore the
endpoint geometry agrees exactly with the annular junction frame convention.

## Conservative routed envelopes

A route is audited with a conservative circular envelope radius equal to the
largest annular outer radius appearing anywhere in that edge assembly, plus an
optional route padding.

The actual future bend field may occupy less volume.  Passing this envelope
test is therefore a sufficient, not necessary, collision condition.

## Collision audit

For every pair of graph edges that do not share a graph node, the implementation
computes the minimum Euclidean distance between all pairs of route segments.

The clearance is

centerline distance - radius_e - radius_f.

The global routing is rejected if any nonincident clearance is negative.

Every routed edge is also checked against a spherical bound for every
nonincident junction control volume.

Incident edges are allowed to share their endpoint neighborhood because their
annular port bands are already locally disjoint and belong to the same
junction.  This checkpoint does not claim the conservative tube envelopes are
disjoint there.

## What is established

The implementation verifies:

- one global rigid translation per annular junction;
- one routed centerline per framed graph edge;
- exact signed endpoint tangent agreement;
- unique y and z routing lanes;
- positive route lengths;
- no nonincident edge-envelope collisions in Vesica and Flower/Tree examples;
- positive edge-to-nonincident-junction clearance;
- deterministic clearance growth under route padding;
- rejection of invalid global spacing parameters.

## Evidence boundary

This is a global geometric routing envelope, not yet a globally smooth current
field.

The orthogonal route has sharp corners.  No divergence-free bend map has yet
been constructed at those corners.  The straightened local edge assembly from
the previous checkpoint is therefore not silently claimed to follow the entire
polyline as a physical current field.

No dynamics, physical units, or material constitutive law are introduced.

## Next gate

Replace every orthogonal corner by an explicit smooth positive-Jacobian bend
map for an annular tube.  Transport the local divergence-free field through the
bend by the Piola transform, preserve signed flux and endpoint frames, and
re-run the same global collision audit on the actual curved volume.

That smooth routed field is the remaining kinematic geometry gate before an
independent dynamics or physical-normalization program can begin.
