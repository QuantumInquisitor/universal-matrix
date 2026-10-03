# Remaining work — reconciled 2026-10-02

The master register retains **41 IDs**: 12 main workstreams, 24 research/source scope-review entries and five recovery records. These are not 41 active or wholly unimplemented experiments. Original scopes and dependencies are preserved; current statuses reflect bounded progress without closing whole workstreams.

## Accepted integration checkpoint through PR163

This dated checkpoint records recovery `58042ea16dff339008a4b0fd177409c2e16f202e`.
PR153-163, 117 and 118 are integrated in addition to the earlier recovered
experiments. PR161's source audits, PR162's instantaneous distributed-inertia
graph contract and PR163's combined delay/actuator comparison passed their
reviewed-head full verification; the two code additions also passed focused checks. The local combined review passed 89
controller, inertia, baseline and documentation checks.

The LC reference, mechanical-energy viewer, conditional timing delivery,
paired-helix adapter and Q-ball scalar export are implemented. Their stated
physical and numerical limits remain in force. The Q-ball artifact contains 101
samples per channel with all 288 source hashes verified; no stable period is
established. The graph adapter adds no recursive trajectory or depth-convergence
claim, and the combined controller does not establish hardware limits.

Current recovery integration CI is a separate gate; PR122 remains draft against
main. PR164's documentation-only chiral audit is separately reviewed and awaits
its own CI and integration. All 41 original task contracts remain intact.
Completing every physical or research workstream is not a prerequisite for
bounded experimental integration. This checkpoint is historical evidence of the
listed accepted batch; live PR/CI state must be verified before further merges.

## Actuator comparison scope

The additive actuator-bandwidth report preserves the original controller and
tracking criterion. At the sampled synthetic response times, 0.1 s meets the
0.05 m RMS target while 0.5 s and 2 s do not; refinement preserves these outcomes.
See [the scope and controls](../actuator_bandwidth.md). This does not close P05,
calibrate hardware, or establish a continuous stability boundary.

## Earlier checkpoint after published-draft integration (superseded)

PRs #119, #120, #121, #123, #124 and #152 are merged into recovery at
`851693c40bb59a67c03bce4bad5411df6ca980ca`. Each candidate passed its full CI;
combined local controls passed 109 geometry/boundary and 105 wave/timing tests.
Final integrated verification run 37067766522 remains a separate gate. PR #122
is still open against main. The original 41 IDs and 24 research items remain.

The LC input fixes reproduced the preserved valid report and passed 97 local
regression checks. The optional repository reference is now being prepared;
physical calibration, piezoelectric coupling and whole-system energy closure
remain open. The next actions below supersede the older dated snapshots.

## Earlier integrated checkpoint and parallel work (superseded)

Recovery head `78e413f84debd1eadd78b6409bd73932aa5a65bc` has all 22 reported
workflows passed. The full-suite aggregate verified 3,044 collected tests.
PRs #148-151 are merged into recovery; PR #122 remains open against main.
All 84 records in the bounded historical inventory have dispositions; the
broader census remains open. Desktop replay is implemented and checked;
physical-headset, image, attachment-frame and full mechanical-energy work remain.

PR #123 is separately undergoing full CI at `9f98b02`; 41 focused checks pass.
PRs #119/#120/#121/#124 remain published drafts with individually green CI.
Their 77 added files are absent from tracked recovery at this head; historical
local-checkout presence is not integration evidence. Independent staging of
#119 and #124 is in progress. Keep final integration serial and verify the
combined result.

The preserved coupled-LC candidate passes its original controls when rerun,
but extra API probes expose invalid-input gaps. Harden it before promotion;
no physical calibration or whole-system electrical closure is claimed.
The current next actions below supersede earlier dated snapshots.

## Distributed trajectory continuation

The isolated 0.4 s trajectory/energy experiment passes 47 combined local tests. See [the report and limits](../fold_distributed_trajectories.md). Existing production dynamics and all workstream completion criteria remain unchanged. Remote CI is a separate gate.

## Earlier integration and inertia snapshot (superseded)

PRs #143, #144, #145 and #146 are merged into recovery, not main. Recovery head after these merges is `585593e0f69d6ad07d0e7bce1ad08c532b2809bd`. PR #129 is closed as superseded after review; its archived head and replacement energy/loss comparisons are preserved in [the disposition evidence](pr129-disposition.json). No geometry, collision tolerance or governing-contact solver criteria changed.

