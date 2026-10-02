# Independent small-motion fold reference

The synthetic 22-point reduction has two coordinates: scale and fold angle.
Linearizing its unforced, undamped mechanics at equilibrium gives
`M(q0) displacement_acceleration + K displacement = 0`. The geometric inertia
term is quadratic in velocity and therefore absent from this linearization.

`scripts/report_fold_modes.py` solves the symmetric mass-whitened eigenproblem
and compares the exact linear cosine trajectories against the existing nonlinear
integrator, with zero initial velocity. No fitting of the trajectories is used.
The frequencies are **0.2741982850 Hz and 0.3163579847 Hz**. These are predictions
of the chosen synthetic masses and stiffnesses, not measured material resonances.
Mode vectors are normalized by their largest numerical coordinate component;
scale and radians are kept separate, without a combined physical error norm.

Six 10-second comparisons cover both modes at amplitude parameters 0.02, 0.01,
and 0.005. Halving amplitude reduces position discrepancies by approximately
four, consistent with the local nonlinear correction. This window spans about
three oscillations; it does not establish indefinitely stable motion. A seventh
run halves the step from 0.01 to 0.005 seconds: final coordinate/rate differences
are at most 1.184e-10 in their respective units. Two steps demonstrate agreement,
not an independently measured convergence order.

The compact report at `docs/experiments/fold-modes-summary.json` retains each
coordinate's errors, mode shapes, energy residuals and normalized-text hashes
of the three source scripts. Tests independently check the equilibrium dynamics
Jacobian, generalized eigenvalue trace/determinant, mass orthogonality, frozen-mass
energy conservation and amplitude scaling. The Jacobian finite-difference error
is below 2e-9. This adds an independent reference to the existing energy tests.

For finite damping/drive/initial-state sensitivity, see `fold_robustness.md`.
Neither study supplies material calibration, recursive whole-structure exchange,
continuous collision certification, nor sustained autonomous breathing. The next
mechanistic extension needs an explicit energy reservoir and its own accounting.
