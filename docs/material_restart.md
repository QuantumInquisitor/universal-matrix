# Material specimen restart and switched-input control

This optional experiment extends the existing synthetic two-mass specimen. It does not map material properties onto the 69-component assembly and does not establish autonomous breathing or recursive coupling.

Run `python scripts/report_material_restart.py --output docs/experiments/material-restart-summary.json` from the repository root. The report compares 0.04, 0.02 and 0.01 second fixed timesteps over 12 seconds. The sinusoidal input acts for the first 4 seconds and is then removed for 8 seconds. This is a true change within each trajectory, rather than a separate initially undriven run.

## Reproducible state

The checkpoint contains the model identifier, normalized UTF-8 hashes of both the existing material source and this adapter, all SI parameters, timestep, drive cutoff step and time, absolute integer step and time, original initial conditions, displacements, velocities and accumulated work/loss/transfer channels. Restart rejects changes to this contract, invalid state shape, nonfinite values, negative loss, inconsistent loss sums, or a time that disagrees with the integer step. Contract comparison uses a canonical digest, distinguishing booleans from numeric versions.

The JSON envelope includes a SHA-256 payload checksum. This detects an altered payload without an updated checksum; it is not authentication or protection against somebody rewriting the payload and checksum together. Schema checks do not prove that a loaded trajectory was physically generated. Exact replay is demonstrated on the same floating-point implementation, not promised across architectures or Python versions.

The split run serializes and reloads before, at and after cutoff and at the final step. Every stored state channel matches the unsplit run exactly in all three timestep cases. Absolute step-based time prevents restart from resetting the drive phase.

## Drive switching and energy ownership

RK4 uses the driven model throughout each interval strictly before the cutoff, including its endpoint quadrature. The next interval uses zero input throughout. This one-sided treatment respects the discontinuity without mixing the two forcing laws inside an interval. Accumulated external work is exactly unchanged after cutoff.

Body 0 owns its kinetic and anchor-spring energy; body 1 owns its own corresponding terms. The connecting spring has a single separate storage account. With link force on body 0 denoted F, the independently integrated transfers into the bodies are F v0 and -F v1. Anchor losses are ca viÂ², and link loss is cl(v1-v0)Â². Thus:

- Î”E0 = external work âˆ’ anchor-0 loss + link-to-body-0 transfer.
- Î”E1 = âˆ’anchor-1 loss + link-to-body-1 transfer.
- Î”Elink = âˆ’both link transfers âˆ’link loss.

Adding these accounts recovers the original global energy equation without counting spring storage twice. Loss is integrated at RK stages independently of endpoint energy.

## Validation and interpretation

Tests compare the input-off continuation with an independent analytic damped normal-mode solution. For these chosen coefficients the symmetric and antisymmetric displacement envelopes decay as exp(-0.05 t) and exp(-0.25 t), respectively, measured from cutoff. The final displacement and velocity errors at 0.01 second steps are below 5e-9 in their respective SI units. Each owner balance error decreases by more than 100 times across the 4:1 timestep refinement and is below 1e-9 joule at the finest timestep. Zero-state and disconnected-link controls remain exactly zero where expected.

The loss of stored energy after input removal is passive decay, not sustained emergent motion. Geometry-dependent constitutive parameters, nonlinear contact, real specimen calibration, multilevel ownership and a specified energy supply for sustained motion remain unfinished.
