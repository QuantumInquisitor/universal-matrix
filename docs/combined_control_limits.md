# Combined measurement delay and actuator force lag

This optional P05 experiment composes the two existing synthetic paired-mode controller limits. It preserves the plant, target, controller gains, clipped command, unit stiffness, declared metre/second scales, and original diagnostic: 20 target periods, with position RMS over the final five periods no greater than 0.05 m. This is prescribed active tracking, not autonomous breathing or a physical hardware calibration.

## Composition contract

The plant is `q'=v`, `v'=-0.04v-(1+0.2 cos(2t))q+f`. The existing controller computes current-time target feedforward and feedback from the error measured at `t-delay`. The target is known analytically; subtracting its delayed value follows the existing `mode_pair_trace` convention. This is not a model of transporting an unknown source signal. Negative-time history holds the initial displacement error `(0.25,0)` relative to the travelling target; delayed stored states are linearly interpolated. Noise and stiffness mismatch are absent.

After vector clipping to the force-per-mass limit, the command `u` drives `f'=(u-f)/tau`. Positive-tau force starts at zero; tau=0 applies the command directly. The existing guards remain: a nonzero delay must span at least one step and `dt/tau<=0.5`. Both are numerical resolution restrictions, not inferred hardware boundaries. The RK4 method of steps only reads previously available mechanical history. Linear history interpolation and startup derivative changes limit the global convergence order; the report measures convergence rather than claiming fourth order for delayed runs.

The mechanical energy per unit modal mass is `E=(|v|²+k|q|²)/2`; its rate is `f·v -0.2 sin(2t)|q|² -0.04|v|²`. Integrated work uses the actual applied force, never the command. This force-state model specifies no electrical supply, storage, regeneration, heat or efficiency. It therefore cannot answer a total actuator-energy question.

## Validation and reproduction

The focused tests require exact trajectory recovery of the existing actuator model when delay is zero, and the existing delayed paired-mode model when tau is zero. Combined runs use three timestep resolutions, independently integrate sampled delivered mechanical power, require decreasing errors and nonnegative damping loss, and reject a deliberately incorrect command-work ledger.

Run `python -m pytest tests/test_combined_control_limits.py tests/test_proposed_actuator_bandwidth.py -q -p no:cacheprovider` and `python scripts/report_combined_control_limits.py --output docs/experiments/combined-control-limits-summary.json`.

The [summary](experiments/combined-control-limits-summary.json) records seven bounded cases at 256, 512 and 1024 steps per period, with normalized-text source hashes, actual RMS values and energy residuals. It includes zero-delay and zero-lag controls, combined delay/lag cases and a low-force negative control. These discrete cases do not locate a continuous failure boundary, establish indefinite stability, or cover broader delay/noise/saturation distributions. Measured actuator calibration and assembly-port coupling remain open.

## Bounded observations

At tau=0.1 s and delay=0.2 s, the finest-grid late RMS is approximately 0.017566 m, within the declared criterion. At tau=0.5 s and delay=0.2 s it is approximately 0.086469 m, outside it. At tau=0.5 s and delay=1 s the late RMS is approximately 17.7872 m, a large finite-run failure; maximum common-time state differences fall from approximately 0.03588 to 0.002656 between successive refinements. Agreement on failure does not imply a precisely converged failure boundary or indefinite stability. The zero-lag delay-only case has a small interpolation error that decreases with refinement.
