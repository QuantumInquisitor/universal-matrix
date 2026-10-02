# Nonlinear connector with explicit port-length mapping

`scripts/report_fold_mapped.py` implements a bounded candidate for interaction
between two modules with different effective connection lengths. This study
changes connector leverage only: both modules retain their existing masses,
inertia, restoring potential and reservoir laws. It does not yet represent
geometrically scaled solid bodies or a calibrated material connection.

## One potential, both forces

For scale s, angle theta and equilibrium angle theta0, define a synthetic port
displacement in metres:

`f(q,l) = l [s-1, s sin(theta-theta0)]`.

Its Jacobian is `J = l [[1,0],[sin(theta-theta0),s cos(theta-theta0)]]`.
Parent length is .1 m; child length is .1 times the chosen ratio. With
`K=diag(.3,.1) N/m`, mismatch d=fA-fB and energy U=d^T K d/2, the generalized
forces are `QA=-JA^T K d` and `QB=JB^T K d`. Thus
`dU/dt + QA dot vA + QB dot vB = 0`.

The port forces are opposite; generalized scale/angle forces need not be equal
because the Jacobians differ. This virtual-work construction prevents a change
in leverage from silently creating energy. The two-component port is a chosen
mathematical mapping, not an observed spatial joint or measurement from the
reference image. It remains nonsingular in the currently validated domain.

## Results

Five four-second cases and one timestep refinement are recorded in
`experiments/fold-mapped-summary.json`, with initial states, five source hashes,
separate module/connector/global accounts and work/loss samples.

| Case | Maximum global residual (J) | Child mechanical energy at 4 s (J) |
| --- | ---: | ---: |
| Equal port lengths | 1.900e-13 | 2.216e-6 |
| Half-length child port | 2.036e-13 | 6.669e-7 |
| Quarter-length child port | 2.068e-13 | 1.733e-7 |
| Conservative, half-length, no fuel | 7.403e-14 | 6.431e-7 |
| Incorrect child Jacobian | 1.416e-6 | invalid as conservative mapping |

The half-length refinement from .02 to .01 s reduces global residual to
1.018e-14 J; per-coordinate/rate endpoint differences are below 3.628e-9 in
their respective units. Two steps show agreement, not a measured convergence
order. The wrong-Jacobian control leaves module work accounts near balanced
but violates connector/global balance, localizing the defect to force mapping.
Differences among the three valid cases describe this finite experiment; they
do not establish an optimal ratio or general scaling law.

Independent tests differentiate the port map and potential, check connector
power, derive the equilibrium stiffness blocks, and verify conservative transfer.
At equilibrium the connection Hessian is .01 times the block matrix
`[[K,-r K],[-r K,r^2 K]]`, with two null directions for common port displacement.
The module restoring potentials remain separate. Independent review checked
24 interior configurations: energy-rate agreement within 4.41e-14 W and
equilibrium Hessian agreement within 8.03e-14. No blocking issue was found.

## Remaining work

This establishes a conservative mapped connector candidate. Body geometry/mass
scaling, actual attachment locations, collision clearance, calibration and
hierarchical deployment remain unvalidated. No sustained breathing claim follows.
Next: specify how module length, mass and inertia scale together and check those
assumptions independently before applying the connector across recursive levels.
