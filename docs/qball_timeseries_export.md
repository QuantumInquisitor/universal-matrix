# Q-ball scalar-sample export

The existing `t=2.5` run can now preserve its direct and perturbed scalar sample
arrays without a second evolution. Its default report text, numerical driver,
geometry, timestep, sample cadence and diagnostic criteria are unchanged.

```text
python -m src.qball_highres_timeseries_t2p5 --samples-json artifacts/qball-t2p5-samples.json
```

The long-timeseries CI job adds this export option to its existing invocation
and uploads `qball-t2p5-samples`. It does not add a numerical run. A skipped
numerical job produces no new artifact; old successful CI is not retroactively
claimed to contain samples.

## Data and provenance

Both channels preserve all sample fields at JSON/Python floating-point precision:
integration step, model time, relative energy drift, relative charge drift,
normalized peak amplitude and normalized RMS radius. Each channel uses its own
initial normalization. Model time and length have no newly assigned seconds or
metres; normalized ratios and drifts are dimensionless. The existing sampler's
zero-reference conventions are unchanged and documented in the hashed source.

The payload records steps, timestep, sample stride, fixed default grid and
perturbation configuration, candidate-selection method, Python/package versions,
Git head/dirty-source state when Git metadata is available, and normalized
UTF-8/LF hashes of every top-level `src/*.py` file. This intentionally broader
source snapshot includes unused files; it is not a claimed execution dependency
trace. The selected radial field, absolute initial normalization values and
complex lattice fields are not stored. Detailed solver parameters/tolerances
remain in the hashed source snapshot.

`timeseries_payload` and `write_timeseries_samples` also accept already-computed
results with **explicit caller-supplied** configuration and provenance. They do
not infer default physical parameters for arbitrary results. The convenience
`export_t2p5_samples` is specifically for the existing default driver.

## Limits

These arrays support later diagnostic reanalysis, not restart: they are not
field checkpoints and contain no complex-field phase signal. Export does not
identify a breathing period, establish sustained oscillation or prove stability.
The existing negative classification of the short record remains unchanged:
retained peak intervals `1.375` and `.675` are inconsistent, and a single radius
maximum does not establish repeated phase relations. Longer/converged evidence
remains a separate scientific question.

Tests round-trip every sample field using explicit synthetic data, reject
nonfinite JSON, verify normalized source hashes, and prove that either CLI mode
calls the driver once and preserves the original report output. No expensive
evolution is needed for serializer tests.
