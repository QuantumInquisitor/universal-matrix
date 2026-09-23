# Toroidal connector topology and annular Piola connector v0.1

## Why the previous interfaces do not fit smoothly

The connected junction checkpoint uses rectangular lane ports. A rectangle is
disk-like: it has one boundary component, Euler characteristic one, and first
Betti number zero.

The canonical poloidal cut of a solid torus is an annulus: it has two boundary
components, Euler characteristic zero, and first Betti number one.

A nonsingular steady connector for which every streamline crosses each
transverse section exactly once defines a smooth first-return map between its
cross-sections. Those cross-sections must therefore be diffeomorphic.

The current rectangle-to-annulus pair fails that condition.

This is a geometric no-fit, not a numerical inconvenience. A valid continuation
must either change the junction port topology, allow a controlled critical
set/topology change, or change which toroidal flux cut represents the graph
edge.

## The torus must be cut open before it can be a channel

The previous toroidal field is a closed circulation domain. Its annular cut is
an internal measurement surface, not an external boundary.

For a network edge, the model now treats the solid torus as cut along that
annulus. The cut creates two distinct manifold-boundary copies with opposite
outward normals.

For signed poloidal flux I:

- inlet-copy outward flux = -I;
- outlet-copy outward flux = +I.

The field inside the cut-open torus remains the same divergence-free field.
The two boundary copies are topological records in the original chart; this
checkpoint does not yet separate them into a new nonoverlapping Euclidean
embedding.

## Compatible annular source port

Once the source port is annular, the source and toroidal cut have matching
topology.

The connector uses parameters

s in [0,1],
q in [0,1],
theta in [0,2*pi].

Its source radius is linear in q. Its target radius is the toroidal inner-cut
radius

rho_target(q) = R-a+a q.

A cubic smoothstep

h(s)=3s^2-2s^3

interpolates the radius. Because h'(0)=h'(1)=0, the connector field is normal
to both interface planes.

## Flux measure inherited from the torus

Let t=1-q. The existing toroidal field supplies the inner-cut flux measure

k(q) = (3 I / pi) t (1-t^2)^2.

It satisfies

integral_0^{2 pi} integral_0^1 k(q) dq dtheta = I.

The connector carries this same measure on every transverse section.

## Piola field

Let F(s,q,theta) be the connector map and let rho_q and rho_s be the q and s
derivatives of its radius.

The Jacobian determinant is

det DF = L rho rho_q,

which stays positive for the admitted geometry.

Applying the contravariant Piola transform to the reference current
(k(q),0,0) gives cylindrical components

J_rho = k rho_s / (L rho rho_q),

J_z = k / (rho rho_q),

J_phi = 0.

Because the reference current is independent of s, its reference divergence is
zero. The Piola identity therefore gives zero physical divergence.

At the target, h'(1)=0, so J_rho=0. Since rho_q=a there,

J_z = k/(rho a),

which is exactly the existing toroidal field's vector on the inner cut for a
purely poloidal channel.

Thus the connector matches the toroidal vector point by point at the target,
not merely in total flux.

## What is established

The implementation verifies:

- the rectangle-to-annulus topology no-fit;
- two opposite annular boundary copies for a cut-open torus;
- exact signed cut-flux accounting;
- positive connector Jacobian;
- source and target surface flux equal to the graph flux;
- pointwise target-vector agreement with the toroidal field;
- zero radial component at both interfaces;
- numerical divergence convergence to zero in the connector interior;
- reversed signed flux;
- rejection of invalid annuli and nonzero toroidal swirl.

## Evidence boundary

This does not yet make the complete graph network spatially continuous.

The current connected junction control volume still exposes disk-like
rectangular lane ports. The annular connector proves what a compatible
source-to-torus connector looks like and proves why the present rectangular
port cannot be substituted silently.

The cut-open torus is also represented as a manifold-with-boundary in the
original torus chart; the two cut copies have not yet been physically separated
in one global Euclidean embedding.

## Next gate

Redesign the external edge ports of the connected junction control volume as
annular flux ports, while preserving its internal conservative transfer
decomposition. Then attach one annular Piola connector to each cut-open
toroidal edge boundary.

That is the remaining kinematic geometry needed before opening dynamics or
physical normalization.
