# R18 chiral-consistency source audit

The existing implementation supplies finite-lattice diagnostics and representation
bookkeeping. A globally compatible fermion-measure prescription and its complete
gauge-variation/anomaly consistency remain open. This audit advances R18's scope
review; it does not close its original completion requirement.

Source snapshot: `84be1a0510be5f3ca3bbf8ed3f7d3b304ace06c9`.
The [evidence map](r18-chiral-evidence-map.json) records exact Git blob identities
for each implementation and test file. These are repository-object identities,
not raw working-tree hashes affected by Windows line endings. No source,
test implementation, physical input, tolerance or solver criterion changes here.

## Existing capabilities and their limits

| Capability | Source and existing controls | What the evidence does not establish |
| --- | --- | --- |
| U(1), SU(2), SU(3), product-group overlap | [Non-Abelian operator](../../src/nonabelian_overlap_dirac_lattice.py), [product operator](../../src/product_group_overlap_dirac.py); corresponding covariance/Ginsparg-Wilson tests identified in the map | A global Weyl measure; older requests merely to add these operators are superseded |
| Weyl projector curvature | [Curvature](../../src/weyl_measure_curvature.py); reconstruction, covariance, transport, antisymmetry, reality and gauge-invariance controls | Local curvature alone does not prove an uncancelled anomaly or global consistency |
| Loop transport and local Stokes comparison | [Holonomy](../../src/weyl_measure_holonomy.py), [Stokes](../../src/weyl_measure_stokes.py); basis invariance, orientation, shrinking-loop controls | The local consistency comparison already exists; it is not an anomaly-cancellation theorem |
| Weyl determinant | [Determinant](../../src/weyl_determinant.py); square trivial-index blocks, basis-phase covariance and rectangular rejection | A globally compatible phase choice across patches/sectors |
| Charged U(1) gauge-orbit response | [Gauge orbit](../../src/u1_weyl_gauge_orbit.py), especially `infinitesimal_gauge_measure_response`; endpoint, neutral/zero, basis-invariance and path-refinement controls | The response-specific test establishes finiteness at one fixture, not a quantitative identity with local anomaly density |
| Local index density and covariant candidate | [U(1) ledger](../../src/u1_chiral_anomaly_ledger.py); sum-to-index, gauge invariance and vectorlike cancellation controls | The candidate is explicitly distinguished from the consistent anomaly of a global measure |
| Supplied-representation consistency | [Product ledger](../../src/product_group_anomaly_ledger.py); local coefficients and SU(2) fundamental-doublet parity, including a neutral odd-doublet negative control | Supported parity is implemented; it is not a construction over arbitrary gauge sectors or a derivation of the physical spectrum |

The exact source/test pairings in the map distinguish inspected implementations
from newly executed checks. Targeted inspection of current `src` and `tests`
found no quantitative comparison calling both
`infinitesimal_gauge_measure_response` and `local_overlap_index_density`.
This bounded search is not a claim about every historical branch.

## Remaining obligations and next step

1. Specify a globally compatible measure/phase convention, including transitions
   between patches and topologically nontrivial sectors.
2. Derive the expected gauge-response/local-density relation under that convention,
   distinguishing consistent and covariant anomalies and stating the continuum
   normalization. Do this before choosing a numerical comparison or fitting any
   coefficient to its output.
3. Address non-Abelian local measure/anomaly treatment and global consistency
   beyond the supported fundamental SU(2) parity bookkeeping.
4. Keep complete representation assumptions and consistency checks separate from
   any claim that the kernel derives a physical spectrum.

The smallest subsequent study is a declared-convention derivation for item 2,
followed only then by a bounded comparison using the existing diagnostics.
The remaining global obligations are not discharged by that local comparison.
These boundaries agree with section 8 of the
[gauge-orbit document](../u1_weyl_gauge_orbit_v0.1.md) and section 11 of the
[product-ledger document](../product_group_anomaly_ledger_v0.1.md). Older gap lists
remain historical; their already-implemented intermediate steps are not reopened.

## Verification performed for this audit

- 41 existing tests across Weyl curvature, holonomy, Stokes, determinant,
  U(1) gauge orbit and U(1) anomaly ledger passed locally in 5.04 seconds.
- Eight existing product-group anomaly-ledger tests passed together with the
  12 documentation-governance checks (20 tests in 2.36 seconds).
- The non-Abelian/product-overlap sources and test inventories were inspected;
  their test suites were not rerun for this documentation-only audit.
- All 41 task contracts and statuses are preserved. Only R18's latest evidence
  and next action, plus its readable row, change; its earlier next action is
  retained in a historical snapshot. No full remote CI success for
  this audit is implied by these local checks.

Reproduction of the 49 focused checks uses the existing test files:

```text
python -m pytest tests/test_weyl_measure_curvature.py tests/test_weyl_measure_holonomy.py tests/test_weyl_measure_stokes.py tests/test_weyl_determinant.py tests/test_u1_weyl_gauge_orbit.py tests/test_u1_chiral_anomaly_ledger.py tests/test_product_group_anomaly_ledger.py -q
python -m pytest tests/test_documentation_governance.py -q
```
