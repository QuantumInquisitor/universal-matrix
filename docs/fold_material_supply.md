# Powered unequal-size material graph

This checkpoint extends the geometry-derived unequal-size material graph with explicit finite
energy reserves and bounded external replenishment. It does not introduce a new material
calibration or claim an autonomous energy source.

## Owned quantities

Each module carries separate cumulative ledgers for:

1. stored reserve energy,
2. work delivered from the reserve into the mechanical state,
3. damping, conversion and leakage losses, and
4. externally supplied energy.

Connector potential is owned once per graph edge. Delivered work is a transfer from the
reserve to the mechanical account, not additional stored energy. External input is counted
once as an energy source and is not folded into losses or delivered work.

The material restoring force is the gradient of the geometry-derived constitutive potential
used by `fold_material_multiscale.py`. Point inertia, geometric bias, mapped connector
forces and the previously declared conditional size laws are retained.

## External supply law

For module size `s`, reserve capacity is `2e-5 s^3 J`. The ideal replenishing source is
bounded by `power_density * s^2` and decreases linearly to zero as the reserve approaches
capacity. This power scaling is chosen so integrated supplied energy follows the existing
conditional `s^3` energy similarity over a time scale proportional to length.

This is a synthetic source law. It is not a battery, piezoelectric harvester, electromagnetic
power stage or other validated hardware model.

## Controls

The report contains four cases:

- `powered`: finite reserves plus bounded external replenishment,
- `source_off`: identical model with external power set to zero,
- `omitted_reserve_debit`: a deliberately incorrect node account that delivers work without
  charging that work to its reserve, and
- `fine_powered`: the powered case with tighter integration settings.

For valid cases, node mechanical energy, reserve energy, connector energy, group totals and
external input are checked separately. The powered trajectory is also evaluated with the input
term intentionally omitted from postprocessing; that diagnostic must expose otherwise
unidentified energy equal to the missing source contribution.

## Viewer handoff

`export_fold_material_viewer_frames.py` converts saved powered samples into a viewer-neutral
time-series contract. Metre geometry is preserved, and a separate normalized display coordinate
is added. Modules remain in their verified local frames. No global placement of the four-module
graph is invented before a physical or geometric correspondence is established.

## Limits

The present run is short and bounded. It does not establish sustained breathing, arbitrary-depth
recursive stability, measured material response, physical supply hardware, spatial joint
validity, or correspondence to the separate 69-domain flow assembly.
