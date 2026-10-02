# Recovery checkpoint — recursive spatial, phase, and attachment work

Date: 2026-10-02

This file is a durable recovery point for the Matrix Engine / Universal Matrix work. Resume from the live repository state recorded here rather than from older timeout traces.

## Live reconciliation state

- Recovery PR: #122
- Recovery branch: `codex/recovery-plan-log`
- Recovery head when this checkpoint was written: `972600dfc33b0d85154065b7ec2596ac474e643f`
- PR #122 remains open and draft against `main`.

## Completed and merged recursive checkpoints

The following scientific checkpoints are merged into the recovery branch:

- PR #130 — isolated recursive pairs versus embedded cascade dynamics
- PR #131 — drive-history versus downstream-loading replay
- PR #132 — upstream parent-drive attenuation audit
- PR #133 — binary material recursion versus Seed/Vesica geometry
- PR #134 — explicit 22-body recursive material placement
- PR #135 — energy-derived recursive spatial connector frames
- PR #136 — fixed connector port-to-body correspondence search
- PR #137 — recursive modal phase and mechanical power-flow audit

Important merged conclusions:

1. The local 1:2 recursive interface is statically and dynamically self-similar across the tested scales.
2. Strong depth attenuation appears when interfaces are embedded in the cascade, and causal replay localizes that suppression primarily to upstream parent trajectory/history rather than downstream loading.
3. The binary material cadence 1, 1/2, 1/4, 1/8 matches the alternating contained-vessel / Seed-circle cadence through depth 3, but the binary tree is not the full 12-address Vesica recursion.
4. Three opposite-Seed-axis binary slices are symmetry-equivalent. No canonical axis is selected.
5. The 22-body module fits a local recursive vessel at a common radius/module-length ratio of about 2.19 for local containment and conservative sibling separation.
6. A real spatial connector needs a geometric rest offset and a mirrored-branch attachment-frame treatment.
7. The parent-aligned spatial attachment frame reproduces the validated local connector essentially to numerical roundoff. The body-following mirrored frame changes the dynamics substantially and is therefore not silently substituted.
8. The abstract two-component connector port can be reproduced algebraically from many body markers using fixed anisotropic linear maps, but no searched single marker is a literal scaled-orthogonal projection of the port.
9. Modal phase-space instrumentation is useful: parent-child phase lag strongly correlates with signed connector power and connector storage in the recursive material model. This is mechanical power flow, not electrical current.

## Circle / phase / current checkpoint

The circle-to-wave idea has been incorporated only as a measurable state-space diagnostic.

For one linearized material mode:

`x = v^T(q-Q0)`

`y = -v^T(qdot)/omega`

`z = x + i y = A exp(i phi)`

so the modal state is represented as rotation in a phase plane and x/y are cosine/sine projections.

Merged PR #137 measured phase lag against signed connector power.

Representative correlations for sin(child-parent phase lag) versus child connector power:

- mode 0: level 1 = +0.9998, level 2 = -0.9503, level 3 = +0.7088
- mode 1: level 1 = -0.8538, level 2 = -0.9959, level 3 = +0.7017

The sign is mode/depth dependent, so no universal `J ∝ sin(Δphi)` law is claimed for the mechanical recursion.

A separate experimental U(1) gauge-matter sector already exists in the repository and contains an actual conserved phase-dependent current of the form

`J = kappa sqrt(A_x A_y) sigma_x sigma_y sin(phi_y - phi_x + theta_link)`.

That sector remains physically distinct from the mechanical recursive connector. A future bridge must be tested as an adapter hypothesis without fitting sign flips or arbitrary phase offsets. No plasma claim follows from wave similarity alone.

## Current open spatial gate

PR #138 — “Search relative-marker recursive attachment frames”

- Branch: `codex/recursive-relative-attachment-frame`
- Current head: `adf579862870378fa14272d2e8ec29507f51e232`
- State at checkpoint: open, draft
- Focused workflow: green
- Candidate marker count: 58
- Unordered relative-marker segment count: 1,653
- Fixed-linear matches: 980
- Scaled-orthogonal matches: 0
- Unit-orthogonal matches: 0
- Same-body scaled-orthogonal matches: 0

Best reported candidate:

`panel-0:vertex-0 -> bridge-5-3:vertex-1`

with approximately:

- displacement error = 1.56e-11
- Jacobian error = 1.05e-10
- condition number = 2.81
- uniform projection scale = 1.63
- scaled-orthogonal relative error = 0.775

Interpretation:

The current 22-body source geometry contains many fixed anisotropic reduced-coordinate readouts of the abstract port, but no searched single point or real marker-to-marker segment is a literal rigid/scaled-orthogonal connector frame. Do not invent or select a physical attachment point from least-squares fit alone.

## Exact next steps

1. Preserve PR #138's green result and merge it only after its result is documented on the PR.
2. Keep the abstract connector port explicitly reduced unless a separately justified physical attachment geometry is introduced.
3. Continue the spatial lane with exact body proximity/collision auditing over the recursive placement and bounded fold-state grid. Do not use cross-generation bounding spheres as an exact collision certificate.
4. In parallel, design a zero-fit comparison between the merged mechanical modal phase diagnostic and the existing gauge-invariant U(1) phase-current sector. The two sectors must remain physically distinct unless an explicit adapter passes conservation, gauge-invariance, and dimensional checks.
5. Do not label the mechanical phase/power result as plasma. A plasma extension would require explicit charged-particle or charged-fluid variables and electromagnetic field dynamics, then a comparison to observables such as plasma frequency, dispersion and collective modes.
6. Keep the computed-state viewer lane separate until the spatial placement/attachment contract is sufficiently explicit. Do not invent global geometry to make the viewer look complete.

## Do not regress to older recovery points

Do not restart from PR #88, #92, #96, #97, the old `e311df0` main head, or the early depth-3 experiments.

The current scientific lane is post-PR #137 with PR #138 as the active unmerged spatial gate.
