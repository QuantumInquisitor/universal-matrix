# Geometry experiment checkpoint

These are optional reference experiments, not a completed physical engine.

## Reproduce from the repository root

```text
uv sync --group test --group lint --extra scientific --extra visualization
uv run python scripts/report_recursive_mirror_motion.py artifacts/geometry/recursive-mirror-motion.json
uv run python scripts/report_lynchpin_relative_motion.py artifacts/geometry/lynchpin-relative-motion.json
uv run python scripts/report_lynchpin_finite_panels.py artifacts/geometry/finite-panel-surfaces.json
uv run python scripts/report_lynchpin_breathing.py artifacts/geometry/breathing-fold.json
uv run python scripts/report_lynchpin_connected.py --output artifacts/geometry --audit
```

## Validation

```text
uv run python -m pytest -q tests/test_recursive_mirror_motion_control.py tests/test_lynchpin_relative_motion_control.py tests/test_lynchpin_finite_panel_control.py tests/test_lynchpin_breathing_control.py tests/test_lynchpin_connected_control.py tests/test_lynchpin_geometry_audit.py tests/test_stella_octangula_register_bridge.py tests/test_recursive_omniverse_contract.py
```

The dedicated workflow repeats these commands. Full generated traces and figures
are written under `artifacts/geometry`; they are not required to run the tests.
The checked-in summary records the original bounded results, including failures.
Reproduction regenerates evidence; it does not certify hardware or omitted physics.

## Reference documents

- [recursive_mirror_motion_control_v0.1](../recursive_mirror_motion_control_v0.1.md)
- [lynchpin_relative_motion_control_v0.1](../lynchpin_relative_motion_control_v0.1.md)
- [lynchpin_finite_panel_control_v0.1](../lynchpin_finite_panel_control_v0.1.md)
- [lynchpin_breathing_control_v0.1](../lynchpin_breathing_control_v0.1.md)
- [lynchpin_connected_control_v0.1](../lynchpin_connected_control_v0.1.md)

## Older local work

[The inventory](local-work-inventory.json) records 607 local code/report files by
relative collection path, size and SHA-256. It excludes dependency folders,
existing repository clones, binary source documents and synced project sources.
The inventory preserves provenance; it does not upload those files or establish
that every historical scratch result is production-ready. Toroidal aperture/
fan-out candidates, source/corpus work, XR assets and other older experiments
remain locally preserved and require their own promotion review.
