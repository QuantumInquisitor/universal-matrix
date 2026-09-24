# Local junction bore passage v0.1

Status: a static local passage through the unchanged C junction of the
balanced three-node fan-out reference. The two ends remain unattached.
This supplies a component for further routing experiments, not a completed
fan-out embedding, a sideways exit through an outer tube, or a safe motion.

## Why use the central opening?

The preceding shared-prefix control intersects where an inner tube turns
sideways through the enclosing outer straight. There is a local reason to
look elsewhere. For a fixed finite annular wall

$$
W=\{0\le u\le L,\ a\le r\le b\},
$$

a continuous material-point path from r < a to r > b, remaining in
0 < u < L, must cross r = (a+b)/2. At that point its wall penetration is
min(u, L-u, (b-a)/2) > 0. Thus it cannot leave sideways without crossing
the intact wall. This is a statement about one fixed finite wall, not all
fan-out geometries. Passing beyond an end, changing the wall, or staying
inside the bore are distinct possibilities.

This experiment stays inside the bore. It retains C's existing annular
junction and the existing incoming edge 3 outlet and outgoing edge 1 inlet
transitions. A separate transit contracts before the incoming transition,
passes through the empty center, and expands after the outgoing transition.
Its open ends use edge 0's annulus [2,2.4] and signed current 0.4 I. These
ends are not connected to the remainder of edge 0 in this experiment.
The host route through C carries signed current 0.6 I.

## Geometry and separation argument

Let u be axial distance from C's center in the declared route direction.
For the reference taper length 1, the finite construction is:

| Axial interval | Transit | Existing host geometry | Radial gap bound |
| --- | --- | --- | --- |
| [-2.5,-1.5] | [2,2.4] contracts to [0.1,0.2] | Incoming channel [12.2,12.6] | 9.8 |
| [-1.5,-0.5] | [0.1,0.2] | Incoming transition to port [0.5,1.5] | 0.3 |
| [-0.5,0.5] | [0.1,0.2] | C junction [0.5,1.5] | 0.3 |
| [0.5,1.5] | [0.1,0.2] | Outgoing transition to channel [5.4,5.8] | 0.3 |
| [1.5,2.5] | [0.1,0.2] expands to [2,2.4] | Outgoing channel [5.4,5.8] | 3.0 |

Every transition radius is a convex combination of its endpoint radii.
Consequently the transit stays inside the host inner radius at each axial
position. Since all pieces are coaxial, a shared point would require the
same axial position and radial distance; the strict radial inequalities
exclude such a point. Different axial intervals meet only at their declared
faces. The reported bounds are radial bounds, not a general minimum-distance
or interval-arithmetic certificate.

The validator checks actual axes, ordered axial intervals, interface annuli
and signed flux records before issuing these bounds. Both host ports must
cover their junction's annulus and full flux range. Host flux orientation
is checked independently of its magnitude. Annular radii and widths must
exceed 1e-10, and Jacobian bounds must be finite and positive; extremely
small numerically unresolved bores are rejected. It rejects unresolved
clearance. Both tapers fit within the existing straight sections before
their bends; a longer requested collar is rejected. The certificate does
not cover those bends, other routes, or the eventual open-end connections.

## Field and orientation

The transit reuses the existing annular Piola transition field and a
constant-annulus straight field. The junction and its transitions use their
existing fields. At each transition end the smoothstep derivative vanishes,
so the matching profile is axial. The evaluator selects one component at a
shared interface, avoiding double counting.

Placement reuses the proper rotation diag(1,sign(I),sign(I)); its determinant
is +1 for either current sign. Oriented physical cuts recover signed flux
0.4 I for the transit and 0.6 I for the host separately. Their geometry is
disjoint, so transit does not exchange current with the C junction. This
does not add a graph port or alter C's conservation equation.

The four transition maps retain positive Jacobians; their simple lower
bound is 0.01 in the reference. The construction is dimensionless and
piecewise smooth. No energy cost, dynamics law or physical identification
is inferred from these geometric and current checks.

## Reproduction and next gate

Run `python -m src.toroidal_junction_bore_passage` for signed reference
currents and the three radial bounds. Verification lives in
`tests/test_toroidal_junction_bore_passage.py`.

Next, connect this local passage to the surrounding routes with matching
annuli and currents, then audit all altered pieces against the other tubes
and junctions. Passing through C's bore does not itself let the transit
leave sideways through the outgoing enclosing tube. Junction placement,
end access and any later turn remain part of that separate integration.
