# Framed toroidal edge assembly v0.1

## Purpose

The annular junction checkpoint makes every graph edge port locally compatible
with the annular Piola connector. This checkpoint assembles the complete local
edge path from one graph endpoint to the other.

The construction remains edge-local. It does not yet place all graph edges in
one collision-free global embedding.

## Five-part edge assembly

For graph edge e with signed current J_e, the local assembly is:

1. source annular junction port;
2. inlet annular Piola transition;
3. straightened cut-open toroidal channel;
4. exit annular Piola transition;
5. target annular junction port.

Every component uses the same signed current J_e.

## General annular Piola transition

The inlet and exit pieces use the same positive-Jacobian smoothstep geometry as
the earlier torus connector, but allow arbitrary source and target annular
radii.

The flux measure is unchanged across the transition, so the field remains
divergence-free and the boundary profiles match the adjacent annular domains.

## Straightened cut-open toroidal chart

A cut-open purely poloidal toroidal channel has two annular boundary copies.
For edge-local assembly it is represented by a straight annular prism carrying
the same pointwise cut profile at every axial section.

This straightened chart preserves:

- the signed poloidal flux;
- the annular cut profile;
- zero divergence;
- zero radial side-wall flux;
- pointwise equality with the original toroidal vector on the cut.

It is a flux-equivalent cut-open chart, not a claim that the original donut
metric has become Euclidean.

## Signed-current frame rule

The annular junction field always routes from its lower face toward its upper
face.

For an edge with positive current, the edge-local axial frame agrees with the
junction +z axis.

For an edge with negative current, the edge-local axial frame is flipped.

Thus

axis_sign = sign(J_e)

for nonzero current.

The edge-local connector and channel vectors already carry the signed current.
Multiplying their local axial component by axis_sign makes the endpoint vector
agree with the junction field for both current signs.

Zero-current edges retain explicit zero-field assemblies and use axis_sign=+1.

## Flux chain

At every shared interface, the two outward fluxes cancel:

source junction + inlet source = 0,

inlet target + channel source = 0,

channel target + exit source = 0,

exit target + target junction = 0.

The implementation verifies this edge by edge.

It also verifies pointwise vector equality at both internal interfaces and,
after applying the one-bit endpoint frame rule, at both junction interfaces.

## What is established

The implementation verifies:

- a general divergence-free annular Piola transition;
- positive transition Jacobians;
- a straightened cut-open toroidal chart with the original cut profile;
- one complete five-part assembly per graph edge;
- positive-current endpoint matching;
- negative-current axis-flip matching;
- explicit zero-current assemblies;
- complete Vesica and Flower/Tree framed edge networks;
- pointwise internal vector continuity;
- signed flux cancellation at every local interface;
- endpoint vector agreement with the annular junction fields.

## Evidence boundary

This is a local framed assembly, not yet a global spatial network.

Each edge currently owns its own local axial coordinate. The model does not yet
supply:

- global rigid transforms placing every edge assembly between its actual source
  and target junction centers;
- bends between arbitrary junction-port normals;
- collision avoidance among edge assemblies;
- a separated Euclidean embedding of all cut-open toroidal channels;
- dynamics, physical units, or material laws.

## Next gate

Assign global rigid frames and routed centerlines to every framed edge assembly.
The embedding must preserve endpoint vectors and fluxes while keeping all
nonincident edge volumes disjoint.

Only after that collision-free geometric network exists should the project open
the independent dynamics and physical-normalization gate.
