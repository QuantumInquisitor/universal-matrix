# Connected shared return endpoint v0.1

Status: opt-in static Vesica construction assembling the existing annular
junctions, radial Piola transitions, and shared routed channels into one
global current evaluator. Conservative geometric checks exclude overlapping
interiors while allowing intended boundary contact. This is not a physical
motion, general fan-out algorithm, or new dynamics law.

## Why this step is needed

The shared-route endpoint separates the two routed return tubes, but its
constant channel annuli begin at junction-axis frames. Those channel annuli
do not equal the much smaller junction port annuli. For the two returns,
the port intervals are [0.5,1.0] and [1.0,1.5], while the channel intervals
are [8.8,9.2] and [12.2,12.6]. A matching axis alone is insufficient to
join those faces geometrically.

The repository already supplies an `AnnularPiolaTransition` for each
inlet and outlet. This candidate places those transitions globally and
shortens the first and last constant-shell straight of **all four** edges
by the corresponding connector length. The reference connector length is
1. The shared returns' end straights shorten from 217.1 to 216.1; every
trimmed segment remains positive. Junctions, bends, shell radii, signed
graph currents, and graph port positions are unchanged.

## Placement and field orientation

Let $a\in\{-1,1\}$ be the assembly's axial sign. The local-to-global
rotation is

$$
Q_a=\operatorname{diag}(1,a,a),\qquad \det Q_a=1.
$$

The source transition begins at the source port's axis point. The target
transition begins one outlet length before the target port in the declared
axial direction. Its local `z_start` is subtracted before applying the
rotation and translation. Both position and vector current use the same
proper rotation, so reversal of the axial frame does not introduce the
orientation ambiguity of a reflection.

At each junction/transition interface, the annular radii and signed normal
profile are the existing port profile. At each transition/channel
interface, they are the existing channel profile. The smoothstep's radial
derivative vanishes at both transition ends, giving zero radial current
there and the matching axial profile. The bend/straight interfaces retain
their previously checked matching fields.

`ConnectedSharedReturnNetwork.current(point)` evaluates a translated
junction, placed transition, or routed piece. A shared face is evaluated
through one matching component; its current is not summed twice. The
field is zero outside the construction. Junction and edge field formulas
are reused, not replaced by a new field model.

The assembled field is continuous across the declared faces. Its component
fields are divergence-free in their interiors and their normal currents
match on shared faces. This is a piecewise construction; no claim of
globally continuous field derivatives is made.

## Geometric checks

The audit verifies that every placed component equals the one derived from
the declared route and transitions before using the route certificate.
The shared-route certificate covers the return tube interiors; trimming
their end straights only shrinks those volumes. Additional checks cover
the self-separation and mutual separation of the two unchanged routes.

Every transition fits inside the solid cylinder with radius equal to its
largest endpoint outer radius and the exact axial interval of its placement.
Conservative axis-aligned boxes then check transitions against all routed
pieces and junction volumes, junctions against all routed pieces, and
junctions against one another. A zero signed box separation is permitted
at an intended face; negative separation must be resolved or rejected.

The two same-face return transitions have overlapping boxes because they
are coaxial. Their annular interiors are checked by radial order instead.
They have the same axial origin, direction, and length, so they share the
smoothstep parameter $h(s)=3s^2-2s^3$. If $g_0$ and $g_1$ are their two
endpoint radial gaps, the gap at every intermediate cross-section is

$$
g(s)=(1-h(s))g_0+h(s)g_1.
$$

Here the source pair has gaps (0,3), and the target pair has gaps (3,0).
Their interiors are separated for $0<s<1$. At a junction face the annular
bands touch at radius 1.0, where both boundary profiles vanish. Therefore
the construction has intended boundary contact, **not** a strictly positive
clearance between every closed component.

Each transition's parameter Jacobian satisfies the conservative bound

$$
\det DF \ge L\min(r_{\mathrm{inner},0},r_{\mathrm{inner},1})
                 \min(w_0,w_1)>0.
$$

The bend Jacobians and tube-separation arguments are inherited from the
checked shared-route endpoint. All numerical bounds use floating-point
arithmetic; this is not a formal interval-arithmetic proof.

## Reference results and tests

Run `python -m src.toroidal_shared_return_connectors`.

For both current 1 and current -1:

| Quantity | Computed value |
| --- | --- |
| Placed inlet/outlet transitions | 8 |
| Coaxial transition pairs requiring radial-order checks | 2 |
| Minimum endpoint radial gap | 0 (intended port-boundary contact) |
| Minimum transition Jacobian bound | 0.2 |
| Minimum nonadjacent/mutual unchanged-tube box clearance | 0.0707106781187 |
| Maximum junction/connector/channel field residual | about $1.07\times10^{-15}$ |

Independent tests integrate signed flux through every placed transition
using finite differences of its actual mapped surface and the global
current evaluator. They also check positive orientation, inverse placement,
numerical divergence inside the transitions, continuity on both sides of
all transition interfaces, single evaluation at shared faces, fixed graph
ports, positive trimmed lengths, radial ordering, and rejection of altered
components or overlong transitions.

## Scope and remaining questions

This is a static, dimensionless reference assembly for the parallel-return
Vesica graph. Its channel charts remain the existing flux-equivalent
straightened cut-open toroidal charts. It does not establish a separate
embedding of closed uncut tori, an energy principle, or a physical evolution.

The earlier interpolation from the overlapping route still collides. A
collision-free motion must start from a collision-free configuration and
be checked independently. General fan-out to different destinations and
recursive Flower/Tree graphs are not certified here. The next bounded
question is which graph/port configurations permit shared routing and
where distinct destinations require another construction; dormant-path
semantics remain relevant before recursive claims.
