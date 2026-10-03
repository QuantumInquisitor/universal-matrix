# Finite-band measurement-noise comparison

This optional P05 experiment adds declared synthetic measurement disturbances to the accepted paired-mode controller. It preserves the plant, unit-radius/unit-frequency target, gains, vector force limit 10 m/s², initial mechanical state, 20-period duration and original final-five-period position RMS target of 0.05 m. It is active tracking of a known reference, not spontaneous breathing, quantum bath dynamics or calibrated hardware performance. Existing production defaults and reports remain unchanged.

## Frozen protocol

Two configurations are compared: instantaneous actuator/measurement timing `(tau,delay)=(0,0)` and the accepted combined limit `(0.1 s,0.2 s)`. Each uses position/velocity noise sigmas `(0.01 m,0.01 m/s)` and `(0.1 m,0.1 m/s)` with seeds 7,19,41, at 256 and 512 steps per target period. Each configuration also has zero noise at both resolutions. Seed 7 at the larger amplitude adds 1024-step refinement in both configurations: 30 integrations total, not 30 independent statistical samples. The numerical gates were independently reviewed before the sweep. A five-period 256-step timing pilot took approximately 1.48 seconds; it is not an additional scientific result.

For each of four independent measurement channels, saved standard-Gaussian coefficients define

`eta_c(t)=sigma_c/sqrt(8) sum_j [a_cj cos(omega_j t)+b_cj sin(omega_j t)]`,

with fixed angular frequencies `[0.5,1,2,3,5,7,11,13] rad/s`. The [coefficient fixture](../tests/fixtures/control_noise_coefficients.json) records all arrays and generator PCG64, pinned by normalized-text hash. Coefficients are reused across configurations, amplitudes and timestep refinements; RNG is never called in integration/RK stages. The finite Fourier ensemble has zero ensemble mean and pointwise ensemble variance sigma². Each realization is smooth, temporally correlated and, with these commensurate frequencies, repeats every 4pi seconds. It is not white noise, a calibrated sensor spectrum or an ergodic reliability sample.

Position disturbances use metres; velocity disturbances use metres/second. Equal numeric sigmas mean the synthetic choice `sigma_v=omega_target*sigma_q`, not equal units. Independently perturbed velocity is a separate readout/estimate channel, not the derivative of noisy position. The same realization is evaluated at `t-delay`, including negative-time history, and added only to the delayed measured error. It does not change true initial state or current-time feedforward.

## Metrics and numerical decisions

The 0.05 m tracking diagnostic always uses true positions. Realized noise mean/RMS, actual-force RMS and clipping fractions use equal-weight output samples from t=0 through the final time, inclusive. Noise is evaluated at the corresponding delayed measurement time. They are not RK-stage averages or exact continuous-time statistics. Late position RMS retains the existing last 5*steps samples, excluding the first endpoint of the final-five-period window.

All actual actuator work uses delivered force dot true velocity. Pump work and damping loss retain the original mechanical-per-unit-mass ledger, in m²/s². Command is not delivered force when tau is positive. A separately sampled trapezoidal total-power balance and a deliberately wrong command-work substitution provide independent accounting controls. There is no electrical supply, actuator storage, efficiency or joule/hardware advantage model.

The fixed reproduction gates are common-time position difference <5e-4 m, velocity difference <5e-4 m/s, late-RMS difference <1e-4 m and integrated energy-balance residual <1e-5 m²/s². For the two preselected finest runs, differences must decrease unless already below 1e-10 in their respective units. Sampled power-quadrature residual must decrease under refinement; damping increments must be nonnegative. These thresholds assess numerical reproducibility, not stability. A failure is retained as `numerically_unresolved`; no physical-controller failure is inferred from it.

If the original tracking classification changes across resolutions or a result is within 1e-4 m of 0.05 m, the case is `borderline_unresolved` unless a numerical gate has already failed. Otherwise its label is `meets_finite_run_target` or `fails_finite_run_target`. No gain/sigma/threshold was tuned to obtain a desired outcome. The two 1024 runs have paired zero-noise differences only at 256/512 because the frozen budget does not include 1024 zero-noise runs.

## Reproduction and scope

Run `python -m pytest tests/test_proposed_noisy_control.py -q -p no:cacheprovider`, then `python scripts/report_control_noise.py --output artifacts/control-noise-report.json --summary docs/experiments/control-noise-summary.json`. The full artifact preserves every trajectory and realization; the committed summary retains all case metrics, failures, refinements, coefficients and source hashes. Hashes use UTF-8 text normalized to LF. Runtime is metadata and can vary across machines.

Tests cover exact zero-amplitude equivalence and positive-sigma/all-zero-coefficient equivalence through the noisy arithmetic, independent Fourier evaluation including delayed negative times, common paths under refinement, a per-step-random-redraw negative control, actual-force/limited-command accounting, input validation and classification precedence/borderlines/nonconvergence. Scientific failures are valid outcomes; numerical failures remain explicitly unresolved.

Three seeds cannot establish a population failure probability, indefinite stability or a continuous noise threshold. A redesign comparison is not included. Hardware use needs measured position/velocity spectra and cross-correlations, estimator bandwidth/latency/quantization, actuator response/limits and physical calibration. Quantum noise and electrical energy remain separate contracts.

## Completed frozen results and durable backup

All 30 integrations completed. All 14 case groups passed the reviewed numerical reproduction gates and none is borderline/unresolved. Both zero-noise controls and all six lower-noise cases meet the unchanged 0.05 m target; all six higher-noise cases fail it. At 512 steps/period, lower-noise ideal RMS spans 0.006714–0.007711m and combined lag/delay spans 0.016814–0.020424m. Higher-noise ideal RMS spans 0.067138–0.077106m and combined lag/delay spans 0.068269–0.074309m. The preselected 1024-step cases retain the same failure classification. These are outcomes for the saved realizations, not population reliability estimates.

The complete original trajectory report is retained in Git as [control-noise-report.json.gz](experiments/control-noise-report.json.gz), alongside its [archive manifest](experiments/control-noise-archive-manifest.json) and [summary](experiments/control-noise-summary.json). The manifest records compressed/restored byte counts and SHA-256 hashes. Compression uses gzip level 9 with zero timestamp; decompression was verified byte-identical to the original completed report, and the summary equals the full report with only `traces` omitted. All consumed source hashes were checked after completion. No integration was rerun to create this archive.

To restore without changing original line endings, run from the repository root:

```python
from pathlib import Path
import gzip, hashlib, json
folder = Path("docs/experiments")
manifest = json.loads((folder / "control-noise-archive-manifest.json").read_text())
archive = Path(manifest["archive_path"]).read_bytes()
assert hashlib.sha256(archive).hexdigest() == manifest["archive_sha256"]
raw = gzip.decompress(archive)
assert hashlib.sha256(raw).hexdigest() == manifest["restored_sha256"]
Path("control-noise-report.json").write_bytes(raw)
```
