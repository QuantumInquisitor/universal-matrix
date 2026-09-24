# Shared-prefix fan-out control v0.1

Status: a reproducible failure of one different-destination candidate. The
connected shared-return Vesica reference remains valid. This control supplies
neither a general fan-out impossibility theorem nor a field on overlapping
components.

## Balanced graph and endpoint contract

The three-node graph has currents B to A = 0.4, C to A = 0.6, A to B = 0.4,
and A to C = 0.6, in that edge order. Every node has zero graph divergence.
Reversing all current signs preserves balance and flips the junction faces.
At A the same-face pairs are edges 0/1 and edges 2/3.

Outgoing edges 2/3 have the same source frame but different target frames.
Their target origins differ by approximately 54.6623. The existing complete
shared-return helper therefore rejects the pair: sharing a complete ordered
centerline requires matching both ordered endpoint frames. Matching frames
is a necessary condition, not a general clearance guarantee. Reverse-route
sharing and arbitrary graph groupings are outside this experiment.

## Shared prefix and explicit collision

Use the existing separated-shell builder with shell gap 3 and bend margin
0.05. Copy outer edge 3's first four route points, lane height, lane y and
bend radius onto inner edge 2. Keep edge 2's destination at B and the last
three route points' x-coordinate at B. The graph ports, channel annuli,
currents and other edges remain unchanged. Both routes now share a prefix,
then depart toward their respective destinations.

The candidate retains matching local straight/bend fields, positive
Jacobians and all endpoint frames. It nevertheless intersects where the
inner branch leaves the common run: inner edge 2's fourth bend (piece 7)
passes through outer edge 3's x-directed straight (piece 6).

Let R = 12.65, inner midpoint radius r = 9, and outer midpoint radius
rho = 12.4. Set q = 0.5, theta = 0, and

$$
\phi=\arccos\frac{R-\rho}{R-r}\approx1.50224950895.
$$

The mapped point has radial distance rho from the outer straight axis.
For positive current it is approximately (-9.00857170879, 191.6, -230.25).
Reversing current changes the z-coordinate to +230.25. Actual finite-volume
membership checks give penetration 0.2 in **both** pieces, including the
straight's finite axial interval. A small neighborhood also lies inside
both volumes. This is an explicit interior intersection, independent of
sampling density. Independent shifted-grid sampling found it as well.

This particular shared prefix relocates the collision to the destination
split. The next geometric question is a local split construction that lets
the inner route reach its destination while preserving the annular ports
and current, without crossing the enclosing outer shell. No such split is
certified by this control.

## Reproduction

Run `python -m src.toroidal_shared_prefix_fanout` for both signed reference
currents and the explicit witness. `tests/test_toroidal_shared_prefix_fanout.py`
checks balance, endpoint constraints, local regularity, unchanged edges,
and direct Cartesian membership in the outer straight.
