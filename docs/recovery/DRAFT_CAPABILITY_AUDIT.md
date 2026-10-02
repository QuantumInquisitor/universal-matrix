# Draft capability reconciliation and lynchpin reuse

Audit requested after the material/harmonic checkpoint. The owner-scoped GitHub
search returned six visible open drafts, all in `QuantumInquisitor/universal-matrix`.
The two known local clones also point to that repository. This audit covers
those six drafts and their full changed-file inventories; it is not a new audit
of every historical closed PR or every file on disk. PR117/118 are open dependency
updates, not scientific drafts. No PR was merged or closed.

## What was already done

| Draft | Implemented evidence to retain | What remains |
| --- | --- | --- |
| [119: folding and breathing geometry](https://github.com/QuantumInquisitor/universal-matrix/pull/119) | Exact six-panel/four-hinge incidence; fixed-angle rigidity; explicit compliant folding; finite panel metrics; connected 22-body specimen with localized attachment checks; continuous clearance controls; prescribed size/current transport; 202-frame geometry export; continuous mirror control | Material/contact physics, force-driven motion, whole-flow correspondence, generalized recursive assembly and actual viewer integration |
| [120: nonlinear waves and controllers](https://github.com/QuantumInquisitor/universal-matrix/pull/120) | 14 nonlinear single-mode controls, eight two-mode controls, 11 controller robustness runs, energy/angular-momentum diagnostics; saturation, detuning, seed/restart/refinement and long-duration comparisons | Broader wavelength/boundary/stochastic ensembles, bandwidth/redesign, physical coupling and pattern selection; the later third/fifth-harmonic work is a new extension |
| [121: optional timing subsystem](https://github.com/QuantumInquisitor/universal-matrix/pull/121) | Timing adapter and ordinary-divider comparison; 168 runs with six/eight spins, eight seeds, interaction/pulse/readout controls and a 1,024-period extension; explicit resource counts | Hardware backaction, loading, latency, continuous readout, joule costs and a supported practical advantage |
| [122: recovery and mechanics](https://github.com/QuantumInquisitor/universal-matrix/pull/122) | Recovery ledger, source/image reviews, phase controls, material benchmarks, source-derived inertia, force/energy tests, mapped and hierarchical coupling, scaling, reserves/supply, onset/continuation, new constitutive and harmonic checkpoints | Integration of these optional reductions into the declared assembly and viewer, real material/joint laws and calibration; static constitutive potential is not yet the dynamics' restoring law |
| [123: patterned boundary flux](https://github.com/QuantumInquisitor/universal-matrix/pull/123) | Six spatial face arrays, Gauss compatibility, independent dense-graph controls and corrected invalid-input handling | Moving boundaries, material constitutive relation, spatial continuum convergence and geometric embedding |
| [124: combined aperture assembly](https://github.com/QuantumInquisitor/universal-matrix/pull/124) | Modified host apertures and replacement routing; full fixed inventory of 69 components/2,346 pairs/62 interfaces/eight ports; prescribed common scaling with transported flux; declared-state/winding recurrence and replay | Relative folding of that different graph, nonuniform compatible material maps, joint/contact physics, generalized branching and autonomous dynamics |

These are implemented bounded capabilities, not proof of a complete physical
engine. Published test counts above are inspected evidence unless a fresh local
run is separately identified. Passing CI is not material or scientific calibration.

## Publication versus current checkout

At the inspected heads, all listed workflows pass for PR119, 120, 121, 123 and
124. PR122 head `7dd38fb994fa09902ab68ce6a0e586906ae21e0f` has experimental,
container and CodeQL success; broad verification is still running at snapshot.
`draft-capability-audit.json` pins heads, URLs, file hashes and workflow results.

All 24 PR119 files, 17 PR120 files and eight PR121 files are absent from the
current tracked checkout: **49 published files are not integrated here**.
They are not lost or unimplemented. All seven PR123 and 28 PR124 files match
their published blob contents in this checkout. Local content presence does
not mean the drafts are merged into main.

PR122's initial comparison found five documentation differences. Inspection
identified UTF-8/Windows encoding drift, including corrupted mathematical
symbols, rather than missing experimental source. Publication now reads these
files explicitly as UTF-8; existing mathematical text is preserved, and fourteen
already-corrupted range dashes in the older plan were repaired. The raw audit
retains the pre-correction comparison rather than rewriting history.

## Lynchpin fills a real interface gap

The local `lynchpin_geometry_audit.py` already owns panel/hinge incidence and
symmetry; `recursive_omniverse_contract.py` owns dimensionless address/mirror
semantics. Fresh validation of those local modules passed 28 tests. Address
recursion is not physical recursive coupling, and PR119's four-dimensional
mirror isometry does not add dynamics in dimensions 5-13.

The separately published PR119 modules provide reusable interfaces:

- `lynchpin_relative_motion_control`: constraint Jacobian, rigidity report and
  compliant rays. A fixed-angle common-origin construction is rigid; compliance
  is an explicit model choice, not a recovered freely moving rigid hinge.
- `lynchpin_finite_panel_control`: actual panel vertices and principal
  stretches/area ratios. Surface measurements do not specify stress or bending.
- `lynchpin_connected_control`: stable body IDs, complete coefficient geometry,
  radii, localized attachment checks and scene export. Geometric contact regions
  do not supply a contact-force law.
- `report_lynchpin_connected.py`: 202-frame geometry output already exists.
  Reuse its identity/geometry contract rather than invent another disconnected
  visual model. Rendering and headset validation are still separate work.

The important reference mismatch is now resolved: older stretch measurements
use theta=0, while the new elastic law declares its rest at theta=pi/12. Taking
old stretch values directly as material strains would be incorrect.

The new `export_lynchpin_material_scene.py` joins the nine independently saved
original-source fixture frames to the material law by stable body ID. It takes
the phase-0.25 source geometry at scale 1.1, removes that scale and uses the
result as the material reference. Independent least-squares affine fits of the
original panel vertices give principal stretches; their singular values agree
with the new Green-strain values within 8.89e-16 across 54 comparisons. Using
the old theta=0 reference instead gives a discrepancy of 0.17537 in the control.

All 198 body vertex sets agree within 2.78e-17 m. Eighteen reduced elastic owners
sum exactly to total potential; four hubs retain explicit null/unmodeled energy
and force values. Original offset radii stay envelope metadata, not material
thickness. Fourteen new overlay tests pass. This is a verified geometry/material
data interface, not a new motion simulation, replacement of the 202-frame
exporter, or completed viewer integration.

```sh
uv run python scripts/export_lynchpin_material_scene.py --output artifacts/lynchpin-material/scene.json
uv run python -m pytest tests/test_lynchpin_material_scene.py
```

## Corrections to the remaining queue

P04 should reuse the existing fixed 69-component inventory and common-scaling
proof. Its missing piece is a compatible relative-fold/material correspondence,
not another count of retained pairs. The 22-body lynchpin specimen and 69-domain
flow assembly must not be equated merely because both have a breathing adapter.

P05 should expand the controller's known failures instead of asking to add
saturation/delay/mismatch from scratch. The previous measurement disturbance
is deterministic; a stochastic noise ensemble is still open. The two-mode
model did not establish seed-independent orientation selection.

P06 already has size, selected error, longer-duration and resource comparisons.
At the reported 0.97 pulse setting, the interacting candidate delivered in
16/16 seed/size cases and the interaction-off control in 0/16, while the ordinary
divider passed 128/128 cases. The endpoint-readout protocol counts 65,792
preparations and 8,421,376 Floquet periods per described experiment. This is
not a measured power cost or demonstrated timing advantage. Retain the candidate
as optional; specify a justified use and fair cost comparison before expanding it.

P10/P11 can reuse persistent identities, exact winding serialization, recurrence
controls and the existing geometry exports. They still need independent physical
component states, declared coupling, transport/energy interfaces and actual
viewer integration. Stable breathing does not gate this work.

Next integration order: review and stage the published geometry interfaces;
use the reference-correct overlay; integrate the new potential with inertia and
energy controls; connect the same state/IDs to the viewer. Keep wave and optional
timing decisions in independent queues. Draft merging remains a separate review
decision, and this audit does not authorize or perform it.
