# Declared-state recurrence and persistent phase history

The Matrix Engine is intended to model observed behavior and explore alternative
possibilities. A candidate is not excluded for being unfamiliar. Each model
must make its assumptions, state variables, units and consequences explicit so
that useful, failed and undecided results can be distinguished. Model identity
and evidence boundaries support that exploration; popularity is not a test.

This optional diagnostic makes one of those distinctions executable: returning
to the same visible position does not necessarily return the same state.
It reuses the existing canonical 36-tick clock rather than changing its algebra
or physical interpretation. No existing engine defaults are changed.

## Three different return questions

1. **Position return:** do the declared representative points return within
   their length tolerance?
2. **Declared-state return:** do position, velocity, relative orientation,
   wrapped phase and every declared internal scalar return, with separate
   channel tolerances?
3. **History return:** is exact integer winding unchanged?

History is not automatically a new physical degree of freedom. An ordinary
periodic oscillator can return physically after a full turn while its recorded
turn count advances. `winding_is_state` is an explicit required comparison
policy: use true only when the declared model treats that history as state.
This policy control does not itself implement a force or coupling to winding.

Snapshots record unique component identities, model identity, units, proper 3D
rotations, canonical wrapped phases and named internal scalars. Winding is
serialized as an exact canonical integer string, preserving arbitrarily large
turn counts without relying on a browser's floating-point integer range.
Negative ticks use Euclidean division, so reverse paths cross zero consistently.
No winding is inferred from undersampled wrapped phases.

Comparisons reject changed models/units, inconsistent inventories, missing
tolerances, invalid rotations, nonfinite values and incompatible state schemas.
They return per-channel maximum errors and the identities of failing components.
Position/velocity distances and rotation skew use stable hypotenuse calculations;
tests prevent extremely small resolved changes from vanishing through squared-
norm underflow. This is still floating-point comparison, not arbitrary precision.

## Connection to the actual breathing assembly

`scripts/report_assembly_recurrence.py` uses the existing 69-component fixed
assembly at currents +1 and -1. Its representative point for each component
is the center of its enclosing bounds. Common scale and signed drive current
are declared internal variables; orientation is the deformation rotation
relative to the reference, not each tube's absolute spatial frame. The adapter
does not claim that representative points alone describe arbitrary geometry.
Here the fixed source geometry, two host-cut definitions and the common scale
map specify the shape separately.

The adapter assigns 36 canonical routing ticks to one prescribed size cycle.
That alignment is a dimensionless experiment assumption, not a measured timing
law or a consequence of the clock algebra. Source hashes, including the adapter
script, contribute to model identity. Units are reference length, reference
length per phase, radians and explicitly named dimensionless/current channels.
The reported absolute tolerances are numerical controls, not sensor calibration.

At tick 18, every representative point and the scale return to their initial
values, but motion is reversed and wrapped phase differs by pi. The position
check passes and the declared-state check rejects recurrence. At tick 36,
the declared cyclic state returns while all 69 winding histories advance by one.
Both results hold for positive and negative current.

An injected internal-current change is detected even though positions match.
Serialization restores the tick-35 snapshot exactly. The retained phase/winding
reconstruct the clock tick and reproduce the prescribed tick-36 snapshot.
This is a prescribed-model replay check, not a restart of autonomous material
dynamics. Unit tests also cover negative crossings, reverse steps and a turn
count beyond ordinary floating-point exact-integer range.

## Reproduction and validation

```sh
uv run python -m pytest tests/test_declared_state_recurrence.py tests/test_canonical_polarity_clock.py
uv run python scripts/report_assembly_recurrence.py --output-dir artifacts/assembly-recurrence
```

The linked batch passes 32 tests. Both assembly report cases pass all acceptance
assertions. Ruff check and formatting pass. Full snapshots and per-component
failure/history records regenerate in the output directory; the compact report
and source hashes are in
[assembly-recurrence-summary.json](experiments/assembly-recurrence-summary.json).
The dedicated experimental workflow repeats tests and report checks.

This is completeness relative to the declared state only. Undeclared energy,
material memory, phase of another mode, chemistry, higher-dimensional state or
history-dependent forces cannot be inferred from these fields. The current
schema is a 3D diagnostic, not a replacement for abstract 13D state handling.
Additional channels need explicit units, tolerances and appropriate geometry.

## Next experiments

Use these diagnostics to compare common-phase and traveling-phase patterns,
and models with versus without an explicit memory coupling. Declare the graph,
reference cycles, coupling law, damping, forcing, delays, observable and resource
cost before comparing outcomes. Alternative laws can be explored under separate
model identities; their predictions still require checks against observations
before being described as reproducing the outside world.

Relative inward folding still needs a correspondence from the recovered
compliant hinge specimen to the flow assembly, or a separately justified
nonuniform deformation. The new recorder makes state comparisons inspectable;
it supplies neither that deformation nor material forces, energy closure,
emergent motion or recursive dynamics. These remain open in the recovery queue.
