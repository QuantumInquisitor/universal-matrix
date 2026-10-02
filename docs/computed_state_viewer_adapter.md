# Computed-state science viewer adapter

The current repository contains several visualizers, but none is a validated direct consumer of
the powered material time-series report. This adapter therefore defines the data contract first
instead of modifying a visualizer to display invented state.

## Contract

`scripts/export_fold_material_viewer_frames.py` reads a computed powered-material report and
emits ordered frames. Every frame includes:

- physical time in seconds,
- each module's generalized coordinates and rates,
- reserve energy,
- delivered work,
- damping, conversion and leakage losses,
- external input energy,
- connector potential and work ledgers, and
- the 22-body geometry generated from the same module state.

Source geometry remains in metres. For rendering systems that expect unit-scale coordinates,
the adapter additionally supplies `vertices_display` using an explicit
`display_m_per_unit` conversion. The original metre coordinates are never discarded.

## Spatial policy

Each unequal-size module remains in its own local material frame. The adapter intentionally
does not assign arbitrary world-space offsets, orientations or a recursive embedding. A global
placement must come from the later geometry-to-network or material-to-flow correspondence work.

## Next integration gate

After the adapter and powered report pass remote validation, one existing repository viewer can
be updated to consume one adapter frame at a time and then replay the ordered frame sequence.
That viewer should expose provenance, units and the energy ledgers alongside geometry so a
reviewer can distinguish computed state from decoration.
