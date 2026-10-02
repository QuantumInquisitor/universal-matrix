# Conditional length, mass and inertia scaling

`scripts/report_fold_scaling.py` reconstructs the existing 22-point kinematics
at lengths .1 lambda metres and assigns each synthetic mass its original value
times lambda cubed. This is an explicit constant-density, geometrically similar
scaling hypothesis. The original lump masses are not measured materials, and
the calculation does not create distributed strain or intrinsic solid rotation.

## Assumptions and consequences

The coordinates remain dimensionless scale and fold angle. For equal coordinates:

| Quantity | Scaling with lambda | Basis |
| --- | --- | --- |
| Positions, coordinate Jacobians and Hessians | lambda | Uniform geometric length scaling |
| Lump masses | lambda cubed | Constant-density similarity assumption |
| Generalized mass matrix and point angular inertia | lambda to the fifth | Mass times length squared |
| Restoring potential and stiffness in these coordinates | lambda cubed | Assumed equal strain-energy density at equal coordinates |
| Generalized damping matrix | lambda to the fourth | Chosen to preserve damping ratios |
| Corresponding time interval | lambda | Consequence of inertia/stiffness scaling |

Geometric inertial bias scales to the fifth power at fixed coordinate rates.
Along corresponding trajectories, rates scale inversely with lambda, so the
bias instead scales cubically. Damping power then scales quadratically, and
integrated loss scales cubically. These distinctions are checked explicitly.
Point angular inertia is computed about the scaled coordinate origin; it omits
each body's intrinsic solid rotational inertia.

## Reproduction

Runs use lambda=1, .5 and .25, with initial rates divided by lambda. They cover
physical durations 2, 1 and .5 seconds respectively and timesteps .02 lambda.
These are corresponding intervals, **not equal physical durations**. The
reference is the existing unforced damped solver, evaluated at t/lambda.

| Length factor | Total synthetic mass (kg) | Maximum energy balance residual (J) |
| --- | ---: | ---: |
| 1 | .7400000 | 8.170e-15 |
| .5 | .0925000 | 1.021e-15 |
| .25 | .0115625 | 1.277e-16 |

Reconstructed inertia agrees with the predicted fifth-power law. All stored
trajectory coordinates, appropriately rescaled rates and energies match the
reference exactly for these binary scale factors in this run. Automated checks
allow rounding error; bitwise equality is not claimed for arbitrary factors.
The source-hashed report is `experiments/fold-scaling-summary.json`.

An intentionally wrong acceleration mass matrix scales cubically instead of
to the fifth power while the independent energy account uses the correctly
reconstructed geometry. It creates a 3.210e-7 J balance defect. This tests a
specific inconsistent inertia law; it does not prove the adopted material law
is physically correct.

Independent review of 24 interior states at factors .25, .37, .5 and 1 found
energy-rate errors <=4.793e-14 W and acceleration similarity error <=9.715e-17.
Tests also compare Cartesian point kinetic energy with generalized kinetic
energy, recover the original unit-scale dynamics and detect the wrong inertia.
No blocking mathematical defect was found.

## Connector and recursive limits

The mapped connector previously used a fixed physical spring constant. Scaling
both its port lengths by lambda would scale its potential by lambda squared,
which differs from the module potential's cubic law. For whole-system similarity
under these assumptions, physical connector stiffness must also scale by lambda.
This remains to be implemented and checked with the scaled module dynamics.

Next: combine scaled bodies and appropriately scaled connector stiffness in one
experiment, keeping force mapping, boundary work and total energy explicit.
Calibration, real attachment geometry, collision clearance, full recursive
assembly and sustained breathing remain open.
