# Recursive drive-history and downstream-loading replay

The isolated pair experiment established that the local 1:2 recursive interface is dynamically
self-similar across the tested scales. The same interface behaves very differently when embedded
at levels 2 and 3 of the full recursive cascade.

This checkpoint separates two causes without changing any force or scale law:

1. upstream drive history, because an embedded parent does not follow the isolated-pair reference
   trajectory;
2. downstream loading, because an embedded child is simultaneously connected to its own children.

## Full-tree parent capture

The complete 15-module tree is integrated through 0.1 seconds using the existing equations.
Representative parent-child edges are:

- level 1: node 0 to node 1;
- level 2: node 1 to node 3;
- level 3: node 3 to node 7.

The parent generalized coordinate and rate histories are retained on the original 0.0005 second
grid. Cubic Hermite interpolation uses both coordinate and rate data to provide parent state at
Runge-Kutta substeps without changing the full-tree trajectory.

## Free-child replay

For each interface the actual embedded parent trajectory is prescribed, but only the child module
is allowed to respond. This keeps the upstream history while removing downstream loading.

The ratio

free replay child-work fraction / isolated-pair child-work fraction

therefore measures the effect of upstream drive history relative to the corresponding freely
evolving isolated pair.

## Loaded-subtree replay

The same prescribed parent trajectory is then applied to the child with its real downstream
subtree restored:

- level-1 child plus levels 2 and 3;
- level-2 child plus level 3;
- level-3 child alone.

The ratio

loaded replay fraction / free replay fraction

measures the additional downstream-loading effect.

Because the loaded replay contains the same child subtree and is driven by the actual parent
history, it should reproduce the representative embedded edge within numerical interpolation
error. Level 3 is an especially direct control because its free and loaded replays are identical.

## Energy accounting

Each replay owns its child/subtree mechanical energy, damping losses, internal connector
potentials and the external parent-child connector potential. The prescribed parent's cumulative
endpoint work is the only external energy boundary. The replay balance is therefore

subtree energy change + parent endpoint work = 0.

## Limits

This is a causal decomposition inside the current synthetic recursive equations. It does not
validate a physical recursive assembly, measured material response, arbitrary depth or the
material-to-69-component flow correspondence. No coefficient is tuned to improve replay fidelity.
