# Toroidal shared return route v0.1

Status: opt-in endpoint candidate with conservative clearance bounds for the
two reference routed return tubes. The interpolating family contains
collisions and is not a safe physical motion. Existing builders are unchanged.

## Construction

The gap-3 Vesica reference has parallel return edges 2 and 3, each directed
from cusp_b to cusp_a, carrying currents 0.4 and 0.6. Their channel shells
are respectively [8.8,9.2] and [12.2,12.6]. The earlier fixed-interface
obstruction rules out changing only the bend interiors.

This candidate instead moves all seven route points of edge 2 toward the
corresponding points of edge 3 and increases its bend radius from 9.25 to
12.65. With progress $s\in[0,1]$,

$$
P_i(s)=(1-s)P_i(0)+sP_i(1),\qquad
R_2(s)=(1-s)9.25+s12.65.
$$

The lateral lane moves from 153 to 204 and the symmetric height from
179.25 to 230.25. Both channels have the same ordered junction endpoints,
so their fixed port origins and axes coincide throughout. The internal
bend joins and trimmed straight sections move together. Currents, channel
shell radii, junction placements, and edges 0, 1, and 3 stay unchanged.

At $s=1$ the two returns follow the same centerline with the same bend
radius, while occupying different annular radial intervals. This is
possible for this parallel-edge pair; it does not solve a general
different-destination junction fan-out.

## Endpoint clearance argument

Each route is decomposed into six trimmed straights and five quarter bends.
The candidate is checked against the actual changed pieces, not against a
certificate copied from the old route.

1. Within corresponding shared pieces, the two annular shells have a radial
   gap of 3. A straight has unique cylindrical coordinates. A quarter bend
   has unique bend coordinates because its radius exceeds the outer shell
   radius. Thus these corresponding volumes do not intersect.
2. Consecutive straight/bend interiors lie on opposite sides of their shared
   end-face plane. Their shared face also has disjoint annular intervals.
   The positive bend Jacobian and positive trimmed lengths are essential.
3. Every nonadjacent pair of outer-tube pieces has disjoint conservative
   axis-aligned enclosing boxes. These same boxes enclose the corresponding
   inner-tube pieces, so intersections between different route portions are
   excluded as well.
4. Every outer-tube piece has a disjoint box from every piece of edges 0 and
   1. This bounds both shared return tubes against the unchanged routes.
   The global nonincident-junction envelope check is also recomputed.

A straight box uses the exact coordinate extents of its finite solid
cylinder. A bend box extends by $R+r_{\mathrm{outer}}$ from its corner in
each coordinate. These boxes contain the annular volumes conservatively.
Box separation can prove disjointness; overlapping boxes alone cannot prove
a collision. Bounds are evaluated in floating-point arithmetic, with
strict positive margins, rather than by a formal interval-arithmetic proof.

## Continuous local validity and limited separation

Segment directions stay fixed. Segment lengths and bend trims vary
affinely, so positivity at both endpoints gives positive trimmed lengths
throughout the move. The inner bend radius always exceeds its shell's
outer radius. Existing Piola bend fields therefore retain positive
Jacobians and match the adjacent straight profiles at every progress
value. Independent numerical cut integrals check the signed flux at
progress 0, 0.5, and 1 for both current directions.

Enclosing-box faces also vary affinely. For each nonadjacent piece pair of
the moving tube, and each moving/edge-0-or-1 pair, the audit finds one
coordinate and direction separating the boxes at both ends. The minimum
of those two signed separations bounds the entire interval. In the
reference case the minimum bound is 0.05. This excludes self-overlap and
collisions with edges 0 and 1 throughout this particular move. It does
**not** exclude collisions with edge 3.

## Measured reference report

Run `python -m src.toroidal_shared_return_route`.

The intermediate diagnostic checks every moving-edge/other-edge piece
pair, including straight/straight and bend/bend pairs absent from the old
incident bend/straight sampler. Positive box clearance excludes a pair;
otherwise samples from both volumes are tested for strict membership in
both. The grid is (13,5,24) with half-step offsets in each coordinate.
The first coordinate samples either bend angle or straight axial progress.

| Progress | Detected intersecting piece pairs | Maximum sampled shared penetration |
| --- | --- | --- |
| 0 | 2 | 0.15 |
| 0.25 | 2 | 0.15 |
| 0.5 | 2 | 0.15 |
| 0.75 | 14 | 0.15 |
| 1 | 0 | 0 |

All detected pairs involve the two return channels. Counts refer to piece
pairs on this finite grid, not an exhaustive enumeration of intersections.
Penetration is the minimum margin in both volumes, unlike the earlier
one-sided incident witness metric. These values must not be directly
compared with that metric's maximum penetration.

The endpoint's no-intersection conclusion for the two return tubes rests
on the geometric argument and bounds above, independently of zero sampled
detections. Its computed values are:

- shell gap: 3;
- minimum local Jacobian scale: 0.00395256916996;
- minimum nonadjacent outer-piece box distance: 0.0707106781187;
- minimum box distance to edges 0 and 1: 1;
- recomputed nonincident-junction envelope clearance: 27.8334255512;
- maximum interface-vector residual: about $1.94\times10^{-14}$.

## Remaining work

This provides a separated endpoint for the reference routed return tubes,
not a collision-free transition from the already intersecting reference.
Additional intersections occur during the simple interpolation. A physical
motion would need a collision-free initial configuration and an independently
checked path from it; positive local Jacobians alone do not provide that.

The result does not certify a full embedding of all junction control
volumes, connector transitions, and toroidal channels into the routed
construction, or generalize the shared-path strategy to branches with
different destinations. The next small audit is compatibility of these
shared routed return shells with the existing junction/connector endpoint
contract. Recursive topology and dormant-path semantics remain separate
open questions. No dynamics or physical units are introduced.
