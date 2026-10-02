# Recursive scale-impedance audit

The depth-three transport and fixed-dimension backreaction experiments show two facts at once:
the perturbation reaches level 3, yet only a few percent of parent-side work at the deeper
interfaces reaches the child during the tested interval. Most of the work remains stored as
connector potential.

Before adding any new recursive coupling, this checkpoint asks whether that behavior is already
consistent with the scale structure of the existing equations.

## Local linearization

The audit linearizes the current material and mapped-connector equations at the unloaded material
reference state. No coefficient is changed.

For module scale s, the existing model declares:

- generalized mass/inertia proportional to s^5;
- constitutive energy, gradient and tangent stiffness proportional to s^3;
- damping proportional to s^4.

Those relations imply corresponding natural angular frequencies proportional to 1/s and
fixed-mode characteristic impedance proportional to s^4. Modal damping ratios should therefore
remain scale invariant.

The audit evaluates scales 1, 1/2, 1/4 and 1/8 numerically and verifies these tangent identities.

## Parent-child connector scaling

Mapped connectors are linearized for the actual recursive interfaces:

- 1 to 1/2;
- 1/2 to 1/4;
- 1/4 to 1/8.

The connector tangent is compared after division by the parent scale cubed. Because child material
stiffness and connector tangent share the same parent-scale cubic factor for a fixed 1:2 scale
ratio, the dimensionless local parent-to-child tangent transfer should repeat at every depth if
the implemented similarity law is internally self-consistent.

A small quasi-static diagnostic uses the already declared initial root displacement direction
(0.005,-0.008). The parent displacement is held while the child is allowed to relax against its
material tangent plus connector tangent. The resulting child displacement, connector energy and
child material energy are reported. This is a local tangent diagnostic, not a prediction of the
finite-time dynamic child-work fraction.

## Interpretation

If module and connector tangents are self-similar while finite-time work uptake remains near
2–3%, the attenuation is not evidence that the recursive law changes arbitrarily with depth.
It instead points toward the repeated dynamical impedance and elastic-storage behavior of the
existing half-scale interface.

If the tangent scaling fails, that is a model inconsistency to repair before considering deeper
recursion.

This audit does not validate a spatial recursive embedding, measured material properties,
arbitrary/infinite depth, or correspondence with the 69-component toroidal flow assembly.
