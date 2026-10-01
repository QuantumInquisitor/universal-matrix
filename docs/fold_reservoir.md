# Finite reservoir for fold feedback

The optional experiment `scripts/report_fold_reservoir.py` retains the synthetic
22-point kinematics, inertia and restoring potential. A velocity-aligned feedback
force replaces the external time waveform. This is an autonomous equation with
a finite internal energy source, not a demonstration of sustained breathing.

With reserve R, activation scale R*=1e-5 J, feedback gain g and efficiency eta:

- Force A = g R/(R+R*) D v; delivered power P = v^T A >= 0.
- Reserve rate = -P/eta - leakage R.
- Mechanical energy rate = P - damping v^T D v.
- Separate loss rates are damping v^T D v, (1/eta-1)P and leakage R.

Mechanical energy plus reserve plus all three losses is constant. Transferred
work is tracked separately and must not be counted twice in total energy.
The finite supply bound is W <= eta R_initial. Zero reserve disables feedback;
exact rest at equilibrium does not self-start. This phenomenological actuator
law has no measured material implementation or controller-power calibration.

For g>damping>0, mechanical energy can grow only while
R > damping R*/(g-damping). With g=4 and damping=1 this threshold is
3.333333e-6 J. The exact reserve stays nonnegative and approaches depletion
asymptotically; negative numerical stages are rejected without clipping.
RK stages and endpoints retain the existing coordinate-domain checks, which
are not a continuous solid-body collision certificate.

## Reproduced results

Six 10-second cases cover fueled feedback, empty reserve, disconnected feedback,
exact equilibrium, ideal lossless transfer, and a deliberately omitted reserve
debit. A seventh run refines the fueled timestep from .02 to .01 seconds.
The source-hashed compact output is `experiments/fold-reservoir-summary.json`.

Default reserve falls from 2e-5 J to 6.61439e-7 J. Delivered work is
7.40857e-6 J; damping, conversion and leakage losses are respectively
5.67028e-6, 1.85214e-6 and 1.00778e-5 J. Mechanical energy at 10 seconds is
7.91447e-6 J, below its earlier sampled peak of 8.93690e-6 J. The reserve is
below the damping threshold, so continuing mechanical growth is impossible
under this law. Positive losses prevent an indefinitely fueled nonzero cycle.

Maximum total ledger residual is 1.83306e-13 J, improving to 8.49182e-15 J
under refinement; per-coordinate endpoint differences are below 8e-9 in
their respective units. Ideal transfer conserves mechanics plus reserve to
8.01e-13 J. Omitting the reserve debit produces 1.54121e-5 J of unaccounted
energy. This negative control distinguishes a simulated energy source from
an accounting mistake.

Tests independently differentiate total energy, replay the existing passive
model, compare isolated leakage with its exponential solution, check finite
supply and monotonic ledgers, and detect the deliberately broken accounting.
No new default engine behavior, calibrated material, full-structure recursive
exchange or XR integration is supplied. Next: explicit equal-and-opposite
energy exchange between two coupled modules, then recursive composition.
