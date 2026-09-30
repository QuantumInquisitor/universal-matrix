# Combined fixed aperture assembly

This optional audit joins the retained network, first aperture, inner and outer
attachments, and replacement edge 2 into one fixed inventory. It does not change
the default engine builder. The second aperture removes material from the
original host envelope; the inventory records both modified host identities.
The returned component names describe this fixed construction, not an arbitrary
geometry validator or a global field evaluator.

`combined_components()` returns the original enclosing host geometry. Its raw
tuple must not be rendered or sampled as the cut assembly: use the first
aperture's `modified_host_contains` and `SecondAperture.contains` to define the
actual host domains. All pairs are classified with declared contacts allowed;
the result does not assert strictly positive clearance at joined faces.

There are 69 components (66 conduits and three junctions), 2,346 unique unordered
pairs, four directed routes, 62 internal route interfaces, and eight declared
junction ports. The 13 original edge-2 components are removed. Both modified
hosts, `edge3_piece_10` and `edge3_piece_00`, remain under their stable identities.

The general enclosing-geometry classifier handles 2,334 pairs. Twelve remaining
pairs use freshly evaluated fixed aperture/bend bounds, a nested smoothstep
bound, or exact junction support-plane checks. Subtracting the aperture from a
host cannot invalidate an original separation bound for that host envelope.
The special aperture bounds check the removed region separately. Each report
lists every pair and the source of its classification; the inventories in the
earlier attachment report overlap and must not be added together.

Each conduit belongs to exactly one directed route. Interfaces check exact cap
positions, orientations, radii and signed current, with sampled vector-field
matching. Junction connections additionally check the entire connector lies
outside its port support plane. All declared junction ports are accounted for
once and signed current balances at every junction. Geometric touching alone
does not establish a flow connection; the separate interface registry does.

## Reproduce and inspect

```sh
uv run python -m pytest tests/test_toroidal_combined_aperture.py
uv run python scripts/report_combined_aperture.py --output-dir artifacts/combined-aperture
```

The six cases are I = +/-1, +/-2e-8 and +/-7. The compact snapshot is
[combined-aperture-summary.json](experiments/combined-aperture-summary.json).
Full reports include component/removed-host inventories, routes, all pair
classifications, interface residuals, port residuals and junction balances.
Source hashes accompany the summary. The dedicated aperture workflow reruns
the tests and both exporters. Rejection controls include tiny cap displacement,
radius mismatch, reversed orientation, wrong signed flux and nonfinite fields.

## What this establishes and what remains

The result covers the complete pair inventory of this specific fixed assembly
at the six sampled nonzero currents. Bounds use floating-point arithmetic,
not formal interval verification. Vector-field comparisons are finite samples.
The original enclosing host geometry is intentionally conservative except at
the two explicitly removed aperture regions. This is not evidence for arbitrary
deformations, generalized branching, every possible current or a physical device.

This static audit alone leaves continuous breathing open. Freeze the permitted deformation
map and follow all components, host cuts, ports, Jacobians and clearance bounds
through an out-and-back cycle. Collision-free static endpoints would not prove
the intervening motion safe. The central stagnating streamline, wall-opening
feasibility, material laws, energy accounting, emergent motion and recursive
coupling remain unresolved. No time-crystal subsystem is installed by this audit.

Follow-up: [prescribed common breathing](toroidal_assembly_breathing_v0.1.md)
now transports this entire static assembly under the recovered 0.9–1.1 size
cycle. Its continuous similarity argument covers that restricted motion;
relative folding and physical motion remain open as described above.

The [earlier integration report](toroidal_aperture_integration_v0.1.md) records
the individual constructions. Its per-module whole-network flags remain false;
this separate audit adds the combined static inventory only.
