# Remaining work — reconciled 2026-10-02

The master register retains **41 IDs**: 12 main workstreams, 24 research/source scope-review entries and five recovery records. These are not 41 active or wholly unimplemented experiments. Original scopes, dependencies and statuses are preserved; completed bounded milestones and current next actions are added separately.

## Verified changes since the older list

- Powered material reserves/supply, bounded restart and computed-state export are already implemented on the recovery branch. Do not repeat them as missing work.
- PR #122's exact-head broad verification is successful, replacing the older pending entry.
- PR #143 (local numerical contact) and #144 (phase/current contracts) are green but unmerged.
- PR #129 is still open with failed CI. Its overlap with merged #130 requires review, not an assumed closure or an automatic rerun.
- PRs #119-124 remain open. Merged recursive work is in the recovery branch, not main.

The timestamped [PR/CI evidence](register-reconciliation-2026-10-02.json) covers #119-144 and first-page PR workflow listings for nine open heads. It is not an exhaustive branch census or proof of merge readiness. The [master register](tasks.json) preserves earlier result text in labeled historical snapshots.

## Working order

1. Review/disposition green #143 and #144 and unresolved #129; do not infer merge authorization from green CI.
2. P04/P07: specify missing physical interfaces and the 22-body/69-domain mapping.
3. P08/P10: maintain owned-energy controls and scope unresolved state/depth/attachment requirements.
4. P11: connect the existing computed-state export directly to the viewer with explicit local frames.
5. P05/P06/P12: continue bounded independent experiments/source triage without a breathing gate.
6. P09: retest emergent motion after relevant model changes.

## Main workstreams

| ID | Workstream | Next action | Remaining limit |
|---|---|---|---|
| P01 | Recover surviving work from disk and Git before finalizing the task register. | Finish the unresolved source/test branch comparisons using exception-file-comparison.json; give each unique item an explicit retained, superseded or unresolved disposition. | No new global census performed; remaining historical differences need file-level evidence. |
| P02 | Finish review and integration disposition of the published drafts. | Review and disposition open drafts #119-124, #143 and #144; check #129 against merged #130 before deciding whether it is superseded. Confirm compatibility and merge authorization separately. | Green listed CI is not completed scientific review, combined compatibility, or merge authorization. |
| P03 | Promote the remaining validated local candidates in small groups. | Select the next preserved Tesla/resonator or helix-clock candidate for source/provenance review; retain the published aperture work without repeating it. | Candidate-specific geometry, parameters and source evidence must be identified before promotion. |
| P04 | Close the whole-assembly geometry and motion questions. | Specify the missing material-point/deformation correspondence between the 22-body specimen and 69-domain flow assembly; separate that from physical joint and finite-thickness work. | No validated relative-fold map between these assemblies; source-midsurface clearance does not supply thickness or joint geometry. |
| P05 | Finish the wave and control experiments already started. | Reconcile W2 artifact provenance, then define one bounded stochastic-noise/actuator-bandwidth or wavelength/mode comparison with controls and acceptance criteria. | W2 legacy artifact lacks source hashes; broader convergence and Q-ball period protocol remain unresolved. |
| P06 | Decide whether crystal components provide a useful engine capability. | Define a timing-component use case and matched ordinary-divider comparison including load, latency, readout and energy; retain the existing 168-run evidence. | No established practical advantage or matched hardware cost/calibration. Spatial crystal tests require explicit coordinates. |
| P07 | Define material forces for one explicit connected specimen. | Choose and specify one missing joint/bending/contact or distributed-inertia law with explicit geometry and synthetic-versus-measured parameters before adding it. | Physical joint/attachment geometry and measured calibration are absent; four hubs lack constitutive energy. |
| P08 | Close the energy budget across the coupled specimen. | Retain validated powered-material/reserve/restart ledgers; extend independent work/energy/loss controls whenever a new joint, contact, electrical or flow coupling is introduced. | New physical interfaces and supply calibration are unspecified; no electromechanical or whole-flow energy closure claimed. |
| P09 | Test whether breathing and folding emerge from the equations. | Rerun the existing emergent-motion controls after a relevant material/joint/supply change; define stability and perturbation criteria before longer runs. | No sustained stable cycle established; do not tune a prescribed outcome or make breathing a global gate. |
| P10 | Extend to recursive coupling and persistent state. | Review the green local contact solve in #143 and contract audit in #144; then scope broader state/depth coverage and physical connector realization without changing settled laws by default. | Global continuous clearance, arbitrary-depth convergence, dormant-path rules and a physical attachment/phase-current adapter remain unvalidated. |
| P11 | Use the viewer to inspect the same computed engine state. | Connect the existing computed-state export to the science viewer with local-frame replay, units, provenance and energy ledgers; label any placement display separately. | No literal physical attachment frame; full image correspondence and visible desktop/headset verification still required. |
| P12 | Close the remaining independent experiment and source queues. | Triage R01-R24 one bounded item at a time into executable, evidence-blocked or explicitly deferred work; preserve each item's existing completion criterion. | Source/input gaps vary by item; queued suggestions are not 24 active experiments. |

## Detailed independent queue — scope review, not newly launched experiments

| ID | Topic | Next scope-review action | Missing evidence or limit |
|---|---|---|---|


## Recovery records

- **REC-NEUMANN — validated_published_draft_review_pending:** Review #123's supported numerical scope and compatibility for integration; retain passing controls.
- **REC-OLD-KERNEL — closed_superseded:** Keep the closed/superseded disposition; do not restore the old polarity-gradient channel without new justification.
- **REC-BRANCH-DIFFS — in_progress:** Finish unresolved source/test and historical documentation comparisons after the recorded E8 and bend-spacing dispositions.
- **REC-APERTURE — validated_published_draft_review_pending:** Review #124 integration; advance only the missing relative-fold/material correspondence rather than repeat its static/common-scaling inventory.
- **REC-IMAGES-8 — reviewed_controls_passed_published_draft:** Retain the reviewed image controls; pursue only source-backed material/flow correspondence or timing follow-ons.

## Completed bounded milestones to reuse

- **powered-material (implemented_on_recovery_branch):** Sized reserves, external input and owned energy on the material graph. Evidence: docs/fold_material_supply.md
- **restart (bounded_validation_on_recovery_branch):** 48-component 0.4+0.4 s versus 0.8 s powered/source-off restart. Evidence: docs/fold_material_persistence.md
- **viewer-export (implemented_on_recovery_branch):** Computed-state metre geometry and local-frame viewer contract. Evidence: scripts/export_fold_material_viewer_frames.py
- **recursive (merged_into_recovery_not_main):** Depth/impedance/pair/replay/phase/placement and attachment audits. Evidence: https://github.com/QuantumInquisitor/universal-matrix/pull/130
- **dense-clearance (merged_into_recovery_not_main):** Dense finite-grid zero-thickness contact family. Evidence: https://github.com/QuantumInquisitor/universal-matrix/pull/142
- **continuous-contact (green_unmerged):** Local numerical contact and broad-grid control; not global certification. Evidence: https://github.com/QuantumInquisitor/universal-matrix/pull/143
- **phase-current-contract (green_unmerged):** Conservation/gauge contract audit; no physical adapter. Evidence: https://github.com/QuantumInquisitor/universal-matrix/pull/144

No scientific workstream was declared complete by this documentation update. No equations, tests, geometry, tolerance, workflow or source artifacts were changed.
