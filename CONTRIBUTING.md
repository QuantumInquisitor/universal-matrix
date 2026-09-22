# Contributing to Universal Matrix

Thank you for contributing to Universal Matrix.

The repository contains canonical mathematics, research physics, numerical
software, robotics/XR productization, digital-twin tooling, manufacturing and
hardware adapters, APIs, deployment assets, and legacy compatibility code.
Contributions should preserve the distinctions between those layers.

## 1. Contributor License Agreement

External contributions require acceptance of `CLA.md` before merge unless
Waters Legacy Trust expressly waives that requirement in writing.

The repository does **not** currently claim to have an automated CLA bot.
Contributor acceptance must be recorded by an approved manual or electronic
process until such automation is actually installed.

## 2. Public license

Accepted project code is distributed publicly under AGPL-3.0-or-later unless a
specific file clearly states another compatible license.

Waters Legacy Trust may also license project code separately under proprietary
commercial terms where it has the necessary rights.

## 3. Create a focused branch

Use a descriptive branch name and keep unrelated changes separate.

Examples:

- `fix/open-dec-boundary-balance`
- `feature/spatial-telemetry-store`
- `docs/reciprocity-assumptions`

## 4. Preserve status boundaries

Label claims and modules accurately.

Use the repository's maturity distinctions:

- CANONICAL
- NUMERICALLY VERIFIED
- EXPERIMENTAL
- LEGACY / COMPATIBILITY

Do not promote an experimental or calibrated result to a canonical or
experimentally confirmed claim without evidence.

## 5. Canonical mathematics

Changes to the finite canonical kernel require:

1. an explicit mathematical definition;
2. regression tests;
3. compatibility analysis;
4. documentation of any changed invariant;
5. explanation of whether the change is a correction, extension, or breaking
   canonical revision.

Do not introduce older Z_114, SO(13), "64-bit spacetime", 3/6/9, or similar
historical labels into the canonical kernel unless they are separately and
rigorously derived and reviewed.

## 6. Research physics and numerical models

New physical or numerical claims should include, where relevant:

- governing equations;
- units and conventions;
- assumptions;
- boundary and initial conditions;
- calibration inputs;
- numerical tolerances;
- conservation or covariance checks;
- comparison against an independent oracle where practical;
- falsification or external validation criteria.

Calibration to a known result must be described as calibration, not derivation.

## 7. Robotics, XR, manufacturing, and hardware

Contributions involving physical systems must fail closed by default.

Do not:

- silently enable real hardware;
- bypass workspace, deadman, replay, authorization, or stop controls;
- claim a software stop is equivalent to physical power removal;
- describe simulation or mock behavior as certified hardware performance.

Real hardware integrations should include timeouts, status reporting, error
handling, and documentation of independent physical safety requirements.

## 8. Security and API changes

Do not commit:

- production credentials;
- private keys;
- passwords;
- secret API tokens;
- customer data.

Public API changes should include authentication/authorization analysis and
tests appropriate to the affected surface.

## 9. Licensing and third-party material

Identify third-party code, assets, datasets, models, standards content, or other
licensed materials.

Do not submit material if you lack the right to contribute it under the CLA and
the project's licensing model.

## 10. Testing

For ordinary changes, run the relevant test subset and the core checks.

Typical commands:

```bash
uv sync --group dev --extra scientific
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest
```

API or integration changes may require:

```bash
uv sync --group dev --extra api --extra scientific
```

Pull requests should leave required CI checks green.

## 11. Documentation

Update documentation when behavior, interfaces, mathematical definitions,
commercial product boundaries, safety assumptions, or user-facing commands
change.

The single authoritative white paper is:

`white_paper.md`

## 12. Pull request description

A good pull request should state:

- what changed;
- why it changed;
- affected modules;
- maturity/status classification;
- tests performed;
- safety impact, if any;
- licensing or third-party-material impact, if any.

## 13. Review and merge

Waters Legacy Trust may request changes, reject a contribution, or delay merge
for mathematical, scientific, security, safety, licensing, product, or
maintenance reasons.

Questions:
waterslegacytrust@gmail.com
