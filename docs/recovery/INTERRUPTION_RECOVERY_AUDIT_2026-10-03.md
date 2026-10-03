# Interrupted-work and publication audit

This is a bounded evidence snapshot, not a live CI certificate or a claim that
all historical work is complete. The comparison baseline is accepted recovery
`dd468ba6926a4b96b70417fd18c089ee5c5a3f03`; PR166 was separately published at
`4572d197a53af38ecbcd316a31bb91bd3cd702f2` during the census and subsequently
passed all three workflows and merged as `57f812f0122aea43b085204777950010fd6c8c87`.
Always verify the current accepted head before continuing integration.

## What the audit established

The current shared repository census covered 39 local branches and 37 registered
worktrees, including the active audit worktree. The older repository had 16
branches and one clean worktree. Neither repository had a stash. The sole
current reflog-only commit, `173743d22cf2c48376a3f52745c7ce69d0e8443b`, is replaced
by accepted `e26caea3d131d8b78e08b18a21edf5ff06e50cb1`: scientific files match;
only six text-encoding corrections distinguish the trees. Historical integration
branches mostly preserve identical source blobs or patch-equivalent work.
Different commit IDs alone do not establish missing changes.
The older fixed-interface commit `d3068d0` has 7/7 changed-path blobs identical
to published `14d0f5e` (PR106); downstream-bore `8398671` has 8/8 identical to
`dc96dbc` (PR115). Both published successors are ancestors of main `a78576f`.
Those apparent patch-ID differences contain no unique unpublished delta.

An earlier local census incorrectly summarized every checkout as having no
tracked modifications. The original checkout's status call had failed ownership
validation. A fresh command-local safe-directory check found one modified
workflow and five untracked powered-supply files. The files were preserved;
no global Git configuration, reset or cleanup was used. An unsuccessful status
call must be reported as unknown, never converted into a clean result.

The audit checked linked reports, numerical artifacts and test logs. Concrete
later repository evidence resolves the old interrupted supply/publication
uncertainty; it does not certify every surviving scratch file as equivalent.
Raw session-log traversal was unnecessary for those outcomes. Never-reflogged
unreachable objects, every ignored file and unrelated home directories were not
scanned. The older 607-file census remains an inventory, not 607 validated or
published experiments.

## Preserved work and its disposition

| Family | Evidence and disposition |
|---|---|
| Geometry, waves, timing and boundary publication | PR119Ã¢â‚¬â€œ124 implementations are represented in accepted recovery. Old reports saying unpublished or unmerged are historical snapshots. Preserve them; do not redo their implementations. |
| Powered-material implementation | Accepted source, tests, documentation and workflow evidence exist. The original checkout also retains a different scratch package; its homothetic/empty/gain-zero trajectory controls, finite-difference ledger checks and scaled-state tests are unpromoted validation candidates. Its RK4 integrator and strict stage capacity rejection differ from accepted adaptive RK45 behavior. Review additive controls separately; do not replace the accepted implementation or copy those solver semantics silently. |
| LC and paired helix | Promoted through PR153/160. Original scratch remains provenance; physical coupling and time/geometry calibration remain open. |
| Shell probe | Saved source/report is explicitly a synthetic analytic family, with no observational fit. Retain under R01/R02; no astrophysical fit or formation/stability claim follows. |
| Egg-of-Columbus phase probe | Saved assertions cover normalized phase synthesis and rotation/slip kinematics. Retain under R03/R04; induced-current, torque, heating, contact and rising-egg dynamics remain absent from this evidence. |
| Quantum-mode-named scratch | Its JSON describes classical degenerate-mode controls. Do not relabel it as a completed quantum bath or repeat the already promoted W2 controls. |
| Standalone viewer and tetrahedral reconstruction | Historical log records 138 passing tests. A separate audit maps 20 source-text associations to accepted code; two tetra64 snapshots remain distinct in the inspected source search. This is neither current headset validation nor image correspondence. Select a specific adapter or presentation feature before promotion. |
| Combined review history | Two additional P02/P03 historical snapshots survive only in the local combined branch. They are preserved documentation history, not missing scientific behavior. Do not merge the combined branch wholesale. |
| PR166 numerical result | Full verification37081984192, focused37081984336 and contract37081984188 passed. Downloaded artifact11258463073 passes the original checks and all 13 source hashes match. No broad depth convergence, physical connector or stable-breathing claim is made. |

Ten older candidate/evidence files and six original-checkout supply paths have hashes in
[the candidate manifest](PRESERVED_CANDIDATE_EVIDENCE_2026-10-03.json). Raw local
files are not uploaded by that manifest. Local workspace aliases identify
provenance families, not repository-relative source locations.

## Next disposition for the powered-supply candidate

All 15 source hashes in the saved scratch summary match its preserved files;
13 shared dependency texts match accepted recovery. This links the saved result
to source, but does not certify a fresh run. The scratch's RK4 trajectory suite,
strict stage upper-capacity rejection and output schema differ from accepted
adaptive RK45 and its viewer/restart interfaces.

The smallest follow-up is an additive test-only proposal against accepted
`report_fold_material_supply`: constitutive passive reduction at zero gain or
empty reserve; independent finite-difference node/edge/group energy derivatives
with external input; and full derivative homothety at scale 0.5, including reserve
and input ledgers. Existing tests on separate predecessor models do not prove
all combined-model assertions. Preserve the accepted solver, schema and criteria.
Do not import strict capacity rejection or the old workflow as incidental fixes.
Longer RK4/refinement and full-state trajectory comparisons remain separate
review candidates. Nothing here demonstrates failure of the accepted equations.

## Preventing another stale restart

The active `execution_policy.immediate_actions` field retained an old recovery
hash and incorrectly implied the mechanical-energy display was missing. This
change preserves the old array verbatim and replaces only those two active
entries. All 41 task records, completion criteria, statuses and dependencies
remain unchanged. Dated history is evidence; current active instructions must
not direct a continuation to redo accepted work.

Future closure reviews must retain the original P11 object-to-test links,
projection/uncertainty displays, navigation, performance and interaction clauses;
P05 wavelength/mode/phase/boundary ensembles; and P06 actual-coordinate spatial
order and matched readout/energy costs. These obligations already exist in the
full register even when a short status summary omits them. Distributed replay
and persistence need explicit inertia-model, state and ledger identities before
using point-model checkpoints.

## Evidence retention and remaining inputs

[The retention manifest](RECOVERY_EVIDENCE_RETENTION_2026-10-03.json) records two
downloaded CI artifacts, local hashes, original ZIP-member hashes, reproduction
commands and actual hosted expiry metadata. The Q-ball artifact expires on
2026-12-31 UTC; the graph trajectory artifact on 2027-01-01 UTC. Verified original
ZIPs are retained locally. The graph JSON working copy was reserialized and is
parsed-equivalent, not byte-identical to its original ZIP member. A manifest is
not a backup: an independent durable archive of raw evidence remains an explicit
preservation action before deleting local copies or relying on hosted retention.

Missing original course images/editions, apparatus measurements, the unresolved
Watts reading, sensor/material calibration, image landmarks/camera/depth
assumptions and physical-headset observations remain evidence gaps. Saved success
flags do not close them. Original supplied images remain locally preserved;
this audit does not broaden their publication scope.
