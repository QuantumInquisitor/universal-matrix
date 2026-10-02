# Ordinary phase tracking with delayed information

This bounded P05/P06 control measures delayed response to an intervention, noise filtering and recovery. It does not simulate a time crystal or establish a time-crystal advantage. Existing `artifacts/time-crystal/time-crystal-subsystem.json` already records a finite six-qubit timing-source/divider comparison with pulse and readout errors; the present experiment adds a distinct classical transport/control baseline rather than repeating that calculation. Those older results were inspected, not rerun here.

## Declared model

All times and couplings are dimensionless; phase is in radians. In coordinates rotating with an ideal prescribed clock, the receiver obeys

`dq/dt = K sin(s(t - tau) + eta(t - tau) - q)`.

The source `s` is zero until time 2 and then jumps by a seeded randomly selected signed amplitude between 0.5 and 0.8 radians. The receiver has no anticipatory term and no access to the source's random generator. This is a reproducible unpredictable-to-the-receiver intervention, not a cryptographic randomness claim. Before time zero the input and noise histories are exactly zero. `eta` is independent held uniform measurement noise in `[-a, a]`, held for 0.1 time units at the source and transported with the same delay. A paired trajectory removes the jump but retains exactly the same noise history.

The ordinary comparison readout is direct transport `s(t-tau)+eta(t-tau)`, with no filtering. It responds immediately at programmed arrival and retains the measurement noise. `K=0` supplies the disconnected receiver control. This is a deliberately simple comparator, not an optimized phase-locked loop or the existing divider implementation.

Classical RK4 integrates over intervals with constant input, respecting every discontinuity on the time grid. The three step sizes share the same source noise realization; a fresh noise draw per integration step would not provide this convergence comparison. Unaligned event times are rejected rather than rounded silently.

## Observables and results

The committed report is [phase-delay-controls-summary.json](experiments/phase-delay-controls-summary.json). The reporter includes its own normalized-text SHA-256 and all 54 case records: three delays (0, 0.5, 1), three coupling strengths (0, 0.5, 2), two noise amplitudes (0, 0.03), and three seeds (7, 19, 41). Each committed record includes its exact injected amplitude, first detected intervention difference, final error, sustained recovery and an effort proxy. The compact committed snapshot omits per-case traces; the reporter produces full downsampled traces when rerun.

* Arrival uses the difference between intervention and no-intervention receiver states, exceeding `1e-6` radians. Their difference is exactly zero through the declared transport-arrival boundary. With nonzero coupling, detection occurs at the next integration sample, not before arrival. The disconnected receiver never detects the intervention.
* Recovery is the first sample within 0.05 radians of the noiseless delayed target that remains within that tolerance for the rest of the record, with at least one time unit of confirmed residence. Missing recovery is JSON `null`, not a fabricated zero or success. It is a finite-record criterion, not a proof of indefinite stability.
* For delay 0.5, coupling 2 and noise 0.03, recovery after arrival is 1.36–1.44 time units across the three seeds. The paired no-kick receiver RMS in the final two time units is 0.00329–0.00595 radians, versus 0.01494–0.01734 for direct noisy transport. Smoothing therefore trades response time for reduced measurement noise in these cases. No broad optimum is claimed from three seeds.
* Refinement at steps 0.02, 0.01 and 0.005 gives final-state differences of `1.039e-10` and `6.381e-12` radians. The same case detects at 2.52, 2.51 and 2.505, approaching the prescribed arrival 2.5 from above. A separate noiseless test checks the exact solution `q=A-2 atan(tan(A/2) exp(-K*(t-t_arrival)))`.
* Integrated squared phase drive is a model control-effort proxy. It is **not joules**, a full thermodynamic balance, or evidence that time supplies energy. Direct transport has no assigned actuator-energy model; the experiment consequently does not claim an energy advantage for either method.

## Reproduction and remaining work

For the full reproducible traces, run `python scripts/report_phase_delay_controls.py --output artifacts/phase-delay/results.json` and `python -m pytest tests/test_phase_delay_controls.py -q -p no:cacheprovider`. The focused suite contains 13 passing test cases; Ruff passes on reporter and tests.

Remaining: apply matched latency/loading/readout assumptions to the existing divider and proposed timing component; quantify jitter and missed ticks at the actual 36-step interface; supply physical actuator/bath units and energy costs; test receiver feedback delay (the present delay is transport-only), detuning, saturation, much longer runs and wider noise ensembles; map channels to actual assembly ports; test multi-hop or recursive propagation with independent persistent state. This experiment has no spatial distance or physical propagation speed, no faster-than-light conclusion, no autonomous breathing mechanism, and no material-force model. P05 and P06 remain open.