Distributed panel/bridge inertia advances P07: 22 owners, 82 quadrature points and the same 0.74 kg total. All 34 focused tests and [CI](https://github.com/QuantumInquisitor/universal-matrix/actions/runs/37049094404) pass. Production trajectories, finite-thickness/hub inertia, joints and calibration remain open.

At the latest check, 17 of 19 listed workflows for the earlier combined head `e39dcc9` passed; broad verification and experimental controls were still running. This is a dated snapshot, not a claim that all checks passed at the newer head.

Immediate order: finish remaining draft dispositions; advance direct computed-state viewer replay and scope recursive use of the validated single-specimen distributed inertia. Keep physical-input gaps and the independent research queue explicit. The original 41 IDs, completion criteria, dependencies and workstream statuses remain intact.

## Earlier reconciliation snapshot (superseded where noted below)

- Powered material reserves/supply, bounded restart and computed-state export are already implemented on the recovery branch. Do not repeat them as missing work.
- PR #122's exact-head broad verification is successful, replacing the older pending entry.
- PR #143 (local numerical contact) and #144 (phase/current contracts) are green but unmerged.
- PR #129 is still open with failed CI. Its overlap with merged #130 requires review, not an assumed closure or an automatic rerun.
- PRs #119-124 remain open. Merged recursive work is in the recovery branch, not main.

The timestamped [PR/CI evidence](register-reconciliation-2026-10-02.json) covers #119-144 and first-page PR workflow listings for nine open heads. It is not an exhaustive branch census or proof of merge readiness. The [master register](tasks.json) preserves earlier result text in labeled historical snapshots.

## Earlier working order (superseded by current checkpoint)

1. Review/disposition green #143 and #144 and unresolved #129; do not infer merge authorization from green CI.
2. P04/P07: specify missing physical interfaces and the 22-body/69-domain mapping.
3. P08/P10: maintain owned-energy controls and scope unresolved state/depth/attachment requirements.
4. P11: connect the existing computed-state export directly to the viewer with explicit local frames.
5. P05/P06/P12: continue bounded independent experiments/source triage without a breathing gate.
6. P09: retest emergent motion after relevant model changes.

## Main workstreams

| ID | Workstream | Next action | Remaining limit |
|---|---|---|---|
| P01 | Recover surviving work from disk and Git before finalizing the task register. | Continue the broader location/work-family census and published-draft integration; use the completed 84-record inventory as evidence rather than repeating its reviewed comparisons. | The bounded 84-record inventory is dispositioned; broader location/work-family census and candidate provenance remain incomplete. |
| P02 | Finish review and integration disposition of the published drafts. | Assess current recovery CI and pending documentation audits, then complete the bounded recovery-to-main integration review. Preserve the wider physical and research queue without reopening accepted implementations. | Green listed CI is not completed scientific review, combined compatibility, or merge authorization. |
| P03 | Promote the remaining validated local candidates in small groups. | Select the next preserved candidate by source, inputs and independent controls. Do not repeat completed LC or paired-helix promotion; physical calibration and coupling remain separate. | Candidate-specific geometry, parameters and source evidence must be identified before promotion. |
| P04 | Close the whole-assembly geometry and motion questions. | Specify the missing material-point/deformation correspondence between the 22-body specimen and 69-domain flow assembly; separate that from physical joint and finite-thickness work. | No validated relative-fold map between these assemblies; source-midsurface clearance does not supply thickness or joint geometry. |
| P05 | Finish the wave and control experiments already started. | Specify the next separately bounded stochastic-noise or broader-limit study with independent controls. Preserve integrated combined delay/lag results; hardware calibration, wider convergence and Q-ball period requirements remain open. | W2 manifest links original data/source hashes and equal parsed content; chronology remains unauthenticated. Broader convergence and Q-ball period protocol remain unresolved. |
| P06 | Decide whether crystal components provide a useful engine capability. | Review the conditional acquisition/delivery contract; supply an independently justified physical acquisition/readout backend, loading and energy costs before claiming timing usefulness. Preserve existing signal and scheduling evidence; spatial claims still require coordinates. | No practical advantage established. Acquisition assumptions are asymmetric and explicitly conditional; hardware readout/backaction, energy, loading and absolute time remain uncalibrated. |
| P07 | Define material forces for one explicit connected specimen. | Validate a separately bounded distributed-inertia graph trajectory comparison with matched initial conditions before expanding depth or duration. Physical joints, finite thickness, hub rotation and measured calibration remain open. | Physical joint/attachment geometry and measured calibration are absent; four hubs lack constitutive energy. |
| P08 | Close the energy budget across the coupled specimen. | Retain validated powered-material/reserve/restart ledgers; extend independent work/energy/loss controls whenever a new joint, contact, electrical or flow coupling is introduced. | New physical interfaces and supply calibration are unspecified; no electromechanical or whole-flow energy closure claimed. |
| P09 | Test whether breathing and folding emerge from the equations. | Rerun the existing emergent-motion controls after a relevant material/joint/supply change; define stability and perturbation criteria before longer runs. | No sustained stable cycle established; do not tune a prescribed outcome or make breathing a global gate. |
| P10 | Extend to recursive coupling and persistent state. | Assess bounded distributed graph trajectories and broader state/depth coverage under the preserved scale guards; keep physical connector realization, powered persistence adaptation and remaining pathway rules separate from the validated instantaneous contract. | Global continuous clearance, arbitrary-depth convergence, dormant-path rules and a physical attachment/phase-current adapter remain unvalidated. |
| P11 | Use the viewer to inspect the same computed engine state. | Resolve physical assembly attachment frames and image correspondence and validate on a physical headset. Retain the integrated mechanical-energy display, desktop replay and separate energy ownership. | Global physical attachment frames, image correspondence and physical headset validation remain open. The integrated mechanical-energy display uses the existing point-inertia model; it does not certify whole-assembly energy closure or distributed-inertia replay. |
| P12 | Close the remaining independent experiment and source queues. | Triage R01-R24 one bounded item at a time into executable, evidence-blocked or explicitly deferred work; preserve each item's existing completion criterion. | Source/input gaps vary by item; queued suggestions are not 24 active experiments. |

## Detailed independent queue — scope review, not newly launched experiments

| ID | Topic | Next scope-review action | Missing evidence or limit |
|---|---|---|---|
| R01 | A1 shell-model observations | Freeze an observational sample, nuisance treatment, baseline and held-out protocol before fitting the shell model. | Observational dataset/protocol and covariance/selection treatment not frozen. |
| R02 | A2 shell realizability | Specify a collisionless realizability/stability experiment with declared initial and boundary conditions. | Formation and relativistic-source assumptions remain separate and unspecified. |
| R03 | P1 and T1–T2 electromechanics | Inventory ring geometry, material tensors/poling, supports, electrodes and losses; specify one reciprocal electrical/piezoelectric coupling. | Physical component data and measured response required for calibration. |
| R04 | T3 wider Tesla mechanisms | Triage the proposed Tesla mechanisms and select or explicitly defer each before starting a bounded test. | Proposals lack selected scope/inputs; archive and patent access gaps remain. |
| R05 | W3 quantum mode pair | Specify bath/noise, observables and coupling for the quantum-mode comparison. | Open-system model and measurement protocol not specified. |
| R06 | H1–H2 helix geometry | Review the optional paired-helix adapter and preserved controls; specify independently justified thickness, pitch, junctions, flow coupling and physical time calibration before a physical geometry/flow implementation. | The adapter is synthetic kinematics only. Physical thickness, flow/junction coupling, dynamics and tick duration remain unspecified; neither handedness nor physical geometry follows from the clock alone. |
| R07 | R1 Russell corpus and apparatus | Collate remaining original chart/page images and edition witnesses; retain the completed WR008 reading and limited course recovery rather than repeating them as absent. Recover authenticated apparatus drawings, dimensions, wiring and measurements. | Only one saved chart was re-inspected. The five pending page images, original181/183, full edition/course collation and apparatus evidence remain open. |
| R08 | R2 Watts and spectral matching | Resolve the iron-table medium and original readings; compare modern line identities with uncertainty, retaining 7817.2 as unresolved. | Original-source/medium evidence and unmatched line identification remain missing. |
| R09 | F1 frequency and conventional controls | Resolve the 12 instrument settings where evidence permits and bound the next species/transition dataset. | Catalog labels are not resonance predictions; provenance/settings remain incomplete. |
| R10 | F2 alternative theories and M4 | Recover M4 authorship/equations and define an observable before choosing a simulation; keep other theory suggestions separately deferred. | Primary equations and testable quantities unavailable or unspecified. |
| R11 | Earlier geometry references | List remaining Rao/Sri Yantra constraints and seek an independent historical Meru metric. | Independent reference constraints/metric remain incomplete. |
| R12 | S1–S2 historical apparatus | Recover actual apparatus geometry, boundaries and measured inputs, including octave-direction discrepancy. | Apparatus source evidence missing; completed generic storage/acoustic modules are not reopened. |
| R13 | Primitive state and local dynamics | Audit which richer matter/gauge terms follow from the canonical kernel versus additional assumptions; select one locality/continuum check. | Derivation and physical locality/continuum limits remain open. |
| R14 | Physical normalization and clock mapping | Choose one justified subsystem pair and record independent length/time/energy/charge scales, source, uncertainty and validity range before cross-system conversion. Preserve synthetic, measured and unavailable statuses separately. | Dimensional consistency is not calibration. Missing base scales and absolute reference values prevent physical cross-system conversion; no physical constants are selected by this audit. |
| R15 | Boundary and six-gate coupling | Specify a boundary-to-core coupling and freeze one discriminating observable; preserve the bare-core clock no-go result. | Six-gate/sevenfold dynamical coupling lacks independent justification. |
| R16 | Matter and particle interpretation | Use the now-preserved direct/perturbed samples and provenance for further diagnostics; obtain additional repeated peak and radius extrema plus temporal/sampling/spatial convergence before assigning a period. Keep stability/excitation and particle identification separate from finite-time boundedness. | The preserved extrema do not establish a stable period. Complete sample export supports inspection but is not a restart checkpoint or complex-field phase measurement. Longer-window convergence, stability and independent particle identification remain open. |
| R17 | Charge, representations and couplings | Separate input charge/representation/coupling choices from derived results and select a bounded derivation target. | Charge quantization, spectrum and running are not derived. |
| R18 | Chiral consistency | [Source audit](CHIRAL_CONSISTENCY_AUDIT.md) completed with 49 focused tests; declare the measure convention and derive the gauge-response/density relation before a bounded comparison. Existing overlap, Stokes and supported SU(2) parity work is preserved. | Global patch/sector measure, non-Abelian measure and full anomaly consistency remain incomplete. |
| R19 | Quantum state and measurement | Specify a quantum state space, measurement/probability rule and falsifiable entanglement/Bell observables. | Existing classical/finite-operator controls do not supply the missing quantum theory. |
| R20 | Reciprocity and gravity | Audit matter/gauge coupling to evolving geometry; freeze one independent gravity comparison and its physical assumptions. | Canonical premises, dimensional coupling and observation/emission/boundary inputs remain unresolved. |
| R21 | Thermodynamics and cosmology | Separate thermodynamic coarse-graining/arrow-of-time and cosmological evolution questions; scope one derivation. | Declared laws and initial-condition derivation remain incomplete. |
| R22 | E8 physical extension | Keep extra radial dynamics deferred unless an independent requirement motivates them; retain exact E8 geometry/lift results. | No independent justification for a new radial degree of freedom. |
| R23 | Independent prediction | Select one independently fixed dimensionless prediction; freeze uncertainty and rejection criteria before comparison. | Prediction, fixed inputs and rejection protocol not selected. |
| R24 | Software and engineering backlog | Assess current recovery integration CI; retain completed dependency reviews and non-publishing Buildx execution evidence. Continue the separate audit of hardware adapters, packaging and documentation coverage against actual implementations. | Current recovery integration CI remains separate. Buildx smoke does not validate registry authentication/pushes, multi-platform output or published attestations. Hardware coverage and adapters still require independent evidence. |

## Recovery records

- **REC-NEUMANN — validated_merged_into_recovery:** Retain optional patterned-face capability and its finite-grid limits; address physical boundary coupling through P04/P08/R15 rather than recreating the solver.
- **REC-OLD-KERNEL — closed_superseded:** Keep the closed/superseded disposition; do not restore the old polarity-gradient channel without new justification.
- **REC-BRANCH-DIFFS — in_progress:** Continue the broader location/work-family census and published-draft integration; use the completed 84-record inventory as evidence rather than repeating its reviewed comparisons.
- **REC-APERTURE — validated_merged_into_recovery:** Develop the missing22-body/69-domain material correspondence and physical interface specification underP04; preserve the integrated aperture controls.
- **REC-IMAGES-8 — reviewed_controls_passed_merged_into_recovery:** Retain the reviewed image controls; pursue only source-backed material/flow correspondence or timing follow-ons.

## Completed bounded milestones to reuse

- **powered-material (implemented_on_recovery_branch):** Sized reserves, external input and owned energy on the material graph. Evidence: docs/fold_material_supply.md
- **restart (bounded_validation_on_recovery_branch):** 48-component 0.4+0.4 s versus 0.8 s powered/source-off restart. Evidence: docs/fold_material_persistence.md
- **viewer-export (implemented_on_recovery_branch):** Computed-state metre geometry and local-frame viewer contract. Evidence: scripts/export_fold_material_viewer_frames.py
- **recursive (merged_into_recovery_not_main):** Depth/impedance/pair/replay/phase/placement and attachment audits. Evidence: https://github.com/QuantumInquisitor/universal-matrix/pull/130
- **dense-clearance (merged_into_recovery_not_main):** Dense finite-grid zero-thickness contact family. Evidence: https://github.com/QuantumInquisitor/universal-matrix/pull/142
- **continuous-contact (green_unmerged):** Local numerical contact and broad-grid control; not global certification. Evidence: https://github.com/QuantumInquisitor/universal-matrix/pull/143
- **phase-current-contract (green_unmerged):** Conservation/gauge contract audit; no physical adapter. Evidence: https://github.com/QuantumInquisitor/universal-matrix/pull/144

No scientific workstream was declared complete by this documentation update. No equations, tests, geometry, tolerance, workflow or source artifacts were changed.
