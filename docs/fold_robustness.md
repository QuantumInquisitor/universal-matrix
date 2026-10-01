# Bounded fold-dynamics sensitivity

This study advances the existing synthetic, 22-lump, two-coordinate force model without changing its masses, force law, geometry, or numerical domain. It is a finite-duration sensitivity check, not a physical material validation or a long-time stability theorem.

## Experiment

`scripts/report_fold_robustness.py` produces a compact, finite JSON report at a supplied `--output` path. The stored `docs/experiments/fold-robustness-summary.json` records normalized-text SHA-256 hashes of all three scripts: kinematics, dynamics, and this experiment.

The 24 cases comprise:

- 18 combinations of duration 2 or 10 s, damping multiplier 0, 0.25 or 1, and external-drive multiplier 0, 1 or 3, with timestep 0.02 s.
- Two independently perturbed initial conditions using NumPy PCG64 seed 20260930. Uniform perturbation amplitudes are 0.01 scale, 0.015 rad, 0.01 scale/s and 0.015 rad/s around the existing initial condition. The full initial vectors are saved.
- One accepted 10 s, damping 0.25, drive 1 case repeated at timestep 0.01 s.
- A deliberate high initial scale rate of 2/s, repeated at 0.02, 0.01 and 0.005 s timesteps, with no drive or damping.

“Success” means the integrator completed inside its declared rectangle, including checked Runge–Kutta stages. “Domain-rejected” means the specific existing coordinate-domain exception was raised. It does **not** establish a collision, an exact physical boundary-crossing time, or a solver-independent escape trajectory. Linear-algebra, overflow and floating-point failures are classified separately as numerical errors. Unrelated `ValueError` exceptions propagate rather than being relabeled as physics failures.

## Results

There are **21 successful integrations, 3 domain rejections and no numerical-error outcomes**. All three deliberate high-rate runs are rejected. That agreement across refinement shows that rejection is not confined to the coarsest step; it is not a collision certificate or an event-localized proof.

Across accepted cases the largest absolute energy-balance residual is **2.997711101701203e-12 J**, and the largest relative residual is **1.4244619905469117e-8**. The relative denominator is the maximum of initial energy, maximum absolute energy, maximum absolute accumulated work, and maximum absolute accumulated damping loss. It is not final energy, which may decay. The balance is `E - E_initial - work + loss`; its small residual checks this synthetic model's accounting, not missing real-world energy channels.

For the 10 s accepted refinement, the maximum residual falls from **1.541244269457286e-13 J** to **4.298032156891426e-15 J**. Final coarse-to-fine differences, kept separate by coordinate and unit, are:

| Quantity | Absolute difference |
| --- | ---: |
| Scale | 6.597585811007889e-9 |
| Fold angle (rad) | 6.105568550740514e-9 |
| Scale rate (1/s) | 3.0069218504014117e-9 |
| Fold rate (rad/s) | 4.6377732626501356e-9 |

At 10 s with the drive off, final/initial energy is approximately 1.0000000, 0.8410630 and 0.5012077 for damping multipliers 0, 0.25 and 1 respectively. With drive multiplier 3 those ratios are 34.6948478, 32.2868921 and 26.1567080: the applied source can add energy even as damping removes some. This does not establish autonomous sustained breathing.

The JSON retains separate scale, angle and both rate minima/maxima for each accepted trajectory. These are endpoint-sampled extrema; intermediate derivative stages are domain-checked but their extrema are not reported. Rejected runs have no fabricated final-state or partial-trajectory metrics.

## What remains

These observations cover only the stated finite settings and two seeded perturbations, not a distributional robustness guarantee. Larger ranges, longer than 10 s, continuous collision verification, calibrated masses/materials, force/contact laws, and coupling across the whole structure remain separate work. Existing geometry clearance reports must not be silently applied to this trajectory.

Tests exercise accepted metrics, deterministic input generation, the refined deliberate rejection, unrelated-error propagation, numerical-error classification, and decreasing energy error under accepted-step refinement.
