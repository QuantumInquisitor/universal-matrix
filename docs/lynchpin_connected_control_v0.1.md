# Connected folding and breathing specimen

30 September 2026. Optional geometric reference, with existing engine behavior preserved.

## Result

Six compliant pentagonal cores are now connected through four shared hubs and
twelve flexible bridge capsules. Their incidence graph is connected throughout
the prescribed relative fold and 0.9–1.1 common size cycle. This is an explicit
new joint specimen, not a claim that the original rigid common-origin panels
can flex without strain.

| Control | Body pairs | Checked pair-time intervals | Smallest retained clearance bound after breathing |
| --- | ---: | ---: | ---: |
| 3 spatial coordinates | 231 | 1,208 | 0.00003773014616157734 |
| 4 mathematical coordinates | 231 | 1,193 | 0.00015314435529788402 |

All intervals pass. The connected, breathing, finite-panel and relative-motion
test batch has **57 passing tests**; Ruff checks and formatting pass. Bounds are dimensionless and conservative, not the exact
minimum distance. Every inventory contains 195 fully separated pairs, 12
bridge-to-panel attachment pairs, 12 bridge-to-own-hub pairs and 12 bridge pairs
sharing a hub. Unique pair counts and gap-free coverage of phase [0,1] were
independently checked on the exported results.

## Construction and contact argument

Panel cores retain the coefficient collar 0.15 and isotropic offset radius 0.01.
Hub i is a radius-0.05 ball centered at `0.5 r_i`. For panel ij, two radius-0.008
bridge capsules connect `0.5 r_i` to `0.5 r_i + 0.17 r_j`, and conversely.
The bridge tips lie in their panels' convex hulls; their bases lie in the hubs.
All lengths, offset radii and contact regions scale with the breathing factor.

Intended contact is localized rather than blanket-exempted:

- Any intersection with the bridge's own hub is inside that actual hub ball.
- For bridges sharing a hub, an initial centerline length 0.042 and its radius
  0.008 offset fit in the radius-0.05 hub. The remaining capsule tails are
  continuously separated from each other, so no contact can occur outside it.
- At a panel attachment, a terminal centerline length 0.072 and its offset fit
  inside a radius-0.08 ball centered at the bonded tip. The remaining bridge
  prefix stays separated from the panel. This ball bounds the attachment region;
  it is not an additional material body.

For each required separation, vertex support planes give a lower bound on
convex-body distance. Analytic vertex-speed bounds extend midpoint checks over
whole phase intervals. Common positive breathing rescales each bound by at
least 0.9. Computation uses floating-point arithmetic, not rigorous outward-
rounded interval arithmetic. The 4D control is mathematical geometry, not a
claim of a realizable four-spatial-dimensional material.

## Reproduction and artifacts

From the local repository, run:

```text
uv run python scripts/report_lynchpin_connected.py --output artifacts/geometry --audit
uv run python -m pytest -q -p no:cacheprovider tests/test_lynchpin_connected_control.py tests/test_lynchpin_breathing_control.py tests/test_lynchpin_finite_panel_control.py tests/test_lynchpin_relative_motion_control.py
```

`connected-fold-3d.json` and `connected-fold-4d.json` contain the full interval
audits. `connected-fold-scene.json` contains 202 frames, all body vertices and
offset radii, source hashes and motion/provenance labels. `connected-fold.png`
shows computed 3D panel midsurfaces, hub surfaces and bridge centerlines, with
the same camera and axes at four phases. It is an inspection figure, not a new
VR viewer or a full material-volume rendering.

## Next gates

Material stiffness, strain limits, actuator energy, dissipation, moving-boundary
flow and recursive multi-cell coupling are unresolved. The clearance result
does not prove a mechanically feasible material, the entire fractal, a measured
breathing period or a time crystal. Current motion is prescribed. The separate
Q-ball trace still has no consistent measured period.

The parallel research assessment is saved in
`the separately reviewed time-crystal subsystem research`. Its proposed
spatial-order and collective-dynamics controls are new queue entries, not
completed experiments.
