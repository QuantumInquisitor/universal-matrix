# Recursive spatial connector attachment-frame audit

The recursive placement envelope showed that a physical Seed-axis embedding separates
parent and child module origins and mirrors one child body by pi. The current recursive connector,
however, was validated only in co-located module-local coordinates.

This checkpoint introduces no new stiffness or material coefficient. It asks how the existing
energy-derived connector behaves after adding the geometry required by placement.

## Geometric rest offset

For a vessel/module ratio k, each child center lies one half parent-vessel radius from the parent
center. The physical center translation is therefore

k/2 times the parent module length.

That translation is treated as a geometric connector rest vector. Subtracting it from the
physical parent-to-child attachment vector leaves only the port deformation. The audit verifies
that connector energy and generalized forces are independent of the chosen k after this exact
rest subtraction.

The tested k values include:

- the conservative sibling/3D-containment threshold 2.193830551297614;
- an intermediate value 5;
- the conservative all-generation sphere-separation threshold 19.744474961678524.

## Two attachment-frame candidates

### Parent-aligned attachment frame

The child attachment coordinates are expressed in the parent connector frame even when the body
itself is mirror rotated.

This adapter must reproduce the already validated local recursive connector exactly. It can be
interpreted only as a candidate internal attachment transform until an explicit body attachment
site is identified.

### Body-following attachment frame

The attachment frame rotates with the mirrored child body.

For child-bit 0, parent and child remain co-oriented and the existing local connector is recovered.

For child-bit 1, the child port vector is rotated by pi. The resulting connector remains
energy-derived and conservative, but it is a physically different dynamics from the current
recursive model.

## Energy derivation

For rest-corrected parent-frame port separation delta and the unchanged mapped stiffness K,

U = 1/2 delta^T K delta.

Parent and child generalized forces are derived directly from the corresponding port Jacobians.
Finite differences verify both generalized force gradients.

Because the center translation is removed exactly as a rest vector, the energy and forces must
not depend on k.

## Interpretation boundary

If parent-aligned attachment exactly reproduces the existing connector while body-following
mirrored attachment does not, the spatial problem is an attachment-frame question rather than
evidence for a missing force law.

The present 22-body geometry does not identify which panel, bridge or hub carries the abstract
two-component connector port. Therefore this checkpoint cannot select a physical attachment
convention.

A later port-to-body correspondence must identify a specific material attachment or prove that
the connector frame is an independent internal degree of freedom before the spatial assembly can
be called physical.
