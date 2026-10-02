# Distributed-inertia trajectory controls

This isolated P07/P08 experiment uses PR #146's uniform reference-panel and
bridge-line inertia with the existing synthetic constitutive potential,
damping matrix and prescribed drive. Historical production dynamics remain
unchanged. The same 22 mass owners total 0.74 kg; no new mass or material
coefficient is fitted.

The equation is `M(q) a + bias(q,v) + grad V(q) + D v = force(t)`.
Applied work and damping loss are integrated separately. The audit evaluates
kinetic energy from the 82 Cartesian material-point velocities, then checks
`T + V - initial energy - work + loss = 0`. Work is a transfer, not additional
stored energy.

The declared interval is 0.4 s. DOP853 uses rtol 1e-10 and atol 1e-13, with
maximum steps 0.02 and 0.01 s and 81/161 output samples. These are maximum-step
and output-quadrature comparisons, not a claim of measured solver order.
Cases cover equilibrium, conservative, passive, driven and smooth drive-off
motion. Independent trapezoidal power quadrature must converge on refinement.
A conservative time-reversal control and deliberately omitted inertial bias
test the dynamical reduction. Omitting damping loss from the passive audit
must also be detectable.

Acceptance: energy residual below 1e-10 J, refinement and reversal state
differences below 1e-8, independent work/loss quadrature errors below 1e-9 J,
and omitted-bias error above 1e-9 J. Coordinate validation applies at derivative
stages and output samples; it is not a continuous collision certificate.

Reproduce with:

```text
python -m scripts.report_fold_distributed_trajectories --output artifacts/distributed-trajectories.json
```

The report records source hashes,
solver settings, traces and controls. Run the matching pytest module for
independent quadrature convergence and ledger fault checks.

The committed run's maximum healthy energy residual across the five cases is
8.09e-19 J. Independent power quadrature errors fall by approximately four
when sample spacing is halved; their fine-grid maximum is 8.33e-12 J.
The reversal error is 7.39e-16, and the omitted-bias control produces
2.96e-6 J error versus 6.92e-19 J in its healthy counterpart. These are
bounded numerical observations, not physical measurement precision.

This does not close P07 or P08: finite-thickness inertia, hub rotation,
physical joints, contact and calibration remain absent. The external drive
is prescribed and has no finite supply in this isolated experiment. Recursive
network integration, direct viewer replay and sustained breathing remain open.
