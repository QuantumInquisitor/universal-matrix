# Historical file reconciliation — bounded continuation

This refresh compares the 84 branch/file records in the existing 14-branch
exception inventory with tracked recovery commit
`05d12c31ebe41a4749318058e6faa4f710cc9c8c`. It is not a new census of all
repositories, branches, scratch files or unpublished candidates.

The [machine-readable evidence](historical-file-reconciliation-2026-10-02.json)
preserves each archived blob, current blob and disposition:

| Disposition | Records |
|---|---:|
| Exact blob match, preserved | 38 |
| Reviewed later extension | 1 |
| Absent in agreement with documented superseded kernel | 3 |
| Math delimiters only, exact normalized text match | 11 |
| Later documentation updates reviewed | 3 |
| Test revisions reviewed | 3 |
| Preserved in published PR #123, not integrated | 2 |
| Workflow evolution reviewed | 6 |
| Markup regressions repaired from archived evidence | 5 |
| Original design-question content retained | 6 |
| Status-index evolution reviewed | 2 |
| Content-clock clarification reviewed | 1 |
| Architecture reorganization reviewed | 1 |
| Superseded local-law documentation reviewed | 2 |
| Still requires semantic review in this inventory | 0 |

These are branch/file records, not unique files or experiments. The first
snapshot left 42 unresolved records and 15 unavailable archived blobs. The
checkout's configured fetch covered only main. An explicit historical-branch
fetch recovered all 15 objects; none in this inventory is now unavailable.
Previous availability and counts remain in the JSON as history.

Eleven documents match exactly after converting only LaTeX math delimiters
to dollar delimiters. Three small documentation differences record later
spacing/clearance progress. The amplitude test fixes broadcast-mask shape;
the radial tests share a six-point fixture and remove an invalid strict zip.
The radial virial path changes from four to six continuation points, so it is
not trajectory-identical. Governance tests follow the reorganized section
numbering with added authority checks, not identical named-heading coverage.
All 27 current amplitude, radial and governance tests pass. No scientific
source or acceptance threshold was changed in this audit.

Six workflow comparisons retain historical explicit test/report targets except
the documented superseded local-kernel test. The current workflow adds
changed-file numerical gating, pins Python environments and separates long
Q-ball work; the full suite remains unconditional. Changed scheduling is not
claimed to be identical execution coverage.

Five older notes had doubled delimiters and missing backslashes in math
commands. Their text is otherwise identical to the archived blobs when
backslashes are removed. The repair restores only the archived backslashes
and converts math delimiters to dollar syntax. Other pre-existing malformed
notation is not reconstructed. Twelve documentation-governance tests pass.

Nine further records now have documentation dispositions. Six design-question
versions preserve the complete original question section exactly after math
delimiter conversion. Later replacements change the progress date, nested-scale
status and two code references; the scale row distinguishes a chosen planar
ratio from unresolved physical scale and boundary coupling. Two status-index
versions retain prior nonempty lines, except the already superseded old-kernel
entry. Later progress additions are historical reports retained here, not
independently revalidated scientific conclusions.

The content-clock revision preserves the exponential lapse, inverse rate and
speed, fixed phase increment and explicit link-per-tick hypothesis. Its added
first-order lapse expansion agrees with the current source. The evidence
boundary makes unresolved physical parameters and gravity claims explicit.
The final architecture review identifies section renumbering, corrected
cross-references, removal of duplicate Huet references retained elsewhere, and
later sampled-clearance documentation. The other architecture version and
design checkpoint omit the intentionally superseded two-channel pair-rotation
law, consistent with REC-OLD-KERNEL and the recorded PR #7 closure. The current
phase/momentum rotor Hamiltonian is a different model; this audit does not
establish replacement equivalence. Archived blobs remain the provenance record.

The reviewed bend-spacing source retains the original scan and adds sampling
metadata and phase offsets. Its updated wording correctly limits
`collision_free` to no detected collision on a finite grid. The three absent
old-kernel paths agree with REC-OLD-KERNEL's existing closed/superseded
disposition; this audit does not re-prove replacement equivalence.

## Published capability versus tracked integration

PR #123 remains open at `b7add2892868d5e8150c3a4b148b3c3200642d57`.
The tracked recovery head does not contain its optional six-face-array solver
or its additional patterned-flux tests. Earlier statements that all seven
files matched a local checkout describe local presence, not incorporation into
this branch. Preserve the published implementation; do not recreate it.

A separate local compatibility checkout merged #148 and #149 without
conflicts and passed 47 mechanics tests plus 11 viewer tests. Adding the
unchanged #123 head to that checkout also merged cleanly; the boundary solver,
independent manufactured checks, property invariants and documentation controls
passed 41 tests. This is local combined compatibility evidence, not merge into
recovery or main, and not physical boundary calibration.

The original recovery full-suite run exhausted its 40-minute budget at 28%.
PR #151 now tests eight file partitions with a complete-execution aggregate.
Run 37056625500 has seven partitions passed and one still running at this review;
full compatibility is pending. No server-side branch was merged during this audit.

## Next actions

1. Continue the broader location and work-family census. All 84 records in
   this bounded inventory now have dispositions; that does not close P01.
2. Complete review and integration disposition of #123 using its preserved
   implementation and the fresh compatibility evidence.
3. Integrate reviewed #148/#149 after the ongoing recovery verification has
   finished, without repeatedly cancelling the long legacy suite.
4. Continue the wider P01 census and P03 candidate provenance work. This audit
   does not close either workstream or remove any of the 24 research entries.
