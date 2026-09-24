# Smooth annular toroidal bends v0.1

## Purpose

The global-routing checkpoint provides collision-free orthogonal centerlines,
but those routes have sharp corners. A sharp corner is not a smooth flow
domain.

This checkpoint replaces every right-angle corner by an explicit annular
quarter bend with a positive-Jacobian map and a flux-preserving current.

## Quarter-bend map

Let u be the incoming unit tangent and v the outgoing orthogonal unit tangent.
For bend angle phi in [0, pi/2], define

T(phi) = cos(phi) u + sin(phi) v,

N(phi) = -sin(phi) u + cos(phi) v.

For bend radius R_b and graph corner C, the centerline is

C_b(phi) = C
          + R_b (sin(phi)-1) u
          + R_b (1-cos(phi)) v.

The bend enters at C-R_b u and exits at C+R_b v.

With annular radius r and binormal B=u x v, the volume map is

F(phi,r,theta)
 = C_b(phi)
 + r cos(theta) N(phi)
 + r sin(theta) B.

## Positive Jacobian

Relative to a straight annular tube, the Jacobian scale is

1 - (r/R_b) cos(theta).

Therefore a sufficient global condition is

R_b > r_outer.

The implementation rejects any bend that violates this inequality.

## Piola current

The straight annular channel has axial density g(r), where g is the same
connector-compatible profile already used by the annular junction and
straightened cut-open toroidal channel.

Under the bend map,

dF/ds = [1 - (r/R_b) cos(theta)] T(phi).

The same scale appears in the Jacobian. The contravariant Piola transform
therefore cancels the geometric stretch, leaving

J_bend = g(r) T(phi).

The current is tangent to the bent tube, is divergence-free, and has the same
signed cross-sectional flux at every bend section.

At phi=0 it matches the incoming straight annular field point by point. At
phi=pi/2 it matches the outgoing straight field point by point.

## Global smooth-routing certificate

Each orthogonal routed edge has five internal corners. One quarter bend is
constructed at every corner.

The global route is rebuilt with an intentionally enlarged conservative
envelope. The envelope radius includes the maximum bend radius in addition to
the local annular radius. Since each bend centerline stays within one bend
radius of the original two-segment corner, the entire curved annular volume is
contained in that expanded envelope.

The already exact segment-distance collision audit can therefore certify the
smoothed volume without approximating curved-volume intersections.

## What is established

The implementation verifies:

- exact quarter-circle bend endpoints and tangents;
- invertible bend coordinates;
- positive Jacobian across the complete annulus;
- pointwise straight-to-bend vector matching at both interfaces;
- numerical divergence convergence to zero inside the bend;
- positive trimmed straight lengths between neighboring bends;
- one smooth bend at every global route corner;
- containment of all curved bends inside the collision-audited envelopes;
- positive nonincident edge and junction clearance for Vesica and Flower/Tree
  smooth-routing examples.

## Evidence boundary

This completes the kinematic smoothing of the routed middle annular channels.

It does not add an equation of motion, propagation speed, physical units,
material constitutive law, or experimental interpretation. The endpoint Piola
transitions and annular junction fields remain the earlier separately verified
components.

## Next gate

The remaining step before dynamics is a unified field sampler over the complete
global network: junction interiors, endpoint Piola transitions, straight
annular segments, and smooth bends. It must prove single-valued vector
continuity at every shared interface and zero divergence away from those
measure-zero interfaces.

Once that unified kinematic field is verified, the project can open a separate
dynamics and physical-normalization program.
