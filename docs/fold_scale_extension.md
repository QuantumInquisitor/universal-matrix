# Experimental scale-extension audit to one eighth

The existing production scaling contract intentionally rejects module length factors below
0.25. A half-scale binary material tree therefore stops at physical depth 2, where the leaf
scale is exactly 0.25. Depth 3 would require scale 0.125.

This checkpoint does not change that production guard. Instead it independently evaluates the
underlying kinematics, constitutive material law and mapped-port formula at 0.125.

## Lower-level numerical domains

At scale 0.125:

- reference specimen length is 0.0125 m, above the kinematics minimum of 1e-6 m;
- the smallest existing lump mass remains above the kinematics minimum mass;
- effective membrane thickness is 1.25e-5 m, inside the constitutive material domain;
- bridge EA is 0.0015625 N, inside the constitutive material domain;
- mapped port length is 0.0125 m, inside the port domain (0,1] m.

Those facts only show that the lower-level validators admit the inputs. They do not by themselves
justify changing the model's declared scale range.

## Audit

The experimental adapter reconstructs the same conditional laws without calling the production
`scale_value()` guard:

- mass scales with length cubed;
- generalized inertia scales with length to the fifth power;
- constitutive membrane and bridge energies and gradients scale cubically;
- damping scales with length to the fourth power;
- corresponding physical time scales linearly with length;
- the mapped connector uses endpoint port lengths directly and stiffness proportional to the
  larger endpoint scale.

The audit compares 1, 0.25 and 0.125 scales at corresponding times, checks energy balance,
Cartesian/generalized kinetic consistency, constitutive energy and gradient scaling, connector
directional derivatives, uniform connector energy scaling and timestep refinement.

## Decision rule

A passing audit is numerical evidence that 0.125 is internally consistent with the currently
declared synthetic similarity laws. It is not physical calibration and does not automatically
change the repository-wide production guard.

Only after this audit passes should a separate review decide whether to expand the production
scale contract and attempt a 15-module depth-3 recursive tree.
