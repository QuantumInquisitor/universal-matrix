# Fixed aperture and replacement route integration

This optional reference carries preserved local aperture, inner/outer attachment
and edge-2 rerouting experiments into repository modules. Existing default
builders are unchanged. All lengths are dimensionless model units. This is a
static kinematic current construction, not a material or moving assembly model.

The first aperture explicitly modifies the enclosing annular host and diverts
its 0.6 I current around a separate 0.4 I transit. One bend and one straight
connect that transit to the existing C-bore downstream reference. An eight-piece
outer detour connects B to the aperture's outer cap. The outer detour is an
existence candidate, not an optimized or compact route.

A separate fourteen-piece replacement for edge 2 uses a second aperture and a
negative-y detour. The second patch is a proper rotation of the first local
streamfunction chart and lies on another host leg. The detour remains at
negative y for both current signs; reversing current is not assumed to rotate
the entire original scene. Source and destination port geometry, orientation,
current profile and signed flux are checked against the original ports.

## Interfaces and audit scope

| Module | Role | Explicit scope |
| --- | --- | --- |
| `src/toroidal_aperture_local.py` | Local modified-host streamfunction and transit | Fixed aperture specimen; stagnating central streamline remains. |
| `src/toroidal_aperture_attachment.py` | First aperture plus inner connection | 117 inner changed-component pairs and 56 aperture/environment pairs, plus the explicit host bound. |
| `src/toroidal_outer_attachment.py` | B-to-outer-aperture detour | 508 pairs involving the eight new pieces and declared environment. |
| `src/toroidal_aperture_fanout.py` | Edge-2 replacement and second patch | 861 replacement-route pairs against its pieces and 55 environment components; 13 internal interfaces. |
| `src/toroidal_retained_collision.py` | Original retained-geometry rejection control | A positive sampled penetration can establish a collision; no hit never establishes clearance. |

The public entry points are `build_aperture_attachment(current)`,
`audit_aperture_attachment(reference)`, and the optional outer/fanout modules'
`build_candidate(reference)` and `run(current)`. The supported regression grid
is I = +/-1, +/-2e-8, +/-7. Passing that grid is not a parameter-interval proof.

These inventories overlap and must not be added into a unique whole-network
count. The original retained-only control still refers to the old edge-2 route.
Its collision finding and the replacement candidate's passing result describe
different configurations. The fan-out certificate deliberately sets
`full_network_certified` and `motion_certified` to false. The first attachment's
open-boundary flags describe that partial reference, not the later detour.

Clearance classifications use analytic bounding boxes, coaxial shells, support
planes and fixed geometric bounds evaluated in floating point. Intended port
contacts have zero gap. This is not outward-rounded interval certification.
Changed-host flux and route flux are independently integrated using physical
cut areas; field matching and divergence refinement are separate numerical
checks. The exact fixed builder constraints must remain visible if the
geometry is later generalized.

## Reproduction

From the repository root:

```sh
uv run python -m pytest tests/test_toroidal_aperture_attachment.py tests/test_toroidal_outer_attachment.py tests/test_toroidal_aperture_fanout.py tests/test_toroidal_bore_downstream.py tests/test_toroidal_bore_downstream_adversarial.py
uv run python scripts/report_aperture_integration.py --output-dir artifacts/aperture
```

The report command writes six complete case records and a source-hashed summary.
It rejects any failed outer/replacement result or accidental whole-network
completion flag. A compact checked-in snapshot is at
`docs/experiments/aperture-summary.json`; full pair/field records regenerate
under `artifacts/aperture`. The dedicated workflow repeats tests and reports.

Fresh integration validation: 121 selected attachment/fan-out/downstream tests
passed in 73.22 seconds. All six report cases and the workflow's acceptance
assertions passed locally. Maximum outer-cut relative flux error was
1.97e-14. All 28 transitive existing source dependencies match main after
newline normalization. Nine new Python files pass Ruff check and formatting.
This is not a fresh full-repository test result.

Integration changes are limited to module/import organization, removal of
scratch-file output and import-time bytecode side effects, explicit zip lengths,
bound loop closures, formatting, and a portable exporter. Original scratch
files are preserved. The field equations and fixed route coordinates are
carried forward unchanged.

## Remaining geometry and physical work

Assemble a single authoritative combined inventory with both host patches,
replacement ports and intended contacts, then audit every retained-retained and
changed-retained pair under that same state. Follow with safe continuous motion,
wall-opening feasibility, material mechanics, full energy/flow accounting and
recursive coupling. This checkpoint neither removes the central stagnating
streamline nor supplies physical calibration or experimental validation.
