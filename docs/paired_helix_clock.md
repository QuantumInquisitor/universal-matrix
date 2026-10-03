# Declared paired-helix clock adapter

This optional kinematic construction represents the existing canonical
36-tick phase as a rigid rotation of two labeled strands. It preserves the
clock law; it does not derive geometry from routing, infer depth from an image,
assign a physical tick duration, or modify the DNA/VR viewers.

## Geometry and action

In synthetic coordinate units, choose radius `a`, signed pitch `p`, parameter
`u`, and strand label `s = 0 or 1`:

```text
h_s(u) = (a*cos(u+s*pi), a*sin(u+s*pi), p*u/(2*pi))
Q = Rz(azimuth) Rx(tilt)
X_s(u,k) = Q Rz(polarity_phase_from_tick(k)) h_s(u)
```

The implementation imports `polarity_phase_from_tick` directly from the
unchanged integrated `src/canonical_polarity_clock.py`. Elapsed tick `k` is an
explicit signed integer, independent of any base-node label. One routing cycle
contains 36 ticks; the 108 core labels are not 108 ticks per cycle.

The preserved controls use `a=.4`, both `p=+.3` and `p=-.3`, tilt `.49` radians,
azimuth `-.27` radians, and 101 points per strand over `[-2*pi,2*pi]`. The tilt
and azimuth are display choices. They do not imply a physical orientation.

| Tick increment | Chosen geometric action |
| --- | --- |
| 9 | Quarter-turn about the tilted helix axis |
| 18 | Strand positions exchange; marked material points move |
| 36 | Each labeled strand and material marker returns |

The unlabeled pair has an 18-tick outline period, while the labeled geometry
has a 36-tick period. Rotation adds no axial translation. Pitch sign remains
independently supplied: the proper half-turn is not a reflection or handedness
reversal. The parameter `u` remains the same material coordinate under rotation.

## Public API

```python
import numpy as np
from src.paired_helix_clock import PairedHelixClock

adapter = PairedHelixClock(radius=.4, pitch=.3)
u = np.linspace(-2*np.pi, 2*np.pi, 101)
frame = adapter.frame(9, u)  # shape (2, 101, 3), labeled strands
marker_pair = adapter.frame(18, .35)  # shape (2, 3)
```

`strand(u, label)` supplies local geometry; `orientation` returns the chosen
proper placement rotation. `frame` returns a new array. Radius must be positive;
pitch can be positive, negative, or zero (the degenerate planar-circle limit).
Complex, nonfinite and boolean inputs, malformed parameter shapes and noninteger
ticks reject explicitly. Unrepresentable coordinate arithmetic raises an error.
The model does not claim reliable geometric resolution for arbitrarily extreme
finite scales or angles.
The second strand uses the equivalent radial sign reversal rather than adding
pi to a large material parameter. This preserves diametric pairing even when
floating-point addition would absorb that offset; it does not restore phase
information already lost in an externally supplied large value.

## Reproduction and provenance

```text
python -m pytest -q tests/test_paired_helix_clock.py tests/test_canonical_polarity_clock.py
python -m scripts.report_paired_helix_clock --output artifacts/paired-helix-clock.json
```

The reporter reruns all 28 preserved grouped checks against the reusable adapter:
108 base-node clock contracts, all 36 starting ticks for both pitch signs, all
1,296 rotation compositions, marker motion, labeled/unlabeled returns, and the
incorrect 108-tick-denominator negative controls. Independent tests check direct
cardinal coordinates, preservation of distances/axial coordinates and signed
rise, wrapping, malformed inputs, and failure of the preserved audit when the
adapter is deliberately changed to the wrong 108-tick action.

The local promotion run passed all 28 controls and 53 focused tests. Original
inputs, thresholds and check names are preserved. The equivalent radial-sign
construction changes some roundoff-level residuals from the archived report;
bounded results agree within the original tolerances. The committed summary
stores the reproduction evidence; remote
platform execution remains a separate validation step.

Preserved scratch files remain unchanged. Original raw SHA256 values:

- Probe `helix_clock_adapter_probe.py`: `577b02dfd476973e97b08a9b424ceb6b1ecad2b109d727f72a5962265caf78e3`
- Result `helix-clock-adapter.json`: `c5c80a5853c0b20118dcc0dc5ffc1cd42cc866a402a3f625aac939ef3bf2eba0`
- Note `helix-clock-adapter.md`: `67829dd1fbb962c9d65e33a0ede09225e6ebd25206ad7b3f7a7793b3351856dc`
- Imported clock (original CRLF bytes): `1ad6e30821c4283bd0f18df06d3ce0ace9b7182b2a21d8ae5f4725aa309e545a`
- Same clock normalized as UTF-8/LF: `e1a2f869cb62c2a9694a4bd941b217f18aaa511b5eedd49ba059a2894198c055`

The integrated clock is exactly equal to the preserved clock after newline
normalization. The reporter distinguishes raw original hashes from current
UTF-8/LF source hashes, including the canonical kernel, clock, adapter and
reporter. Metadata now explicitly includes tilt and azimuth; the new summary
is therefore not claimed byte-identical to the preserved report.

## Remaining scope

This supplies a declared representation, not a unique physical derivation.
No seconds, hertz, torque, energy, flow, joints, thickness, or material dynamics
are inferred. Physical calibration and helix/flow correspondence remain open.
Canonical clock results, current material mechanics, and viewer geometry are
not replaced by this adapter.
