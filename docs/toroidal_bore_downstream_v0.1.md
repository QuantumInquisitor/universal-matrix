# Toroidal bore downstream partial route v0.1

Status: an opt-in, fixed downstream connection from the existing C bore
passage to A's original edge-0 port. The upstream inlet and B's edge-0 port
remain open. This is not a closed graph embedding, a repair of retained
fan-out collisions, or a collision-free motion. Existing builders are unchanged.

## The connection and its two open faces

Let `s=sign(I)` and `c=54.66227766016838`. The existing transit contracts from
annulus [2,2.4] at `(c,0,-2.5s)` to [0.1,0.2], passes through C's central
bore, and expands to [2,2.4] at `(c,0,2.5s)`. C's junction and its edge-3
outlet/edge-1 inlet transitions retain their original geometry and current.

The downstream extension follows edge 1's existing C-to-A centerline,
with its five bend radii 5.85 and eleven straight/bend pieces. Its own
annulus is [2,2.4] and its signed flux is `0.4I`; the enclosing edge 1
annulus is [5.4,5.8] and carries `0.6I`. The final connector is edge 0's
original A outlet, from `(-c,0,-1.5s)` to `(-c,0,-0.5s)`, reaching port
[0.5,1]. Both signed cases use proper transition placement
`diag(1,s,s)`, with determinant +1. All lengths and currents remain the
dimensionless reference quantities used by the existing geometry modules.

The original edge-0 route and its B source connector are excluded from
this partial construction. Keeping them as another path would change the
current inventory. The eight original junction ports are inspected explicitly:
A's edge-0 port attaches to the new downstream connector; all other retained
ports keep their original connectors except B's exposed edge-0 port.

| Open face | Position | Outward normal | Annulus | Outward flux |
| --- | --- | --- | --- | --- |
| B's edge-0 port | `(0,0,0.5s)` | `(0,0,s)` | [0.5,1.5] | `0.4I` |
| Transit inlet near C | `(c,0,-2.5s)` | `(0,0,-s)` | [2,2.4] | `-0.4I` |

Their net flux is zero, but the faces are spatially distinct and each has
a nonzero normal trace. Cancellation does not connect them or establish a
closed conservative graph. No graph port is added at C: transit passes
through the empty bore without exchanging current with the host junction.

## Complete changed-component inventory

The partial transit has fifteen components: three bore components, eleven
downstream pieces, and the A connector. Its retained environment contains
all thirteen components of each of edges 1, 2, and 3, plus A/B/C junctions.
Host collars from the local bore construction are portions of those retained
straight pieces and are not counted twice.

The audit derives and checks every changed/changed and changed/retained pair.
In the reference this gives `15*14/2 + 15*42 = 735` pairs per current sign.
The number is a reported result, not a success precondition. Retained/retained
pairs are outside scope, including the existing edge-2/3 fan-out obstruction.
The complete shared-return helper is not relaxed or reused as a certificate
for these different endpoint frames.

Each pair receives one inspectable geometric argument:

- Strict separation of conservative enclosing boxes.
- Coaxial radial bounds using convex interpolation of transition radii.
- Separated annuli in one cylindrical straight chart or one injective bend
  chart, with a common centerline and `R > r_outer`.
- Opposite support half-planes at exactly matching cap centers and axes,
  followed by comparison of the actual cap annuli.
- Ordered interpolation of the nested A connector radii.

For a quarter bend the coordinate beyond its source cap is
`(R-r*cos(theta))*sin(phi) >= 0`; its coordinate beyond the target cap is
`-(R-r*cos(theta))*cos(phi) <= 0`. The strict inequality `R > r_outer`
keeps the entire bend in these half-spaces. Adjacent straight/bend volumes
therefore have disjoint interiors. Exactly shared cap geometry is required:
a small inward displacement is not promoted to separation by a tolerance.

The reference has fourteen intended transit-interface annuli, one final
A-port face, and one common target circle of the A connectors. Other pairs
have no contact. Corresponding host/transit shells have radial gap 3.
At A the connector gap is `3*(1-h(t))`, with `h(t)=3t^2-2t^3`; it is positive
for `t<1` and vanishes only at the target circle `r=1`. The inner connector's
`q=1`, outer connector's `q=0`, and junction port-boundary profiles vanish
there. This intended boundary contact is not a positive clearance margin.

These are analytic geometric arguments evaluated in floating-point arithmetic,
not a formal interval-arithmetic proof. Overlapping boxes alone never establish
collision or separation. Any unresolved pair causes the audit to reject the
candidate. Modified candidate data are rejected by an independent rebuild of
the fixed reference, including sub-tolerance changes to attachments or currents.
This strict contract supplies no general router or parameterized certificate.

## Interfaces, fields, and positive Jacobians

Every successive interface matches its center, directed axis, annulus and
signed flux. The original A port and connector records are checked separately.
The common annular source profile gives matching endpoint currents; the smooth
transition derivative vanishes at each end. The evaluator selects one chart at
a shared interface instead of adding duplicate copies of the same current.

All component Jacobian bounds are positive. For the transition chart `(t,q,theta)`,
a lower bound is `length * min(inner radii) * min(widths)`. For each new bend
chart `(phi,q,theta)`, it is `(R-r_outer)*r_inner*width = 2.76`, while its
Cartesian Piola scale is at least `1-2.4/5.85`, approximately 0.589744. For a
straight chart with normalized axial coordinate, the bound is
`length*r_inner*width`. The smallest partial-route bound is 0.01 in a bore
transition. These different chart bounds are identified in the typed inventory.

The reported interface residuals are explicitly finite numerical diagnostics,
scaled by the magnitude of the nonzero transit current. They supplement the
matching-profile argument. Tests independently integrate physical polar area
`r dr dtheta`, compare finite-difference map Jacobians and support planes, check
interior continuity, and exhibit real overlaps in rejected altered candidates.
Material coupling, physical energy and motion require separate formulations.

## API and reproduction

`build_bore_downstream_reference(current=1.0)` creates an audited frozen
`BoreDownstreamReference`. The only configurable quantity is current; it must
be finite with magnitude greater than `1e-10`, and supported by the existing
reference builders and finite field checks. Both signs are handled. The fixed
geometry does not accept bore, shell, routing or taper overrides.

`audit_bore_downstream(reference)` returns typed pair checks, interface records,
Jacobian bounds, all junction-port attachments, two exposed boundaries, and the
existing bore certificate. `reference.components` exposes the named partial
transit charts. `reference.current_if_inside(point)` returns that partial
transit's current or `None`; it does not evaluate the retained network fields.
A manually replaced candidate must be audited before being used as a reference.

Run `python -m src.toroidal_bore_downstream` for both signed reports. Verification
is in `tests/test_toroidal_bore_downstream.py` and the independent
`tests/test_toroidal_bore_downstream_adversarial.py`. The next geometric question
is upstream access from B's exposed port to the inlet near C while preserving
separation and the two interface contracts. That connection remains unbuilt.
